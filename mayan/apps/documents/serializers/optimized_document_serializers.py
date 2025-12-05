"""
Optimized Document Serializers.

Phase B2: Performance Optimization.
Serializers that use prefetched data to avoid N+1 queries.

Created: Phase B2 of TRANSFORMATION_PLAN.md
Author: Backend Performance Engineer
"""
import logging
from typing import Optional

from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from mayan.apps.rest_api import serializers as mayan_serializers

from ..models.document_models import Document
from ..models.document_file_models import DocumentFile

logger = logging.getLogger(name=__name__)


# Cache TTL for thumbnail URLs (1 hour)
THUMBNAIL_CACHE_TTL = 3600


class CachedThumbnailMixin:
    """
    Mixin for caching thumbnail/preview URLs.
    
    Phase B2.3: Implements Cache-Aside Pattern for thumbnail URLs.
    S3 presigned URLs are expensive to generate, so we cache them.
    
    Cache invalidation happens via signal on DocumentFile post_save.
    See: mayan/apps/documents/signals.py
    """
    
    def _get_cached_thumbnail_url(
        self, 
        document_id: int, 
        width: int = 150, 
        height: int = 150,
        version_id: Optional[int] = None,
        page_id: Optional[int] = None
    ) -> Optional[str]:
        """
        Get thumbnail URL with caching.
        
        Pattern:
        1. Check cache: GET thumbnail_url_{doc_id}_{width}x{height}
        2. If miss: Generate URL -> Save to cache (TTL 1 hour) -> Return
        3. If hit: Return immediately
        """
        cache_key = f'thumbnail_url_{document_id}_{width}x{height}'
        
        # Try cache first
        cached_url = cache.get(cache_key)
        if cached_url is not None:
            return cached_url
        
        # Cache miss - generate URL
        if version_id and page_id:
            url = (
                f'/api/v4/documents/{document_id}/versions/{version_id}'
                f'/pages/{page_id}/image/?width={width}&height={height}'
            )
        else:
            # Fallback URL pattern
            url = (
                f'/api/v4/documents/{document_id}/versions/latest'
                f'/pages/1/image/?width={width}&height={height}'
            )
        
        # Cache the URL
        cache.set(cache_key, url, THUMBNAIL_CACHE_TTL)
        
        return url
    
    def _get_cached_preview_url(
        self,
        document_id: int,
        width: int = 800,
        version_id: Optional[int] = None,
        page_id: Optional[int] = None
    ) -> Optional[str]:
        """Get preview URL with caching."""
        cache_key = f'preview_url_{document_id}_{width}'
        
        cached_url = cache.get(cache_key)
        if cached_url is not None:
            return cached_url
        
        if version_id and page_id:
            url = (
                f'/api/v4/documents/{document_id}/versions/{version_id}'
                f'/pages/{page_id}/image/?width={width}'
            )
        else:
            url = (
                f'/api/v4/documents/{document_id}/versions/latest'
                f'/pages/1/image/?width={width}'
            )
        
        cache.set(cache_key, url, THUMBNAIL_CACHE_TTL)
        
        return url
    
    def _get_cached_download_url(
        self,
        document_id: int,
        file_id: int
    ) -> str:
        """Get download URL (no caching needed - stable URL)."""
        return f'/api/v4/documents/{document_id}/files/{file_id}/download/'


class OptimizedDocumentFileSerializer(serializers.ModelSerializer):
    """
    Optimized file serializer for embedded use in document serializer.
    Only includes essential fields to reduce payload size.
    """
    
    class Meta:
        model = DocumentFile
        fields = (
            'id', 'filename', 'mimetype', 'size', 'timestamp', 'checksum'
        )
        read_only_fields = fields


