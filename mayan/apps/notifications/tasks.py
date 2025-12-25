import logging
from datetime import timedelta

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from mayan.apps.events.models import Notification as EventNotification

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_notification_async(self, notification_id: int):
    """Mark notification as sent and optionally send email (Phase 3).

    WebSocket delivery is deferred to Phase 4.
    """

    if not hasattr(EventNotification, 'state'):
        return

    try:
        notification = EventNotification.objects.select_related('user', 'action').get(pk=notification_id)
        user = notification.user

        preference = getattr(user, 'notification_preference', None)
        if preference and not preference.notifications_enabled:
            return

        notification.sent_at = timezone.now()
        notification.state = 'SENT'
        notification.save(update_fields=('sent_at', 'state'))

        if preference and preference.email_notifications_enabled:
            send_notification_email.apply_async(args=(notification.pk,), queue='notifications')

        if preference and getattr(preference, 'push_notifications_enabled', False):
            send_websocket_notification.apply_async(args=(notification.pk,), queue='notifications')
    except Exception as exc:
        logger.exception('send_notification_async failed for notification=%s', notification_id)
        raise self.retry(exc=exc)


@shared_task
def send_notification_email(notification_id: int):
    """Send a notification email to the user."""

    if not hasattr(EventNotification, 'title'):
        return

    try:
        notification = EventNotification.objects.select_related('user', 'action').get(pk=notification_id)
        user = notification.user

        if not user.email:
            return

        subject = notification.title or 'Уведомление'
        message = notification.message or ''

        html_message = None
        try:
            html_message = render_to_string(
                template_name='notifications/notification_email.html',
                context={'user': user, 'notification': notification}
            )
        except Exception:
            html_message = None

        send_mail(
            subject=subject,
            message=message,
            from_email=None,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=True
        )
    except Exception:
        logger.exception('send_notification_email failed for notification=%s', notification_id)


@shared_task
def cleanup_old_notifications():
    """Cleanup notifications older than 90 days (Phase 3)."""

    if not hasattr(EventNotification, 'state'):
        return

    cutoff = timezone.now() - timedelta(days=90)

    # Use action.timestamp for age (existing field), not a custom created_at.
    qs = EventNotification.objects.filter(
        action__timestamp__lt=cutoff,
        state__in=('ARCHIVED', 'DELETED')
    )
    deleted_count, _ = qs.delete()
    logger.info('cleanup_old_notifications deleted=%s', deleted_count)


@shared_task
def send_websocket_notification(notification_id: int):
    """Send notification to Channels group (Phase 4)."""

    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        notification = EventNotification.objects.select_related('user', 'action').get(pk=notification_id)

        if not hasattr(notification, 'title'):
            return

        channel_layer = get_channel_layer()
        if not channel_layer:
            return

        async_to_sync(channel_layer.group_send)(
            'notifications_{}'.format(notification.user_id),
            {
                'type': 'notification.new',
                'data': {
                    'id': notification.pk,
                    'title': getattr(notification, 'title', '') or '',
                    'message': getattr(notification, 'message', '') or '',
                    'priority': getattr(notification, 'priority', 'NORMAL') or 'NORMAL',
                    'icon_type': getattr(notification, 'icon_type', 'info') or 'info',
                    'created_at': notification.action.timestamp.isoformat() if notification.action else None,
                },
            },
        )
    except Exception:
        logger.exception('send_websocket_notification failed for notification=%s', notification_id)

