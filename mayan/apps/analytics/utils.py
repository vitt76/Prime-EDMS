from typing import Any, Dict, Optional

from django.contrib.auth import get_user_model
from django.conf import settings

from .models import AssetEvent
from .event_stream import publish_asset_event


User = get_user_model()


def track_asset_event(
    *,
    document,
    event_type: str,
    user: Optional[User] = None,
    channel: str = 'dam_interface',
    intended_use: str = '',
    bandwidth_bytes: Optional[int] = None,
    latency_seconds: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[AssetEvent]:
    """Create a raw asset analytics event (Level 1).

    Args:
        document: Instance of `documents.Document`.
        event_type: One of the AssetEvent.EVENT_TYPE_* constants.
        user: Optional user that triggered the event.
        channel: Source channel (dam_interface/public_link/api/etc).
        intended_use: Optional intended use of downloaded asset (email/social/etc).
        bandwidth_bytes: Optional bandwidth used for delivery events.
        latency_seconds: Optional latency metric for search-to-download.
        metadata: Arbitrary JSON-serializable metadata.

    Returns:
        Created AssetEvent instance if written synchronously; otherwise None.
    """
    user_department = ''
    if user:
        # Department might not exist on all deployments; keep best-effort.
        user_department = getattr(user, 'department', '') or ''

    # Prefer Redis Streams (Event Stream pattern) for high throughput.
    entry_id = publish_asset_event(
        document_id=int(getattr(document, 'pk', 0) or 0),
        event_type=event_type,
        user_id=int(getattr(user, 'pk', 0) or 0) if user else None,
        user_department=user_department,
        channel=channel or '',
        intended_use=intended_use or '',
        bandwidth_bytes=bandwidth_bytes,
        latency_seconds=latency_seconds,
        metadata=metadata or {},
    )
    if entry_id:
        return None

    # Fallback: keep best-effort compatibility if stream publishing is disabled/down.
    if bool(getattr(settings, 'ANALYTICS_EVENT_STREAM_FALLBACK_TO_DB', True)) is False:
        return None

    return AssetEvent.objects.create(
        document=document,
        event_type=event_type,
        user=user,
        user_department=user_department,
        channel=channel or '',
        intended_use=intended_use or '',
        bandwidth_bytes=bandwidth_bytes,
        latency_seconds=latency_seconds,
        metadata=metadata or {}
    )


def track_cdn_delivery(
    *,
    document,
    bandwidth_bytes: int,
    user: Optional[User] = None,
    channel: str = 'cdn',
    metadata: Optional[Dict[str, Any]] = None
) -> AssetEvent:
    """Track a CDN delivery event (Level 1).

    This is a lightweight helper for integrations that can report delivery
    bandwidth per asset. In Phase 1-2 this is typically fed by internal
    distribution/public links; Phase 3 can integrate external CDN billing.

    Args:
        document: Instance of `documents.Document`.
        bandwidth_bytes: Delivered bandwidth in bytes.
        user: Optional user that triggered the delivery.
        channel: Delivery channel identifier (cdn/public_link/etc).
        metadata: Arbitrary JSON-serializable metadata.

    Returns:
        Created AssetEvent instance.
    """
    return track_asset_event(
        document=document,
        event_type=AssetEvent.EVENT_TYPE_DELIVER,
        user=user,
        channel=channel,
        bandwidth_bytes=bandwidth_bytes,
        metadata=metadata or {}
    )


def anonymize_ip_address(ip_address: Optional[str]) -> Optional[str]:
    """Anonymize an IP address for privacy/GDPR.

    IPv4: keep first two octets, zero the rest: 192.168.0.0
    IPv6: keep first 4 hextets, zero the rest (best-effort): abcd:ef01:2345:6789:0000:0000:0000:0000
    """
    if not ip_address:
        return None

    value = str(ip_address).strip()
    if not value:
        return None

    if '.' in value:
        parts = value.split('.')
        if len(parts) == 4:
            return f'{parts[0]}.{parts[1]}.0.0'
        return value

    if ':' in value:
        parts = value.split(':')
        # best-effort, do not try to fully normalize compressed IPv6 here
        if len(parts) >= 4:
            return ':'.join(parts[:4] + ['0000'] * 4)
        return value

    return value


