"""
Phase B4: Processing Status API Views

Provides `/api/v4/documents/{id}/processing_status/` endpoint for frontend polling.

Features:
- Real-time processing status for document uploads
- Progress percentage (0-100) for frontend spinners
- Current step description for user feedback
- AI analysis, OCR, and thumbnail readiness flags
- ETag/Last-Modified headers for efficient caching
"""
import hashlib
import logging
from datetime import datetime

from django.core.exceptions import PermissionDenied
from django.utils.http import http_date

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from mayan.apps.acls.models import AccessControlList

from ..models import Document
from ..permissions import permission_document_view

logger = logging.getLogger(__name__)


class APIDocumentProcessingStatusView(generics.RetrieveAPIView):
    """
    Phase B4: Processing Status API
    
    GET /api/v4/documents/{id}/processing_status/
    
    Returns the current processing status for a document including:
    - Overall status (pending, processing, complete, failed)
    - Progress percentage (0-100)
    - Current step description
    - AI analysis readiness flags
    - OCR and thumbnail status
    
    Response format:
    {
        "status": "processing" | "complete" | "failed" | "pending",
        "progress": 45,
        "current_step": "OCR scanning",
        "ai_tags_ready": false,
        "ai_description_ready": false,
        "ai_colors_ready": false,
        "ocr_ready": true,
        "thumbnail_ready": true,
        "error_message": null,
        "task_id": "abc-123-def",
        "started_at": "2025-12-03T14:00:00Z",
        "completed_at": null
    }
    
    Headers:
    - ETag: Hash of current status for cache validation
    - Last-Modified: Timestamp of last status change
    - Cache-Control: max-age=5 for short-term caching during polling
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    lookup_url_kwarg = 'document_id'
    
    @swagger_auto_schema(
        operation_id='document_processing_status',
        operation_description='''
        Get the current processing status for a document.
        
        This endpoint is designed for frontend polling to show real-time
        progress during document uploads and AI analysis.
        
        **Polling Strategy:**
        - Poll every 2-5 seconds while status is "processing"
        - Use ETag header for conditional requests (If-None-Match)
        - Stop polling when status is "complete" or "failed"
        
        **Status Values:**
        - `pending`: Waiting to start processing
        - `processing`: Currently being processed
        - `complete`: Processing finished successfully
        - `failed`: Processing failed (check error_message)
        - `no_files`: Document has no files uploaded yet
        ''',
        manual_parameters=[
            openapi.Parameter(
                'document_id',
                openapi.IN_PATH,
                description='Document ID',
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'If-None-Match',
                openapi.IN_HEADER,
                description='ETag from previous response for cache validation',
                type=openapi.TYPE_STRING,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description='Processing status retrieved successfully',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'document_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'status': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            enum=['pending', 'processing', 'complete', 'failed', 'no_files']
                        ),
                        'progress': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='Progress percentage 0-100'
                        ),
                        'current_step': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Human-readable current step'
                        ),
                        'ai_tags_ready': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'ai_description_ready': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'ai_colors_ready': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'ocr_ready': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'thumbnail_ready': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'analysis_provider': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='AI provider name (e.g., qwenlocal, gigachat)'
                        ),
                        'error_message': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Error message if status is failed'
                        ),
                        'task_id': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Celery task ID for tracking'
                        ),
                        'started_at': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format='date-time'
                        ),
                        'completed_at': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format='date-time'
                        )
                    }
                )
            ),
            304: openapi.Response(description='Not Modified (ETag match)'),
            403: openapi.Response(description='Access denied'),
            404: openapi.Response(description='Document not found')
        },
        tags=['documents', 'processing']
    )
    def get(self, request, document_id):
        # Get document
        try:
            document = Document.objects.get(pk=document_id)
        except Document.DoesNotExist:
            return Response(
                {'error': 'Document not found', 'error_code': 'NOT_FOUND'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check access permissions
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
        
        # Check for DAM AI analysis
        ai_status = self._get_ai_analysis_status(document)
        
        # Check OCR status
        ocr_ready = self._check_ocr_status(document)
        
        # Check thumbnail status
        thumbnail_ready = self._check_thumbnail_status(document)
        
        # Determine overall status
        if not document.files.exists():
            overall_status = 'no_files'
            progress = 0
            current_step = 'No files uploaded'
        elif ai_status['status'] == 'not_started':
            overall_status = 'pending'
            progress = 10 if thumbnail_ready else 0
            current_step = 'Waiting for AI analysis'
        else:
            overall_status = ai_status['status']
            progress = ai_status['progress']
            current_step = ai_status['current_step']
        
        response_data = {
            'document_id': str(document_id),
            'status': overall_status,
            'progress': progress,
            'current_step': current_step,
            'ai_tags_ready': ai_status.get('ai_tags_ready', False),
            'ai_description_ready': ai_status.get('ai_description_ready', False),
            'ai_colors_ready': ai_status.get('ai_colors_ready', False),
            'ocr_ready': ocr_ready,
            'thumbnail_ready': thumbnail_ready,
            'analysis_provider': ai_status.get('provider'),
            'error_message': ai_status.get('error_message'),
            'task_id': ai_status.get('task_id'),
            'started_at': ai_status.get('started_at'),
            'completed_at': ai_status.get('completed_at')
        }
        
        # Generate ETag based on status data
        etag = self._generate_etag(response_data)
        
        # Check If-None-Match header for cache validation
        if_none_match = request.headers.get('If-None-Match')
        if if_none_match and if_none_match == etag:
            return Response(status=status.HTTP_304_NOT_MODIFIED)
        
        # Generate Last-Modified from completed_at or started_at
        last_modified = ai_status.get('completed_at') or ai_status.get('started_at')
        
        response = Response(response_data)
        
        # Add caching headers
        response['ETag'] = etag
        if last_modified:
            try:
                # Parse ISO format datetime
                dt = datetime.fromisoformat(last_modified.replace('Z', '+00:00'))
                response['Last-Modified'] = http_date(dt.timestamp())
            except (ValueError, AttributeError):
                pass
        
        # Short cache for polling (5 seconds)
        response['Cache-Control'] = 'private, max-age=5'
        
        return response
    
    def _generate_etag(self, data):
        """Generate ETag hash from response data."""
        # Create deterministic string from key fields
        key_data = f"{data['status']}:{data['progress']}:{data['current_step']}"
        return f'"{hashlib.md5(key_data.encode()).hexdigest()}"'
    
    def _get_ai_analysis_status(self, document):
        """Get AI analysis status from DAM module if available."""
        try:
            # Import DAM model if available
            from mayan.apps.dam.models import DocumentAIAnalysis
            
            try:
                ai_analysis = document.ai_analysis
                
                # Map status
                status_mapping = {
                    'pending': 'pending',
                    'processing': 'processing',
                    'completed': 'complete',
                    'failed': 'failed'
                }
                
                return {
                    'status': status_mapping.get(ai_analysis.analysis_status, 'processing'),
                    'progress': getattr(ai_analysis, 'progress', 0),
                    'current_step': getattr(ai_analysis, 'current_step', '') or self._default_step(ai_analysis.analysis_status),
                    'ai_tags_ready': bool(ai_analysis.ai_tags),
                    'ai_description_ready': bool(ai_analysis.ai_description),
                    'ai_colors_ready': bool(ai_analysis.dominant_colors),
                    'provider': ai_analysis.ai_provider or None,
                    'error_message': getattr(ai_analysis, 'error_message', None) if ai_analysis.analysis_status == 'failed' else None,
                    'task_id': getattr(ai_analysis, 'task_id', None),
                    'started_at': ai_analysis.created.isoformat() if ai_analysis.created else None,
                    'completed_at': ai_analysis.analysis_completed.isoformat() if ai_analysis.analysis_completed else None
                }
                
            except DocumentAIAnalysis.DoesNotExist:
                return {'status': 'not_started'}
                
        except ImportError:
            # DAM module not available
            return {'status': 'not_available'}
    
    def _default_step(self, analysis_status):
        """Get default step description."""
        mapping = {
            'pending': 'Queued for AI analysis',
            'processing': 'AI analysis in progress',
            'completed': 'Analysis complete',
            'failed': 'Analysis failed'
        }
        return mapping.get(analysis_status, 'Unknown')
    
    def _check_ocr_status(self, document):
        """Check if OCR has been performed."""
        try:
            latest_version = document.versions.order_by('-timestamp').first()
            if latest_version:
                # Check for content in first page
                for page in latest_version.pages.all()[:1]:
                    if hasattr(page, 'content_object') and page.content_object:
                        content = getattr(page.content_object, 'content', None)
                        if content:
                            return True
            return False
        except Exception:
            return False
    
    def _check_thumbnail_status(self, document):
        """Check if thumbnails have been generated."""
        try:
            latest_version = document.versions.order_by('-timestamp').first()
            return bool(latest_version and latest_version.pages.exists())
        except Exception:
            return False

