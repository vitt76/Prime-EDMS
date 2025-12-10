"""
Rich Document Serializers for Frontend Integration.

Phase B1: API Gap Fill - Task 1.
Provides flattened, frontend-friendly JSON structure for document details.

Created: Phase B1 of TRANSFORMATION_PLAN.md
Author: Backend Adaptation Team
"""
import logging
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models import Document
from mayan.apps.documents.permissions import (
    permission_document_edit, permission_document_file_download,
    permission_document_trash, permission_document_view
)

logger = logging.getLogger(__name__)


class DocumentRichSerializer(serializers.Serializer):
    """
    Rich Document Serializer for Frontend Integration.
    
    Provides a flattened, frontend-friendly structure with:
    - Core document info (id, uuid, label, description, created_at)
    - File info (download_url, size, mimetype, filename)
    - Metadata as simple key-value dict (not nested objects)
    - Tags as list of objects with label and color
    - AI analysis data (if available)
    - Permission flags for current user
    - Thumbnail/preview URLs
    
    CRITICAL: Uses SerializerMethodField for metadata dict output.
    """
    
    # Core fields
    id = serializers.IntegerField(read_only=True)
    uuid = serializers.UUIDField(read_only=True)
    label = serializers.CharField()
    description = serializers.CharField(allow_blank=True, required=False)
    language = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(source='datetime_created', read_only=True)
    
    # Document type
    document_type_id = serializers.IntegerField(source='document_type.id', read_only=True)
    document_type_label = serializers.CharField(source='document_type.label', read_only=True)
    
    # Status
    in_trash = serializers.BooleanField(read_only=True)
    is_stub = serializers.BooleanField(read_only=True)
    
    # File info - computed fields
    file_id = serializers.SerializerMethodField()
    filename = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    mime_type = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    checksum = serializers.SerializerMethodField()
    file_timestamp = serializers.SerializerMethodField()
    page_count = serializers.SerializerMethodField()
    
    # URLs
    thumbnail_url = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()
    
    # Metadata as dict - CRITICAL: SerializerMethodField
    metadata = serializers.SerializerMethodField()
    
    # Tags
    tags = serializers.SerializerMethodField()
    
    # AI Analysis
    ai_analysis = serializers.SerializerMethodField()
    
    # Versions
    versions_count = serializers.SerializerMethodField()
    versions = serializers.SerializerMethodField()
    
    # Permissions for current user
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        fields = (
            # Core
            'id', 'uuid', 'label', 'description', 'language', 'created_at',
            'document_type_id', 'document_type_label',
            'in_trash', 'is_stub',
            # File
            'file_id', 'filename', 'file_size', 'mime_type', 'download_url',
            'checksum', 'file_timestamp', 'page_count',
            # URLs
            'thumbnail_url', 'preview_url',
            # Metadata & Tags
            'metadata', 'tags',
            # AI
            'ai_analysis',
            # Versions
            'versions_count', 'versions',
            # Permissions
            'permissions'
        )
    
    # ==================== File Info Methods ====================
    
    def _get_file_latest(self, obj) -> Optional[Any]:
        """Get latest file from document (cached or fresh)."""
        # Try cached prefetch first
        if hasattr(obj, '_prefetched_file_latest'):
            return obj._prefetched_file_latest
        
        # Fallback to property
        return obj.file_latest
    
    def get_file_id(self, obj) -> Optional[int]:
        """Get latest file ID."""
        file_obj = self._get_file_latest(obj)
        return file_obj.pk if file_obj else None
    
    def get_filename(self, obj) -> Optional[str]:
        """Get latest file's filename."""
        file_obj = self._get_file_latest(obj)
        return file_obj.filename if file_obj else None
    
    def get_file_size(self, obj) -> Optional[int]:
        """Get latest file's size in bytes."""
        file_obj = self._get_file_latest(obj)
        return file_obj.size if file_obj else None
    
    def get_mime_type(self, obj) -> Optional[str]:
        """Get latest file's MIME type."""
        file_obj = self._get_file_latest(obj)
        return file_obj.mimetype if file_obj else None
    
    def get_checksum(self, obj) -> Optional[str]:
        """Get latest file's checksum."""
        file_obj = self._get_file_latest(obj)
        return file_obj.checksum if file_obj else None
    
    def get_file_timestamp(self, obj) -> Optional[str]:
        """Get latest file's timestamp."""
        file_obj = self._get_file_latest(obj)
        if file_obj and file_obj.timestamp:
            return file_obj.timestamp.isoformat()
        return None
    
    def get_page_count(self, obj) -> int:
        """Get page count from latest file."""
        file_obj = self._get_file_latest(obj)
        if file_obj:
            return file_obj.pages.count()
        return 0
    
    def get_download_url(self, obj) -> Optional[str]:
        """
        Get download URL for latest file.
        Returns API endpoint for file download.
        """
        file_obj = self._get_file_latest(obj)
        if not file_obj:
            return None
        
        return f'/api/v4/documents/{obj.pk}/files/{file_obj.pk}/download/'
    
    # ==================== URL Methods ====================
    
    def get_thumbnail_url(self, obj) -> Optional[str]:
        """
        Get thumbnail URL (150x150).
        Uses document version page image endpoint.
        """
        version = obj.version_active
        if version and version.pages.exists():
            return (
                f'/api/v4/documents/{obj.pk}/versions/{version.pk}'
                f'/pages/{version.pages.first().pk}/image/'
                f'?width=150&height=150'
            )
        return None
    
    def get_preview_url(self, obj) -> Optional[str]:
        """
        Get preview URL (800px width).
        Uses document version page image endpoint.
        """
        version = obj.version_active
        if version and version.pages.exists():
            return (
                f'/api/v4/documents/{obj.pk}/versions/{version.pk}'
                f'/pages/{version.pages.first().pk}/image/'
                f'?width=800'
            )
        return None
    
    # ==================== Metadata Method (CRITICAL) ====================
    
    def get_metadata(self, obj) -> Dict[str, str]:
        """
        Get document metadata as simple key-value dictionary.
        
        CRITICAL: This uses SerializerMethodField to output metadata as:
        {
            "Year": "2025",
            "Campaign": "Summer",
            "Author": "John Doe"
        }
        
        Instead of list of objects like:
        [
            {"id": 1, "metadata_type": {"name": "Year"}, "value": "2025"},
            ...
        ]
        
        This is required for frontend compatibility.
        """
        metadata_dict = {}
        
        try:
            # Use prefetched data if available
            metadata_queryset = obj.metadata.select_related('metadata_type').all()
            
            for metadata_entry in metadata_queryset:
                if metadata_entry.metadata_type:
                    # Use metadata type name as key, value as value
                    key = metadata_entry.metadata_type.name
                    value = metadata_entry.value or ''
                    metadata_dict[key] = value
        except Exception as e:
            logger.warning(
                f'Error fetching metadata for document {obj.pk}: {e}'
            )
        
        return metadata_dict
    
    # ==================== Tags Method ====================
    
    def get_tags(self, obj) -> List[Dict[str, Any]]:
        """
        Get document tags as list of objects with label and color.
        
        Returns:
        [
            {"id": 1, "label": "Important", "color": "#ff0000"},
            {"id": 2, "label": "Review", "color": "#00ff00"}
        ]
        """
        tags_list = []
        
        try:
            for tag in obj.tags.all():
                tags_list.append({
                    'id': tag.pk,
                    'label': tag.label,
                    'color': tag.color
                })
        except Exception as e:
            logger.warning(
                f'Error fetching tags for document {obj.pk}: {e}'
            )
        
        return tags_list
    
    # ==================== AI Analysis Method ====================
    
    def get_ai_analysis(self, obj) -> Optional[Dict[str, Any]]:
        """
        Get AI analysis data if available.
        
        Returns structured AI analysis or None if not analyzed.
        """
        try:
            analysis = getattr(obj, 'ai_analysis', None)
            if not analysis:
                return None
            
            return {
                'id': analysis.pk,
                'status': analysis.analysis_status,
                'provider': analysis.ai_provider,
                'description': analysis.ai_description,
                'tags': analysis.get_ai_tags_list() if hasattr(analysis, 'get_ai_tags_list') else (analysis.ai_tags or []),
                'categories': analysis.categories or [],
                'people': analysis.people or [],
                'locations': analysis.locations or [],
                'dominant_colors': analysis.dominant_colors or [],
                'alt_text': analysis.alt_text,
                'copyright_notice': analysis.copyright_notice,
                'usage_rights': analysis.usage_rights,
                'rights_expiry': analysis.rights_expiry.isoformat() if analysis.rights_expiry else None,
                'completed_at': analysis.analysis_completed.isoformat() if analysis.analysis_completed else None,
                'created_at': analysis.created.isoformat() if analysis.created else None,
                'updated_at': analysis.updated.isoformat() if analysis.updated else None
            }
        except Exception as e:
            logger.warning(
                f'Error fetching AI analysis for document {obj.pk}: {e}'
            )
            return None
    
    # ==================== Versions Method ====================
    
    def get_versions_count(self, obj) -> int:
        """Get total version count."""
        try:
            return obj.versions.count()
        except Exception:
            return 0
    
    def get_versions(self, obj) -> List[Dict[str, Any]]:
        """
        Get document versions (limited to last 10).
        
        Returns list of version objects with basic info.
        """
        versions_list = []
        
        try:
            versions = obj.versions.order_by('-timestamp')[:10]
            
            for idx, version in enumerate(versions):
                versions_list.append({
                    'id': version.pk,
                    'active': version.active,
                    'comment': version.comment,
                    'timestamp': version.timestamp.isoformat() if version.timestamp else None,
                    'page_count': version.pages.count()
                })
        except Exception as e:
            logger.warning(
                f'Error fetching versions for document {obj.pk}: {e}'
            )
        
        return versions_list
    
    # ==================== Permissions Method ====================
    
    def get_permissions(self, obj) -> Dict[str, bool]:
        """
        Get permission flags for current user.
        
        Returns dict with boolean flags for each permission.
        """
        request = self.context.get('request')
        if not request or not getattr(request, 'user', None):
            return {
                'can_view': False,
                'can_edit': False,
                'can_download': False,
                'can_delete': False
            }
        
        user = request.user
        
        permission_map = {
            'can_view': permission_document_view,
            'can_edit': permission_document_edit,
            'can_download': permission_document_file_download,
            'can_delete': permission_document_trash
        }
        
        results = {}
        for key, permission in permission_map.items():
            try:
                AccessControlList.objects.check_access(
                    obj=obj,
                    permissions=(permission,),
                    user=user
                )
                results[key] = True
            except PermissionDenied:
                results[key] = False
            except Exception:
                results[key] = False
        
        return results


