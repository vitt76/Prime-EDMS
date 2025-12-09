"""Serializers for document versions exposed via headless API."""

from typing import Optional

from rest_framework import serializers

from mayan.apps.documents.models import DocumentVersion
from mayan.apps.documents.serializers.optimized_document_serializers import (
    CachedThumbnailMixin,
)


class HeadlessDocumentVersionSerializer(
    CachedThumbnailMixin, serializers.ModelSerializer
):
    """Lightweight serializer for document versions with preview/download URLs."""

    document_id = serializers.IntegerField(source='document.pk', read_only=True)
    thumbnail_url = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = DocumentVersion
        fields = (
            'id',
            'document_id',
            'timestamp',
            'comment',
            'active',
            'thumbnail_url',
            'download_url',
        )
        read_only_fields = fields

    def _get_first_page_id(self, obj: DocumentVersion) -> Optional[int]:
        try:
            page = obj.pages.first()
            return page.pk if page else None
        except Exception:  # pragma: no cover - defensive
            return None

    def get_thumbnail_url(self, obj: DocumentVersion) -> Optional[str]:
        page_id = self._get_first_page_id(obj)
        if page_id:
            return self._get_cached_thumbnail_url(
                document_id=obj.document_id,
                width=300,
                height=300,
                version_id=obj.pk,
                page_id=page_id,
            )
        return self._get_cached_thumbnail_url(document_id=obj.document_id)

    def get_download_url(self, obj: DocumentVersion) -> Optional[str]:
        try:
            file_latest = obj.document.file_latest
            if not file_latest:
                return None
            return self._get_cached_download_url(
                document_id=obj.document_id,
                file_id=file_latest.pk,
            )
        except Exception:  # pragma: no cover - defensive
            return None

