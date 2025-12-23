"""Headless endpoints for creating document versions from the web editor."""

import logging

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
from mayan.apps.storage.models import SharedUploadedFile
from mayan.apps.headless_api import settings as headless_settings
from mayan.apps.headless_api.tasks import process_editor_version_task

logger = logging.getLogger(__name__)


class HeadlessEditView(APIView):
    """
    Create a new document version from an edited image (non-destructive).

    POST /api/v4/headless/documents/{id}/versions/new_from_edit/
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, document_id: int):
        """
        Create a new document version from an edited image (asynchronous).
        
        Returns 202 Accepted with task_id for polling status.
        """
        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_document_version_create,
            queryset=Document.valid.all(),
            user=request.user
        )
        document = get_object_or_404(queryset, pk=document_id)

        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response(
                {'error': 'file_required'}, status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка размера файла
        max_size = headless_settings.setting_editor_max_upload_size.value
        if uploaded_file.size > max_size:
            return Response(
                {
                    'error': 'file_too_large',
                    'detail': 'File size exceeds maximum allowed size',
                    'max_size': max_size,
                    'file_size': uploaded_file.size
                },
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            )

        # Сохранение во временное хранилище
        shared_file = SharedUploadedFile.objects.create(file=uploaded_file)

        # Параметры для задачи
        target_format = request.data.get('format')
        comment = request.data.get('comment') or _('Edited via Web Editor')
        action_id = request.data.get('action_id') or DocumentFileActionUseNewPages.backend_id

        # Запуск Celery task
        try:
            task_result = process_editor_version_task.apply_async(
                kwargs={
                    'shared_uploaded_file_id': shared_file.pk,
                    'document_id': document.pk,
                    'target_format': target_format,
                    'comment': comment,
                    'action_id': action_id,
                    'user_id': request.user.pk,
                },
                queue='converter'
            )
        except Exception as exc:
            logger.exception('Failed to enqueue editor version task: %s', exc)
            # Очистка временного файла при ошибке
            try:
                shared_file.delete()
            except Exception:
                pass
            return Response(
                {
                    'error': 'task_enqueue_failed',
                    'detail': str(exc)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                'task_id': task_result.id,
                'status': 'processing',
                'message': 'Image conversion started'
            },
            status=status.HTTP_202_ACCEPTED
        )

