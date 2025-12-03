"""
Rich Document Detail API Views.

Phase B1: API Gap Fill - Task 1.
Provides rich document detail endpoint for frontend integration.

Created: Phase B1 of TRANSFORMATION_PLAN.md
Author: Backend Adaptation Team
"""
import logging

from django.db.models import Prefetch

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models import Document
from mayan.apps.documents.models.document_file_models import DocumentFile
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.serializers.document_rich_serializers import (
    DocumentRichSerializer, DocumentRichListSerializer
)

logger = logging.getLogger(__name__)


class APIDocumentRichDetailView(generics.RetrieveAPIView):
    """
    Rich Document Detail Endpoint.
    
    Endpoint: GET /api/v4/documents/{document_id}/rich_details/
    
    Returns flattened, frontend-friendly JSON structure with:
    - Core document info (id, uuid, label, description, created_at)
    - File info (download_url, size, mimetype, filename)
    - Metadata as simple key-value dict
    - Tags as list of objects with label and color
    - AI analysis data (if available)
    - Permission flags for current user
    - Thumbnail/preview URLs
    - Version history
    
    Optimized with prefetch_related to minimize N+1 queries.
    """
    serializer_class = DocumentRichSerializer
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    lookup_url_kwarg = 'document_id'
    
    def get_queryset(self):
        """
        Get optimized queryset with all related data prefetched.
        Minimizes database queries for rich document view.
        """
        queryset = Document.objects.select_related(
            'document_type'
        ).prefetch_related(
            # Prefetch latest file
            Prefetch(
                'files',
                queryset=DocumentFile.objects.order_by('-timestamp'),
                to_attr='_prefetched_files'
            ),
            # Prefetch metadata with types
            'metadata__metadata_type',
            # Prefetch tags
            'tags',
            # Prefetch versions with pages
            'versions__version_pages'
        )
        
        # Apply ACL filtering
        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_document_view,
            queryset=queryset,
            user=self.request.user
        )
        
        return queryset
    
    def get_object(self):
        """Get document and attach prefetched file for serializer."""
        document = super().get_object()
        
        # Attach prefetched latest file for serializer efficiency
        if hasattr(document, '_prefetched_files') and document._prefetched_files:
            document._prefetched_file_latest = document._prefetched_files[0]
        else:
            document._prefetched_file_latest = None
        
        # Try to prefetch AI analysis
        try:
            _ = document.ai_analysis
        except Exception:
            pass
        
        return document
    
    def get_serializer_context(self):
        """Include request in serializer context for permission checks."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @swagger_auto_schema(
        operation_id='document_rich_detail',
        operation_description='''
Retrieve rich document details optimized for frontend.

Returns flattened, frontend-friendly JSON structure with:
- Core document info (id, uuid, label, description, datetime_created)
- File info (download_url, size, mimetype, filename)
- **thumbnail_url**: URL for 150x150 preview image
- **preview_url**: URL for 800px preview image
- **download_url**: Direct file download URL
- Metadata as simple key-value dict (SerializerMethodField)
- Tags as list of objects with label and color
- AI analysis data (if available)
- Permission flags for current user
- Version history

**Phase B1 Implementation:**
- Uses JSONRenderer only (no HTML)
- Optimized with prefetch_related
- Includes URL fields for media access
        ''',
        manual_parameters=[
            openapi.Parameter(
                'document_id',
                openapi.IN_PATH,
                description='Document ID',
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description='Success',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            404: openapi.Response(description='Document not found'),
        },
        tags=['Documents - Rich Details']
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve rich document details.
        
        Returns structured JSON response optimized for frontend.
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return Response({
                'success': True,
                'data': serializer.data
            })
            
        except Document.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'error': 'Document not found',
                    'error_code': 'NOT_FOUND'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception(
                'Error retrieving rich document details',
                extra={
                    'user_id': request.user.id,
                    'document_id': kwargs.get('document_id'),
                    'error': str(e)
                }
            )
            return Response(
                {
                    'success': False,
                    'error': 'Failed to retrieve document details',
                    'error_code': 'RETRIEVAL_ERROR'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class APIDocumentRichListView(generics.ListAPIView):
    """
    Rich Document List Endpoint.
    
    Endpoint: GET /api/v4/documents/rich_list/
    
    Returns list of documents with rich metadata, optimized for gallery view.
    
    Query parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 50, max: 100)
    - search: Search query
    - document_type: Filter by document type ID
    - ordering: Sort field (e.g., 'datetime_created', '-label')
    """
    serializer_class = DocumentRichListSerializer
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    
    def get_queryset(self):
        """Get optimized queryset with prefetching for list view."""
        queryset = Document.valid.select_related(
            'document_type'
        ).prefetch_related(
            Prefetch(
                'files',
                queryset=DocumentFile.objects.order_by('-timestamp')[:1],
                to_attr='_prefetched_files'
            ),
            'metadata__metadata_type',
            'tags'
        )
        
        # Apply ACL filtering
        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_document_view,
            queryset=queryset,
            user=self.request.user
        )
        
        # Apply search filter
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(label__icontains=search)
        
        # Apply document type filter
        doc_type = self.request.query_params.get('document_type')
        if doc_type:
            queryset = queryset.filter(document_type_id=doc_type)
        
        # Apply ordering
        ordering = self.request.query_params.get('ordering', '-datetime_created')
        allowed_orderings = [
            'datetime_created', '-datetime_created',
            'label', '-label',
            'id', '-id'
        ]
        if ordering in allowed_orderings:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-datetime_created')
        
        return queryset
    
    @swagger_auto_schema(
        operation_id='document_rich_list',
        operation_description='''
List documents with rich metadata, optimized for gallery view.

Returns paginated list with thumbnail URLs and metadata summaries.
        ''',
        manual_parameters=[
            openapi.Parameter(
                'page', openapi.IN_QUERY, 
                description='Page number', 
                type=openapi.TYPE_INTEGER, default=1
            ),
            openapi.Parameter(
                'page_size', openapi.IN_QUERY,
                description='Items per page (max 100)',
                type=openapi.TYPE_INTEGER, default=50
            ),
            openapi.Parameter(
                'search', openapi.IN_QUERY,
                description='Search query',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'document_type', openapi.IN_QUERY,
                description='Filter by document type ID',
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'ordering', openapi.IN_QUERY,
                description='Sort field (datetime_created, -datetime_created, label, -label)',
                type=openapi.TYPE_STRING, default='-datetime_created'
            ),
        ],
        responses={
            200: openapi.Response(
                description='Success',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'page': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'page_size': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_pages': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                    }
                )
            ),
        },
        tags=['Documents - Rich Details']
    )
    def list(self, request, *args, **kwargs):
        """List documents with rich metadata."""
        queryset = self.get_queryset()
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = min(int(request.query_params.get('page_size', 50)), 100)
        
        total_count = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        
        documents = queryset[start:end]
        
        # Attach prefetched file for each document
        for doc in documents:
            if hasattr(doc, '_prefetched_files') and doc._prefetched_files:
                doc._prefetched_file_latest = doc._prefetched_files[0]
            else:
                doc._prefetched_file_latest = None
        
        serializer = self.get_serializer(documents, many=True)
        
        return Response({
            'success': True,
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size,
            'next': page + 1 if end < total_count else None,
            'previous': page - 1 if page > 1 else None,
            'results': serializer.data
        })
    
    def get_serializer_context(self):
        """Include request in serializer context."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

