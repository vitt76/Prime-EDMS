"""Management command to enhance existing notifications without title."""

from django.core.management.base import BaseCommand

from mayan.apps.events.models import Notification as EventNotification
from mayan.apps.notifications.utils import create_enhanced_notification


class Command(BaseCommand):
    help = 'Enhance existing notifications without title'

    def handle(self, *args, **options):
        notifications = EventNotification.objects.filter(
            title__isnull=True
        ).select_related('action', 'user')
        total = notifications.count()
        self.stdout.write(f'Found {total} notifications to enhance')

        enhanced_count = 0
        error_count = 0

        for notification in notifications.iterator(chunk_size=100):
            try:
                result = create_enhanced_notification(
                    user=notification.user,
                    action=notification.action,
                    event_type=notification.action.verb
                )
                if result:
                    enhanced_count += 1
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'Failed to enhance notification {notification.id}: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Enhancement completed: {enhanced_count} enhanced, {error_count} errors'
            )
        )
