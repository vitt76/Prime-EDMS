import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class NotificationTemplate(models.Model):
    """Template used to enrich Mayan notifications with title/message/actions."""

    event_type = models.CharField(
        max_length=64, unique=True, verbose_name=_('Event type')
    )
    title_template = models.CharField(
        max_length=255, verbose_name=_('Title template')
    )
    message_template = models.TextField(
        blank=True, default='', verbose_name=_('Message template')
    )

    icon_type = models.CharField(
        blank=True, default='info', max_length=50, verbose_name=_('Icon type')
    )
    icon_url = models.URLField(
        blank=True, default='', verbose_name=_('Icon URL')
    )

    default_priority = models.CharField(
        blank=True, default='NORMAL', max_length=20, verbose_name=_('Default priority')
    )

    recipients_config = models.JSONField(
        blank=True, default=dict, verbose_name=_('Recipients config')
    )
    actions = models.JSONField(
        blank=True, default=list, verbose_name=_('Actions')
    )

    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated'))

    class Meta:
        db_table = 'notifications_template'
        verbose_name = _('Notification template')
        verbose_name_plural = _('Notification templates')
        indexes = (
            models.Index(fields=('event_type',), name='notif_tpl_event_type_idx'),
        )

    def __str__(self):
        return str(self.event_type)


class NotificationPreference(models.Model):
    """User preferences (extra settings) for notifications.

    Note: Subscriptions are managed by Mayan's EventSubscription models.
    This model stores only additional delivery settings (email, quiet hours, etc.).
    """

    user = models.OneToOneField(
        on_delete=models.CASCADE,
        related_name='notification_preference',
        to=settings.AUTH_USER_MODEL,
        verbose_name=_('User')
    )

    notifications_enabled = models.BooleanField(default=True, verbose_name=_('Notifications enabled'))
    email_notifications_enabled = models.BooleanField(default=True, verbose_name=_('Email notifications enabled'))
    push_notifications_enabled = models.BooleanField(default=True, verbose_name=_('Push notifications enabled'))

    email_digest_enabled = models.BooleanField(default=False, verbose_name=_('Email digest enabled'))
    email_digest_frequency = models.CharField(
        blank=True, default='never', max_length=20, verbose_name=_('Email digest frequency')
    )

    quiet_hours_enabled = models.BooleanField(default=False, verbose_name=_('Quiet hours enabled'))
    quiet_hours_start = models.TimeField(blank=True, null=True, verbose_name=_('Quiet hours start'))
    quiet_hours_end = models.TimeField(blank=True, null=True, verbose_name=_('Quiet hours end'))

    notification_language = models.CharField(
        blank=True, default='ru', max_length=10, verbose_name=_('Notification language')
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated'))

    class Meta:
        db_table = 'notifications_preference'
        verbose_name = _('Notification preference')
        verbose_name_plural = _('Notification preferences')
        indexes = (
            models.Index(fields=('user',), name='notif_pref_user_idx'),
        )

    def __str__(self):
        return 'Notification preferences: {}'.format(self.user)


class NotificationLog(models.Model):
    """Audit log of actions performed on notifications (read, deleted, etc.)."""

    # We reference events.Notification to keep one unified source of truth.
    notification = models.ForeignKey(
        on_delete=models.CASCADE,
        related_name='logs',
        to='events.Notification',
        verbose_name=_('Notification')
    )
    action = models.CharField(max_length=50, verbose_name=_('Action'))
    action_data = models.JSONField(blank=True, default=dict, verbose_name=_('Action data'))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('Timestamp'))

    # Reserved field for future idempotency / external correlation.
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name=_('UUID'))

    class Meta:
        db_table = 'notifications_log'
        verbose_name = _('Notification log')
        verbose_name_plural = _('Notification logs')
        indexes = (
            models.Index(fields=('notification', '-timestamp'), name='notif_log_notif_ts_idx'),
        )

    def __str__(self):
        return '{}: {}'.format(self.notification_id, self.action)


