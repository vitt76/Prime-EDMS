"""
Headless API: Potential duplicates by file checksum (SHA256).

Sprint 3.2: GET /api/v4/headless/documents/<id>/potential-duplicates/
Returns other documents in the same organization that have a file with the same
checksum as the current document's latest file. Tenant-scoped, ACL-filtered.
"""

import logging

from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models import Document, DocumentFile
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.serializers.optimized_document_serializers import (
    OptimizedDocumentListSerializer,
)

logger = logging.getLogger(__name__)

POTENTIAL_DUPLICATES_LIMIT = 20


class PotentialDuplicatesView(APIView):
    """
    GET /api/v4/headless/documents/<document_id>/potential-duplicates/

    Returns documents in the current organization that have at least one file
    with the same checksum as the given document's latest file (excluding the
    given document). Respects ACL (only documents the user can view).
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, document_id: int):
        organization = getattr(request, 'organization', None)
        if not organization:
            return Response(
                {'detail': 'Organization context required (X-Organization-Id or tenant).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Resolve document with view permission
        base_queryset = Document.valid.all()
        if hasattr(Document, 'organization'):
            base_queryset = base_queryset.filter(organization=organization)
        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_document_view,
            queryset=base_queryset,
            user=request.user
        )
        try:
            document = queryset.get(pk=document_id)
        except Document.DoesNotExist:
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        latest_file = document.file_latest
        if not latest_file or not latest_file.checksum:
            return Response(
                {'results': [], 'count': 0},
                status=status.HTTP_200_OK
            )

        checksum = latest_file.checksum

        # Other documents in same org with same checksum (any file)
        dup_docs_queryset = (
            Document.valid.filter(
                files__checksum=checksum
            )
            .exclude(pk=document_id)
            .distinct()
        )
        if hasattr(Document, 'organization'):
            dup_docs_queryset = dup_docs_queryset.filter(organization=organization)

        dup_docs_queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_document_view,
            queryset=dup_docs_queryset,
            user=request.user
        )
        dup_docs_queryset = dup_docs_queryset[:POTENTIAL_DUPLICATES_LIMIT]

        serializer = OptimizedDocumentListSerializer(
            dup_docs_queryset,
            many=True,
            context={'request': request}
        )
        return Response({
            'results': serializer.data,
            'count': len(serializer.data),
        }, status=status.HTTP_200_OK)
