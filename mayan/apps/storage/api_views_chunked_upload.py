"""
API Views for Chunked Upload.
Phase B3.2 - Chunked Upload API Support.
Phase B3.3 - Error Handling.
"""
import logging

from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models import Document, DocumentType
from mayan.apps.documents.permissions import permission_document_create

from .literals import (
    CHUNKED_UPLOAD_STATUS_PENDING,
    CHUNKED_UPLOAD_STATUS_UPLOADING,
    CHUNKED_UPLOAD_STATUS_COMPLETED,
    CHUNKED_UPLOAD_DEFAULT_CHUNK_SIZE,
    CHUNKED_UPLOAD_MAX_PARTS
)
from .serializers_chunked_upload import (
    ChunkedUploadInitSerializer,
    ChunkedUploadInitResponseSerializer,
    ChunkedUploadAppendSerializer,
    ChunkedUploadAppendResponseSerializer,
    ChunkedUploadCompleteSerializer,
    ChunkedUploadCompleteResponseSerializer,
    ChunkedUploadStatusSerializer,
    ChunkedUploadAbortSerializer,
    S3ErrorResponseSerializer
)

logger = logging.getLogger(__name__)


class S3ServiceUnavailable(APIException):
    """Custom exception for S3 service unavailability."""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('S3 storage service is temporarily unavailable. Please try again later.')
    default_code = 's3_unavailable'


class S3UploadFailed(APIException):
    """Custom exception for S3 upload failures."""
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = _('Failed to communicate with S3 storage.')
    default_code = 's3_error'


