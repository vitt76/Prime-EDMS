"""Dashboard response cache (Sprint 4 performance)."""

from django.core.cache import cache

DASHBOARD_CACHE_TTL = 300  # 5 minutes
DASHBOARD_CACHE_KEY_PREFIX = 'analytics:dashboard:'


def get_dashboard_cache_key(org_id):
    return f'{DASHBOARD_CACHE_KEY_PREFIX}{org_id}'


def get_dashboard_cached(org_id):
    return cache.get(get_dashboard_cache_key(org_id))


def set_dashboard_cached(org_id, data):
    cache.set(get_dashboard_cache_key(org_id), data, timeout=DASHBOARD_CACHE_TTL)


def invalidate_dashboard_cache_for_org(org_id):
    """Invalidate dashboard cache when org data changes (e.g. new AssetEvent)."""
    cache.delete(get_dashboard_cache_key(org_id))
