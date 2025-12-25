import logging
from typing import Any, Dict, Optional

from mayan.apps.events.models import Notification as EventNotification

from .models import NotificationPreference, NotificationTemplate

logger = logging.getLogger(__name__)


def _build_action_context(action) -> Dict[str, Any]:
    """Build a safe template context from an actstream Action."""

    # Action has GenericFKs; string conversion is safe and avoids DB chasing.
    return {
        'actor': str(action.actor) if getattr(action, 'actor', None) else '',
        'target': str(action.target) if getattr(action, 'target', None) else '',
        'action_object': str(action.action_object) if getattr(action, 'action_object', None) else '',
        'timestamp': action.timestamp.strftime('%d.%m.%Y %H:%M') if getattr(action, 'timestamp', None) else '',
    }


def create_enhanced_notification(user, action, event_type: str, template: Optional[NotificationTemplate] = None):
    """Create or enrich a Mayan `events.Notification` instance.

    This function updates existing base notifications with extra fields:
    title/message/priority/state/icon/actions/event_data timestamps.

    Notes:
    - We do NOT create a new notification table; we enrich `events_notification`.
    - If the schema is not migrated yet, this function becomes a no-op.
    - NotificationPreference.notifications_enabled is checked BEFORE calling this function
      in EventType.commit() for DB optimization. If notification was created, user is
      subscribed and notifications are enabled.
    """

    # Schema may not be migrated yet. Keep runtime safe.
    if not hasattr(EventNotification, 'title'):
        return None

    # NOTE: NotificationPreference.notifications_enabled check is removed.
    # It is now performed in EventType.commit() BEFORE creating the base notification
    # to optimize DB size (no record created if user disabled notifications).

    # Find "the" base notification for (user, action). Handle duplicates gracefully.
    notification = EventNotification.objects.filter(user=user, action=action).order_by('-pk').first()
    if not notification:
        logger.warning('Base notification not found for user=%s, action=%s', user.id, action.id)
        return None

    # Do not overwrite already enhanced notifications.
    if getattr(notification, 'title', None):
        return notification

    if template is None:
        template = NotificationTemplate.objects.filter(event_type=event_type, is_active=True).first()

    context = _build_action_context(action=action)

    title = None
    message = ''
    priority = 'NORMAL'
    icon_type = 'info'
    icon_url = ''
    actions_payload = []
    event_data = {}

    if template:
        try:
            title = template.title_template.format(**context)
        except Exception:
            title = template.title_template

        try:
            message = (template.message_template or '').format(**context)
        except Exception:
            message = template.message_template or ''

        priority = template.default_priority or priority
        icon_type = template.icon_type or icon_type
        icon_url = template.icon_url or icon_url
        actions_payload = template.actions or []
        event_data = {}
    else:
        title = 'Событие: {}'.format(event_type)
        message = str(action)

    # Update fields (only those available in the current schema).
    notification.title = title
    notification.message = message
    notification.event_type = event_type
    notification.event_data = event_data
    notification.priority = priority
    notification.state = 'CREATED'
    notification.icon_type = icon_type
    notification.icon_url = icon_url
    notification.actions = actions_payload
    notification.sent_at = None
    notification.read_at = None
    notification.archived_at = None
    notification.deleted_at = None
    notification.expires_at = None
    notification.is_mutable = True
    notification.is_removable = True
    notification.metadata = {}
    notification.save()

    logger.info(
        'Enhanced notification id=%s for user=%s, event_type=%s',
        notification.pk, user.id, event_type
    )

    # Trigger async delivery (Phase 3).
    try:
        from .tasks import send_notification_async
        send_notification_async.apply_async(args=(notification.pk,), queue='notifications')
    except Exception:
        logger.exception('Failed to enqueue send_notification_async for notification=%s', notification.pk)

    return notification
