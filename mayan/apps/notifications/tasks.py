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


def _document_organization_id(document_pk):
    """Get organization_id for a Document by pk (unfiltered)."""
    from mayan.apps.documents.models import Document
    qs = Document.objects
    if hasattr(qs, 'all_organizations'):
        qs = qs.all_organizations()
    row = qs.filter(pk=document_pk).values_list('organization_id', flat=True).first()
    return str(row) if row is not None else None


def get_organization_id_for_notification(notification):
    """
    Resolve organization_id for a notification (Variant A: no events schema change).

    Priority: action.target if Document -> target.organization_id;
    else action.action_object if Document -> action_object.organization_id;
    else user's default organization from UserOrganizationRole.
    Returns str UUID or None.
    """
    from django.contrib.contenttypes.models import ContentType

    try:
        action = notification.action
        if not action:
            return _default_organization_id_for_user(notification.user_id)

        from mayan.apps.documents.models import Document
        doc_ct = ContentType.objects.get_for_model(Document)

        if action.target_content_type_id == doc_ct.pk and action.target_object_id:
            org_id = _document_organization_id(action.target_object_id)
            if org_id:
                return org_id

        if action.action_object_content_type_id == doc_ct.pk and action.action_object_object_id:
            org_id = _document_organization_id(action.action_object_object_id)
            if org_id:
                return org_id

        return _default_organization_id_for_user(notification.user_id)
    except Exception:
        logger.debug('get_organization_id_for_notification failed', exc_info=True)
        return _default_organization_id_for_user(notification.user_id)


def _default_organization_id_for_user(user_id):
    """User's default organization or first organization they belong to."""
    from mayan.apps.organizations.models import UserOrganizationRole
    row = UserOrganizationRole.objects.filter(
        user_id=user_id,
        is_default=True,
    ).values_list('organization_id', flat=True).first()
    if row is not None:
        return str(row)
    row = UserOrganizationRole.objects.filter(user_id=user_id).values_list('organization_id', flat=True).first()
    return str(row) if row is not None else None


@shared_task
def send_websocket_notification(notification_id: int):
    """Send notification to Channels group (Phase 4). Group is scoped by organization_id."""

    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        notification = EventNotification.objects.select_related('user', 'action').get(pk=notification_id)

        if not hasattr(notification, 'title'):
            return

        organization_id = get_organization_id_for_notification(notification)
        if not organization_id:
            logger.debug('send_websocket_notification: no organization_id for notification=%s', notification_id)
            return

        channel_layer = get_channel_layer()
        if not channel_layer:
            return

        group_name = 'notifications_{}_{}'.format(organization_id, notification.user_id)
        async_to_sync(channel_layer.group_send)(
            group_name,
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

