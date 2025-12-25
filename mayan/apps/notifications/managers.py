from mayan.apps.events.managers import NotificationManager as BaseNotificationManager


class EnhancedNotificationManager(BaseNotificationManager):
    """Extended manager for `events.Notification` to support new states."""

    def unread_for_user(self, user):
        queryset = self.filter(user=user)

        # Prefer new state-based unread if present; fallback to legacy `read`.
        if hasattr(self.model, 'state'):
            return queryset.filter(state='SENT')

        return queryset.filter(read=False)