class OptimizedDocumentListSerializer(
    CachedThumbnailMixin,
    mayan_serializers.HyperlinkedModelSerializer
):
    """
    Optimized serializer for document list view.
    
    Phase B2.1: Uses prefetched data instead of triggering new queries.
    Phase B2.3: Uses cached thumbnail URLs.
    
    Key optimizations:
    - Uses _prefetched_file_latest_list instead of file_latest property
    - Uses _prefetched_version_active_list instead of version_active property
    - Caches thumbnail/preview URLs
    - Minimal field set for list view performance
    """
    
    # Core fields
    id = serializers.IntegerField(read_only=True)
    uuid = serializers.UUIDField(read_only=True)
    label = serializers.CharField(read_only=True)
    datetime_created = serializers.DateTimeField(read_only=True)
    
    # Document type (uses select_related)
    document_type_id = serializers.IntegerField(
        source='document_type.id', 
        read_only=True
    )
    document_type_label = serializers.CharField(
        source='document_type.label',
        read_only=True
    )
    
    # File info (uses prefetched data)
    file_latest_id = serializers.SerializerMethodField()
    file_latest_filename = serializers.SerializerMethodField()
    file_latest_mimetype = serializers.SerializerMethodField()
    file_latest_size = serializers.SerializerMethodField()
    
    # URLs (cached)
    thumbnail_url = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    
    # Tags (uses prefetch_related)
    tags = serializers.SerializerMethodField()
    
    # AI analysis status (optional)
    ai_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = (
            'id', 'uuid', 'label', 'datetime_created',
            'document_type_id', 'document_type_label',
            'file_latest_id', 'file_latest_filename', 
            'file_latest_mimetype', 'file_latest_size',
            'thumbnail_url', 'preview_url', 'download_url',
            'tags', 'ai_status'
        )
    
    def _get_file_latest(self, obj):
        """Get prefetched file_latest or fallback to property."""
        if hasattr(obj, '_prefetched_file_latest_list'):
            files = obj._prefetched_file_latest_list
            return files[0] if files else None
        if hasattr(obj, '_cached_file_latest'):
            return obj._cached_file_latest
        # Fallback (triggers query - should not happen with optimized view)
        return obj.file_latest
    
    def _get_version_active(self, obj):
        """Get prefetched version_active or fallback."""
        if hasattr(obj, '_prefetched_version_active_list'):
            versions = obj._prefetched_version_active_list
            return versions[0] if versions else None
        if hasattr(obj, '_cached_version_active'):
            return obj._cached_version_active
        return obj.version_active
    
    def get_file_latest_id(self, obj):
        file = self._get_file_latest(obj)
        return file.pk if file else None
    
    def get_file_latest_filename(self, obj):
        file = self._get_file_latest(obj)
        return file.filename if file else None
    
    def get_file_latest_mimetype(self, obj):
        file = self._get_file_latest(obj)
        return file.mimetype if file else None
    
    def get_file_latest_size(self, obj):
        file = self._get_file_latest(obj)
        return file.size if file else None
    
    def get_thumbnail_url(self, obj):
        """Get cached thumbnail URL."""
        version = self._get_version_active(obj)
        if version:
            # Get first page from prefetched pages
            pages = getattr(version, 'version_pages', None)
            if pages:
                page_list = list(pages.all()) if hasattr(pages, 'all') else []
                if page_list:
                    return self._get_cached_thumbnail_url(
                        document_id=obj.pk,
                        width=150,
                        height=150,
                        version_id=version.pk,
                        page_id=page_list[0].pk
                    )
        
        # Fallback URL
        return self._get_cached_thumbnail_url(document_id=obj.pk)
    
    def get_preview_url(self, obj):
        """Get cached preview URL."""
        version = self._get_version_active(obj)
        if version:
            pages = getattr(version, 'version_pages', None)
            if pages:
                page_list = list(pages.all()) if hasattr(pages, 'all') else []
                if page_list:
                    return self._get_cached_preview_url(
                        document_id=obj.pk,
                        width=800,
                        version_id=version.pk,
                        page_id=page_list[0].pk
                    )
        
        return self._get_cached_preview_url(document_id=obj.pk)
    
    def get_download_url(self, obj):
        """Get download URL for latest file."""
        file = self._get_file_latest(obj)
        if file:
            return self._get_cached_download_url(
                document_id=obj.pk,
                file_id=file.pk
            )
        return None
    
    def get_tags(self, obj):
        """Get tags from prefetched data."""
        # tags are prefetched via prefetch_related
        return [
            {'id': tag.pk, 'label': tag.label, 'color': tag.color}
            for tag in obj.tags.all()
        ]
    
    def get_ai_status(self, obj):
        """Get AI analysis status if available."""
        try:
            if hasattr(obj, 'ai_analysis') and obj.ai_analysis:
                return obj.ai_analysis.analysis_status
        except Exception:
            pass
        return None


