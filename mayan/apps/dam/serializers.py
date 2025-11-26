import logging
from typing import Any, Dict, List

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models import Document
from mayan.apps.documents.models.document_version_models import DocumentVersion
from mayan.apps.documents.permissions import (
    permission_document_edit, permission_document_file_download,
    permission_document_trash, permission_document_view
)
from mayan.apps.documents.serializers.document_serializers import DocumentSerializer
from mayan.apps.metadata.permissions import permission_document_metadata_edit
from mayan.apps.permissions.models import Permission

from .models import DocumentAIAnalysis, DAMMetadataPreset
from .permissions import permission_ai_analysis_view

logger = logging.getLogger(__name__)


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


class MetadataFieldSerializer(serializers.Serializer):
    """Serializer for a single metadata entry."""

    key = serializers.CharField()
    value = serializers.CharField(allow_blank=True, allow_null=True)
    metadata_type = serializers.CharField()
    metadata_type_label = serializers.CharField()
    lookup = serializers.CharField(allow_blank=True, allow_null=True)


class DocumentVersionSummarySerializer(serializers.ModelSerializer):
    """Minimal summary of a document version history entry."""

    class Meta:
        model = DocumentVersion
        fields = ('id', 'timestamp', 'comment', 'active')
        read_only_fields = ('id', 'timestamp', 'comment', 'active')


