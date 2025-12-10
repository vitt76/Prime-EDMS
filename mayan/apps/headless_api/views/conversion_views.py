"""
Headless download/convert endpoints for document files.
Uses simple Pillow-based conversions for images to avoid hitting the SPA HTML.
"""

import io
from typing import Tuple

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models import Document
from mayan.apps.documents.permissions import permission_document_file_view


def _convert_image(file_obj, target_format: str) -> Tuple[io.BytesIO, str, str]:
    """Convert image-like file to target format using Pillow."""
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


class HeadlessDocumentConvertView(APIView):
    """
    Convert latest document file to requested format and return as attachment.

    GET /api/v4/headless/documents/{id}/convert/?format=jpeg|png|webp|tiff|pdf
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, document_id: int):
        target_format = request.GET.get('format', 'jpeg').lower()

        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_document_file_view,
            queryset=Document.valid.all(),
            user=request.user
        )
        document = get_object_or_404(queryset, pk=document_id)
        document_file = document.file_latest
        if not document_file:
            return Response(
                {'error': 'no_file', 'detail': _('Document has no files')},
                status=status.HTTP_404_NOT_FOUND
            )

        # Only basic image conversions for now
        try:
            with document_file.file.open() as f:
                buffer, content_type, extension = _convert_image(f, target_format=target_format)
        except Exception as exc:  # pragma: no cover - defensive
            return Response(
                {'error': 'conversion_failed', 'detail': str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )

        filename = document_file.filename or document.label or f'document-{document.pk}'
        if '.' in filename:
            filename = filename.rsplit('.', 1)[0]
        filename = f'{filename}.{extension}'

        response = HttpResponse(buffer.getvalue(), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename=\"{filename}\"'
        return response

