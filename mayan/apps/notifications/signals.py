import logging

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import NotificationPreference

logger = logging.getLogger(__name__)


@receiver(post_save, sender=get_user_model())
def create_notification_preference(sender, instance, created, **kwargs):
    """Create NotificationPreference for new users."""

    if created:
        NotificationPreference.objects.get_or_create(user=instance)


# [REMOVED] enhance_notification_on_create signal
# Enhancement is now done via direct call in EventType.commit() for better
# transaction control and to avoid unnecessary DB records.
# See: mayan/apps/events/classes.py EventType.commit() method


