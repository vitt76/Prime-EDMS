import logging

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import OuterRef, Subquery
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models import Document, DocumentVersion
from mayan.apps.documents.models.document_file_models import DocumentFile
from mayan.apps.documents.models.document_file_page_models import DocumentFilePage
from mayan.apps.documents.permissions import (
    permission_document_edit, permission_document_file_download,
    permission_document_trash, permission_document_view
)
from mayan.apps.metadata.permissions import permission_document_metadata_edit
from mayan.apps.permissions.models import Permission

from .models import DocumentAIAnalysis, DAMMetadataPreset
from .permissions import permission_ai_analysis_view
from .cache_utils import (
    get_preset_count_cache_key, get_preset_count_cache_ttl
)

logger = logging.getLogger(__name__)


class DocumentAIAnalysisSerializer(serializers.ModelSerializer):
    """
    Serializer for Document AI Analysis model.
    """
    document_title = serializers.CharField(source='document.label', read_only=True)
    document_filename = serializers.SerializerMethodField()
    ocr_text = serializers.SerializerMethodField()
    ocr_status = serializers.SerializerMethodField()

    class Meta:
        model = DocumentAIAnalysis
        fields = [
            'id', 'document', 'document_title', 'document_filename',
            'ai_description', 'ai_tags', 'dominant_colors', 'alt_text',
            'categories', 'language', 'people', 'locations',
            'copyright_notice', 'usage_rights', 'rights_expiry',
            'ai_provider', 'analysis_status', 'created', 'updated', 'analysis_completed',
            'ocr_text', 'ocr_status'
        ]
        read_only_fields = ['id', 'created', 'updated', 'analysis_completed']

    def get_document_filename(self, obj):
        """Get the filename of the latest document file."""
        latest_file = obj.document.files.order_by('-timestamp').first()
        return latest_file.filename if latest_file else None

    def get_ocr_text(self, obj):
        """Get OCR text from all document version pages."""
        try:
            from mayan.apps.ocr.models import DocumentVersionPageOCRContent
            
            # Get latest version
            latest_version = obj.document.versions.order_by('-timestamp').first()
            if not latest_version:
                return None
            
            # Get all pages with OCR content
            ocr_texts = []
            for page in latest_version.version_pages.all():
                try:
                    ocr_content = page.ocr_content
                    if ocr_content and ocr_content.content:
                        ocr_texts.append(ocr_content.content)
                except DocumentVersionPageOCRContent.DoesNotExist:
                    continue
            
            if ocr_texts:
                return '\n\n'.join(ocr_texts)
            return None
        except Exception as e:
            logger.warning(f"Error getting OCR text: {e}")
            return None

    def get_ocr_status(self, obj):
        """Determine OCR status for the document."""
        try:
            from mayan.apps.ocr.models import DocumentVersionPageOCRContent
            
            latest_version = obj.document.versions.order_by('-timestamp').first()
            if not latest_version:
                return 'not_run'
            
            # Check if any page has OCR content
            has_ocr = False
            for page in latest_version.version_pages.all():
                try:
                    ocr_content = page.ocr_content
                    if ocr_content and ocr_content.content:
                        has_ocr = True
                        break
                except DocumentVersionPageOCRContent.DoesNotExist:
                    continue
            
            return 'completed' if has_ocr else 'not_run'
        except Exception as e:
            logger.warning(f"Error getting OCR status: {e}")
            return 'not_run'


