from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from actstream import action as actstream_action

from mayan.apps.events.classes import EventType
from mayan.apps.events.models import Notification as EventNotification
from mayan.apps.notifications.models import NotificationPreference, NotificationTemplate
from mayan.apps.notifications.utils import create_enhanced_notification


User = get_user_model()


class NotificationIntegrationTestCase(TestCase):
    """Integration tests for end-to-end notification flow."""

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        NotificationPreference.objects.create(user=self.user)

    @mock.patch('mayan.apps.notifications.tasks.send_notification_async.apply_async', autospec=True)
    def test_event_to_enhanced_notification_flow(self, mock_send_task):
        """Test complete flow: Event → EventType.commit() → Enhanced Notification."""
        # Create template
        template = NotificationTemplate.objects.create(
            event_type='documents.document_created',
            title_template='Document created by {actor}',
            message_template='Document: {target}',
            default_priority='HIGH',
            icon_type='success',
            actions=[{'id': 'view', 'label': 'View', 'url': '/documents/1/'}],
            is_active=True
        )

        # Create action (simulating EventType.commit())
        action = actstream_action.send(
            self.user,
            verb='documents.document_created',
            target=self.user
        )[0][1]

        # Create base notification (what Mayan does)
        notification = EventNotification.objects.create(
            user=self.user,
            action=action,
            read=False
        )

        # Enhance notification (what our signal does)
        enhanced = create_enhanced_notification(
            user=self.user,
            action=action,
            event_type='documents.document_created',
            template=template
        )

        # Verify enhancement
        self.assertIsNotNone(enhanced)
        enhanced.refresh_from_db()
        self.assertEqual(enhanced.title, f'Document created by {self.user}')
        self.assertEqual(enhanced.message, f'Document: {self.user}')
        self.assertEqual(enhanced.priority, 'HIGH')
        self.assertEqual(enhanced.icon_type, 'success')
        self.assertEqual(len(enhanced.actions), 1)
        self.assertEqual(enhanced.state, 'CREATED')
        self.assertEqual(enhanced.event_type, 'documents.document_created')

        # Verify async task was triggered
        mock_send_task.assert_called_once()

    @mock.patch('mayan.apps.notifications.tasks.send_notification_async.apply_async', autospec=True)
    def test_notification_with_preference_disabled(self, mock_send_task):
        """Test that notifications are not created if user disabled them."""
        pref = NotificationPreference.objects.get(user=self.user)
        pref.notifications_enabled = False
        pref.save()

        action = actstream_action.send(
            self.user,
            verb='documents.document_created',
            target=self.user
        )[0][1]

        notification = EventNotification.objects.create(
            user=self.user,
            action=action,
            read=False
        )

        enhanced = create_enhanced_notification(
            user=self.user,
            action=action,
            event_type='documents.document_created'
        )

        # Should return None if disabled
        self.assertIsNone(enhanced)
        mock_send_task.assert_not_called()

    @mock.patch('mayan.apps.notifications.tasks.send_notification_async.apply_async', autospec=True)
    def test_notification_fallback_without_template(self, mock_send_task):
        """Test that notification uses fallback when no template exists."""
        action = actstream_action.send(
            self.user,
            verb='unknown.event_type',
            target=self.user
        )[0][1]

        notification = EventNotification.objects.create(
            user=self.user,
            action=action,
            read=False
        )

        enhanced = create_enhanced_notification(
            user=self.user,
            action=action,
            event_type='unknown.event_type'
        )

        # Should still create notification with fallback values
        self.assertIsNotNone(enhanced)
        enhanced.refresh_from_db()
        self.assertIn('Событие:', enhanced.title)
        self.assertEqual(enhanced.priority, 'NORMAL')
        mock_send_task.assert_called_once()

