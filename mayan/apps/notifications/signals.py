import logging

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import NotificationPreference

logger = logging.getLogger(__name__)


@receiver(post_save, sender=get_user_model())
def create_notification_preference(sender, instance, created, **kwargs):
    """Create NotificationPreference for new users and auto-subscribe to document events."""

    if created:
        preference, _ = NotificationPreference.objects.get_or_create(user=instance)
        
        # Auto-subscribe user to document events for notifications
        try:
            from mayan.apps.events.models import EventSubscription, StoredEventType
            
            # Subscribe to common document events
            document_event_types = [
                'documents.document_file_created',
                'documents.document_created',
                'documents.document_edited',
                'documents.document_version_created',
                # Lifecycle (trash/restore/delete) - must appear in Notification Center
                'documents.document_trashed',
                'documents.trashed_document_restored',
                'documents.trashed_document_deleted',
            ]
            
            for event_type_name in document_event_types:
                try:
                    stored_event_type = StoredEventType.objects.get(name=event_type_name)
                    EventSubscription.objects.get_or_create(
                        user=instance,
                        stored_event_type=stored_event_type
                    )
                    logger.info('Auto-subscribed user %s to event %s', instance.username, event_type_name)
                except StoredEventType.DoesNotExist:
                    logger.debug('Event type %s not found, skipping auto-subscription', event_type_name)
                except Exception as e:
                    logger.warning('Failed to auto-subscribe user %s to event %s: %s', instance.username, event_type_name, e)
        except Exception as e:
            logger.warning('Failed to auto-subscribe user %s to document events: %s', instance.username, e)


# [REMOVED] enhance_notification_on_create signal
# Enhancement is now done via direct call in EventType.commit() for better
# transaction control and to avoid unnecessary DB records.
# See: mayan/apps/events/classes.py EventType.commit() method


