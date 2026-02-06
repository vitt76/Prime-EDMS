"""Redis Streams producer for analytics events.

This module implements an "Event Stream" pattern using Redis Streams.
The request/response path should never block on heavy DB writes for analytics.

Constraints:
    - Best-effort. If Redis is unavailable, producers should fail gracefully.
    - Keep payloads small and JSON-serializable.

Stream key:
    - default: dam:analytics:events
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from django.conf import settings

logger = logging.getLogger(name=__name__)


def _get_stream_key() -> str:
    return str(getattr(settings, 'ANALYTICS_EVENT_STREAM_KEY', 'dam:analytics:events'))


def _get_stream_maxlen() -> int:
    return int(getattr(settings, 'ANALYTICS_EVENT_STREAM_MAXLEN', 1000000))


def _is_enabled() -> bool:
    return bool(getattr(settings, 'ANALYTICS_EVENT_STREAM_ENABLED', True))


def _get_redis_client():
    """Return a redis-py client using the configured Django cache Redis."""
    try:
        from django_redis import get_redis_connection
    except Exception:
        return None

    try:
        return get_redis_connection('default')
    except Exception:
        return None


def publish_event(*, payload: Dict[str, Any], stream_key: Optional[str] = None) -> Optional[str]:
    """Publish an analytics event payload to Redis Streams.

    Args:
        payload: JSON-serializable dictionary.
        stream_key: Optional override for the stream key.

    Returns:
        Redis stream entry id or None on failure.
    """
    if not _is_enabled():
        return None

    stream = (stream_key or _get_stream_key()).strip()
    if not stream:
        return None

    client = _get_redis_client()
    if not client:
        return None

    # Redis Streams fields must be string/bytes/int/float.
    fields: Dict[str, Any] = {}
    for key, value in (payload or {}).items():
        if value is None:
            continue
        if isinstance(value, (dict, list, tuple)):
            fields[key] = json.dumps(value, ensure_ascii=False, separators=(',', ':'))
        else:
            fields[key] = str(value)

    try:
        entry_id = client.xadd(
            name=stream,
            fields=fields,
            maxlen=_get_stream_maxlen(),
            approximate=True
        )
        # redis-py may return bytes depending on config.
        if isinstance(entry_id, (bytes, bytearray)):
            return entry_id.decode('utf-8', errors='ignore')
        return str(entry_id)
    except Exception as exc:
        logger.debug('Failed to publish analytics event to Redis stream: %s', exc)
        return None


def publish_asset_event(
    *,
    document_id: int,
    event_type: str,
    user_id: Optional[int] = None,
    user_department: str = '',
    channel: str = '',
    intended_use: str = '',
    bandwidth_bytes: Optional[int] = None,
    latency_seconds: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """Publish an asset event (Level 1) to the stream."""
    payload: Dict[str, Any] = {
        'kind': 'asset_event',
        'document_id': document_id,
        'event_type': event_type,
        'user_id': user_id or '',
        'user_department': user_department or '',
        'channel': channel or '',
        'intended_use': intended_use or '',
        'bandwidth_bytes': '' if bandwidth_bytes is None else int(bandwidth_bytes),
        'latency_seconds': '' if latency_seconds is None else int(latency_seconds),
        'metadata': metadata or {},
    }
    return publish_event(payload=payload)


def publish_user_session_event(
    *,
    action: str,
    user_id: int,
    session_key: str = '',
    ip_address: str = '',
    user_agent: str = '',
    geo_country: str = '',
    geo_city: str = '',
    timestamp_iso: str = '',
) -> Optional[str]:
    """Publish a user session event (Level 3) to the stream.

    action:
        - login
        - logout
    """
    payload: Dict[str, Any] = {
        'kind': 'user_session',
        'action': (action or '').strip(),
        'user_id': user_id,
        'session_key': session_key or '',
        'ip_address': ip_address or '',
        'user_agent': user_agent or '',
        'geo_country': geo_country or '',
        'geo_city': geo_city or '',
        'timestamp': timestamp_iso or '',
    }
    return publish_event(payload=payload)


def publish_portal_event(
    *,
    event_type: str,
    occurred_at_iso: str,
    document_id: Optional[int] = None,
    share_link_id: Optional[int] = None,
    publication_id: Optional[int] = None,
    campaign_id: str = '',
    user_id: Optional[int] = None,
    session_key: str = '',
    ip_address: str = '',
    user_agent: str = '',
    views: Optional[int] = None,
    clicks: Optional[int] = None,
    conversions: Optional[int] = None,
    bandwidth_bytes: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """Publish a portal/public-link analytics event.

    This is used for branded portals / public share links where the user may be
    anonymous. The consumer will persist:
      - PortalSession (session-level aggregation)
      - AssetEvent with channel='portal' (view/download/deliver)
    """
    payload: Dict[str, Any] = {
        'kind': 'portal_event',
        'event_type': (event_type or '').strip(),
        'occurred_at': occurred_at_iso or '',
        'document_id': '' if not document_id else int(document_id),
        'share_link_id': '' if not share_link_id else int(share_link_id),
        'publication_id': '' if not publication_id else int(publication_id),
        'campaign_id': campaign_id or '',
        'user_id': '' if not user_id else int(user_id),
        'session_key': session_key or '',
        'ip_address': ip_address or '',
        'user_agent': user_agent or '',
        'views': '' if views is None else int(views),
        'clicks': '' if clicks is None else int(clicks),
        'conversions': '' if conversions is None else int(conversions),
        'bandwidth_bytes': '' if bandwidth_bytes is None else int(bandwidth_bytes),
        'metadata': metadata or {},
    }
    return publish_event(payload=payload)


