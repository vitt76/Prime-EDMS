from mayan.apps.testing.tests.base import GenericViewTestCase

from .mixins import MessageTestMixin, MessageViewTestMixin

from ..events import event_message_created, event_message_edited
from ..models import Message
from ..permissions import (
    permission_message_create, permission_message_delete,
    permission_message_edit, permission_message_view
)


class MessageViewTestCase(
    MessageTestMixin, MessageViewTestMixin, GenericViewTestCase
):
    def test_message_create_view_no_permission(self):
        message_count = Message.objects.count()

        self._clear_events()

        response = self._request_test_message_create_view()
        self.assertEqual(response.status_code, 403)

        self.assertEqual(Message.objects.count(), message_count)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_message_create_view_with_permissions(self):
        self.grant_permission(permission=permission_message_create)

        message_count = Message.objects.count()

        self._clear_events()

        response = self._request_test_message_create_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Message.objects.count(), message_count + 1)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_message)
        self.assertEqual(events[0].verb, event_message_created.id)

    def test_message_create_view_for_superuser_with_permissions(self):
        self.grant_permission(permission=permission_message_create)

        message_count = Message.objects.count()

        self._create_test_superuser()

        self._clear_events()

        response = self._request_test_message_create_view(
            extra_data={'user': self._test_superuser.pk}
        )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Message.objects.count(), message_count)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_message_delete_view_no_permission(self):
        self._create_test_message()

        message_count = Message.objects.count()

        self._clear_events()

        response = self._request_test_message_delete_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(Message.objects.count(), message_count)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_message_delete_view_with_access(self):
        self._create_test_message()

        self.grant_access(
            obj=self._test_message, permission=permission_message_delete
        )

        message_count = Message.objects.count()

        self._clear_events()

        response = self._request_test_message_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Message.objects.count(), message_count - 1)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_message_detail_view_no_permission(self):
        self._create_test_message()

        test_message_read = self._test_message.read

        self._clear_events()

        response = self._request_test_message_detail_view()
        self.assertEqual(response.status_code, 404)

        self._test_message.refresh_from_db()
        self.assertEqual(
            self._test_message.read, test_message_read
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_message_detail_view_with_access(self):
        self._create_test_message()

        self.grant_access(
            obj=self._test_message, permission=permission_message_view
        )

        test_message_read = self._test_message.read

        self._clear_events()

        response = self._request_test_message_detail_view()
        self.assertContains(
            text=self._test_message.get_rendered_body(), response=response,
            status_code=200
        )

        self._test_message.refresh_from_db()
        self.assertNotEqual(
            self._test_message.read, test_message_read
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_message)
        self.assertEqual(events[0].verb, event_message_edited.id)

    def test_message_list_view_with_no_permission(self):
        self._create_test_message()

        self._clear_events()

        response = self._request_test_message_list_view()
        self.assertNotContains(
            response=response, text=self._test_message.subject, status_code=200
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_message_list_view_with_access(self):
        self._create_test_message()

        self.grant_access(
            obj=self._test_message, permission=permission_message_view
        )

        self._clear_events()

        response = self._request_test_message_list_view()
        self.assertContains(
            response=response, text=self._test_message.subject, status_code=200
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_message_mark_all_read_view_no_permission(self):
        self._create_test_message()

        self._clear_events()

        response = self._request_test_message_mark_all_read_view()
        self.assertEqual(response.status_code, 302)

        self._test_message.refresh_from_db()
        self.assertEqual(self._test_message.read, False)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_message_mark_all_read_view_with_access(self):
        self._create_test_message()

        self.grant_access(
            obj=self._test_message, permission=permission_message_edit
        )

        self._clear_events()

        response = self._request_test_message_mark_all_read_view()
        self.assertEqual(response.status_code, 302)

        self._test_message.refresh_from_db()
        self.assertEqual(self._test_message.read, True)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_message)
        self.assertEqual(events[0].verb, event_message_edited.id)

    def test_message_mark_unread_view_no_permission(self):
        self._create_test_message()

        self._test_message.mark_read()

        self._clear_events()

        response = self._request_test_message_mark_unread_view()
        self.assertEqual(response.status_code, 404)

        self._test_message.refresh_from_db()
        self.assertEqual(self._test_message.read, True)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_message_mark_unread_view_with_access(self):
        self._create_test_message()

        self.grant_access(
            obj=self._test_message, permission=permission_message_edit
        )

        self._test_message.mark_read()

        self._clear_events()

        response = self._request_test_message_mark_unread_view()
        self.assertEqual(response.status_code, 302)

        self._test_message.refresh_from_db()
        self.assertEqual(self._test_message.read, False)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_message)
        self.assertEqual(events[0].verb, event_message_edited.id)

    def test_message_mark_read_view_no_permission(self):
        self._create_test_message()

        self._clear_events()

        response = self._request_test_message_mark_read_view()
        self.assertEqual(response.status_code, 404)

        self._test_message.refresh_from_db()
        self.assertEqual(self._test_message.read, False)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_message_mark_read_view_with_access(self):
        self._create_test_message()

        self.grant_access(
            obj=self._test_message, permission=permission_message_edit
        )

        self._clear_events()

        response = self._request_test_message_mark_read_view()
        self.assertEqual(response.status_code, 302)

        self._test_message.refresh_from_db()
        self.assertEqual(self._test_message.read, True)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_message)
        self.assertEqual(events[0].verb, event_message_edited.id)
