import logging
from typing import Any, Dict, Optional

from mayan.apps.events.models import Notification as EventNotification

from .models import NotificationPreference, NotificationTemplate

logger = logging.getLogger(__name__)


def _build_action_context(action) -> Dict[str, Any]:
    """Build a safe template context from an actstream Action."""

    # Action has GenericFKs; string conversion is safe and avoids DB chasing.
    context: Dict[str, Any] = {
        'actor': str(action.actor) if getattr(action, 'actor', None) else '',
        'target': str(action.target) if getattr(action, 'target', None) else '',
        'action_object': str(action.action_object) if getattr(action, 'action_object', None) else '',
        'timestamp': action.timestamp.strftime('%d.%m.%Y %H:%M') if getattr(action, 'timestamp', None) else '',
    }

    # IDs and content-type metadata (safe, no GFK dereference).
    # These keys enable URL/action templating, e.g. `/documents/{document_id}/`.
    context['actor_id'] = getattr(getattr(action, 'actor', None), 'pk', None)
    context['target_id'] = getattr(action, 'target_object_id', None)
    context['action_object_id'] = getattr(action, 'action_object_object_id', None)
    context['verb'] = getattr(action, 'verb', '') or ''

    # Convenience: document_id if the action references a Document as target or action_object.
    try:
        target_ct = getattr(action, 'target_content_type', None)
        action_object_ct = getattr(action, 'action_object_content_type', None)
        if target_ct and getattr(target_ct, 'model', None) == 'document' and context['target_id']:
            context['document_id'] = context['target_id']
        elif action_object_ct and getattr(action_object_ct, 'model', None) == 'document' and context['action_object_id']:
            context['document_id'] = context['action_object_id']
        else:
            context['document_id'] = None
    except Exception:
        context['document_id'] = None

    return context


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
    - Enterprise reliability: if Celery is unavailable when enqueueing delivery tasks,
      we fall back to synchronously marking the notification as SENT so the user can
      still see it in the UI.
    """
    # #region agent log
    import json
    try:
        with open('c:\\DAM\\Prime-EDMS\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'A',
                'location': 'notifications/utils.py:23',
                'message': 'create_enhanced_notification entry',
                'data': {'user_id': user.id, 'action_id': action.id, 'event_type': event_type},
                'timestamp': int(__import__('time').time() * 1000)
            }) + '\n')
    except Exception:
        pass
    # #endregion

    # Schema may not be migrated yet. Keep runtime safe.
    if not hasattr(EventNotification, 'title'):
        # #region agent log
        try:
            with open('c:\\DAM\\Prime-EDMS\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'C',
                    'location': 'notifications/utils.py:41',
                    'message': 'Schema not migrated - returning None',
                    'data': {'user_id': user.id, 'action_id': action.id},
                    'timestamp': int(__import__('time').time() * 1000)
                }) + '\n')
        except Exception:
            pass
        # #endregion
        return None

    # NOTE: NotificationPreference.notifications_enabled check is removed.
    # It is now performed in EventType.commit() BEFORE creating the base notification
    # to optimize DB size (no record created if user disabled notifications).

    # Find "the" base notification for (user, action). Handle duplicates gracefully.
    notification = EventNotification.objects.filter(user=user, action=action).order_by('-pk').first()
    # #region agent log
    try:
        with open('c:\\DAM\\Prime-EDMS\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'B',
                'location': 'notifications/utils.py:49',
                'message': 'Base notification lookup',
                'data': {'user_id': user.id, 'action_id': action.id, 'notification_found': notification is not None, 'notification_id': notification.pk if notification else None},
                'timestamp': int(__import__('time').time() * 1000)
            }) + '\n')
    except Exception:
        pass
    # #endregion
    if not notification:
        logger.warning('Base notification not found for user=%s, action=%s', user.id, action.id)
        return None

    # Do not overwrite already enhanced notifications.
    existing_title = getattr(notification, 'title', None)
    # #region agent log
    try:
        with open('c:\\DAM\\Prime-EDMS\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'C',
                'location': 'notifications/utils.py:55',
                'message': 'Check if already enhanced',
                'data': {'notification_id': notification.pk, 'existing_title': existing_title, 'already_enhanced': bool(existing_title)},
                'timestamp': int(__import__('time').time() * 1000)
            }) + '\n')
    except Exception:
        pass
    # #endregion
    if existing_title:
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
    else:
        title = 'Событие: {}'.format(event_type)
        message = str(action)

    # Build event_data for client-side routing/actions.
    # No PII; only IDs and model labels.
    event_data = {}
    try:
        event_data['verb'] = event_type
        event_data['actor_id'] = context.get('actor_id')
        event_data['target'] = {
            'content_type_id': getattr(getattr(action, 'target_content_type', None), 'pk', None),
            'model': getattr(getattr(action, 'target_content_type', None), 'model', None),
            'object_id': getattr(action, 'target_object_id', None),
        }
        event_data['action_object'] = {
            'content_type_id': getattr(getattr(action, 'action_object_content_type', None), 'pk', None),
            'model': getattr(getattr(action, 'action_object_content_type', None), 'model', None),
            'object_id': getattr(action, 'action_object_object_id', None),
        }
    except Exception:
        event_data = {}

    # Allow action payload templates to reference context variables.
    # Example: { "id": "view", "label": "Открыть", "url": "/documents/{document_id}/", "type": "link" }
    formatted_actions = []
    for item in actions_payload or []:
        if not isinstance(item, dict):
            continue
        new_item = dict(item)
        for key in ('label', 'url'):
            if isinstance(new_item.get(key), str):
                try:
                    new_item[key] = new_item[key].format(**context)
                except Exception:
                    pass
        formatted_actions.append(new_item)
    actions_payload = formatted_actions

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

    # Best-effort: set content_object for document-related notifications to enable
    # consistent object-level filtering and front-end navigation.
    try:
        document_id = context.get('document_id')
        if document_id:
            from django.contrib.contenttypes.models import ContentType
            from mayan.apps.documents.models import Document

            notification.content_type = ContentType.objects.get_for_model(Document)
            notification.object_id = int(document_id)
    except Exception:
        # Do not fail notification creation due to enrichment issues.
        pass
    notification.save()
    # #region agent log
    try:
        with open('c:\\DAM\\Prime-EDMS\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'C',
                'location': 'notifications/utils.py:109',
                'message': 'Notification saved with enhanced fields',
                'data': {'notification_id': notification.pk, 'title': title, 'state': 'CREATED', 'event_type': event_type},
                'timestamp': int(__import__('time').time() * 1000)
            }) + '\n')
    except Exception:
        pass
    # #endregion

    logger.info(
        'Enhanced notification id=%s for user=%s, event_type=%s',
        notification.pk, user.id, event_type
    )

    # Trigger async delivery (Phase 3).
    try:
        from .tasks import send_notification_async
        # #region agent log
        try:
            with open('c:\\DAM\\Prime-EDMS\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'A',
                    'location': 'notifications/utils.py:119',
                    'message': 'Enqueueing Celery task',
                    'data': {'notification_id': notification.pk},
                    'timestamp': int(__import__('time').time() * 1000)
                }) + '\n')
        except Exception:
            pass
        # #endregion
        send_notification_async.apply_async(args=(notification.pk,), queue='notifications')
        # #region agent log
        try:
            with open('c:\\DAM\\Prime-EDMS\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'A',
                    'location': 'notifications/utils.py:120',
                    'message': 'Celery task enqueued successfully',
                    'data': {'notification_id': notification.pk},
                    'timestamp': int(__import__('time').time() * 1000)
                }) + '\n')
        except Exception:
            pass
        # #endregion
    except Exception:
        logger.exception('Failed to enqueue send_notification_async for notification=%s', notification.pk)
        # #region agent log
        try:
            with open('c:\\DAM\\Prime-EDMS\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'A',
                    'location': 'notifications/utils.py:122',
                    'message': 'Celery task failed - using fallback',
                    'data': {'notification_id': notification.pk},
                    'timestamp': int(__import__('time').time() * 1000)
                }) + '\n')
        except Exception:
            pass
        # #endregion
        # Fallback for Enterprise: if Celery is unavailable, mark as SENT synchronously.
        # This ensures notifications are visible to users even if async queue is down.
        try:
            from django.utils import timezone

            notification.sent_at = timezone.now()
            notification.state = 'SENT'
            notification.save(update_fields=('sent_at', 'state'))
            # #region agent log
            try:
                with open('c:\\DAM\\Prime-EDMS\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                    f.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'A',
                        'location': 'notifications/utils.py:130',
                        'message': 'Fallback: marked as SENT synchronously',
                        'data': {'notification_id': notification.pk, 'state': 'SENT'},
                        'timestamp': int(__import__('time').time() * 1000)
                    }) + '\n')
            except Exception:
                pass
            # #endregion
            logger.warning(
                'Notification id=%s marked as SENT synchronously (Celery unavailable)',
                notification.pk
            )
        except Exception:
            logger.exception('Failed to mark notification as SENT synchronously for notification=%s', notification.pk)

    return notification
