from django.contrib.auth import get_user_model
from django.test import TestCase

from mayan.apps.events.models import Notification as EventNotification
from mayan.apps.notifications.models import (
    NotificationLog, NotificationPreference, NotificationTemplate
)

User = get_user_model()


class NotificationTemplateTestCase(TestCase):
    """Test NotificationTemplate model."""

    def setUp(self):
        super().setUp()

    def test_template_creation(self):
        """Test creating a notification template."""
        template = NotificationTemplate.objects.create(
            event_type='documents.document_created',
            title_template='Document created: {actor}',
            message_template='Target: {target}',
            default_priority='NORMAL',
            icon_type='info',
            actions=[{'id': 'view', 'label': 'View', 'url': '/documents/1/'}],
            is_active=True
        )

        self.assertEqual(template.event_type, 'documents.document_created')
        self.assertEqual(template.title_template, 'Document created: {actor}')
        self.assertEqual(template.default_priority, 'NORMAL')
        self.assertTrue(template.is_active)
        self.assertEqual(len(template.actions), 1)

    def test_template_unique_event_type(self):
        """Test that event_type must be unique."""
        NotificationTemplate.objects.create(
            event_type='documents.document_created',
            title_template='Test',
            is_active=True
        )

        with self.assertRaises(Exception):  # IntegrityError
            NotificationTemplate.objects.create(
                event_type='documents.document_created',
                title_template='Test 2',
                is_active=True
            )

    def test_template_str(self):
        """Test template string representation."""
        template = NotificationTemplate.objects.create(
            event_type='documents.document_created',
            title_template='Test',
            is_active=True
        )
        self.assertEqual(str(template), 'documents.document_created')


class NotificationPreferenceTestCase(TestCase):
    """Test NotificationPreference model."""

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )

    def test_preference_creation(self):
        """Test creating notification preferences."""
        pref, created = NotificationPreference.objects.get_or_create(
            user=self.user,
            defaults={
                'notifications_enabled': True,
                'email_notifications_enabled': True,
                'quiet_hours_enabled': True
            }
        )
        # Update if it already existed
        if not created:
            pref.quiet_hours_enabled = True
            pref.save()

        self.assertEqual(pref.user, self.user)
        self.assertTrue(pref.notifications_enabled)
        self.assertTrue(pref.email_notifications_enabled)
        self.assertTrue(pref.quiet_hours_enabled)
        self.assertEqual(pref.notification_language, 'ru')

    def test_preference_defaults(self):
        """Test default values for preferences."""
        pref, created = NotificationPreference.objects.get_or_create(user=self.user)

        self.assertTrue(pref.notifications_enabled)
        self.assertTrue(pref.email_notifications_enabled)
        self.assertFalse(pref.email_digest_enabled)
        self.assertFalse(pref.quiet_hours_enabled)
        self.assertEqual(pref.notification_language, 'ru')

    def test_preference_one_to_one_user(self):
        """Test that one user can have only one preference."""
        NotificationPreference.objects.get_or_create(user=self.user)

        with self.assertRaises(Exception):  # IntegrityError
            NotificationPreference.objects.create(user=self.user)

    def test_preference_str(self):
        """Test preference string representation."""
        pref, created = NotificationPreference.objects.get_or_create(user=self.user)
        self.assertIn('Notification preferences:', str(pref))
        self.assertIn(self.user.username, str(pref))


class NotificationLogTestCase(TestCase):
    """Test NotificationLog model."""

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        from actstream import action as actstream_action
        self.action = actstream_action.send(
            self.user, verb='documents.document_created', target=self.user
        )[0][1]
        self.notification = EventNotification.objects.create(
            user=self.user, action=self.action, read=False
        )

    def test_log_creation(self):
        """Test creating a notification log entry."""
        log = NotificationLog.objects.create(
            notification=self.notification,
            action='read',
            action_data={'source': 'api'}
        )

        self.assertEqual(log.notification, self.notification)
        self.assertEqual(log.action, 'read')
        self.assertEqual(log.action_data, {'source': 'api'})
        self.assertIsNotNone(log.uuid)
        self.assertIsNotNone(log.timestamp)

    def test_log_str(self):
        """Test log string representation."""
        log = NotificationLog.objects.create(
            notification=self.notification,
            action='read'
        )
        self.assertIn(str(self.notification.pk), str(log))
        self.assertIn('read', str(log))


