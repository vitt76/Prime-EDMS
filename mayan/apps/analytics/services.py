"""Analytics domain services.

These helpers implement best-effort linking logic between user actions to enable
enterprise metrics like Search-to-Find Time without breaking core flows.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Optional

from django.utils import timezone

from .models import AssetEvent, FeatureUsage, SearchQuery, SearchSession


def link_download_to_latest_search_session(
    *,
    user,
    download_event: AssetEvent,
    max_window_minutes: int = 30
) -> Optional[SearchSession]:
    """Link a download to the latest open search session for the same user.

    The intended flow is:
    - search happens -> SearchQuery is created, and a SearchSession is opened
      (ended_at is NULL).
    - download happens -> AssetEvent(download) is created.
    - this service links the download to the open SearchSession and updates:
      - SearchSession.ended_at, time_to_find_seconds, last_download_event
      - SearchQuery.was_downloaded, time_to_download_seconds (for the last query
        in the session).

    Args:
        user: Authenticated user instance.
        download_event: AssetEvent instance of type download.
        max_window_minutes: Linking time window (anti-noise).

    Returns:
        Updated SearchSession or None if no session could be linked.
    """
    if not user or getattr(user, 'is_authenticated', False) is False:
        return None

    if not download_event or getattr(download_event, 'pk', None) is None:
        return None

    if getattr(download_event, 'user_id', None) != getattr(user, 'pk', None):
        return None

    if download_event.event_type != AssetEvent.EVENT_TYPE_DOWNLOAD:
        return None

    window_start = download_event.timestamp - timedelta(minutes=int(max_window_minutes))

    session = (
        SearchSession.objects.filter(
            user=user,
            ended_at__isnull=True,
            started_at__gte=window_start
        )
        .order_by('-started_at')
        .first()
    )
    if not session:
        return None

    delta_seconds = int((download_event.timestamp - session.started_at).total_seconds())
    session.ended_at = download_event.timestamp
    session.last_download_event = download_event
    session.time_to_find_seconds = max(0, delta_seconds)
    session.save(update_fields=('ended_at', 'last_download_event', 'time_to_find_seconds'))

    # Update last query in that session.
    last_query = (
        SearchQuery.objects.filter(
            user=user,
            search_session_id=session.pk,
            timestamp__gte=session.started_at,
            timestamp__lte=download_event.timestamp
        )
        .order_by('-timestamp')
        .first()
    )
    if last_query and not last_query.was_downloaded:
        last_query.was_downloaded = True
        last_query.time_to_download_seconds = max(0, int((download_event.timestamp - last_query.timestamp).total_seconds()))
        last_query.save(update_fields=('was_downloaded', 'time_to_download_seconds'))

    return session


def track_feature_usage(
    *,
    user,
    feature_name: str,
    was_successful: bool = True,
    metadata: Optional[dict] = None
) -> Optional[FeatureUsage]:
    """Record feature usage as an analytics event.

    Args:
        user: Authenticated user.
        feature_name: Stable feature identifier, e.g. 'analytics.asset_bank'.
        was_successful: Whether the action completed successfully.
        metadata: Optional JSON metadata.

    Returns:
        FeatureUsage row or None on failure.
    """
    if not user or getattr(user, 'is_authenticated', False) is False:
        return None

    feature_name = (feature_name or '').strip()
    if not feature_name:
        return None

    try:
        return FeatureUsage.objects.create(
            user=user,
            feature_name=feature_name[:100],
            was_successful=bool(was_successful),
            metadata=metadata or {}
        )
    except Exception:
        return None