class DocumentRichListSerializer(serializers.Serializer):
    """
    Lightweight serializer for document list view.
    
    Optimized for performance with minimal database queries.
    """
    id = serializers.IntegerField(read_only=True)
    uuid = serializers.UUIDField(read_only=True)
    label = serializers.CharField()
    description = serializers.CharField(allow_blank=True, required=False)
    created_at = serializers.DateTimeField(source='datetime_created', read_only=True)
    
    # Document type
    document_type_id = serializers.IntegerField(source='document_type.id', read_only=True)
    document_type_label = serializers.CharField(source='document_type.label', read_only=True)
    
    # File info
    filename = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    mime_type = serializers.SerializerMethodField()
    
    # Thumbnail
    thumbnail_url = serializers.SerializerMethodField()
    
    # Metadata as dict
    metadata = serializers.SerializerMethodField()
    
    # Tags (lightweight)
    tags = serializers.SerializerMethodField()
    
    # AI status
    ai_status = serializers.SerializerMethodField()
    
    def _get_file_latest(self, obj):
        if hasattr(obj, '_prefetched_file_latest'):
            return obj._prefetched_file_latest
        return obj.file_latest
    
    def get_filename(self, obj) -> Optional[str]:
        file_obj = self._get_file_latest(obj)
        return file_obj.filename if file_obj else None
    
    def get_file_size(self, obj) -> Optional[int]:
        file_obj = self._get_file_latest(obj)
        return file_obj.size if file_obj else None
    
    def get_mime_type(self, obj) -> Optional[str]:
        file_obj = self._get_file_latest(obj)
        return file_obj.mimetype if file_obj else None
    
    def get_thumbnail_url(self, obj) -> Optional[str]:
        version = obj.version_active
        if version and version.pages.exists():
            return (
                f'/api/v4/documents/{obj.pk}/versions/{version.pk}'
                f'/pages/{version.pages.first().pk}/image/'
                f'?width=150&height=150'
            )
        return None
    
    def get_metadata(self, obj) -> Dict[str, str]:
        """Get metadata as simple key-value dict."""
        metadata_dict = {}
        try:
            for m in obj.metadata.select_related('metadata_type').all():
                if m.metadata_type:
                    metadata_dict[m.metadata_type.name] = m.value or ''
        except Exception:
            pass
        return metadata_dict
    
    def get_tags(self, obj) -> List[str]:
        """Get tag labels as simple list."""
        try:
            return list(obj.tags.values_list('label', flat=True))
        except Exception:
            return []
    
    def get_ai_status(self, obj) -> Optional[str]:
        """Get AI analysis status."""
        try:
            analysis = getattr(obj, 'ai_analysis', None)
            return analysis.analysis_status if analysis else 'not_analyzed'
        except Exception:
            return 'not_analyzed'









