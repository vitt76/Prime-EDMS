import logging
from datetime import timedelta
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models import Count
from django.utils import timezone

from io import BytesIO

from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from mayan.apps.documents.models import Document, DocumentType
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.acls.models import AccessControlList
from mayan.apps.document_comments.models import Comment
from mayan.apps.rest_api import generics as mayan_generics
from mayan.apps.rest_api.pagination import MayanPageNumberPagination

from mayan.apps.cabinets.models import Cabinet

from . import settings as dam_settings
from .models import DocumentAIAnalysis, DAMMetadataPreset
from .permissions import permission_ai_analysis_create
from .serializers import (
    AnalyzeDocumentSerializer, BulkAnalyzeDocumentsSerializer,
    DAMDocumentDetailSerializer, DAMDocumentListSerializer,
    DAMMetadataPresetSerializer, DocumentAIAnalysisSerializer
)
from .tasks import analyze_document_with_ai
from .throttles import AIAnalysisThrottle

logger = logging.getLogger(__name__)

# Try to import Celery app for worker availability check
try:
    from celery import current_app
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    current_app = None


class DocumentAIAnalysisViewSet(ModelViewSet):
    """
    API endpoint for managing AI analysis of documents.
    """
    serializer_class = DocumentAIAnalysisSerializer
    queryset = DocumentAIAnalysis.objects.select_related('document').prefetch_related('document__files')
    renderer_classes = (JSONRenderer,)
    permission_classes = (IsAuthenticated,)
    throttle_classes = (AIAnalysisThrottle,)

    def get_document(self, document_id):
        try:
            document = Document.objects.get(pk=document_id)
        except Document.DoesNotExist:
            logger.warning(
                'Document not found during AI analysis operation',
                extra={'user_id': self.request.user.id, 'document_id': document_id}
            )
            raise

        AccessControlList.objects.check_access(
            obj=document,
            permissions=(permission_document_view,),
            user=self.request.user
        )

        return document

    def _assert_analysis_permission(self, document):
        AccessControlList.objects.check_access(
            obj=document,
            permissions=(permission_ai_analysis_create,),
            user=self.request.user
        )

    def _check_celery_available(self):
        """Check if Celery worker is available."""
        if not CELERY_AVAILABLE:
            return False, 'Celery is not installed or configured'
        
        try:
            # Try to inspect active workers
            inspect = current_app.control.inspect()
            active_workers = inspect.active()
            
            if active_workers is None:
                return False, 'No Celery workers are currently active'
            
            # Check if 'tools' queue has workers (the queue used by analyze_document_with_ai)
            # We'll assume workers are available if we can get the inspect response
            return True, None
        except Exception as e:
            logger.error(f'Failed to check Celery worker availability: {e}')
            # Return False to prevent task execution when Celery is unavailable
            return False, f'Celery worker check failed: {str(e)}'

    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """
        Start AI analysis for a document.
        
        Validates document, permissions, and starts Celery task.
        """
        # Log method entry for debugging
        logger.info(
            'AI analysis endpoint called',
            extra={
                'user_id': request.user.id if request.user else None,
                'method': request.method,
                'path': request.path,
                'data_keys': list(request.data.keys()) if hasattr(request, 'data') else None
            }
        )
        
        document_id = None
        
        try:
            # Step 1: Validate serializer
            logger.debug(
                'Starting AI analysis request',
                extra={'user_id': request.user.id, 'request_data': request.data}
            )
            
            # Pass request context to serializer for access control checks
            try:
                serializer = AnalyzeDocumentSerializer(
                    data=request.data,
                    context={'request': request}
                )
            except Exception as serializer_init_error:
                logger.exception(
                    'Failed to create serializer for AI analysis',
                    extra={
                        'user_id': request.user.id,
                        'error': str(serializer_init_error),
                        'error_type': type(serializer_init_error).__name__
                    }
                )
                return Response(
                    {
                        'error': 'Failed to process request',
                        'error_code': 'SERIALIZER_INIT_ERROR',
                        'detail': str(serializer_init_error) if settings.DEBUG else 'Failed to initialize request validator'
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            try:
                if not serializer.is_valid():
                    logger.warning(
                        'AI analysis request validation failed',
                        extra={
                            'user_id': request.user.id,
                            'errors': serializer.errors
                        }
                    )
                    return Response(
                        {
                            'error': 'Invalid request data',
                            'error_code': 'VALIDATION_ERROR',
                            'detail': serializer.errors
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Exception as validation_error:
                logger.exception(
                    'Exception during serializer validation',
                    extra={
                        'user_id': request.user.id,
                        'error': str(validation_error),
                        'error_type': type(validation_error).__name__
                    }
                )
                return Response(
                    {
                        'error': 'Validation error',
                        'error_code': 'VALIDATION_EXCEPTION',
                        'detail': str(validation_error) if settings.DEBUG else 'An error occurred during request validation'
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            try:
                document_instance = serializer.validated_data['document_instance']
                document_id = document_instance.pk
            except (KeyError, AttributeError) as e:
                logger.error(
                    'Failed to get document_instance from validated_data',
                    extra={
                        'user_id': request.user.id,
                        'error': str(e),
                        'validated_data_keys': list(serializer.validated_data.keys()) if hasattr(serializer, 'validated_data') else None
                    }
                )
                return Response(
                    {
                        'error': 'Invalid request data',
                        'error_code': 'MISSING_DOCUMENT_INSTANCE',
                        'detail': 'Document instance not found in validated data'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            ai_service = serializer.validated_data.get('ai_service', 'openai')
            analysis_type = serializer.validated_data.get('analysis_type', 'classification')
            
            logger.info(
                'AI analysis request validated',
                extra={
                    'user_id': request.user.id,
                    'document_id': document_id,
                    'ai_service': ai_service,
                    'analysis_type': analysis_type
                }
            )
            
            # Step 2: Use document from serializer (already validated with access control)
            # document_instance is already a Document object with access checked
            document = document_instance
            logger.debug(
                'Document retrieved from serializer (access already validated)',
                extra={'user_id': request.user.id, 'document_id': document_id}
            )
            
            # Additional validation step - check document access again for extra safety
            try:
                # Verify access one more time (defense in depth)
                AccessControlList.objects.check_access(
                    obj=document,
                    permissions=(permission_document_view,),
                    user=request.user
                )
                logger.debug(
                    'Document access verified',
                    extra={'user_id': request.user.id, 'document_id': document_id}
                )
            except PermissionDenied:
                logger.warning(
                    'Permission denied to view document for AI analysis',
                    extra={'user_id': request.user.id, 'document_id': document_id}
                )
                return Response(
                    {
                        'error': 'Permission denied to access document',
                        'error_code': 'PERMISSION_DENIED'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            except Exception as access_error:
                logger.exception(
                    'Error verifying document access',
                    extra={
                        'user_id': request.user.id,
                        'document_id': document_id,
                        'error': str(access_error),
                        'error_type': type(access_error).__name__
                    }
                )
                return Response(
                    {
                        'error': 'Error verifying document access',
                        'error_code': 'ACCESS_VERIFICATION_ERROR',
                        'detail': str(access_error) if settings.DEBUG else 'Error verifying document access'
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Step 3: Check analysis permission
            try:
                self._assert_analysis_permission(document)
                logger.debug(
                    'Analysis permission verified',
                    extra={'user_id': request.user.id, 'document_id': document_id}
                )
            except PermissionDenied:
                logger.warning(
                    'Permission denied for AI analysis',
                    extra={'user_id': request.user.id, 'document_id': document_id}
                )
                return Response(
                    {
                        'error': 'Permission denied to perform AI analysis',
                        'error_code': 'PERMISSION_DENIED'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Step 4: Check if document is analyzable
            if not self._is_analyzable(document):
                # Get latest file for logging
                latest_file = document.files.order_by('-timestamp').first()
                document_type = latest_file.mimetype if latest_file and latest_file.mimetype else 'unknown'
                
                logger.warning(
                    'Document type not supported for AI analysis',
                    extra={
                        'user_id': request.user.id,
                        'document_id': document_id,
                        'document_type': document_type
                    }
                )
                return Response(
                    {
                        'error': 'Document type not supported for AI analysis',
                        'error_code': 'UNSUPPORTED_DOC_TYPE',
                        'supported_types': ['pdf', 'image', 'docx', 'doc', 'txt']
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Step 4.5: Check file size before analysis (with type-specific limits)
            from .utils import get_max_file_size_for_mime_type, format_file_size
            
            latest_file = document.files.order_by('-timestamp').first()
            if latest_file and latest_file.size:
                mime_type = latest_file.mimetype or 'application/octet-stream'
                max_file_size = get_max_file_size_for_mime_type(mime_type)
                
                if latest_file.size > max_file_size:
                    file_size_str = format_file_size(latest_file.size)
                    max_size_str = format_file_size(max_file_size)
                    
                    logger.warning(
                        'File size exceeds maximum for AI analysis',
                        extra={
                            'user_id': request.user.id,
                            'document_id': document_id,
                            'file_size': latest_file.size,
                            'max_size': max_file_size,
                            'mime_type': mime_type,
                            'file_type': 'image' if mime_type.startswith('image/') else 'document'
                        }
                    )
                    return Response(
                        {
                            'error': (
                                f'File size ({file_size_str}) exceeds maximum allowed size '
                                f'({max_size_str}) for {mime_type} files'
                            ),
                            'error_code': 'FILE_TOO_LARGE',
                            'file_size': latest_file.size,
                            'max_size': max_file_size,
                            'mime_type': mime_type,
                            'file_size_formatted': file_size_str,
                            'max_size_formatted': max_size_str
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Step 5: Check Celery availability
            celery_available, celery_error = self._check_celery_available()
            if not celery_available:
                logger.error(
                    'Celery worker not available for AI analysis',
                    extra={
                        'user_id': request.user.id,
                        'document_id': document_id,
                        'error': celery_error
                    }
                )
                return Response(
                    {
                        'error': 'AI analysis service is temporarily unavailable',
                        'error_code': 'SERVICE_UNAVAILABLE',
                        'detail': celery_error or 'Celery worker is not running'
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Step 6: Start Celery task
            try:
                logger.info(
                    'Starting Celery task for AI analysis',
                    extra={
                        'user_id': request.user.id,
                        'document_id': document_id
                    }
                )
                
                result = analyze_document_with_ai.delay(document.id)
                
                logger.info(
                    'AI analysis task started successfully',
                    extra={
                        'user_id': request.user.id,
                        'document_id': document_id,
                        'task_id': result.id,
                        'ai_service': ai_service,
                        'analysis_type': analysis_type
                    }
                )
                
                return Response(
                    {
                        'success': True,
                        'analysis_id': result.id,
                        'task_id': result.id,
                        'status': 'pending',
                        'document_id': document_id,
                        'created_at': timezone.now().isoformat()
                    },
                    status=status.HTTP_202_ACCEPTED
                )
                
            except Exception as celery_exc:
                logger.exception(
                    'Failed to start Celery task for AI analysis',
                    extra={
                        'user_id': request.user.id,
                        'document_id': document_id,
                        'error': str(celery_exc),
                        'error_type': type(celery_exc).__name__
                    }
                )
                return Response(
                    {
                        'error': 'Failed to start AI analysis task',
                        'error_code': 'TASK_START_FAILED',
                        'detail': str(celery_exc) if settings.DEBUG else 'Failed to queue analysis task. Please ensure Celery worker is running.'
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        except PermissionDenied:
            logger.warning(
                'Permission denied during AI analysis request',
                extra={'user_id': request.user.id, 'document_id': document_id}
            )
            return Response(
                {
                    'error': 'Permission denied',
                    'error_code': 'PERMISSION_DENIED'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as exc:
            logger.exception(
                'Unhandled error while starting AI analysis',
                extra={
                    'user_id': request.user.id,
                    'document_id': document_id,
                    'error': str(exc),
                    'error_type': type(exc).__name__,
                    'traceback': True
                }
            )
            return Response(
                {
                    'error': 'Analysis failed',
                    'error_code': 'ANALYSIS_ERROR',
                    'detail': str(exc) if settings.DEBUG else 'An unexpected error occurred while starting AI analysis'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def reanalyze(self, request):
        analysis_id = request.data.get('analysis_id')
        force = bool(request.data.get('force', False))

        if not analysis_id:
            return Response(
                {
                    'error': 'analysis_id is required',
                    'error_code': 'MISSING_PARAMETER'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            previous_analysis = DocumentAIAnalysis.objects.select_related('document').get(pk=analysis_id)
            document = self.get_document(previous_analysis.document.pk)
            self._assert_analysis_permission(document)

            if not force and not self._can_reanalyze(previous_analysis):
                logger.warning(
                    'Re-analysis rejected due to rate limit',
                    extra={'user_id': request.user.id, 'analysis_id': analysis_id}
                )
                return Response(
                    {
                        'error': 'Re-analysis too soon, please wait',
                        'error_code': 'RATE_LIMITED',
                        'retry_after': 3600
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            result = analyze_document_with_ai.delay(document.id)

            logger.info(
                'AI re-analysis requested',
                extra={
                    'user_id': request.user.id,
                    'document_id': document.id,
                    'previous_analysis_id': analysis_id,
                    'new_task_id': result.id
                }
            )

            return Response(
                {
                    'success': True,
                    'new_analysis_id': result.id,
                    'status': 'pending',
                    'document_id': document.id,
                    'created_at': timezone.now().isoformat()
                },
                status=status.HTTP_202_ACCEPTED
            )

        except DocumentAIAnalysis.DoesNotExist:
            return Response(
                {
                    'error': 'Analysis not found',
                    'error_code': 'NOT_FOUND'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Document.DoesNotExist:
            return Response(
                {
                    'error': 'Document not found',
                    'error_code': 'NOT_FOUND'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionDenied:
            logger.warning(
                'Permission denied during AI reanalysis',
                extra={'user_id': request.user.id, 'analysis_id': analysis_id}
            )
            return Response(
                {
                    'error': 'Permission denied',
                    'error_code': 'PERMISSION_DENIED'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as exc:
            logger.exception(
                'Unhandled error during AI re-analysis',
                extra={'user_id': request.user.id, 'analysis_id': analysis_id, 'error': str(exc)}
            )
            return Response(
                {
                    'error': 'Re-analysis failed',
                    'error_code': 'ANALYSIS_ERROR',
                    'detail': str(exc) if settings.DEBUG else 'An error occurred'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='bulk-analyze')
    def bulk_analyze(self, request):
        """
        Start bulk AI analysis for multiple documents.
        """
        serializer = BulkAnalyzeDocumentsSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            from .tasks import bulk_analyze_documents

            bulk_id = str(uuid4())
            result = bulk_analyze_documents.delay(
                document_ids=validated_data['document_ids'],
                ai_service=validated_data['ai_service'],
                analysis_type=validated_data['analysis_type'],
                user_id=request.user.id,
                bulk_id=bulk_id
            )

            logger.info(
                'Bulk AI analysis requested',
                extra={
                    'user_id': request.user.id,
                    'bulk_id': bulk_id,
                    'task_id': result.id,
                    'doc_count': len(validated_data['document_ids']),
                    'ai_service': validated_data['ai_service'],
                    'analysis_type': validated_data['analysis_type']
                }
            )

            return Response(
                {
                    'success': True,
                    'bulk_analysis_id': bulk_id,
                    'document_count': len(validated_data['document_ids']),
                    'status': 'pending',
                    'ai_service': validated_data['ai_service'],
                    'created_at': timezone.now().isoformat(),
                    'message': 'Bulk analysis started. Results will be available shortly.'
                },
                status=status.HTTP_202_ACCEPTED
            )

        except Exception as exc:
            logger.exception(
                'Error starting bulk analysis',
                extra={'user_id': request.user.id, 'error': str(exc)}
            )
            return Response(
                {
                    'success': False,
                    'error': 'Failed to start bulk analysis',
                    'error_code': 'BULK_ANALYSIS_ERROR'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @staticmethod
    def _is_analyzable(document):
        """
        Check if document can be analyzed by AI.
        
        Args:
            document: Document instance to check
            
        Returns:
            bool: True if document type is supported for AI analysis
        """
        analyzable_types = ['pdf', 'image', 'docx', 'doc', 'txt']
        
        try:
            latest_file = document.files.order_by('-timestamp').first()
            if not latest_file:
                logger.debug(f'Document {document.id} has no files')
                return False
            
            if not latest_file.mimetype:
                logger.debug(f'Document {document.id} file has no mimetype')
                return False

            mime_type = latest_file.mimetype.lower()
            is_analyzable = any(token in mime_type for token in analyzable_types)
            
            if not is_analyzable:
                logger.debug(
                    f'Document {document.id} type {mime_type} is not analyzable'
                )
            
            return is_analyzable
        except Exception as e:
            logger.warning(
                f'Error checking if document {document.id} is analyzable: {e}'
            )
            return False

    @staticmethod
    def _can_reanalyze(analysis):
        min_interval = timedelta(hours=1)
        return timezone.now() - analysis.created >= min_interval


class DAMMetadataPresetViewSet(ModelViewSet):
    """
    API endpoint for managing DAM metadata presets.
    """
    serializer_class = DAMMetadataPresetSerializer
    queryset = DAMMetadataPreset.objects.all()
    renderer_classes = (JSONRenderer,)

    @action(detail=True, methods=['post'])
    def test_preset(self, request, pk=None):
        """
        Test a metadata preset with a sample document.
        """
        try:
            preset = DAMMetadataPreset.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(
                {
                    'error': 'Preset not found',
                    'error_code': 'NOT_FOUND'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        document_id = request.data.get('document_id')
        if document_id is None:
            return Response(
                {
                    'error': 'document_id is required',
                    'error_code': 'MISSING_PARAMETER'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            document_id = int(document_id)
            if document_id < 1:
                raise ValueError()
        except (TypeError, ValueError):
            logger.warning(
                'Invalid document_id supplied to test_preset',
                extra={'user_id': request.user.id, 'preset_id': pk, 'value': document_id}
            )
            return Response(
                {
                    'error': 'Invalid document_id. Must be a positive integer.',
                    'error_code': 'INVALID_PARAMETER',
                    'received_value': document_id
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            document = Document.objects.get(pk=document_id)
        except Document.DoesNotExist:
            logger.warning(
                f'test_preset called with non-existent document {document_id}',
                extra={'user_id': request.user.id, 'preset_id': pk}
            )
            return Response(
                {
                    'error': f'Document {document_id} not found',
                    'error_code': 'DOCUMENT_NOT_FOUND'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            AccessControlList.objects.check_access(
                obj=document,
                permissions=(permission_document_view,),
                user=request.user
            )
        except PermissionDenied:
            logger.warning(
                f'User {request.user.id} tried to test preset on document {document_id} without permission',
                extra={
                    'user_id': request.user.id,
                    'document_id': document_id,
                    'preset_id': pk
                }
            )
            return Response(
                {
                    'error': 'Permission denied for this document',
                    'error_code': 'PERMISSION_DENIED'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            extracted_metadata = self._apply_preset_to_document(preset, document)
            logger.info(
                f'Successfully tested preset {pk} on document {document_id}',
                extra={
                    'user_id': request.user.id,
                    'document_id': document_id,
                    'preset_id': pk,
                    'extracted_fields': len(extracted_metadata)
                }
            )

            return Response(
                {
                    'success': True,
                    'message': f'Preset {preset.name} applied successfully',
                    'preset_name': preset.name,
                    'document_id': document_id,
                    'metadata_extracted': extracted_metadata,
                    'field_count': len(extracted_metadata)
                },
                status=status.HTTP_200_OK
            )

        except Exception as exc:
            logger.exception(
                f'Error testing preset {pk} on document {document_id}',
                extra={
                    'user_id': request.user.id,
                    'document_id': document_id,
                    'preset_id': pk,
                    'error': str(exc)
                }
            )
            return Response(
                {
                    'error': 'Failed to apply preset',
                    'error_code': 'PRESET_APPLICATION_ERROR',
                    'detail': str(exc) if settings.DEBUG else 'An error occurred'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @staticmethod
    def _apply_preset_to_document(preset, document: Document) -> dict:
        """
        Apply a metadata preset to a document and return extracted values.
        """
        extracted = {}
        document_text = ''
        if hasattr(document, 'get_text') and callable(document.get_text):
            try:
                document_text = document.get_text()
            except Exception as exc:
                logger.warning(
                    'Failed to read document text during preset test',
                    extra={'document_id': document.id, 'error': str(exc)}
                )

        fields = getattr(preset, 'fields', None)
        extractor = getattr(preset, 'extract_field_value', None)

        if not fields or not extractor:
            return extracted

        for field in fields.all():
            try:
                value = extractor(field, document_text)
                if value:
                    extracted[field.name] = {
                        'value': value,
                        'field_type': getattr(field, 'field_type', 'unknown'),
                        'confidence': getattr(field, 'confidence', 1.0)
                    }
            except Exception as exc:
                logger.warning(
                    f'Error extracting field {getattr(field, "name", "unknown")}',
                    extra={'preset_id': preset.id, 'error': str(exc)}
                )
                continue

        return extracted


class AIAnalysisStatusView(mayan_generics.GenericAPIView):
    """
    API endpoint to get AI analysis status for a document.
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)

    def get(self, request, *args, **kwargs):
        document_id = request.query_params.get('document_id')

        if not document_id:
            return Response(
                {'error': 'document_id query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            document = Document.objects.get(pk=document_id)
        except Document.DoesNotExist:
            return Response(
                {'error': 'Document not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            AccessControlList.objects.check_access(
                obj=document,
                permissions=(permission_document_view,),
                user=request.user
            )
        except PermissionDenied:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            ai_analysis = document.ai_analysis
        except DocumentAIAnalysis.DoesNotExist:
            return Response({
                'document_id': document_id,
                'status': 'not_analyzed',
                'message': 'Document has not been analyzed with AI yet'
            })

        return Response({
            'document_id': document_id,
            'analysis_id': ai_analysis.id,
            'status': ai_analysis.analysis_status,
            'provider': ai_analysis.ai_provider,
            'completed_at': ai_analysis.analysis_completed,
            'has_description': bool(ai_analysis.ai_description),
            'tags_count': len(ai_analysis.get_ai_tags_list()),
            'categories_count': len(ai_analysis.categories or []),
            'has_alt_text': bool(ai_analysis.alt_text),
            'updated_at': ai_analysis.updated
        })


class DAMDocumentDetailView(generics.RetrieveAPIView):
    """
    Retrieve structured DAM document detail as JSON.
    """
    serializer_class = DAMDocumentDetailSerializer
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    queryset = Document.objects.all()
    lookup_url_kwarg = 'document_id'  # URL uses document_id, not pk

    def get_queryset(self):
        queryset = Document.objects.select_related(
            'document_type', 'ai_analysis'
        ).prefetch_related(
            'files', 'metadata__metadata_type', 'versions', 'tags',
            # Prefetch активной версии и её страниц для правильного определения version_active_file_id
            'versions__version_pages__content_type',
            'versions__version_pages__content_object',
            'versions__version_pages'
        )

        return AccessControlList.objects.restrict_queryset(
            permission=permission_document_view,
            queryset=queryset,
            user=self.request.user
        )

    def get_serializer_context(self):
        return {'request': self.request}

    def get_object(self):
        document = super().get_object()
        AccessControlList.objects.check_access(
            obj=document,
            permissions=(permission_document_view,),
            user=self.request.user
        )
        return document


class DAMDocumentListView(generics.ListAPIView):
    """
    List documents with their DAM analysis status.
    """
    serializer_class = DAMDocumentListSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = MayanPageNumberPagination
    renderer_classes = (JSONRenderer,)

    def get_queryset(self):
        queryset = Document.objects.order_by('-id').select_related('ai_analysis').prefetch_related('files')

        # Apply search filter if provided
        search_query = self.request.query_params.get('q') or self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(label__icontains=search_query)

        return AccessControlList.objects.restrict_queryset(
            permission=permission_document_view,
            queryset=queryset,
            user=self.request.user
        )


class DocumentProcessingStatusView(generics.RetrieveAPIView):
    """
    Phase B4: Processing Status API
    
    GET /api/v4/documents/{id}/processing_status/
    
    Returns the current processing status for a document including:
    - Overall status (pending, processing, complete, failed)
    - Progress percentage (0-100)
    - Current step description
    - AI analysis readiness flags
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    
    def get(self, request, pk):
        try:
            document = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            return Response(
                {'error': 'Document not found', 'error_code': 'NOT_FOUND'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            AccessControlList.objects.check_access(
                obj=document,
                permissions=(permission_document_view,),
                user=request.user
            )
        except PermissionDenied:
            return Response(
                {'error': 'Access denied', 'error_code': 'PERMISSION_DENIED'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get AI analysis record if exists
        try:
            ai_analysis = document.ai_analysis
            
            # Map analysis_status to frontend-friendly status
            status_mapping = {
                'pending': 'processing',
                'processing': 'processing', 
                'completed': 'complete',
                'failed': 'failed'
            }
            
            processing_status = status_mapping.get(
                ai_analysis.analysis_status, 'processing'
            )
            
            return Response({
                'document_id': pk,
                'status': processing_status,
                'progress': ai_analysis.progress,
                'current_step': ai_analysis.current_step or self._get_default_step(ai_analysis),
                'ai_tags_ready': bool(ai_analysis.ai_tags),
                'ai_description_ready': bool(ai_analysis.ai_description),
                'ai_colors_ready': bool(ai_analysis.dominant_colors),
                'ocr_ready': self._check_ocr_status(document),
                'thumbnail_ready': self._check_thumbnail_status(document),
                'analysis_provider': ai_analysis.ai_provider or None,
                'error_message': ai_analysis.error_message if ai_analysis.analysis_status == 'failed' else None,
                'task_id': ai_analysis.task_id,
                'started_at': ai_analysis.created.isoformat() if ai_analysis.created else None,
                'completed_at': ai_analysis.analysis_completed.isoformat() if ai_analysis.analysis_completed else None
            })
            
        except DocumentAIAnalysis.DoesNotExist:
            # No AI analysis exists - check if document has files
            has_files = document.files.exists()
            
            return Response({
                'document_id': pk,
                'status': 'pending' if has_files else 'no_files',
                'progress': 0,
                'current_step': 'Waiting for AI analysis' if has_files else 'No files uploaded',
                'ai_tags_ready': False,
                'ai_description_ready': False,
                'ai_colors_ready': False,
                'ocr_ready': self._check_ocr_status(document),
                'thumbnail_ready': self._check_thumbnail_status(document),
                'analysis_provider': None,
                'error_message': None,
                'task_id': None,
                'started_at': None,
                'completed_at': None
            })
    
    def _get_default_step(self, ai_analysis):
        """Get default step description based on status"""
        if ai_analysis.analysis_status == 'pending':
            return 'Queued for AI analysis'
        elif ai_analysis.analysis_status == 'processing':
            return 'AI analysis in progress'
        elif ai_analysis.analysis_status == 'completed':
            return 'Analysis complete'
        elif ai_analysis.analysis_status == 'failed':
            return 'Analysis failed'
        return 'Unknown status'
    
    def _check_ocr_status(self, document):
        """Check if OCR has been performed on the document"""
        try:
            # Check if document has parsed content
            latest_version = document.versions.order_by('-timestamp').first()
            if latest_version:
                # Check for OCR content in pages
                for page in latest_version.pages.all()[:1]:
                    if hasattr(page, 'content_object') and page.content_object:
                        content = getattr(page.content_object, 'content', None)
                        if content:
                            return True
            return False
        except Exception:
            return False
    
    def _check_thumbnail_status(self, document):
        """Check if thumbnails have been generated"""
        try:
            latest_version = document.versions.order_by('-timestamp').first()
            if latest_version and latest_version.pages.exists():
                return True
            return False
        except Exception:
            return False


class DocumentOCRExtractView(mayan_generics.GenericAPIView):
    """
    API endpoint for extracting OCR text from a document.
    
    POST /api/v4/documents/{document_id}/ocr/extract/
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    
    def post(self, request, document_id):
        """
        Start OCR extraction for a document.
        """
        try:
            document = Document.objects.get(pk=document_id)
        except Document.DoesNotExist:
            return Response(
                {'error': 'Document not found', 'error_code': 'NOT_FOUND'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        try:
            AccessControlList.objects.check_access(
                obj=document,
                permissions=(permission_document_view,),
                user=request.user
            )
        except PermissionDenied:
            return Response(
                {'error': 'Access denied', 'error_code': 'PERMISSION_DENIED'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get latest version
        latest_version = document.versions.order_by('-timestamp').first()
        if not latest_version:
            return Response(
                {'error': 'Document has no versions', 'error_code': 'NO_VERSIONS'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Start OCR task
        try:
            from mayan.apps.ocr.tasks import task_document_version_ocr_process
            
            task = task_document_version_ocr_process.delay(
                document_version_id=latest_version.pk,
                user_id=request.user.pk if request.user.is_authenticated else None
            )
            
            logger.info(
                'OCR extraction requested',
                extra={
                    'user_id': request.user.id,
                    'document_id': document_id,
                    'version_id': latest_version.pk,
                    'task_id': task.id
                }
            )
            
            return Response(
                {
                    'success': True,
                    'task_id': task.id,
                    'status': 'processing',
                    'document_id': document_id,
                    'version_id': latest_version.pk
                },
                status=status.HTTP_202_ACCEPTED
            )
        except Exception as e:
            logger.error(
                f'Failed to start OCR extraction: {e}',
                extra={'user_id': request.user.id, 'document_id': document_id}
            )
            return Response(
                {
                    'error': 'Failed to start OCR extraction',
                    'error_code': 'OCR_START_FAILED',
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DAMDashboardStatsView(mayan_generics.GenericAPIView):
    """
    Provide dashboard statistics for DAM analyses.
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)

    def get(self, request, *args, **kwargs):
        documents_queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_document_view,
            queryset=Document.objects.all(),
            user=request.user
        )

        total_documents = documents_queryset.count()

        analyses_queryset = DocumentAIAnalysis.objects.filter(
            document__in=documents_queryset
        )

        total_analyses = analyses_queryset.count()
        completed_analyses = analyses_queryset.filter(analysis_status='completed').count()
        processing_analyses = analyses_queryset.filter(analysis_status='processing').count()
        pending_analyses = analyses_queryset.filter(analysis_status='pending').count()
        failed_analyses = analyses_queryset.filter(analysis_status='failed').count()

        provider_breakdown = [
            {
                'provider': entry['ai_provider'] or 'unknown',
                'count': entry['count']
            }
            for entry in analyses_queryset.values('ai_provider').annotate(count=Count('ai_provider')).order_by('-count')
        ]

        # Comments statistics for current user
        now = timezone.now()
        last_7_days = now - timedelta(days=7)
        last_24_hours = now - timedelta(hours=24)
        
        # Get comments for documents user has access to
        # Count all comments to accessible documents (not just user's own comments)
        comments_queryset = Comment.objects.filter(
            document__in=documents_queryset
        )
        
        comments_last_7_days = comments_queryset.filter(
            submit_date__gte=last_7_days
        ).count()
        
        comments_last_24_hours = comments_queryset.filter(
            submit_date__gte=last_24_hours
        ).count()

        return Response({
            'documents': {
                'total': total_documents,
                'with_analysis': total_analyses,
                'without_analysis': max(total_documents - total_analyses, 0)
            },
            'analyses': {
                'completed': completed_analyses,
                'processing': processing_analyses,
                'pending': pending_analyses,
                'failed': failed_analyses
            },
            'providers': provider_breakdown,
            'comments': {
                'last_7_days': comments_last_7_days,
                'last_24_hours': comments_last_24_hours
            }
        })


class YandexDiskBaseAPIView(generics.GenericAPIView):
    """
    Base helpers for Yandex Disk API views.
    """
    permission_classes = (IsAuthenticated,)

    def get_client(self):
        from .services.yandex_disk import YandexDiskClient

        token = dam_settings.setting_yandex_disk_token.value
        if not token:
            logger.warning('Yandex Disk token is not configured.')
            self.permission_denied(
                self.request,
                message='Yandex Disk token is not configured.'
            )
        return YandexDiskClient(token=token)


class APIYandexDiskFolderDetailView(YandexDiskBaseAPIView):
    """
    get:
    Return folder content (subfolders and files) for a given Yandex Disk path.

    Path is passed as base64-encoded string in the URL for safety.
    """

    def get(self, request, encoded_path: str, *args, **kwargs):
        import base64

        try:
            # Восстанавливаем padding, так как на фронтенде он убирается
            padding = '=' * (-len(encoded_path) % 4)
            encoded_with_padding = f'{encoded_path}{padding}'
            raw_path = base64.urlsafe_b64decode(encoded_with_padding.encode()).decode()
        except Exception:
            return Response(
                {'detail': 'Invalid folder path encoding.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        client = self.get_client()
        try:
            items = client.list_directory(path=raw_path)
        except Exception as exc:
            logger.error('Failed to list Yandex Disk directory %s: %s', raw_path, exc)
            return Response(
                {'detail': 'Failed to list Yandex Disk directory.'},
                status=status.HTTP_502_BAD_GATEWAY
            )

        folders = []
        files = []
        for item in items:
            entry = {
                'name': item.get('name'),
                'path': item.get('path'),
                'type': item.get('type'),
                'size': item.get('size'),
            }
            if item.get('type') == 'dir':
                folders.append(entry)
            elif item.get('type') == 'file':
                files.append(entry)

        return Response(
            {
                'path': raw_path,
                'folders': folders,
                'files': files,
                'total_count': len(items),
            },
            status=status.HTTP_200_OK
        )


class APIYandexDiskFileDownloadView(YandexDiskBaseAPIView):
    """
    get:
    Download a file from Yandex Disk.
    
    Path is passed as base64-encoded string in the URL.
    """
    
    def get(self, request, encoded_path: str, *args, **kwargs):
        import base64
        from django.http import StreamingHttpResponse
        
        try:
            # Add padding if needed for base64 decoding (same as in preview view)
            encoded_path_padded = encoded_path
            padding = len(encoded_path) % 4
            if padding:
                encoded_path_padded += '=' * (4 - padding)
            raw_path = base64.urlsafe_b64decode(encoded_path_padded.encode()).decode()
        except Exception as exc:
            logger.error('Failed to decode Yandex Disk path %s: %s', encoded_path, exc)
            return Response(
                {'detail': 'Invalid file path encoding.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        client = self.get_client()
        try:
            # Get file stream from Yandex Disk
            file_stream = client.iter_file(path=raw_path)
            
            # Get file info for headers
            file_info_response = client.session.get(
                url=f'{client.base_url}/resources',
                params={'path': raw_path, 'fields': 'size'},
                timeout=client.timeout
            )
            client._raise_for_status(file_info_response)
            file_info = file_info_response.json()
            filename = raw_path.split('/')[-1] or 'file'
            
            response = StreamingHttpResponse(file_stream, content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            if file_info.get('size'):
                response['Content-Length'] = str(file_info['size'])
            
            return response
        except Exception as exc:
            logger.error('Failed to download Yandex Disk file %s: %s', raw_path, exc)
            return Response(
                {'detail': 'Failed to download file from Yandex Disk.'},
                status=status.HTTP_502_BAD_GATEWAY
            )


class APIYandexDiskFilePreviewView(YandexDiskBaseAPIView):
    """
    get:
    Get preview/thumbnail of an image file from Yandex Disk.
    
    Path is passed as base64-encoded string in the URL.
    Supports query params: width, height
    """
    from rest_framework.renderers import JSONRenderer
    renderer_classes = (JSONRenderer,)  # Required by DRF, but we'll bypass it
    
    def perform_content_negotiation(self, request, force=False):
        """
        Override to skip content negotiation - we return binary data.
        """
        # Return a dummy renderer and media type to satisfy DRF
        from rest_framework.renderers import JSONRenderer
        return (JSONRenderer(), 'application/json')
    
    def get(self, request, encoded_path: str, *args, **kwargs):
        import base64
        from django.http import StreamingHttpResponse
        
        try:
            # Add padding if needed for base64 decoding
            encoded_path_padded = encoded_path
            padding = len(encoded_path) % 4
            if padding:
                encoded_path_padded += '=' * (4 - padding)
            raw_path = base64.urlsafe_b64decode(encoded_path_padded.encode()).decode()
        except Exception as exc:
            logger.error('Failed to decode Yandex Disk path %s: %s', encoded_path, exc)
            return Response(
                {'detail': 'Invalid file path encoding.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        client = self.get_client()
        try:
            # Get preview URL from Yandex Disk (if available)
            # For now, just return the file stream
            # TODO: Implement proper preview with resizing if Yandex Disk API supports it
            file_stream = client.iter_file(path=raw_path)
            
            # Determine content type from file extension
            filename = raw_path.split('/')[-1] or 'file'
            ext = filename.split('.')[-1].lower()
            content_type = 'image/jpeg' if ext in ['jpg', 'jpeg'] else \
                          'image/png' if ext == 'png' else \
                          'image/gif' if ext == 'gif' else \
                          'image/webp' if ext == 'webp' else \
                          'application/octet-stream'
            
            response = StreamingHttpResponse(file_stream, content_type=content_type)
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            # Allow CORS if needed
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET'
            response['Access-Control-Allow-Headers'] = 'Authorization'
            
            return response
        except Exception as exc:
            logger.error('Failed to get Yandex Disk file preview %s: %s', raw_path, exc)
            return Response(
                {'detail': 'Failed to get file preview from Yandex Disk.'},
                status=status.HTTP_502_BAD_GATEWAY
            )


class APIYandexDiskCopyToDAMView(YandexDiskBaseAPIView):
    """
    post:
    Copy a file from Yandex Disk into DAM as a new Document.

    Expected payload:
    {
        "yandex_path": "disk:/folder/file.jpg",
        "document_type_id": 1,          # optional, defaults to first available
        "cabinet_id": 5,                # optional
        "label": "My File"              # optional
    }
    """

    def post(self, request, *args, **kwargs):
        from django.core.files import File

        yandex_path = request.data.get('yandex_path')
        if not yandex_path:
            return Response(
                {'detail': 'Field \"yandex_path\" is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        document_type_id = request.data.get('document_type_id')
        cabinet_id = request.data.get('cabinet_id')
        label = request.data.get('label')

        document_type = None
        if document_type_id:
            document_type = DocumentType.objects.filter(pk=document_type_id).first()
        if not document_type:
            document_type = DocumentType.objects.order_by('label').first()
        if not document_type:
            return Response(
                {'detail': 'No document type available for Yandex Disk import.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        client = self.get_client()

        try:
            chunks = client.iter_file(path=yandex_path)
            buffer = BytesIO()
            for chunk in chunks:
                buffer.write(chunk)
            buffer.seek(0)
        except Exception as exc:
            logger.error('Failed to download Yandex Disk file %s: %s', yandex_path, exc)
            return Response(
                {'detail': 'Failed to download file from Yandex Disk.'},
                status=status.HTTP_502_BAD_GATEWAY
            )

        document_label = label or yandex_path.split('/')[-1] or 'Yandex Disk file'
        document = Document.objects.create(
            document_type=document_type,
            label=document_label
        )

        document.file_new(
            file_object=File(buffer, name=document_label),
            filename=document_label
        )

        if cabinet_id:
            try:
                cabinet = Cabinet.objects.get(pk=cabinet_id)
                cabinet.document_add(document)
            except Cabinet.DoesNotExist:
                logger.warning('Cabinet %s does not exist, skipping document_add.', cabinet_id)

        return Response(
            {'document_id': document.pk},
            status=status.HTTP_201_CREATED
        )


class APIYandexDiskCopyFromDAMView(YandexDiskBaseAPIView):
    """
    post:
    Copy a file from DAM into Yandex Disk.

    Expected payload:
    {
        "document_id": 123,
        "yandex_path": "disk:/folder/",
        "filename": "copy.jpg"  # optional
    }
    """

    def post(self, request, *args, **kwargs):
        document_id = request.data.get('document_id')
        yandex_path = request.data.get('yandex_path')
        filename = request.data.get('filename')

        if not document_id or not yandex_path:
            return Response(
                {'detail': 'Fields \"document_id\" and \"yandex_path\" are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            document = Document.objects.get(pk=document_id)
        except Document.DoesNotExist:
            return Response(
                {'detail': 'Document does not exist.'},
                status=status.HTTP_404_NOT_FOUND
            )

        document_file = document.files.order_by('-timestamp').first()
        if not document_file:
            return Response(
                {'detail': 'Document has no files to upload.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        target_filename = filename or document_file.filename or f'document-{document.pk}'
        if not yandex_path.endswith('/'):
            yandex_path = yandex_path + '/'
        full_path = f'{yandex_path}{target_filename}'

        client = self.get_client()
        try:
          with document_file.open() as file_object:
              client.upload_file(path=full_path, file_data=file_object.read())
        except Exception as exc:
            logger.error('Failed to upload file %s to Yandex Disk: %s', full_path, exc)
            return Response(
                {'detail': 'Failed to upload file to Yandex Disk.'},
                status=status.HTTP_502_BAD_GATEWAY
            )

        return Response(
            {'path': full_path},
            status=status.HTTP_201_CREATED
        )
