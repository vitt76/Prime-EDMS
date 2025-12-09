"""Serializers for headless favorites API."""

from rest_framework import serializers

from mayan.apps.documents.serializers.optimized_document_serializers import (
    OptimizedDocumentListSerializer
)


class FavoriteDocumentEntrySerializer(serializers.Serializer):
    """Favorite document entry with document summary and added timestamp."""

    document = serializers.SerializerMethodField()
    datetime_added = serializers.DateTimeField()

    def get_document(self, obj):
        """
        Render document using optimized serializer.
        Documents are pre-fetched and passed via context to avoid extra queries.
        """
        document_map = self.context.get('document_map', {})
        document = document_map.get(obj.document_id)
        if not document:
            return None

        serializer = OptimizedDocumentListSerializer(
            document,
            context=self.context
        )
        return serializer.data

