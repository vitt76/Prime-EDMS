"""Headless endpoints for creating document versions from the web editor."""

import io
import logging
from typing import Tuple

from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.document_file_actions import DocumentFileActionUseNewPages
from mayan.apps.documents.models import Document
from mayan.apps.documents.permissions import permission_document_version_create
from mayan.apps.headless_api.serializers import HeadlessDocumentVersionSerializer

logger = logging.getLogger(__name__)


def _convert_image(file_obj, target_format: str) -> Tuple[io.BytesIO, str, str]:
    """Convert uploaded image to target format using Pillow."""
    from PIL import Image

    image = Image.open(file_obj)
    output_buffer = io.BytesIO()

    fmt = target_format.upper() if target_format else 'JPEG'
    if fmt == 'JPG':
        fmt = 'JPEG'

    image.save(output_buffer, format=fmt)
    output_buffer.seek(0)

    content_type = f"image/{fmt.lower()}"
    extension = fmt.lower()
    return output_buffer, content_type, extension


class HeadlessEditView(APIView):
    """
    Create a new document version from an edited image (non-destructive).

    POST /api/v4/headless/documents/{id}/versions/new_from_edit/
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, document_id: int):
        document = get_object_or_404(Document.valid, pk=document_id)

        # Permissions check
        try:
            AccessControlList.objects.check_access(
                permission=permission_document_version_create,
                user=request.user,
                obj=document,
            )
        except Exception as exc:
            return Response(
                {'error': 'access_denied', 'detail': str(exc)},
                status=status.HTTP_403_FORBIDDEN,
            )

        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response(
                {'error': 'file_required'}, status=status.HTTP_400_BAD_REQUEST
            )

        target_format = request.data.get('format')
        comment = request.data.get('comment') or _('Edited via Web Editor')
        action_id = request.data.get('action_id') or DocumentFileActionUseNewPages.backend_id

        file_to_save = uploaded_file
        filename = getattr(uploaded_file, 'name', 'edited-image')

        if target_format:
            try:
                buffer, _content_type, extension = _convert_image(
                    uploaded_file, target_format=target_format
                )
                filename_parts = filename.rsplit('.', 1)
                base_name = filename_parts[0] if len(filename_parts) > 1 else filename
                filename = f'{base_name}.{extension}'
                file_to_save = buffer
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception('Image conversion failed: %s', exc)
                return Response(
                    {'error': 'conversion_failed', 'detail': str(exc)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            new_file = document.file_new(
                file_object=file_to_save,
                filename=filename,
                action=action_id,
                comment=comment,
                _user=request.user,
            )
        except Exception as exc:
            logger.exception('Failed to create new version: %s', exc)
            return Response(
                {'error': 'creation_failed', 'detail': str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        version = document.versions.order_by('-timestamp').first()

        serializer = HeadlessDocumentVersionSerializer(
            version, context={'request': request}
        )

        return Response(
            {
                'success': True,
                'document_id': document.pk,
                'file_id': new_file.pk,
                'version_id': version.pk if version else None,
                'version': serializer.data,
            }
        )