class DocumentAIAnalysisFrontendSerializer(DocumentAIAnalysisSerializer):
    """
    Extended serializer for frontend with normalized data format.
    
    Adds tags_with_confidence, colors_with_percentage, and seo_keywords
    for easier frontend consumption.
    """
    tags_with_confidence = serializers.SerializerMethodField()
    colors_with_percentage = serializers.SerializerMethodField()
    seo_keywords = serializers.SerializerMethodField()

    class Meta(DocumentAIAnalysisSerializer.Meta):
        fields = DocumentAIAnalysisSerializer.Meta.fields + [
            'tags_with_confidence', 'colors_with_percentage', 'seo_keywords'
        ]

    def get_tags_with_confidence(self, obj):
        """Transform ai_tags (string[]) into format with confidence for frontend."""
        tags = obj.get_ai_tags_list()
        if not tags:
            return []
        
        return [
            {
                'id': f'tag-{idx}',
                'label': tag,
                'confidence': 80,  # Fixed confidence value
                'category': 'object',  # Default category
                'source': obj.ai_provider or 'unknown'
            }
            for idx, tag in enumerate(tags)
        ]

    def get_colors_with_percentage(self, obj):
        """Transform dominant_colors into format with percentage."""
        colors = obj.get_dominant_colors_list()
        if not colors:
            return []
        
        # Calculate percentage evenly
        total = len(colors)
        percentage_per_color = round(100 / total, 1) if total > 0 else 0
        
        result = []
        for color in colors:
            if isinstance(color, dict):
                # Already has hex and possibly rgb
                result.append({
                    'hex': color.get('hex', ''),
                    'percentage': percentage_per_color
                })
            elif isinstance(color, str):
                # String format, treat as hex
                result.append({
                    'hex': color,
                    'percentage': percentage_per_color
                })
        
        return result

    def get_seo_keywords(self, obj):
        """Extract SEO keywords from ai_tags."""
        tags = obj.get_ai_tags_list()
        if not tags:
            return []
        
        # Return first 5-10 tags as keywords
        return tags[:10]


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
        # Get user from request context
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return 0
        
        user = request.user
        user_id = user.pk
        
        # Generate cache key
        cache_key = get_preset_count_cache_key(obj.id, user_id)
        cache_ttl = get_preset_count_cache_ttl()
        
        # Check cache
        if cache_ttl > 0:
            cached_count = cache.get(cache_key)
            if cached_count is not None:
                return cached_count
        
        try:
            # Get base queryset
            queryset = Document.valid.all()
            
            # Filter by MIME types if specified
            if obj.supported_mime_types:
                # Get latest file mimetype for each document using Subquery
                latest_file_subquery = DocumentFile.objects.filter(
                    document=OuterRef('pk')
                ).order_by('-timestamp').values('mimetype')[:1]
                
                queryset = queryset.annotate(
                    latest_file_mimetype=Subquery(latest_file_subquery)
                ).filter(
                    latest_file_mimetype__in=obj.supported_mime_types
                )
            
            # Apply ACL filtering
            queryset = AccessControlList.objects.restrict_queryset(
                permission=permission_document_view,
                queryset=queryset,
                user=user
            )
            
            # Count documents
            count = queryset.count()
            
            # Cache the result
            if cache_ttl > 0:
                try:
                    cache.set(cache_key, count, cache_ttl)
                except Exception as e:
                    logger.warning(f'Failed to cache preset document count: {e}')
            
            return count
            
        except Exception as e:
            logger.error(f'Error counting applicable documents for preset {obj.id}: {e}')
            # Return 0 on error to avoid breaking the API
            return 0


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


