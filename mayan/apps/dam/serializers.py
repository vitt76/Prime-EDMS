from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from mayan.apps.documents.models import Document

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


class DAMDocumentListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing documents with DAM analysis info.
    """
    latest_filename = serializers.SerializerMethodField()
    latest_mimetype = serializers.SerializerMethodField()
    analysis_status = serializers.SerializerMethodField()
    analysis_status_display = serializers.SerializerMethodField()
    ai_provider = serializers.SerializerMethodField()
    analysis_completed = serializers.SerializerMethodField()
    analysis_updated = serializers.SerializerMethodField()
    has_ai_data = serializers.SerializerMethodField()
    tag_preview = serializers.SerializerMethodField()
    category_preview = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = (
            'id',
            'label',
            'datetime_created',
            'latest_filename',
            'latest_mimetype',
            'analysis_status',
            'analysis_status_display',
            'ai_provider',
            'analysis_completed',
            'analysis_updated',
            'has_ai_data',
            'tag_preview',
            'category_preview'
        )

    def _get_latest_file(self, document):
        return document.files.order_by('-timestamp').only('filename', 'mimetype').first()

    def _get_analysis(self, document):
        return getattr(document, 'ai_analysis', None)

    def get_latest_filename(self, document):
        latest_file = self._get_latest_file(document)
        return latest_file.filename if latest_file else None

    def get_latest_mimetype(self, document):
        latest_file = self._get_latest_file(document)
        return latest_file.mimetype if latest_file else None

    def get_analysis_status(self, document):
        analysis = self._get_analysis(document)
        return analysis.analysis_status if analysis else 'not_analyzed'

    def get_analysis_status_display(self, document):
        analysis = self._get_analysis(document)
        if analysis:
            return analysis.get_analysis_status_display()
        return _('Not analyzed')

    def get_ai_provider(self, document):
        analysis = self._get_analysis(document)
        return analysis.ai_provider if analysis and analysis.ai_provider else None

    def get_analysis_completed(self, document):
        analysis = self._get_analysis(document)
        return analysis.analysis_completed if analysis else None

    def get_analysis_updated(self, document):
        analysis = self._get_analysis(document)
        return analysis.updated if analysis else None

    def get_has_ai_data(self, document):
        analysis = self._get_analysis(document)
        if not analysis:
            return False
        return any([
            bool(analysis.ai_description),
            bool(analysis.get_ai_tags_list()),
            bool(analysis.categories),
            bool(analysis.people),
            bool(analysis.locations)
        ])

    def get_tag_preview(self, document):
        analysis = self._get_analysis(document)
        if not analysis:
            return []
        tags = analysis.get_ai_tags_list()
        return tags[:5] if tags else []

    def get_category_preview(self, document):
        analysis = self._get_analysis(document)
        if not analysis or not analysis.categories:
            return []
        categories = analysis.categories if isinstance(analysis.categories, list) else []
        return categories[:5]


class AnalyzeDocumentSerializer(serializers.Serializer):
    """
    Serializer for triggering single document analysis.
    """
    document = serializers.PrimaryKeyRelatedField(
        queryset=Document.objects.all(),
        source='document_instance'
    )


class BulkAnalyzeDocumentsSerializer(serializers.Serializer):
    """
    Serializer for triggering analysis of multiple documents.
    """
    document_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False
    )