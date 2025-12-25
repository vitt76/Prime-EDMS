import uuid

from django.db import migrations
from django.utils import timezone


def _safe_format(template: str, context: dict) -> str:
    try:
        return (template or '').format(**context)
    except Exception:
        return template or ''


def populate_notifications(apps, schema_editor):
    """Populate new notification fields for existing rows.

    - event_type comes from Action.verb
    - title/message/priority/icon/actions can be generated via NotificationTemplate
    - state set to SENT/READ based on legacy `read` flag
    """

    Notification = apps.get_model('events', 'Notification')
    NotificationTemplate = apps.get_model('notifications', 'NotificationTemplate')

    # Select only rows that were not enriched yet.
    queryset = Notification.objects.filter(title__isnull=True).select_related('action')

    for notification in queryset.iterator():
        action = notification.action
        event_type = getattr(action, 'verb', None) or ''

        template = NotificationTemplate.objects.filter(
            event_type=event_type,
            is_active=True
        ).first()

        context = {
            'actor': str(getattr(action, 'actor', '') or ''),
            'target': str(getattr(action, 'target', '') or ''),
            'action_object': str(getattr(action, 'action_object', '') or ''),
            'timestamp': action.timestamp.strftime('%d.%m.%Y %H:%M') if getattr(action, 'timestamp', None) else '',
        }

        if template:
            title = _safe_format(template.title_template, context=context) or template.title_template
            message = _safe_format(template.message_template, context=context)
            priority = template.default_priority or 'NORMAL'
            icon_type = template.icon_type or 'info'
            icon_url = template.icon_url or ''
            actions_payload = template.actions or []
        else:
            title = 'Событие: {}'.format(event_type)
            message = str(action)
            priority = 'NORMAL'
            icon_type = 'info'
            icon_url = ''
            actions_payload = []

        notification.uuid = notification.uuid or uuid.uuid4()
        notification.title = title
        notification.message = message
        notification.icon_type = icon_type
        notification.icon_url = icon_url
        notification.event_type = event_type
        notification.event_data = notification.event_data or {}
        notification.priority = priority
        notification.actions = actions_payload

        if notification.read:
            notification.state = 'READ'
            notification.read_at = notification.read_at or timezone.now()
        else:
            notification.state = 'SENT'
            notification.sent_at = notification.sent_at or timezone.now()

        notification.save()


def reverse_populate(apps, schema_editor):
    """No-op reverse migration."""


class Migration(migrations.Migration):
    dependencies = [
        ('notifications', '0001_initial'),
        ('events', '0010_extend_notification'),
    ]

    operations = [
        migrations.RunPython(code=populate_notifications, reverse_code=reverse_populate),
    ]


