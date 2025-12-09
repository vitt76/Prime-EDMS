"""Headless API views for Favorites."""

import logging
from typing import Dict

from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models import Document, FavoriteDocument
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.headless_api.serializers import FavoriteDocumentEntrySerializer

logger = logging.getLogger(__name__)


class HeadlessFavoritesPagination(PageNumberPagination):
    """Simple pagination for favorites list."""

    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class HeadlessFavoriteListView(APIView):
    """
    Return list of favorited documents with thumbnail/preview URLs.

    Response (paginated):
    {
        "count": 2,
        "next": null,
        "previous": null,
        "results": [
            {
                "document": {
                    "id": 1,
                    "label": "...",
                    "thumbnail_url": "http://localhost:8080/api/v4/documents/1/versions/latest/pages/1/image/?width=150&height=150",
                    "preview_url": "http://localhost:8080/api/v4/documents/1/versions/latest/pages/1/image/?width=800",
                    ...
                },
                "datetime_added": "2025-12-08T10:00:00Z"
            }
        ]
    }
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Base favorites for user (ordered)
        favorites_qs = FavoriteDocument.objects.filter(
            user=request.user
        ).select_related('document', 'document__document_type').order_by('-datetime_added')

        favorite_doc_ids = list(favorites_qs.values_list('document_id', flat=True))

        # Apply ACLs to documents
        documents_qs = Document.valid.filter(pk__in=favorite_doc_ids)
        documents_qs = AccessControlList.objects.restrict_queryset(
            permission=permission_document_view,
            queryset=documents_qs,
            user=request.user
        ).select_related('document_type').prefetch_related('tags')

        # Map id -> document for serializer usage
        document_map: Dict[int, Document] = {doc.pk: doc for doc in documents_qs}

        # Filter favorites by permitted documents
        filtered_favorites_qs = favorites_qs.filter(
            document_id__in=document_map.keys()
        )

        paginator = HeadlessFavoritesPagination()
        page = paginator.paginate_queryset(filtered_favorites_qs, request, view=self)

        serializer = FavoriteDocumentEntrySerializer(
            page,
            many=True,
            context={'request': request, 'document_map': document_map}
        )
        return paginator.get_paginated_response(serializer.data)


class HeadlessFavoriteToggleView(APIView):
    """
    Toggle favorite status for a document.

    POST /api/v4/headless/favorites/<document_id>/
    Response: {"favorited": true|false}
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, document_id):
        try:
            document = Document.valid.get(pk=document_id)
        except Document.DoesNotExist:
            return Response(
                {'error': 'Document not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Skip ACL for superusers
        if not request.user.is_superuser:
            try:
                AccessControlList.objects.check_access(
                    permission=permission_document_view,
                    user=request.user,
                    obj=document
                )
            except Exception as exc:
                logger.warning(
                    'Favorites toggle denied for user %s on document %s: %s',
                    request.user.username,
                    document_id,
                    exc
                )
                return Response(
                    {'error': 'access_denied', 'detail': str(exc)},
                    status=status.HTTP_403_FORBIDDEN
                )

        try:
            favorite, created = FavoriteDocument.objects.get_or_create(
                user=request.user,
                document=document
            )
        except Exception as exc:
            return Response(
                {'error': 'favorite_failed', 'detail': str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if created:
            return Response({'favorited': True}, status=status.HTTP_200_OK)

        favorite.delete()
        return Response({'favorited': False}, status=status.HTTP_200_OK)

