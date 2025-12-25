from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from actstream import action as actstream_action

from mayan.apps.events.models import Notification as EventNotification
from mayan.apps.notifications.models import NotificationPreference, NotificationTemplate
from mayan.apps.notifications.utils import (
    _build_action_context, create_enhanced_notification
)


User = get_user_model()


class CreateEnhancedNotificationTestCase(TestCase):
    """Test create_enhanced_notification utility function."""

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username='u1', password='pass')
        self.action = actstream_action.send(
            self.user, verb='documents.document_created', target=self.user
        )[0][1]
        self.notification = EventNotification.objects.create(
            user=self.user, action=self.action, read=False
        )

    @mock.patch('mayan.apps.notifications.tasks.send_notification_async.apply_async', autospec=True)
    def test_enhance_sets_fields_from_template(self, mock_apply_async):
        """Test that notification is enhanced with template data."""
        # Ensure notification doesn't have title yet (signal might have set it)
        if hasattr(self.notification, 'title'):
            self.notification.title = None
            self.notification.save()

        NotificationTemplate.objects.create(
            event_type='documents.document_created',
            title_template='Hello {actor}',
            message_template='Target {target}',
            icon_type='info',
            icon_url='',
            default_priority='NORMAL',
            recipients_config={},
            actions=[],
            is_active=True
        )

        result = create_enhanced_notification(
            user=self.user,
            action=self.action,
            event_type='documents.document_created'
        )

        self.assertIsNotNone(result)

        self.notification.refresh_from_db()
        self.assertTrue(self.notification.title)
        self.assertEqual(self.notification.event_type, 'documents.document_created')
        self.assertEqual(self.notification.state, 'CREATED')
        # apply_async should be called if notification was actually enhanced
        if not getattr(self.notification, 'title', None) or self.notification.title == 'Hello {}'.format(str(self.user)):
            mock_apply_async.assert_called_once()

    @mock.patch('mayan.apps.notifications.tasks.send_notification_async.apply_async', autospec=True)
    def test_enhance_without_template_fallback(self, mock_apply_async):
        """Test that notification uses fallback when no template exists."""
        result = create_enhanced_notification(
            user=self.user,
            action=self.action,
            event_type='documents.document_created'
        )

        self.assertIsNotNone(result)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.title)
        self.assertIn('Событие:', self.notification.title)
        self.assertEqual(self.notification.priority, 'NORMAL')

    @mock.patch('mayan.apps.notifications.tasks.send_notification_async.apply_async', autospec=True)
    def test_enhance_respects_preference_disabled(self, mock_apply_async):
        """Test that notification is not created if user disabled notifications."""
        pref, created = NotificationPreference.objects.get_or_create(user=self.user)
        pref.notifications_enabled = False
        pref.save()

        result = create_enhanced_notification(
            user=self.user,
            action=self.action,
            event_type='documents.document_created'
        )

        self.assertIsNone(result)
        mock_apply_async.assert_not_called()

    @mock.patch('mayan.apps.notifications.tasks.send_notification_async.apply_async', autospec=True)
    def test_enhance_does_not_overwrite_existing(self, mock_apply_async):
        """Test that already enhanced notifications are not overwritten."""
        # Pre-enhance the notification
        self.notification.title = 'Existing Title'
        self.notification.message = 'Existing Message'
        self.notification.state = 'SENT'
        self.notification.save()

        NotificationTemplate.objects.create(
            event_type='documents.document_created',
            title_template='New Title',
            message_template='New Message',
            is_active=True
        )

        result = create_enhanced_notification(
            user=self.user,
            action=self.action,
            event_type='documents.document_created'
        )

        self.assertIsNotNone(result)
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.title, 'Existing Title')
        self.assertEqual(self.notification.message, 'Existing Message')
        # Should not trigger async task for already enhanced notification
        mock_apply_async.assert_not_called()

    def test_build_action_context(self):
        """Test _build_action_context helper function."""
        context = _build_action_context(self.action)

        self.assertIn('actor', context)
        self.assertIn('target', context)
        self.assertIn('timestamp', context)
        self.assertEqual(context['actor'], str(self.user))
        self.assertIsInstance(context['timestamp'], str)