class DAMDocumentDetailSerializer(serializers.Serializer):
    """
    Structured representation of a DAM document detail payload.
    
    Phase B1: Added thumbnail_url, preview_url, download_url fields.
    Returns pure JSON (no HTML rendering).
    """

    id = serializers.IntegerField(source='pk')
    title = serializers.CharField(source='label')
    description = serializers.CharField(allow_blank=True)
    asset_type = serializers.SerializerMethodField()
    asset_status = serializers.SerializerMethodField()
    document_type_id = serializers.SerializerMethodField()
    document_type = serializers.SerializerMethodField()

    file_id = serializers.SerializerMethodField()
    filename = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    mime_type = serializers.SerializerMethodField()
    
    # Phase B1: URL fields for frontend integration
    thumbnail_url = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    # Active version info
    version_active_id = serializers.SerializerMethodField()
    version_active_file_id = serializers.SerializerMethodField()

    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    metadata = serializers.SerializerMethodField()
    versions_count = serializers.IntegerField(source='versions.count')
    versions = serializers.SerializerMethodField()

    permissions = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    view_count = serializers.SerializerMethodField()
    download_count = serializers.SerializerMethodField()

    ai_analysis = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'title', 'description',
            'asset_type', 'asset_status', 'document_type_id', 'document_type',
            'file_id', 'filename', 'file_size', 'mime_type',
            # Phase B1: URL fields
            'thumbnail_url', 'preview_url', 'download_url',
            'version_active_id', 'version_active_file_id',
            'created_at', 'updated_at',
            'metadata', 'versions_count', 'versions',
            'permissions', 'tags',
            'view_count', 'download_count',
            'ai_analysis'
        )

    def get_asset_type(self, obj):
        document_type = getattr(obj, 'document_type', None)
        if document_type:
            return document_type.label
        return getattr(obj, 'asset_type', 'document')

    def get_asset_status(self, obj):
        return 'archived' if getattr(obj, 'in_trash', False) else 'active'

    def get_document_type_id(self, obj):
        document_type = getattr(obj, 'document_type', None)
        return document_type.pk if document_type else None

    def get_document_type(self, obj):
        document_type = getattr(obj, 'document_type', None)
        if document_type:
            return {
                'id': document_type.pk,
                'label': document_type.label,
                'internal_name': getattr(document_type, 'internal_name', None)
            }
        return None

    def _latest_file(self, document):
        return document.files.order_by('-timestamp').first()

    def get_file_id(self, obj):
        file_obj = self._latest_file(obj)
        return file_obj.pk if file_obj else None

    def get_filename(self, obj):
        file_obj = self._latest_file(obj)
        return file_obj.filename if file_obj else None

    def get_file_size(self, obj):
        file_obj = self._latest_file(obj)
        return file_obj.size if file_obj else None

    def get_mime_type(self, obj):
        file_obj = self._latest_file(obj)
        return file_obj.mimetype if file_obj else None

    # Phase B1: URL generation methods for frontend integration
    def get_thumbnail_url(self, obj):
        """
        Get thumbnail URL (150x150).
        Uses document version page image endpoint.
        """
        version = getattr(obj, 'version_active', None)
        if version:
            try:
                first_page = version.pages.first()
                if first_page:
                    return (
                        f'/api/v4/documents/{obj.pk}/versions/{version.pk}'
                        f'/pages/{first_page.pk}/image/'
                        f'?width=150&height=150'
                    )
            except Exception:
                pass
        return None

    def get_preview_url(self, obj):
        """
        Get preview URL (800px width).
        Uses document version page image endpoint.
        """
        version = getattr(obj, 'version_active', None)
        if version:
            try:
                first_page = version.pages.first()
                if first_page:
                    return (
                        f'/api/v4/documents/{obj.pk}/versions/{version.pk}'
                        f'/pages/{first_page.pk}/image/'
                        f'?width=800'
                    )
            except Exception:
                pass
        return None

    def get_download_url(self, obj):
        """
        Get download URL for latest file.
        Returns API endpoint for file download.
        """
        file_obj = self._latest_file(obj)
        if file_obj:
            return f'/api/v4/documents/{obj.pk}/files/{file_obj.pk}/download/'
        return None

    # ------------------------------------------------------------------
    # Active version helpers
    # ------------------------------------------------------------------

    def _get_active_version(self, obj) -> DocumentVersion:
        """
        Helper to get the active version of the document, if any.
        """
        try:
            return getattr(obj, 'version_active', None)
        except Exception:
            return None

    def get_version_active_id(self, obj):
        """
        ID активной DocumentVersion документа, если она есть.
        """
        version = self._get_active_version(obj=obj)
        return version.pk if version else None

    def get_version_active_file_id(self, obj):
        """
        Пытаемся сопоставить активную версию с исходным DocumentFile.

        Алгоритм:
        1. Берём активную версию документа
        2. Используем page_content_objects property для получения content_object'ов
        3. Ищем DocumentFilePage среди content_object'ов
        4. Если нашли, берём document_file_id

        Если цепочка не восстанавливается, возвращаем None и позволяем фронтенду
        использовать fallback (file_latest_id).
        """
        import logging
        logger = logging.getLogger(__name__)
        
        version = self._get_active_version(obj=obj)
        if not version:
            logger.warning('No active version for document %s', obj.pk)
            return None

        try:
            # Сначала пробуем через прямой запрос к version_pages с prefetch
            from django.contrib.contenttypes.models import ContentType
            from mayan.apps.documents.models import DocumentFilePage
            
            file_page_content_type = ContentType.objects.get_for_model(DocumentFilePage)
            
            # Пробуем получить страницу с content_object
            page = version.version_pages.filter(
                content_type=file_page_content_type
            ).first()
            
            if page:
                # Явно загружаем content_object
                try:
                    content_obj = page.content_object
                    if content_obj and isinstance(content_obj, DocumentFilePage):
                        file_id = content_obj.document_file_id
                        logger.info(
                            'Found active version file_id=%s for document %s (via DocumentFilePage from version_pages)',
                            file_id, obj.pk
                        )
                        return file_id
                except Exception as e:
                    logger.warning('Error accessing content_object for page %s: %s', page.pk, str(e))
            
            # Fallback: используем page_content_objects property
            try:
                content_objects = version.page_content_objects
                if content_objects:
                    for content_obj in content_objects:
                        if isinstance(content_obj, DocumentFilePage):
                            file_id = content_obj.document_file_id
                            logger.info(
                                'Found active version file_id=%s for document %s (via page_content_objects)',
                                file_id, obj.pk
                            )
                            return file_id
            except Exception as e:
                logger.warning('Error accessing page_content_objects: %s', str(e))
            
            # Последний fallback: пробуем найти через object_id напрямую
            page_with_object_id = version.version_pages.filter(
                content_type=file_page_content_type
            ).first()
            
            if page_with_object_id:
                try:
                    # Пробуем получить DocumentFilePage напрямую по object_id
                    file_page = DocumentFilePage.objects.filter(
                        pk=page_with_object_id.object_id
                    ).select_related('document_file').first()
                    
                    if file_page and file_page.document_file:
                        file_id = file_page.document_file_id
                        logger.info(
                            'Found active version file_id=%s for document %s (via direct DocumentFilePage lookup)',
                            file_id, obj.pk
                        )
                        return file_id
                except Exception as e:
                    logger.warning('Error in direct DocumentFilePage lookup: %s', str(e))
            
            logger.warning(
                'Could not find document_file for active version %s of document %s. '
                'Pages count: %s',
                version.pk, obj.pk, version.version_pages.count()
            )
        except Exception as e:
            logger.error(
                'Error getting version_active_file_id for document %s: %s',
                obj.pk, str(e), exc_info=True
            )

        return None

    def get_created_at(self, obj):
        return getattr(obj, 'datetime_created', None)

    def get_updated_at(self, obj):
        return getattr(obj, 'datetime_modified', None) or getattr(obj, 'datetime_created', None)

    def get_metadata(self, obj):
        entries = []
        for metadata in obj.metadata.select_related('metadata_type').all():
            meta_type = metadata.metadata_type
            if not meta_type:
                continue

            entries.append({
                'key': meta_type.name,
                'value': metadata.value,
                'type': meta_type.name,
                'lookup': meta_type.lookup or ''
            })

        return entries

    def get_versions(self, obj):
        versions = obj.versions.all().order_by('-timestamp')[:5]
        serialized = []
        for idx, version in enumerate(versions, start=1):
            file_obj = getattr(version.document, 'file_latest', None)
            serialized.append({
                'id': version.pk,
                'version_number': idx,
                'timestamp': version.timestamp,
                'file_size': getattr(file_obj, 'size', None),
                'filename': getattr(file_obj, 'filename', None)
            })
        return serialized

    def get_permissions(self, obj):
        request = self.context.get('request')
        if not request or not getattr(request, 'user', None):
            return {}

        user = request.user
        permission_map = {
            'can_view': permission_document_view,
            'can_download': permission_document_file_download,
            'can_edit_metadata': permission_document_metadata_edit,
            'can_delete': permission_document_trash,
            'can_edit': permission_document_edit,
            'can_analyze': permission_ai_analysis_view
        }

        results = {}
        for key, permission in permission_map.items():
            try:
                results[key] = AccessControlList.objects.check_access(
                    obj=obj,
                    permissions=(permission,),
                    user=user
                )
            except PermissionDenied:
                results[key] = False
        return results

    def get_tags(self, obj):
        try:
            return list(obj.tags.values_list('label', flat=True))
        except Exception:
            return []

    def get_view_count(self, obj):
        return getattr(obj, 'view_count', 0)

    def get_download_count(self, obj):
        return getattr(obj, 'download_count', 0)

    def get_ai_analysis(self, obj):
        analysis = getattr(obj, 'ai_analysis', None)
        if not analysis:
            return None

        return DocumentAIAnalysisFrontendSerializer(analysis, context=self.context).data


