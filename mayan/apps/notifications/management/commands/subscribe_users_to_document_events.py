"""Management command to subscribe all users to document events."""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from mayan.apps.events.models import EventSubscription, StoredEventType

User = get_user_model()


class Command(BaseCommand):
    help = 'Subscribe all users to document events for notifications'

    def handle(self, *args, **options):
        # Subscribe to common document events
        document_event_types = [
            'documents.document_file_created',
            'documents.document_created',
            'documents.document_edited',
            'documents.document_version_created',
        ]
        
        subscribed_count = 0
        skipped_count = 0
        
        for event_type_name in document_event_types:
            try:
                stored_event_type = StoredEventType.objects.get(name=event_type_name)
            except StoredEventType.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Event type {event_type_name} not found, skipping')
                )
                continue
            
            for user in User.objects.all():
                subscription, created = EventSubscription.objects.get_or_create(
                    user=user,
                    stored_event_type=stored_event_type
                )
                if created:
                    subscribed_count += 1
                    self.stdout.write(
                        f'Subscribed {user.username} to {event_type_name}'
                    )
                else:
                    skipped_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Subscription completed: {subscribed_count} new subscriptions, {skipped_count} already subscribed'
            )
        )

