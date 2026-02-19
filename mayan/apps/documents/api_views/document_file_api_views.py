import logging

from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.response import Response

from mayan.apps.converter.api_view_mixins import APIImageViewMixin
from mayan.apps.rest_api import generics
from mayan.apps.storage.models import SharedUploadedFile
from mayan.apps.views.generics import DownloadViewMixin

from ..permissions import (
    permission_document_file_delete, permission_document_file_download,
    permission_document_file_edit, permission_document_file_new,
    permission_document_file_view
)
from ..serializers.document_file_serializers import (
    DocumentFileSerializer, DocumentFilePageSerializer
)
from ..tasks import task_document_file_upload

from .mixins import (
    ParentObjectDocumentAPIViewMixin, ParentObjectDocumentFileAPIViewMixin
)

logger = logging.getLogger(name=__name__)


class APIDocumentFileListView(
    ParentObjectDocumentAPIViewMixin, generics.ListCreateAPIView
):
    """
    get: Return a list of the selected document's files.
    post: Upload a new version (create a new document file). Accepts file_new, optional comment, filename, action.
    """
    ordering_fields = ('comment', 'encoding', 'id', 'mime_type')
    serializer_class = DocumentFileSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(status=status.HTTP_202_ACCEPTED)

    def perform_create(self, serializer):
        shared_uploaded_file = SharedUploadedFile.objects.create(
            file=serializer.validated_data['file_new']
        )

        task_document_file_upload.apply_async(
            kwargs={
                'action': serializer.validated_data['action'],
                'comment': serializer.validated_data.get('comment', ''),
                'document_id': self.get_document(
                    permission=permission_document_file_new
                ).pk,
                'filename': serializer.validated_data.get('filename', ''),
                'shared_uploaded_file_id': shared_uploaded_file.pk,
                'user_id': self.request.user.pk
            }
        )

    def get_queryset(self):
        return self.get_document(
            permission=permission_document_file_view
        ).files.all()


class APIDocumentFileDetailView(
    ParentObjectDocumentAPIViewMixin, generics.RetrieveUpdateDestroyAPIView
):
    """
    delete: Delete the selected document file.
    get: Returns the selected document file details.
    """
    lookup_url_kwarg = 'document_file_id'
    mayan_object_permissions = {
        'DELETE': (permission_document_file_delete,),
        'GET': (permission_document_file_view,),
        'PATCH': (permission_document_file_edit,),
        'PUT': (permission_document_file_edit,),
    }
    serializer_class = DocumentFileSerializer

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user
        }

    def get_queryset(self):
        return self.get_document().files.all()


class APIDocumentFileDownloadView(
    DownloadViewMixin, ParentObjectDocumentAPIViewMixin,
    generics.RetrieveAPIView
):
    """
    get: Download a document file.
    Sprint 5.3: If organization has apply_on_download, serve WatermarkedRendition when ready.
    """
    lookup_url_kwarg = 'document_file_id'
    mayan_object_permissions = {
        'GET': (permission_document_file_download,),
    }

    def _should_serve_watermarked(self):
        """True if current organization has apply_on_download and we can use watermarked rendition."""
        org = getattr(self.request, 'organization', None)
        if not org:
            return False
        try:
            from mayan.apps.organizations.models import OrganizationWatermarkSettings
            settings = OrganizationWatermarkSettings.objects.filter(organization=org).first()
            return bool(settings and getattr(settings, 'apply_on_download', False))
        except Exception:
            return False

    def get_download_file_object(self):
        instance = self.get_object()
        instance._event_actor = self.request.user
        if not self._should_serve_watermarked():
            return instance.get_download_file_object()
        org = getattr(self.request, 'organization', None)
        if not org:
            return instance.get_download_file_object()
        try:
            from mayan.apps.distribution.models import WatermarkedRendition
            from mayan.apps.distribution.tasks import apply_watermark_task
            rendition, _ = WatermarkedRendition.objects.get_or_create(
                document_file=instance,
                organization=org,
                defaults={'status': 'pending'}
            )
            if rendition.status == 'completed' and rendition.file:
                return rendition.file.open('rb')
            apply_watermark_task.delay(instance.pk, org.pk)
        except Exception:
            logger.warning(
                'Watermarked download fallback to original for document_file_id=%s: %s',
                instance.pk, __import__('traceback').format_exc()
            )
        return instance.get_download_file_object()

    def get_download_filename(self):
        return self.get_object().filename

    def get_serializer(self, *args, **kwargs):
        return None

    def get_serializer_class(self):
        return None

    def get_queryset(self):
        return self.get_document().files.all()

    def _serve_s3_file_with_range(self, document_file):
        """
        Return a redirect response to the storage URL (typically presigned),
        allowing the storage/CDN to handle Range Requests natively.

        This is optional and must be enabled by passing `?direct=1`.
        """
        storage = document_file.file.storage
        storage_url = None

        # django-storages S3Boto3Storage.url supports `parameters`.
        try:
            storage_url = storage.url(
                name=document_file.file.name,
                parameters={
                    'ResponseContentDisposition': (
                        f'attachment; filename="{document_file.filename}"'
                    )
                }
            )
        except TypeError:
            storage_url = storage.url(name=document_file.file.name)

        if storage_url:
            return HttpResponseRedirect(redirect_to=storage_url)

    def retrieve(self, request, *args, **kwargs):
        # When apply_on_download (watermarked), always stream from Django (rendition or original).
        if self._should_serve_watermarked():
            return self.render_to_response()
        # Optional optimization for S3-backed storages: return a presigned URL
        # and let the storage backend serve the file (including Range support).
        direct = request.query_params.get('direct')
        if direct in ('1', 'true', 'True'):
            try:
                instance = self.get_object()
                return self._serve_s3_file_with_range(document_file=instance)
            except Exception:
                pass
        return self.render_to_response()


# Document file page


class APIDocumentFilePageDetailView(
    ParentObjectDocumentFileAPIViewMixin, generics.RetrieveAPIView
):
    """
    get: Returns the selected document page details.
    """
    lookup_url_kwarg = 'document_file_page_id'
    serializer_class = DocumentFilePageSerializer
    mayan_object_permissions = {
        'GET': (permission_document_file_view,),
    }

    def get_queryset(self):
        return self.get_document_file().pages.all()


class APIDocumentFilePageImageView(
    APIImageViewMixin, ParentObjectDocumentFileAPIViewMixin,
    generics.RetrieveAPIView
):
    """
    get: Returns an image representation of the selected document.
    """
    lookup_url_kwarg = 'document_file_page_id'
    mayan_object_permissions = {
        'GET': (permission_document_file_view,),
    }

    def get_queryset(self):
        return self.get_document_file().pages.all()


class APIDocumentFilePageListView(
    ParentObjectDocumentFileAPIViewMixin, generics.ListAPIView
):
    serializer_class = DocumentFilePageSerializer

    def get_queryset(self):
        return self.get_document_file(
            permission=permission_document_file_view
        ).pages.all()
