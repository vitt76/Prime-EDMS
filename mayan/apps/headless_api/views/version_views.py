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
from mayan.apps.documents.models import Document, DocumentVersion
from mayan.apps.documents.permissions import permission_document_version_create
from mayan.apps.storage.models import SharedUploadedFile
from mayan.apps.headless_api import settings as headless_settings
from mayan.apps.headless_api.serializers.version import (
    HeadlessDocumentVersionSerializer,
)
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
        

class HeadlessVersionActivateView(APIView):
    """
    Explicitly activate a document version from SPA by document + file or version ID.

    POST /api/v4/headless/documents/{id}/versions/activate/
    Body: { "file_id": <document_file_id> } or { "version_id": <version_id> }
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, document_id: int):
        # Restrict by ACL and version create permission (same as HeadlessEditView)
        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_document_version_create,
            queryset=Document.valid.all(),
            user=request.user
        )
        document = get_object_or_404(queryset, pk=document_id)

        version_id = request.data.get('version_id')
        file_id = request.data.get('file_id') or request.data.get('document_file_id')

        version = None
        if version_id:
            try:
                version = document.versions.get(pk=int(version_id))
            except (ValueError, DocumentVersion.DoesNotExist):
                return Response(
                    {'error': 'version_not_found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        elif file_id:
            # В модели DocumentVersion нет прямого поля document_file_id,
            # поэтому сопоставляем версии и файлы по порядку создания.
            try:
                file_pk = int(file_id)
            except (TypeError, ValueError):
                file_pk = None

            if not file_pk:
                return Response(
                    {'error': 'invalid_file_id'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Список файлов документа в порядке создания
            file_list = list(document.files.order_by('timestamp').only('pk', 'timestamp'))
            version_list = list(document.versions.order_by('timestamp').only('pk', 'timestamp'))

            # Ищем индекс файла в списке файлов
            file_index = next(
                (idx for idx, f in enumerate(file_list) if f.pk == file_pk),
                None
            )
            if file_index is None:
                return Response(
                    {'error': 'file_not_found_for_document'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Берём версию с тем же индексом (либо последнюю, если версий меньше)
            if not version_list:
                return Response(
                    {'error': 'versions_not_found_for_document'},
                    status=status.HTTP_404_NOT_FOUND
                )
            if file_index >= len(version_list):
                file_index = len(version_list) - 1
            version = version_list[file_index]
        else:
            return Response(
                {'error': 'file_id_or_version_id_required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Activate selected version; this will deactivate others internally.
        version.active_set(save=True)

        serializer = HeadlessDocumentVersionSerializer(
            version, context={'request': request}
        )
        return Response(
            {
                'success': True,
                'document_id': document.pk,
                'version_id': version.pk,
                'data': serializer.data,
            },
            status=status.HTTP_200_OK
        )