class AnalyzeDocumentSerializer(serializers.Serializer):
    """
    Serializer for single document AI analysis request.

    Validates document instance, AI service and analysis type.
    """
    document_instance = serializers.IntegerField(
        help_text="Document ID to analyze",
        required=True
    )
    ai_service = serializers.ChoiceField(
        choices=['openai', 'claude', 'azure', 'local'],
        default='openai',
        required=False,
        help_text="AI service to use for analysis"
    )
    analysis_type = serializers.ChoiceField(
        choices=['classification', 'extraction', 'summary', 'tagging'],
        default='classification',
        required=False,
        help_text="Type of analysis to perform"
    )
    
    def validate_document_instance(self, value):
        """Validate that document exists, is accessible, and has files."""
        if not value:
            raise serializers.ValidationError("Document instance is required")
        
        # Get request context for access control
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            raise serializers.ValidationError("User authentication required")
        
        user = request.user
        
        # Load document with access control check
        try:
            # Use restricted queryset to ensure user has access
            queryset = AccessControlList.objects.restrict_queryset(
                permission=permission_document_view,
                queryset=Document.objects.all(),
                user=user
            )
            
            try:
                document = queryset.get(pk=value)
            except Document.DoesNotExist:
                logger.warning(
                    f'Document {value} not found or not accessible',
                    extra={'document_id': value, 'user_id': user.id}
                )
                raise serializers.ValidationError(
                    f"Document {value} not found or you don't have access to it"
                )
        except PermissionDenied:
            logger.warning(
                f'Permission denied for document {value}',
                extra={'document_id': value, 'user_id': user.id}
            )
            raise serializers.ValidationError(
                f"Permission denied: You don't have access to document {value}"
            )
        except Exception as e:
            logger.exception(
                f'Error loading document {value}',
                extra={'document_id': value, 'user_id': user.id, 'error': str(e)}
            )
            raise serializers.ValidationError(
                f"Error loading document: {str(e)}" if settings.DEBUG else "Error loading document"
            )
        
        # Check if document has files with error handling
        try:
            if not document.files.exists():
                raise serializers.ValidationError("Document has no files to analyze")
        except Exception as e:
            logger.warning(
                f'Error checking document files for document {document.pk}: {e}',
                extra={'document_id': document.pk, 'user_id': user.id}
            )
            raise serializers.ValidationError(f"Error checking document files: {str(e)}")
        
        # Return document instance instead of ID
        return document


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
