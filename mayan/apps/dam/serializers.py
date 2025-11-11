from rest_framework import serializers

from .models import DocumentAIAnalysis, DAMMetadataPreset


class DocumentAIAnalysisSerializer(serializers.ModelSerializer):
    """
    Serializer for Document AI Analysis model.
    """
    document_title = serializers.CharField(source='document.label', read_only=True)
    document_filename = serializers.SerializerMethodField()

    class Meta:
        model = DocumentAIAnalysis
        fields = [
            'id', 'document', 'document_title', 'document_filename',
            'ai_description', 'ai_tags', 'dominant_colors', 'alt_text',
            'categories', 'language', 'people', 'locations',
            'copyright_notice', 'usage_rights', 'rights_expiry',
            'ai_provider', 'analysis_status', 'created', 'updated', 'analysis_completed'
        ]
        read_only_fields = ['id', 'created', 'updated', 'analysis_completed']

    def get_document_filename(self, obj):
        """Get the filename of the latest document file."""
        latest_file = obj.document.files.order_by('-timestamp').first()
        return latest_file.filename if latest_file else None


class DAMMetadataPresetSerializer(serializers.ModelSerializer):
    """
    Serializer for DAM Metadata Preset model.
    """
    applicable_documents_count = serializers.SerializerMethodField()

    class Meta:
        model = DAMMetadataPreset
        fields = [
            'id', 'name', 'description', 'ai_providers',
            'extract_description', 'extract_tags', 'extract_colors', 'extract_alt_text',
            'supported_mime_types', 'is_enabled', 'created', 'applicable_documents_count'
        ]
        read_only_fields = ['id', 'created', 'applicable_documents_count']

    def get_applicable_documents_count(self, obj):
        """Get count of documents this preset would apply to."""
        # This is a simplified calculation - in practice you'd need to check actual documents
        return 0  # TODO: Implement actual counting logic


class AIProviderStatusSerializer(serializers.Serializer):
    """
    Serializer for AI provider status information.
    """
    name = serializers.CharField()
    display_name = serializers.CharField()
    description = serializers.CharField()
    available = serializers.BooleanField()
    capabilities = serializers.DictField()


class AIAnalysisResultSerializer(serializers.Serializer):
    """
    Serializer for AI analysis results.
    """
    description = serializers.CharField(required=False, allow_blank=True)
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    colors = serializers.ListField(required=False)
    alt_text = serializers.CharField(required=False, allow_blank=True)
    provider = serializers.CharField(required=False)
    confidence = serializers.FloatField(required=False, min_value=0, max_value=1)