class OptimizedDocumentSerializer(
    CachedThumbnailMixin,
    mayan_serializers.HyperlinkedModelSerializer
):
    """
    Full optimized document serializer for detail view.
    
    Includes all document data with prefetched relations.
    """
    
    # Core fields
    id = serializers.IntegerField(read_only=True)
    uuid = serializers.UUIDField(read_only=True)
    label = serializers.CharField()
    description = serializers.CharField(allow_blank=True, required=False)
    language = serializers.CharField(required=False)
    datetime_created = serializers.DateTimeField(read_only=True)
    in_trash = serializers.BooleanField(read_only=True)
    
    # Document type
    document_type_id = serializers.IntegerField(write_only=True, required=False)
    document_type = serializers.SerializerMethodField()
    
    # File info
    file_latest = serializers.SerializerMethodField()
    files_count = serializers.SerializerMethodField()
    
    # Version info
    version_active = serializers.SerializerMethodField()
    versions_count = serializers.SerializerMethodField()
    
    # URLs
    thumbnail_url = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    
    # Related data
    tags = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    ai_analysis = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = (
            'id', 'uuid', 'label', 'description', 'language',
            'datetime_created', 'in_trash',
            'document_type_id', 'document_type',
            'file_latest', 'files_count',
            'version_active', 'versions_count',
            'thumbnail_url', 'preview_url', 'download_url',
            'tags', 'metadata', 'ai_analysis'
        )
    
    def _get_file_latest(self, obj):
        if hasattr(obj, '_cached_file_latest'):
            return obj._cached_file_latest
        if hasattr(obj, '_prefetched_files') and obj._prefetched_files:
            return obj._prefetched_files[0]
        return obj.file_latest
    
    def _get_version_active(self, obj):
        if hasattr(obj, '_cached_version_active'):
            return obj._cached_version_active
        if hasattr(obj, '_prefetched_version_active_list'):
            versions = obj._prefetched_version_active_list
            return versions[0] if versions else None
        return obj.version_active
    
    def get_document_type(self, obj):
        return {
            'id': obj.document_type.pk,
            'label': obj.document_type.label
        }
    
    def get_file_latest(self, obj):
        file = self._get_file_latest(obj)
        if file:
            return {
                'id': file.pk,
                'filename': file.filename,
                'mimetype': file.mimetype,
                'size': file.size,
                'timestamp': file.timestamp,
                'checksum': file.checksum
            }
        return None
    
    def get_files_count(self, obj):
        if hasattr(obj, '_prefetched_files'):
            return len(obj._prefetched_files)
        return obj.files.count()
    
    def get_version_active(self, obj):
        version = self._get_version_active(obj)
        if version:
            return {
                'id': version.pk,
                'active': version.active,
                'comment': version.comment,
                'timestamp': version.timestamp
            }
        return None
    
    def get_versions_count(self, obj):
        return obj.versions.count()
    
    def get_thumbnail_url(self, obj):
        version = self._get_version_active(obj)
        if version:
            pages = getattr(version, 'version_pages', None)
            if pages:
                page_list = list(pages.all()) if hasattr(pages, 'all') else []
                if page_list:
                    return self._get_cached_thumbnail_url(
                        document_id=obj.pk,
                        version_id=version.pk,
                        page_id=page_list[0].pk
                    )
        return self._get_cached_thumbnail_url(document_id=obj.pk)
    
    def get_preview_url(self, obj):
        version = self._get_version_active(obj)
        if version:
            pages = getattr(version, 'version_pages', None)
            if pages:
                page_list = list(pages.all()) if hasattr(pages, 'all') else []
                if page_list:
                    return self._get_cached_preview_url(
                        document_id=obj.pk,
                        version_id=version.pk,
                        page_id=page_list[0].pk
                    )
        return self._get_cached_preview_url(document_id=obj.pk)
    
    def get_download_url(self, obj):
        file = self._get_file_latest(obj)
        if file:
            return self._get_cached_download_url(obj.pk, file.pk)
        return None
    
    def get_tags(self, obj):
        return [
            {'id': tag.pk, 'label': tag.label, 'color': tag.color}
            for tag in obj.tags.all()
        ]
    
    def get_metadata(self, obj):
        """Get metadata as key-value dictionary."""
        result = {}
        for doc_metadata in obj.metadata.all():
            if hasattr(doc_metadata, 'metadata_type') and doc_metadata.metadata_type:
                result[doc_metadata.metadata_type.name] = doc_metadata.value
        return result
    
    def get_ai_analysis(self, obj):
        """Get AI analysis data if available."""
        try:
            if hasattr(obj, 'ai_analysis') and obj.ai_analysis:
                analysis = obj.ai_analysis
                return {
                    'id': analysis.pk,
                    'status': analysis.analysis_status,
                    'provider': analysis.ai_provider,
                    'description': analysis.ai_description,
                    'tags': analysis.ai_tags,
                    'categories': analysis.categories,
                    'dominant_colors': analysis.dominant_colors,
                    'completed_at': analysis.analysis_completed
                }
        except Exception:
            pass
        return None






