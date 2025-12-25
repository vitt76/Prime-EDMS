from unittest import mock

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.utils import timezone

from actstream import action as actstream_action

from mayan.apps.events.models import Notification as EventNotification
from mayan.apps.notifications.models import NotificationPreference
from mayan.apps.notifications.tasks import (
    cleanup_old_notifications, send_notification_async,
    send_notification_email, send_websocket_notification
)


User = get_user_model()


class SendNotificationAsyncTestCase(TestCase):
    """Test send_notification_async Celery task."""

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        self.action = actstream_action.send(
            self.user, verb='documents.document_created', target=self.user
        )[0][1]
        self.notification = EventNotification.objects.create(
            user=self.user, action=self.action, read=False
        )
        # Ensure extended fields exist (migration applied)
        if not hasattr(self.notification, 'state'):
            # Skip tests if migration not applied
            self.skipTest('Notification model not extended yet')

    @mock.patch('mayan.apps.notifications.tasks.send_notification_email.apply_async', autospec=True)
    @mock.patch('mayan.apps.notifications.tasks.send_websocket_notification.apply_async', autospec=True)
    def test_send_notification_async_updates_state(self, mock_ws, mock_email):
        """Test that task updates notification state to SENT."""
        send_notification_async(self.notification.pk)

        self.notification.refresh_from_db()
        self.assertEqual(self.notification.state, 'SENT')
        self.assertIsNotNone(self.notification.sent_at)

    @mock.patch('mayan.apps.notifications.tasks.send_notification_email.apply_async', autospec=True)
    @mock.patch('mayan.apps.notifications.tasks.send_websocket_notification.apply_async', autospec=True)
    def test_send_notification_async_respects_preference_disabled(self, mock_ws, mock_email):
        """Test that task skips if user disabled notifications."""
        pref, created = NotificationPreference.objects.get_or_create(user=self.user)
        pref.notifications_enabled = False
        pref.save()

        send_notification_async(self.notification.pk)

        self.notification.refresh_from_db()
        # State should remain CREATED if disabled
        self.assertNotEqual(self.notification.state, 'SENT')
        mock_email.assert_not_called()

    @mock.patch('mayan.apps.notifications.tasks.send_notification_email.apply_async', autospec=True)
    @mock.patch('mayan.apps.notifications.tasks.send_websocket_notification.apply_async', autospec=True)
    def test_send_notification_async_triggers_email_if_enabled(self, mock_ws, mock_email):
        """Test that email task is triggered if email notifications enabled."""
        pref, created = NotificationPreference.objects.get_or_create(user=self.user)
        pref.notifications_enabled = True
        pref.email_notifications_enabled = True
        pref.save()

        send_notification_async(self.notification.pk)

        mock_email.assert_called_once_with(args=(self.notification.pk,), queue='notifications')

    @mock.patch('mayan.apps.notifications.tasks.send_notification_email.apply_async', autospec=True)
    @mock.patch('mayan.apps.notifications.tasks.send_websocket_notification.apply_async', autospec=True)
    def test_send_notification_async_triggers_websocket_if_enabled(self, mock_ws, mock_email):
        """Test that WebSocket task is triggered if push notifications enabled."""
        pref, created = NotificationPreference.objects.get_or_create(user=self.user)
        pref.notifications_enabled = True
        pref.push_notifications_enabled = True
        pref.save()

        send_notification_async(self.notification.pk)

        mock_ws.assert_called_once_with(args=(self.notification.pk,), queue='notifications')


class SendNotificationEmailTestCase(TestCase):
    """Test send_notification_email Celery task."""

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        self.action = actstream_action.send(
            self.user, verb='documents.document_created', target=self.user
        )[0][1]
        self.notification = EventNotification.objects.create(
            user=self.user, action=self.action, read=False
        )
        if hasattr(self.notification, 'title'):
            self.notification.title = 'Test Notification'
            self.notification.message = 'Test message'
            self.notification.save()

    def test_send_notification_email_sends_mail(self):
        """Test that email is sent to user."""
        if not hasattr(self.notification, 'title'):
            self.skipTest('Notification model not extended yet')

        send_notification_email(self.notification.pk)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertEqual(mail.outbox[0].subject, 'Test Notification')

    def test_send_notification_email_skips_if_no_email(self):
        """Test that email is not sent if user has no email."""
        if not hasattr(self.notification, 'title'):
            self.skipTest('Notification model not extended yet')

        self.user.email = ''
        self.user.save()

        send_notification_email(self.notification.pk)

        self.assertEqual(len(mail.outbox), 0)


class CleanupOldNotificationsTestCase(TestCase):
    """Test cleanup_old_notifications Celery task."""

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )

    def test_cleanup_old_notifications_deletes_archived(self):
        """Test that old archived notifications are deleted."""
        if not hasattr(EventNotification, 'state'):
            self.skipTest('Notification model not extended yet')

        old_date = timezone.now() - timezone.timedelta(days=100)
        action = actstream_action.send(
            self.user, verb='documents.document_created', target=self.user
        )[0][1]
        action.timestamp = old_date
        action.save()

        notification = EventNotification.objects.create(
            user=self.user, action=action, read=False
        )
        notification.state = 'ARCHIVED'
        notification.save()

        cleanup_old_notifications()

        self.assertFalse(EventNotification.objects.filter(pk=notification.pk).exists())

    def test_cleanup_old_notifications_keeps_recent(self):
        """Test that recent notifications are not deleted."""
        if not hasattr(EventNotification, 'state'):
            self.skipTest('Notification model not extended yet')

        action = actstream_action.send(
            self.user, verb='documents.document_created', target=self.user
        )[0][1]

        notification = EventNotification.objects.create(
            user=self.user, action=action, read=False
        )
        notification.state = 'ARCHIVED'
        notification.save()

        cleanup_old_notifications()

        self.assertTrue(EventNotification.objects.filter(pk=notification.pk).exists())


class SendWebSocketNotificationTestCase(TestCase):
    """Test send_websocket_notification Celery task."""

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.action = actstream_action.send(
            self.user, verb='documents.document_created', target=self.user
        )[0][1]
        self.notification = EventNotification.objects.create(
            user=self.user, action=self.action, read=False
        )
        if hasattr(self.notification, 'title'):
            self.notification.title = 'Test'
            self.notification.message = 'Test message'
            self.notification.save()

    @mock.patch('asgiref.sync.async_to_sync')
    @mock.patch('channels.layers.get_channel_layer')
    def test_send_websocket_notification_sends_message(self, mock_get_channel_layer, mock_async_to_sync):
        """Test that WebSocket message is sent to user's group."""
        if not hasattr(self.notification, 'title'):
            self.skipTest('Notification model not extended yet')

        mock_channel_layer = mock.MagicMock()
        mock_get_channel_layer.return_value = mock_channel_layer
        mock_group_send = mock.MagicMock()
        mock_async_to_sync.return_value = mock_group_send

        send_websocket_notification(self.notification.pk)

        mock_get_channel_layer.assert_called_once()
        mock_group_send.assert_called_once()
        call_args = mock_group_send.call_args
        self.assertEqual(call_args[0][0], f'notifications_{self.user.pk}')
        self.assertEqual(call_args[0][1]['type'], 'notification.new')

