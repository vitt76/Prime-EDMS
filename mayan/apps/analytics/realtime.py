from django.utils import timezone


def notify_analytics_refresh(*, reason: str = '') -> None:
    """Broadcast a "refresh" signal to connected analytics dashboard clients."""
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
            'analytics_updates',
            {
                'type': 'analytics.refresh',
                'reason': reason,
                'timestamp': timezone.now().isoformat(),
            }
        )
    except Exception:
        return


