from mayan.apps.events.managers import NotificationManager as BaseNotificationManager


class EnhancedNotificationManager(BaseNotificationManager):
    """Extended manager for `events.Notification` to support new states."""

    def unread_for_user(self, user):
        queryset = self.filter(user=user)

        # Prefer new state-based unread if present; fallback to legacy `read`.
        if hasattr(self.model, 'state'):
            # Include both CREATED and SENT as unread:
            # - CREATED: just created, pending Celery delivery task
            # - SENT: delivered to user (email/WebSocket)
            return queryset.filter(state__in=('CREATED', 'SENT'))

        return queryset.filter(read=False)


