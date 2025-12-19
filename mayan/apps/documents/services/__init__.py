"""
Document Services.

Phase B2: Performance Optimization.
Contains caching and optimization services for documents.
"""

from .thumbnail_cache_service import (
    ThumbnailCacheService,
    thumbnail_cache_service,
    get_thumbnail_url,
    get_preview_url,
    invalidate_document_cache
)

__all__ = [
    'ThumbnailCacheService',
    'thumbnail_cache_service',
    'get_thumbnail_url',
    'get_preview_url',
    'invalidate_document_cache'
]















