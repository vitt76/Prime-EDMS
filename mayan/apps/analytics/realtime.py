from typing import Any, Dict, Optional

from django.utils import timezone


def notify_analytics_refresh(
    *,
    reason: str = '',
    dashboard: str = '',
    asset_id: Optional[int] = None,
    metric: str = '',
    value: Optional[float] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> None:
    """Broadcast an analytics refresh signal to connected dashboard clients.

    The websocket payload is designed to be frontend-friendly and close to the
    DAM analytics spec.
    """
    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
    except Exception:
        return

    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    try:
        async_to_sync(channel_layer.group_send)(
            'analytics_dashboard_default',
            {
                'type': 'analytics.refresh',
                'reason': reason,
                'timestamp': timezone.now().isoformat(),
                'dashboard': dashboard or '',
                'asset_id': asset_id,
                'metric': metric or '',
                'value': value,
                'payload': payload or {},
            }
        )
    except Exception:
        return