class DAMDocumentDetailSerializer(serializers.Serializer):
    """
    Detailed representation of a DAM document replacing the previous HTML blob.
    """

    document = DocumentSerializer(read_only=True)
    ai_analysis = DocumentAIAnalysisSerializer(read_only=True)
    tags = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    versions = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    def get_tags(self, obj: Dict[str, Any]) -> List[str]:
        """Return document tags if available."""
        document = obj.get('document')
        if not document:
            return []

        try:
            return list(document.tags.values_list('label', flat=True))
        except AttributeError:
            return []

    def get_metadata(self, obj: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Return structured metadata entries for the document."""
        document = obj.get('document')
        if not document:
            return []

        entries = []
        for metadata in document.metadata.select_related('metadata_type').all():
            metadata_type = metadata.metadata_type
            if not metadata_type:
                continue

            entries.append({
                'key': metadata_type.name,
                'metadata_type': metadata_type.name,
                'metadata_type_label': metadata_type.label,
                'value': metadata.value,
                'lookup': metadata_type.lookup or ''
            })

        return MetadataFieldSerializer(
            entries, many=True, context=self.context
        ).data

    def get_versions(self, obj: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Return the most recent document versions."""
        document = obj.get('document')
        if not document:
            return []

        versions_qs = document.versions.all().order_by('-timestamp')[:5]
        return DocumentVersionSummarySerializer(
            versions_qs, many=True, context=self.context
        ).data

    def get_permissions(self, obj: Dict[str, Any]) -> Dict[str, bool]:
        """Return actionability flags based on ACLs."""
        document = obj.get('document')
        if not document:
            return {}

        request = self.context.get('request')
        if not request:
            return {}

        user = request.user
        permission_map = {
            'can_view': permission_document_view,
            'can_download': permission_document_file_download,
            'can_edit': permission_document_edit,
            'can_delete': permission_document_trash,
            'can_edit_metadata': permission_document_metadata_edit,
            'can_view_analysis': permission_ai_analysis_view,
        }

        return {
            key: self._check_permission(user, document, permission)
            for key, permission in permission_map.items()
        }

    @staticmethod
    def _check_permission(user, document, permission) -> bool:
        """Check if the user can perform the given permission."""
        try:
            return AccessControlList.objects.check_access(
                obj=document, permissions=(permission,), user=user
            )
        except Exception:
            return False


class AnalyzeDocumentSerializer(serializers.Serializer):
    """
    Serializer for triggering single document analysis.
    """
    document_id = serializers.PrimaryKeyRelatedField(
        help_text=_('ID of the document to analyze.'),
        queryset=Document.objects.all(),
        source='document_instance'
    )
    ai_service = serializers.CharField(
        help_text=_('Preferred AI service (openai, claude, etc.).'),
        default='openai',
        required=False,
        allow_blank=False
    )
    analysis_type = serializers.CharField(
        help_text=_('Analysis type (classification, extraction, etc.).'),
        default='classification',
        required=False
    )


class BulkAnalyzeDocumentsSerializer(serializers.Serializer):
    """
    Serializer for bulk AI analysis of multiple documents.

    Validates batch size, permissions, AI service configuration and analysis type.
    """

    MAX_BULK_SIZE = 100
    ALLOWED_AI_SERVICES = ['openai', 'claude', 'azure', 'local']

    document_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        help_text=_('List of document IDs to analyze'),
        allow_empty=False
    )
    ai_service = serializers.ChoiceField(
        choices=ALLOWED_AI_SERVICES,
        default='openai',
        help_text=_('AI service to use for analysis')
    )
    analysis_type = serializers.CharField(
        max_length=50,
        default='classification',
        help_text=_('Type of analysis (classification, extraction, etc)')
    )

    def _get_request_user(self):
        request = self.context.get('request')
        if not request or not getattr(request, 'user', None):
            raise ValidationError(_('User not authenticated'))
        user = request.user
        if not user.is_authenticated:
            raise ValidationError(_('User not authenticated'))
        return user

    def validate_document_ids(self, value: list) -> list:
        if not value:
            raise ValidationError(_('At least one document_id is required'))

        if len(value) > self.MAX_BULK_SIZE:
            raise ValidationError(
                _(
                    'Too many documents. Maximum %(limit)s allowed, got %(count)s. '
                    'Split into smaller requests.'
                ),
                params={'limit': self.MAX_BULK_SIZE, 'count': len(value)}
            )

        if len(value) != len(set(value)):
            raise ValidationError(_('Duplicate document IDs provided'))

        documents = Document.objects.filter(pk__in=value)
        found_ids = set(documents.values_list('id', flat=True))
        missing_ids = set(value) - found_ids

        if missing_ids:
            raise ValidationError(
                _('Documents not found: %(missing)s') % {'missing': sorted(missing_ids)}
            )

        user = self._get_request_user()

        try:
            permission_analyze = Permission.objects.get(codename='dam_analyze')
        except Permission.DoesNotExist:
            raise ValidationError(_('Permission configuration error: dam_analyze not found'))

        unauthorized_ids = []
        for document in documents:
            try:
                AccessControlList.objects.check_access(
                    obj=document,
                    permissions=(permission_analyze,),
                    user=user
                )
            except PermissionDenied:
                unauthorized_ids.append(document.id)

        if unauthorized_ids:
            raise ValidationError(
                _(
                    'Permission denied for documents %(ids)s. '
                    'You can only analyze documents you have access to.'
                ),
                params={'ids': unauthorized_ids}
            )

        return value

    def validate_ai_service(self, value: str) -> str:
        if value not in self.ALLOWED_AI_SERVICES:
            raise ValidationError(
                _('Invalid AI service %(value)s. Allowed: %(choices)s') % {
                    'value': value,
                    'choices': ', '.join(self.ALLOWED_AI_SERVICES)
                }
            )

        ai_config = getattr(settings, 'DAM_AI_SERVICES', {})
        if value not in ai_config:
            raise ValidationError(
                _('AI service %(value)s not configured. Available: %(available)s') % {
                    'value': value,
                    'available': ', '.join(ai_config.keys() or [])
                }
            )

        service_config = ai_config.get(value, {})
        if not service_config.get('enabled', False):
            raise ValidationError(_('AI service %(value)s is disabled') % {'value': value})

        return value

    def validate_analysis_type(self, value: str) -> str:
        allowed_types = ['classification', 'extraction', 'summarization', 'tagging']
        if value not in allowed_types:
            raise ValidationError(
                _('Invalid analysis_type %(value)s. Allowed: %(choices)s') % {
                    'value': value,
                    'choices': ', '.join(allowed_types)
                }
            )
        return value

    def validate(self, data):
        if 'document_ids' not in data:
            raise ValidationError(_('document_ids is required'))

        user = self._get_request_user()

        logger.info(
            'Bulk AI analysis request',
            extra={
                'user_id': user.id,
                'doc_count': len(data['document_ids']),
                'ai_service': data.get('ai_service'),
                'analysis_type': data.get('analysis_type')
            }
        )

        return data
