"""Analytics cache helpers.

We use django-redis as Django's cache backend. This module provides best-effort
helpers to invalidate analytics-related keys when new events arrive.
"""

from __future__ import annotations

from typing import Optional

from django.core.cache import cache


def invalidate_asset_analytics_cache(*, document_id: int) -> None:
    """Invalidate cache entries related to a single asset/document.

    This is a best-effort implementation. Only keys created by our explicit
    caching helpers are targeted. If the cache backend doesn't support pattern
    deletion, this becomes a no-op.
    """
    doc_id = int(document_id or 0)
    if not doc_id:
        return

    delete_pattern = getattr(cache, 'delete_pattern', None)
    if not callable(delete_pattern):
        return

    # Per-asset drill-down caches (manual caching).
    delete_pattern(f'*analytics:asset_detail:{doc_id}:*')

    # Aggregate caches that are impacted by downloads (leaderboards/top metrics).
    delete_pattern('*analytics:asset_bank:*')


