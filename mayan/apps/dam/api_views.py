import logging
from datetime import timedelta
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models import Count
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from mayan.apps.documents.models import Document
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.acls.models import AccessControlList
from mayan.apps.rest_api import generics as mayan_generics
from mayan.apps.rest_api.pagination import MayanPageNumberPagination

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

    @action(detail=False, methods=['post'])
    def analyze(self, request):
        serializer = AnalyzeDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document_instance = serializer.validated_data['document_instance']
        document_id = document_instance.pk
        ai_service = serializer.validated_data.get('ai_service', 'openai')
        analysis_type = serializer.validated_data.get('analysis_type', 'classification')

        try:
            document = self.get_document(document_id)
            self._assert_analysis_permission(document)

            if not self._is_analyzable(document):
                return Response(
                    {
                        'error': 'Document type not supported for AI analysis',
                        'error_code': 'UNSUPPORTED_DOC_TYPE',
                        'supported_types': ['pdf', 'image', 'docx', 'doc', 'txt']
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            result = analyze_document_with_ai.delay(document.id)

            logger.info(
                'AI analysis requested',
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
                    'status': 'pending',
                    'document_id': document_id,
                    'created_at': timezone.now().isoformat()
                },
                status=status.HTTP_202_ACCEPTED
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
                extra={'user_id': request.user.id, 'document_id': document_id, 'error': str(exc)}
            )
            return Response(
                {
                    'error': 'Analysis failed',
                    'error_code': 'ANALYSIS_ERROR',
                    'detail': str(exc) if settings.DEBUG else 'An error occurred'
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
        analyzable_types = ['pdf', 'image', 'docx', 'doc', 'txt']
        latest_file = document.files.order_by('-timestamp').first()
        if not latest_file or not latest_file.mimetype:
            return False

        mime_type = latest_file.mimetype.lower()
        return any(token in mime_type for token in analyzable_types)

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

    def get_queryset(self):
        queryset = Document.objects.select_related('document_type').prefetch_related(
            'files', 'metadata__metadata_type', 'versions', 'tags'
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
            'providers': provider_breakdown
        })
