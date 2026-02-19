"""
Headless API: Recently Viewed documents.

Returns documents recently viewed or downloaded by the current user in the
current organization, based on AssetEvent (event_type view/download).
Phase 5.2 Sprint 1 Backend Tech Debt.
"""

import logging
from datetime import timedelta

from django.db.models import Case, Max, Prefetch, When

from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mayan.apps.acls.models import AccessControlList
from mayan.apps.analytics.models import AssetEvent
from mayan.apps.documents.models import Document, DocumentFile, DocumentVersion
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.serializers.optimized_document_serializers import (
    OptimizedDocumentListSerializer,
)

logger = logging.getLogger(__name__)


def _get_metadata_queryset():
    """Metadata prefetch for document list (matches optimized view)."""
    try:
        from mayan.apps.metadata.models import DocumentMetadata
        return DocumentMetadata.objects.select_related('metadata_type')
    except ImportError:
        return None


class RecentlyViewedDocumentListView(APIView):
    """
    GET /api/v4/headless/documents/recently-viewed/

    Returns documents the current user recently viewed or downloaded in the
    current organization (AssetEvent event_type view/download). Tenant-scoped.
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organization = getattr(request, 'organization', None)
        if not organization:
            return Response(
                {'detail': 'Organization context required (X-Organization-Id or tenant).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            limit_param = request.query_params.get('limit', '20')
            limit = min(int(limit_param), 50) if limit_param.isdigit() else 20
            limit = max(1, limit)
        except (ValueError, TypeError):
            limit = 20

        try:
            days_param = request.query_params.get('days', '30')
            days = int(days_param) if days_param.isdigit() else 30
            days = max(1, min(days, 365))
        except (ValueError, TypeError):
            days = 30

        from django.utils import timezone
        since = timezone.now() - timedelta(days=days)

        # Document IDs ordered by most recent view/download
        recent_events = (
            AssetEvent.objects.filter(
                organization=organization,
                user=request.user,
                event_type__in=[AssetEvent.EVENT_TYPE_VIEW, AssetEvent.EVENT_TYPE_DOWNLOAD],
                timestamp__gte=since,
            )
            .values('document')
            .annotate(last_ts=Max('timestamp'))
            .order_by('-last_ts')[:limit]
        )
        document_ids = [e['document'] for e in recent_events]
        if not document_ids:
            return Response({'results': [], 'count': 0})

        # Restrict by ACL
        documents_qs = Document.valid.filter(pk__in=document_ids)
        documents_qs = AccessControlList.objects.restrict_queryset(
            permission=permission_document_view,
            queryset=documents_qs,
            user=request.user,
        )
        # Preserve order of document_ids
        preserved_order = Case(
            *[When(pk=pk, then=pos) for pos, pk in enumerate(document_ids)]
        )
        documents_qs = documents_qs.order_by(preserved_order)

        # Same prefetches as optimized list to avoid N+1
        metadata_qs = _get_metadata_queryset()
        prefetches = [
            Prefetch(
                'files',
                queryset=DocumentFile.objects.order_by('-timestamp'),
                to_attr='_prefetched_latest_file_list',
            ),
            Prefetch(
                'versions',
                queryset=DocumentVersion.objects.filter(active=True).prefetch_related('version_pages'),
                to_attr='_prefetched_version_active_list',
            ),
            'tags',
        ]
        if metadata_qs is not None:
            prefetches.append(Prefetch('metadata', queryset=metadata_qs))
        documents_qs = documents_qs.select_related('document_type').prefetch_related(*prefetches)
        try:
            documents_qs = documents_qs.select_related('ai_analysis')
        except Exception:
            pass

        serializer = OptimizedDocumentListSerializer(
            list(documents_qs),
            many=True,
            context={'request': request},
        )
        return Response({
            'results': serializer.data,
            'count': len(serializer.data),
        })
