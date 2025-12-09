"""
Thumbnail Cache Service.

Phase B2.3: Thumbnail Caching Strategy.
Implements Cache-Aside Pattern for thumbnail/preview URLs.

S3 Presigned URLs are CPU-intensive to generate. This service
caches generated URLs in Redis/Memcached with automatic invalidation.

Created: Phase B2 of TRANSFORMATION_PLAN.md
Author: Backend Performance Engineer
"""
import logging
from typing import Optional, Dict, Any

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(name=__name__)


# Cache configuration
THUMBNAIL_CACHE_PREFIX = 'doc_thumb'
PREVIEW_CACHE_PREFIX = 'doc_preview'
DOWNLOAD_CACHE_PREFIX = 'doc_download'
DEFAULT_CACHE_TTL = 3600  # 1 hour


class ThumbnailCacheService:
    """
    Service for caching document thumbnail and preview URLs.
    
    Implements Cache-Aside Pattern:
    1. Check cache for URL
    2. If miss: Generate URL, cache it, return
    3. If hit: Return cached URL
    
    Cache keys:
    - thumbnail_url_{document_id}_{width}x{height}
    - preview_url_{document_id}_{width}
    - download_url_{document_id}_{file_id}
    
    Cache invalidation:
    - On DocumentFile post_save (new version uploaded)
    - On DocumentVersion post_save (new version created)
    - Manual invalidation via invalidate_document_cache()
    """
    
    def __init__(self, cache_ttl: int = DEFAULT_CACHE_TTL):
        """
        Initialize cache service.
        
        Args:
            cache_ttl: Time-to-live for cached URLs in seconds.
        """
        self.cache_ttl = cache_ttl
    
    def get_thumbnail_url(
        self,
        document_id: int,
        width: int = 150,
        height: int = 150,
        version_id: Optional[int] = None,
        page_id: Optional[int] = None,
        force_refresh: bool = False
    ) -> Optional[str]:
        """
        Get thumbnail URL with caching.
        
        Args:
            document_id: Document ID
            width: Thumbnail width
            height: Thumbnail height
            version_id: Specific version ID (optional)
            page_id: Specific page ID (optional)
            force_refresh: Force regeneration of URL
            
        Returns:
            Thumbnail URL string or None
        """
        cache_key = self._get_thumbnail_cache_key(document_id, width, height)
        
        if not force_refresh:
            cached_url = cache.get(cache_key)
            if cached_url is not None:
                logger.debug(
                    f'Thumbnail cache HIT: doc={document_id}, '
                    f'size={width}x{height}'
                )
                return cached_url
        
        # Cache miss - generate URL
        logger.debug(
            f'Thumbnail cache MISS: doc={document_id}, '
            f'size={width}x{height}'
        )
        
        url = self._generate_thumbnail_url(
            document_id, width, height, version_id, page_id
        )
        
        if url:
            cache.set(cache_key, url, self.cache_ttl)
        
        return url
    
    def get_preview_url(
        self,
        document_id: int,
        width: int = 800,
        version_id: Optional[int] = None,
        page_id: Optional[int] = None,
        force_refresh: bool = False
    ) -> Optional[str]:
        """
        Get preview URL with caching.
        
        Args:
            document_id: Document ID
            width: Preview width
            version_id: Specific version ID (optional)
            page_id: Specific page ID (optional)
            force_refresh: Force regeneration
            
        Returns:
            Preview URL string or None
        """
        cache_key = self._get_preview_cache_key(document_id, width)
        
        if not force_refresh:
            cached_url = cache.get(cache_key)
            if cached_url is not None:
                return cached_url
        
        url = self._generate_preview_url(
            document_id, width, version_id, page_id
        )
        
        if url:
            cache.set(cache_key, url, self.cache_ttl)
        
        return url
    
    def get_download_url(
        self,
        document_id: int,
        file_id: int
    ) -> str:
        """
        Get download URL (stable, doesn't need heavy caching).
        
        Args:
            document_id: Document ID
            file_id: File ID
            
        Returns:
            Download URL string
        """
        # Download URLs are stable - just generate directly
        return f'/api/v4/documents/{document_id}/files/{file_id}/download/'
    
    def invalidate_document_cache(self, document_id: int) -> int:
        """
        Invalidate all cached URLs for a document.
        
        Called when:
        - New file uploaded (DocumentFile post_save)
        - New version created (DocumentVersion post_save)
        - Document deleted
        
        Args:
            document_id: Document ID to invalidate
            
        Returns:
            Number of cache keys deleted
        """
        keys_deleted = 0
        
        # Common thumbnail sizes to invalidate
        thumbnail_sizes = [
            (150, 150),   # Small thumbnail
            (200, 200),   # Medium thumbnail
            (300, 300),   # Large thumbnail
            (600, 600),   # Preview thumbnail
        ]
        
        preview_widths = [400, 600, 800, 1200, 1920]
        
        # Invalidate thumbnail cache keys
        for width, height in thumbnail_sizes:
            cache_key = self._get_thumbnail_cache_key(document_id, width, height)
            if cache.delete(cache_key):
                keys_deleted += 1
        
        # Invalidate preview cache keys
        for width in preview_widths:
            cache_key = self._get_preview_cache_key(document_id, width)
            if cache.delete(cache_key):
                keys_deleted += 1
        
        logger.info(
            f'Cache invalidated for document {document_id}: '
            f'{keys_deleted} keys deleted'
        )
        
        return keys_deleted
    
    def invalidate_all_document_caches(self, document_ids: list) -> int:
        """
        Invalidate cache for multiple documents.
        
        Args:
            document_ids: List of document IDs
            
        Returns:
            Total number of keys deleted
        """
        total_deleted = 0
        for doc_id in document_ids:
            total_deleted += self.invalidate_document_cache(doc_id)
        return total_deleted
    
    def warm_cache(
        self,
        document_id: int,
        version_id: Optional[int] = None,
        page_id: Optional[int] = None
    ) -> Dict[str, str]:
        """
        Pre-warm cache for a document.
        
        Useful after upload to generate URLs before first request.
        
        Args:
            document_id: Document ID
            version_id: Version ID (optional)
            page_id: Page ID (optional)
            
        Returns:
            Dict of generated URLs
        """
        urls = {}
        
        # Generate common sizes
        urls['thumbnail_150'] = self.get_thumbnail_url(
            document_id, 150, 150, version_id, page_id, force_refresh=True
        )
        urls['thumbnail_300'] = self.get_thumbnail_url(
            document_id, 300, 300, version_id, page_id, force_refresh=True
        )
        urls['preview_800'] = self.get_preview_url(
            document_id, 800, version_id, page_id, force_refresh=True
        )
        
        logger.info(f'Cache warmed for document {document_id}')
        
        return urls
    
    # Private methods
    
    def _get_thumbnail_cache_key(
        self, 
        document_id: int, 
        width: int, 
        height: int
    ) -> str:
        """Generate cache key for thumbnail."""
        return f'{THUMBNAIL_CACHE_PREFIX}_{document_id}_{width}x{height}'
    
    def _get_preview_cache_key(
        self, 
        document_id: int, 
        width: int
    ) -> str:
        """Generate cache key for preview."""
        return f'{PREVIEW_CACHE_PREFIX}_{document_id}_{width}'
    
    def _generate_thumbnail_url(
        self,
        document_id: int,
        width: int,
        height: int,
        version_id: Optional[int] = None,
        page_id: Optional[int] = None
    ) -> str:
        """
        Generate thumbnail URL.
        
        If version_id and page_id provided, use specific IDs.
        Otherwise, use 'latest' placeholder.
        """
        if version_id and page_id:
            return (
                f'/api/v4/documents/{document_id}/versions/{version_id}'
                f'/pages/{page_id}/image/?width={width}&height={height}'
            )
        else:
            return (
                f'/api/v4/documents/{document_id}/versions/latest'
                f'/pages/1/image/?width={width}&height={height}'
            )
    
    def _generate_preview_url(
        self,
        document_id: int,
        width: int,
        version_id: Optional[int] = None,
        page_id: Optional[int] = None
    ) -> str:
        """Generate preview URL."""
        if version_id and page_id:
            return (
                f'/api/v4/documents/{document_id}/versions/{version_id}'
                f'/pages/{page_id}/image/?width={width}'
            )
        else:
            return (
                f'/api/v4/documents/{document_id}/versions/latest'
                f'/pages/1/image/?width={width}'
            )


# Singleton instance
thumbnail_cache_service = ThumbnailCacheService()


# Convenience functions
def get_thumbnail_url(document_id: int, **kwargs) -> Optional[str]:
    """Get cached thumbnail URL."""
    return thumbnail_cache_service.get_thumbnail_url(document_id, **kwargs)


def get_preview_url(document_id: int, **kwargs) -> Optional[str]:
    """Get cached preview URL."""
    return thumbnail_cache_service.get_preview_url(document_id, **kwargs)


def invalidate_document_cache(document_id: int) -> int:
    """Invalidate all cached URLs for a document."""
    return thumbnail_cache_service.invalidate_document_cache(document_id)








