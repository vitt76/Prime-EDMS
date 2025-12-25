from rest_framework import serializers

from mayan.apps.events.models import Notification as EventNotification

from .models import NotificationPreference


class NotificationActionSerializer(serializers.Serializer):
    """Serializer for notification actions (buttons/links)."""

    id = serializers.CharField()
    label = serializers.CharField()
    url = serializers.CharField()
    type = serializers.ChoiceField(choices=('link', 'button'))
    icon = serializers.CharField(required=False, allow_blank=True)
    style = serializers.CharField(required=False, allow_blank=True)


class NotificationSerializer(serializers.ModelSerializer):
    """Full notification serializer with fallback for legacy notifications."""

    actions = NotificationActionSerializer(many=True, required=False)
    created_at = serializers.DateTimeField(source='action.timestamp', read_only=True)

    class Meta:
        model = EventNotification
        fields = (
            'id',
            'uuid',
            'title',
            'message',
            'event_type',
            'event_data',
            'priority',
            'state',
            'icon_type',
            'icon_url',
            'actions',
            'created_at',
            'sent_at',
            'read_at',
            'archived_at',
            'deleted_at',
            'expires_at',
        )
        read_only_fields = fields

    def to_representation(self, instance):
        """Add fallback for legacy notifications without title.
        
        For legacy notifications (created before migration 0010_extend_notification),
        dynamically generate title, message, and other fields from the Action object.
        This ensures backward compatibility and preserves notification history.
        """
        data = super().to_representation(instance)

        # Fallback для старых уведомлений (title is NULL)
        if not data.get('title'):
            event_type = instance.action.verb if instance.action else 'unknown'
            data['title'] = f'Событие: {event_type}'
            data['message'] = str(instance.action) if instance.action else ''
            data['event_type'] = event_type
            data['priority'] = data.get('priority') or 'NORMAL'
            data['icon_type'] = data.get('icon_type') or 'info'
            data['actions'] = data.get('actions') or []

        return data


class NotificationListSerializer(serializers.ModelSerializer):
    """List serializer optimized for popover with fallback for legacy notifications."""

    created_at = serializers.DateTimeField(source='action.timestamp', read_only=True)

    class Meta:
        model = EventNotification
        fields = (
            'id',
            'uuid',
            'title',
            'message',
            'event_type',
            'priority',
            'state',
            'icon_type',
            'created_at',
            'read_at',
        )
        read_only_fields = fields

    def to_representation(self, instance):
        """Add fallback for legacy notifications without title.
        
        For legacy notifications (created before migration 0010_extend_notification),
        dynamically generate title, message, and other fields from the Action object.
        This ensures backward compatibility and preserves notification history.
        """
        data = super().to_representation(instance)

        # Fallback для старых уведомлений (title is NULL)
        if not data.get('title'):
            event_type = instance.action.verb if instance.action else 'unknown'
            data['title'] = f'Событие: {event_type}'
            data['message'] = str(instance.action) if instance.action else ''
            data['event_type'] = event_type
            data['priority'] = data.get('priority') or 'NORMAL'
            data['icon_type'] = data.get('icon_type') or 'info'

        return data


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreference (without subscriptions)."""

    class Meta:
        model = NotificationPreference
        fields = (
            'notifications_enabled',
            'email_notifications_enabled',
            'push_notifications_enabled',
            'email_digest_enabled',
            'email_digest_frequency',
            'quiet_hours_enabled',
            'quiet_hours_start',
            'quiet_hours_end',
            'notification_language',
        )


