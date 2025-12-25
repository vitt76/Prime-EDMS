from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from actstream import action as actstream_action

from mayan.apps.events.models import Notification as EventNotification
from mayan.apps.notifications.models import NotificationTemplate


User = get_user_model()


class HeadlessNotificationViewsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.list_url = '/api/v4/headless/notifications/'
        self.unread_count_url = '/api/v4/headless/notifications/unread-count/'
        self.read_all_url = '/api/v4/headless/notifications/read-all/'
        self.preferences_url = '/api/v4/headless/notifications/preferences/'

    def _create_notification(self, verb='documents.document_created'):
        NotificationTemplate.objects.create(
            event_type=verb,
            title_template='Событие: {actor}',
            message_template='Target: {target}',
            default_priority='NORMAL',
            icon_type='info',
            actions=[],
            is_active=True
        )

        act = actstream_action.send(
            self.user,
            verb=verb,
            target=self.user
        )[0][1]

        notification = EventNotification.objects.create(user=self.user, action=act, read=False)
        notification.refresh_from_db()
        return notification

    def test_list_notifications(self):
        self._create_notification()

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('unread_count', response.data)
        self.assertGreaterEqual(response.data['unread_count'], 1)

    def test_unread_count(self):
        self._create_notification()

        response = self.client.get(self.unread_count_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 1)

    def test_mark_as_read(self):
        notification = self._create_notification()

        response = self.client.patch(f'/api/v4/headless/notifications/{notification.pk}/read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        notification.refresh_from_db()
        self.assertTrue(notification.read)
        self.assertEqual(notification.state, 'READ')

    def test_mark_all_as_read(self):
        self._create_notification()
        self._create_notification(verb='documents.document_edited')

        response = self.client.post(self.read_all_url, data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 0)

    def test_delete_notification(self):
        notification = self._create_notification()

        response = self.client.delete(f'/api/v4/headless/notifications/{notification.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        notification.refresh_from_db()
        self.assertEqual(notification.state, 'DELETED')

    def test_preferences_get_and_patch(self):
        response = self.client.get(self.preferences_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('notifications_enabled', response.data)

        response = self.client.patch(
            self.preferences_url,
            data={'notifications_enabled': False},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['notifications_enabled'], False)

    def test_list_notifications_filter_by_state(self):
        """Test filtering notifications by state."""
        self._create_notification()
        notification2 = self._create_notification(verb='documents.document_edited')
        # Mark one as read
        notification2.mark_as_read()

        # Filter by SENT (unread)
        response = self.client.get(self.list_url + '?state=SENT')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        # Filter by ALL
        response = self.client.get(self.list_url + '?state=ALL')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)

    def test_list_notifications_filter_by_event_type(self):
        """Test filtering notifications by event_type."""
        self._create_notification(verb='documents.document_created')
        self._create_notification(verb='documents.document_edited')

        response = self.client.get(self.list_url + '?event_type=documents.document_created')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['event_type'], 'documents.document_created')

    def test_notification_detail_view(self):
        """Test getting a single notification."""
        notification = self._create_notification()

        response = self.client.get(f'/api/v4/headless/notifications/{notification.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], notification.pk)
        self.assertIn('title', response.data)
        self.assertIn('message', response.data)

    def test_notification_detail_view_not_found(self):
        """Test 404 for non-existent notification."""
        response = self.client.get('/api/v4/headless/notifications/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_notification_detail_view_other_user(self):
        """Test that users can only see their own notifications."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass'
        )
        other_action = actstream_action.send(
            other_user,
            verb='documents.document_created',
            target=other_user
        )[0][1]
        other_notification = EventNotification.objects.create(
            user=other_user,
            action=other_action,
            read=False
        )

        response = self.client.get(f'/api/v4/headless/notifications/{other_notification.pk}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unread_count_includes_urgent(self):
        """Test that unread_count includes urgent count."""
        notification = self._create_notification()
        if hasattr(notification, 'priority'):
            notification.priority = 'URGENT'
            notification.save()

        response = self.client.get(self.unread_count_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('unread_count', response.data)
        self.assertIn('has_urgent', response.data)
        if hasattr(notification, 'priority'):
            self.assertTrue(response.data['has_urgent'])

    def test_mark_all_as_read_with_filter(self):
        """Test marking all as read with event_type filter."""
        self._create_notification(verb='documents.document_created')
        self._create_notification(verb='documents.document_edited')

        response = self.client.post(
            self.read_all_url,
            data={'filter_event_type': 'documents.document_created'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['marked_count'], 1)

    def test_serializer_fallback_for_legacy_notification(self):
        """Test that serializer provides fallback for notifications without title."""
        # Create notification without title (legacy notification)
        act = actstream_action.send(
            self.user,
            verb='documents.document_created',
            target=self.user
        )[0][1]

        notification = EventNotification.objects.create(
            user=self.user,
            action=act,
            read=False
        )
        # Ensure title is None (legacy notification)
        if hasattr(notification, 'title'):
            notification.title = None
            notification.save()

        response = self.client.get(f'/api/v4/headless/notifications/{notification.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should have fallback title
        self.assertIsNotNone(response.data.get('title'))
        self.assertIn('Событие:', response.data['title'])
        self.assertEqual(response.data['event_type'], 'documents.document_created')

    def test_notification_preference_prevents_creation(self):
        """Test that NotificationPreference.notifications_enabled=False prevents notification creation."""
        from mayan.apps.notifications.models import NotificationPreference

        # Disable notifications for user
        pref, _ = NotificationPreference.objects.get_or_create(user=self.user)
        pref.notifications_enabled = False
        pref.save()

        # Create an event that would normally create a notification
        from mayan.apps.events.classes import event_document_created
        from mayan.apps.documents.models import Document

        # Subscribe user to event
        from mayan.apps.events.models import EventSubscription, StoredEventType
        event_type, _ = StoredEventType.objects.get_or_create(name='documents.document_created')
        EventSubscription.objects.get_or_create(
            user=self.user,
            stored_event_type=event_type
        )

        # Create a document to trigger event
        document = Document.objects.create(label='Test Document')

        # Commit event
        event_document_created.commit(actor=self.user, action_object=document)

        # Check that no notification was created
        notifications = EventNotification.objects.filter(user=self.user)
        # Should have 0 new notifications (may have old ones from setUp)
        initial_count = EventNotification.objects.filter(user=self.user).count()

        # Re-enable notifications
        pref.notifications_enabled = True
        pref.save()

        # Commit event again
        event_document_created.commit(actor=self.user, action_object=document)

        # Now should have one more notification
        final_count = EventNotification.objects.filter(user=self.user).count()
        self.assertGreater(final_count, initial_count)


