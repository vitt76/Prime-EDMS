"""Headless API views for Favorites."""

import logging

from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models import Document, FavoriteDocument
from mayan.apps.documents.permissions import permission_document_view

logger = logging.getLogger(__name__)


class HeadlessFavoriteListView(APIView):
    """
    Return list of document IDs favorited by the current user.

    Response: [1, 2, 3]
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favorite_doc_ids = FavoriteDocument.objects.filter(
            user=request.user
        ).values_list('document_id', flat=True)

        queryset = Document.valid.filter(pk__in=favorite_doc_ids)
        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_document_view,
            queryset=queryset,
            user=request.user
        )

        ids = list(queryset.values_list('pk', flat=True))
        return Response(ids)


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

