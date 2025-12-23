"""
Cache utilities for Headless API.

Provides functions for cache key generation and invalidation.
"""
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Cache prefix
CACHE_PREFIX = 'headless_doc_type_config'


def _get_cache_version():
    """Get cache version from settings (lazy import to avoid circular dependencies)."""
    try:
        from . import settings as headless_settings
        return headless_settings.setting_doc_type_config_cache_version.value or 'v1'
    except Exception:
        return 'v1'


def _get_cache_ttl():
    """Get cache TTL from settings (lazy import to avoid circular dependencies)."""
    try:
        from . import settings as headless_settings
        return headless_settings.setting_doc_type_config_cache_ttl.value or 3600
    except Exception:
        return 3600


def get_cache_key_list():
    """Get cache key for document types list."""
    version = _get_cache_version()
    return f'{CACHE_PREFIX}_list_{version}'


def get_cache_key_detail(document_type_id):
    """Get cache key for specific document type configuration."""
    version = _get_cache_version()
    return f'{CACHE_PREFIX}_{document_type_id}_{version}'


def get_cache_ttl():
    """Get cache TTL value."""
    return _get_cache_ttl()


def invalidate_document_type_config_cache(document_type_id=None):
    """
    Invalidate document type configuration cache.
    
    Args:
        document_type_id: ID of document type to invalidate. If None, invalidates only list cache.
    """
    try:
        if document_type_id:
            detail_key = get_cache_key_detail(document_type_id)
            cache.delete(detail_key)
            logger.debug(f'Invalidated cache for document type {document_type_id}')
        
        # Always invalidate list cache when any type changes
        list_key = get_cache_key_list()
        cache.delete(list_key)
        logger.debug('Invalidated document types list cache')
    except Exception as e:
        logger.warning(f'Error invalidating cache: {e}')


def invalidate_all_document_types_cache():
    """
    Invalidate cache for all document types.
    
    Used when workflows change and we need to invalidate all types.
    """
    try:
        # Invalidate list cache
        list_key = get_cache_key_list()
        cache.delete(list_key)
        
        # Note: We can't easily delete all detail caches without knowing IDs,
        # so we rely on TTL for individual entries. Alternatively, we could
        # use cache.clear() but that's too aggressive.
        logger.debug('Invalidated document types list cache (all types)')
    except Exception as e:
        logger.warning(f'Error invalidating all caches: {e}')