class ChunkedUploadInitView(APIView):
    """
    Initialize a chunked upload session.
    
    POST /api/v4/uploads/init/
    
    Request:
    {
        "filename": "video.mp4",
        "total_size": 524288000,  // 500MB
        "content_type": "video/mp4",
        "document_type_id": 1
    }
    
    Response:
    {
        "upload_id": "uuid",
        "s3_key": "uploads/2024/01/01/abc123_video.mp4",
        "chunk_size": 10485760,  // Recommended chunk size (10MB)
        "max_chunks": 10000
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChunkedUploadInitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        filename = serializer.validated_data['filename']
        total_size = serializer.validated_data['total_size']
        content_type = serializer.validated_data.get('content_type', 'application/octet-stream')
        document_type_id = serializer.validated_data.get('document_type_id')
        
        # Check document creation permission
        if document_type_id:
            try:
                document_type = DocumentType.objects.get(pk=document_type_id)
                AccessControlList.objects.check_access(
                    obj=document_type,
                    permissions=(permission_document_create,),
                    user=request.user
                )
            except DocumentType.DoesNotExist:
                return Response(
                    {
                        'error': 'Not Found',
                        'error_code': 'document_type_not_found',
                        'detail': f'Document type with ID {document_type_id} not found'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
        
        try:
            from .services.chunked_upload_service import ChunkedUploadService, S3ServiceUnavailableError
            from .models_chunked_upload import ChunkedUpload
            
            # Initialize S3 multipart upload
            service = ChunkedUploadService()
            s3_result = service.initiate_multipart_upload(filename, content_type)
            
            # Create database record
            upload = ChunkedUpload.objects.create_upload(
                filename=filename,
                total_size=total_size,
                content_type=content_type,
                user=request.user
            )
            upload.s3_key = s3_result['s3_key']
            upload.s3_upload_id = s3_result['upload_id']
            upload.status = CHUNKED_UPLOAD_STATUS_UPLOADING
            upload.save()
            
            logger.info(
                f'Chunked upload initialized: upload_id={upload.upload_id}, '
                f'user={request.user.username}, filename={filename}'
            )
            
            response_data = {
                'upload_id': str(upload.upload_id),
                's3_key': upload.s3_key,
                'chunk_size': CHUNKED_UPLOAD_DEFAULT_CHUNK_SIZE,
                'max_chunks': CHUNKED_UPLOAD_MAX_PARTS
            }
            
            return Response(
                ChunkedUploadInitResponseSerializer(response_data).data,
                status=status.HTTP_201_CREATED
            )
            
        except S3ServiceUnavailableError as e:
            logger.error(f'S3 service unavailable during upload init: {e}')
            return self._s3_error_response(str(e))
        except Exception as e:
            logger.exception(f'Unexpected error during upload init: {e}')
            return Response(
                {
                    'error': 'Internal Server Error',
                    'error_code': 'upload_init_failed',
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _s3_error_response(self, detail):
        """Generate standardized S3 error response."""
        return Response(
            {
                'error': 'Service Unavailable',
                'error_code': 's3_unavailable',
                'detail': detail,
                'retry_after': 30
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


class ChunkedUploadAppendView(APIView):
    """
    Append a chunk to an existing upload.
    
    POST /api/v4/uploads/append/
    
    Form data:
    - upload_id: UUID
    - part_number: 1-10000
    - chunk: File data
    
    Response:
    {
        "upload_id": "uuid",
        "part_number": 1,
        "etag": "\"abc123\"",
        "size": 10485760,
        "uploaded_size": 10485760,
        "progress_percent": 2.0
    }
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = ChunkedUploadAppendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        upload_id = serializer.validated_data['upload_id']
        part_number = serializer.validated_data['part_number']
        chunk = serializer.validated_data['chunk']
        
        try:
            from .models_chunked_upload import ChunkedUpload
            from .services.chunked_upload_service import ChunkedUploadService, S3UploadError
            
            # Get upload record
            try:
                upload = ChunkedUpload.objects.get(upload_id=upload_id)
            except ChunkedUpload.DoesNotExist:
                return Response(
                    {
                        'error': 'Not Found',
                        'error_code': 'upload_not_found',
                        'detail': f'Upload session {upload_id} not found'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verify ownership
            if upload.user and upload.user != request.user:
                return Response(
                    {
                        'error': 'Forbidden',
                        'error_code': 'upload_access_denied',
                        'detail': 'You do not have permission to access this upload'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Verify upload status
            if upload.status not in [CHUNKED_UPLOAD_STATUS_PENDING, CHUNKED_UPLOAD_STATUS_UPLOADING]:
                return Response(
                    {
                        'error': 'Conflict',
                        'error_code': 'upload_not_active',
                        'detail': f'Upload is not active (status: {upload.status})'
                    },
                    status=status.HTTP_409_CONFLICT
                )
            
            # Upload part to S3
            service = ChunkedUploadService()
            chunk_data = chunk.read()
            
            result = service.upload_part(
                s3_key=upload.s3_key,
                upload_id=upload.s3_upload_id,
                part_number=part_number,
                data=chunk_data
            )
            
            # Update upload record
            upload.add_part(part_number, result['etag'], result['size'])
            
            logger.debug(
                f'Chunk uploaded: upload_id={upload_id}, part={part_number}, '
                f'progress={upload.progress_percent}%'
            )
            
            response_data = {
                'upload_id': str(upload.upload_id),
                'part_number': part_number,
                'etag': result['etag'],
                'size': result['size'],
                'uploaded_size': upload.uploaded_size,
                'progress_percent': upload.progress_percent
            }
            
            return Response(
                ChunkedUploadAppendResponseSerializer(response_data).data,
                status=status.HTTP_200_OK
            )
            
        except S3UploadError as e:
            logger.error(f'S3 upload part failed: {e}')
            return Response(
                {
                    'error': 'Bad Gateway',
                    'error_code': 's3_upload_failed',
                    'detail': str(e),
                    'retry_after': 10
                },
                status=status.HTTP_502_BAD_GATEWAY
            )
        except Exception as e:
            logger.exception(f'Unexpected error during chunk append: {e}')
            return Response(
                {
                    'error': 'Internal Server Error',
                    'error_code': 'chunk_append_failed',
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChunkedUploadCompleteView(APIView):
    """
    Complete a chunked upload and create a Document.
    
    POST /api/v4/uploads/complete/
    
    Request:
    {
        "upload_id": "uuid",
        "label": "My Video",
        "description": "Description",
        "document_type_id": 1
    }
    
    Response:
    {
        "upload_id": "uuid",
        "document_id": 123,
        "document_file_id": 456,
        "s3_key": "...",
        "status": "completed"
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChunkedUploadCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        upload_id = serializer.validated_data['upload_id']
        label = serializer.validated_data.get('label')
        description = serializer.validated_data.get('description', '')
        document_type_id = serializer.validated_data.get('document_type_id')
        
        try:
            from .models_chunked_upload import ChunkedUpload
            from .services.chunked_upload_service import ChunkedUploadService, S3UploadError
            from mayan.apps.documents.models import Document, DocumentFile
            
            # Get upload record
            try:
                upload = ChunkedUpload.objects.get(upload_id=upload_id)
            except ChunkedUpload.DoesNotExist:
                return Response(
                    {
                        'error': 'Not Found',
                        'error_code': 'upload_not_found',
                        'detail': f'Upload session {upload_id} not found'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verify ownership
            if upload.user and upload.user != request.user:
                return Response(
                    {
                        'error': 'Forbidden',
                        'error_code': 'upload_access_denied',
                        'detail': 'You do not have permission to access this upload'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Verify upload has parts
            if not upload.parts_info:
                return Response(
                    {
                        'error': 'Bad Request',
                        'error_code': 'no_parts_uploaded',
                        'detail': 'No chunks have been uploaded yet'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get document type
            if document_type_id:
                document_type = DocumentType.objects.get(pk=document_type_id)
            else:
                document_type = DocumentType.objects.first()
                if not document_type:
                    return Response(
                        {
                            'error': 'Configuration Error',
                            'error_code': 'no_document_type',
                            'detail': 'No document types configured'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Complete S3 multipart upload
            service = ChunkedUploadService()
            parts = upload.get_parts_for_complete()
            
            s3_result = service.complete_multipart_upload(
                s3_key=upload.s3_key,
                upload_id=upload.s3_upload_id,
                parts=parts
            )
            
            # Create Document
            document_label = label or upload.filename
            document = Document.objects.create(
                document_type=document_type,
                label=document_label,
                description=description
            )
            
            # Create DocumentFile pointing to S3
            # Note: We store the S3 key in the file field
            document_file = DocumentFile.objects.create(
                document=document,
                filename=upload.filename,
                mimetype=upload.content_type,
                size=upload.uploaded_size,
                comment=f'Uploaded via chunked upload (S3 key: {upload.s3_key})'
            )
            
            # Store S3 reference
            document_file.file.name = upload.s3_key
            document_file.save(update_fields=['file'])
            
            # Mark upload as completed
            upload.mark_completed(document_id=document.id)
            
            logger.info(
                f'Chunked upload completed: upload_id={upload_id}, '
                f'document_id={document.id}, file_id={document_file.id}'
            )
            
            response_data = {
                'upload_id': str(upload.upload_id),
                'document_id': document.id,
                'document_file_id': document_file.id,
                's3_key': upload.s3_key,
                'status': 'completed'
            }
            
            return Response(
                ChunkedUploadCompleteResponseSerializer(response_data).data,
                status=status.HTTP_201_CREATED
            )
            
        except S3UploadError as e:
            logger.error(f'S3 complete multipart failed: {e}')
            upload.mark_failed(str(e))
            return Response(
                {
                    'error': 'Bad Gateway',
                    'error_code': 's3_complete_failed',
                    'detail': str(e)
                },
                status=status.HTTP_502_BAD_GATEWAY
            )
        except Exception as e:
            logger.exception(f'Unexpected error during upload complete: {e}')
            if 'upload' in locals():
                upload.mark_failed(str(e))
            return Response(
                {
                    'error': 'Internal Server Error',
                    'error_code': 'complete_failed',
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChunkedUploadStatusView(APIView):
    """
    Get status of an upload session.
    
    GET /api/v4/uploads/status/<upload_id>/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, upload_id):
        try:
            from .models_chunked_upload import ChunkedUpload
            
            try:
                upload = ChunkedUpload.objects.get(upload_id=upload_id)
            except ChunkedUpload.DoesNotExist:
                return Response(
                    {
                        'error': 'Not Found',
                        'error_code': 'upload_not_found',
                        'detail': f'Upload session {upload_id} not found'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verify ownership
            if upload.user and upload.user != request.user:
                return Response(
                    {
                        'error': 'Forbidden',
                        'error_code': 'upload_access_denied',
                        'detail': 'You do not have permission to access this upload'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            response_data = {
                'upload_id': str(upload.upload_id),
                'filename': upload.filename,
                'total_size': upload.total_size,
                'uploaded_size': upload.uploaded_size,
                'chunks_received': upload.chunks_received,
                'progress_percent': upload.progress_percent,
                'status': upload.status,
                's3_key': upload.s3_key,
                'document_id': upload.document_id,
                'error_message': upload.error_message,
                'datetime_created': upload.datetime_created,
                'datetime_updated': upload.datetime_updated
            }
            
            return Response(
                ChunkedUploadStatusSerializer(response_data).data,
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.exception(f'Error getting upload status: {e}')
            return Response(
                {
                    'error': 'Internal Server Error',
                    'error_code': 'status_failed',
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChunkedUploadAbortView(APIView):
    """
    Abort an upload session.
    
    POST /api/v4/uploads/abort/
    
    Request:
    {
        "upload_id": "uuid"
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChunkedUploadAbortSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        upload_id = serializer.validated_data['upload_id']
        
        try:
            from .models_chunked_upload import ChunkedUpload
            
            try:
                upload = ChunkedUpload.objects.get(upload_id=upload_id)
            except ChunkedUpload.DoesNotExist:
                return Response(
                    {
                        'error': 'Not Found',
                        'error_code': 'upload_not_found',
                        'detail': f'Upload session {upload_id} not found'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verify ownership
            if upload.user and upload.user != request.user:
                return Response(
                    {
                        'error': 'Forbidden',
                        'error_code': 'upload_access_denied',
                        'detail': 'You do not have permission to access this upload'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Abort the upload
            upload.abort()
            
            logger.info(f'Upload aborted: upload_id={upload_id}, user={request.user.username}')
            
            return Response(
                {
                    'upload_id': str(upload_id),
                    'status': 'aborted',
                    'message': 'Upload session aborted successfully'
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.exception(f'Error aborting upload: {e}')
            return Response(
                {
                    'error': 'Internal Server Error',
                    'error_code': 'abort_failed',
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



