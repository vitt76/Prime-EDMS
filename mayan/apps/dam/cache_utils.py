"""
Cache utilities for DAM preset document counts.
"""
import logging
from django.core.cache import cache
from . import settings as dam_settings

logger = logging.getLogger(__name__)
CACHE_PREFIX = 'dam_preset_doc_count'


def get_preset_count_cache_key(preset_id, user_id=None):
    """Generate cache key for preset document count."""
    if user_id:
        return f'{CACHE_PREFIX}_{preset_id}_user_{user_id}'
    return f'{CACHE_PREFIX}_{preset_id}_global'


def get_preset_count_cache_ttl():
    """Get cache TTL from settings."""
    return dam_settings.setting_preset_document_count_cache_ttl.value or 600


def invalidate_preset_count_cache(preset_id, user_id=None):
    """Invalidate cache for preset document count."""
    try:
        if user_id:
            key = get_preset_count_cache_key(preset_id, user_id)
            cache.delete(key)
        else:
            # Invalidate all user-specific caches (approximate)
            # Full invalidation would require tracking all user IDs
            # For now, rely on TTL
            pass
        logger.debug(f'Invalidated cache for preset {preset_id}')
    except Exception as e:
        logger.warning(f'Error invalidating cache: {e}')

