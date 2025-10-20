from django.core import mail

from mayan.apps.testing.tests.base import GenericViewTestCase

from ..events import (
    event_email_sent, event_profile_created, event_profile_edited
)
from ..models import UserMailer
from ..permissions import (
    permission_user_mailer_create, permission_user_mailer_delete,
    permission_user_mailer_edit, permission_user_mailer_use,
    permission_user_mailer_view
)

from .literals import (
    TEST_EMAIL_ADDRESS, TEST_EMAIL_FROM_ADDRESS,
    TEST_RECIPIENTS_MULTIPLE_COMMA, TEST_RECIPIENTS_MULTIPLE_COMMA_RESULT,
    TEST_RECIPIENTS_MULTIPLE_MIXED, TEST_RECIPIENTS_MULTIPLE_MIXED_RESULT,
    TEST_RECIPIENTS_MULTIPLE_SEMICOLON,
    TEST_RECIPIENTS_MULTIPLE_SEMICOLON_RESULT
)
from .mailers import TestBackend
from .mixins import MailerTestMixin, MailerViewTestMixin


class MailerViewTestCase(
    MailerTestMixin, MailerViewTestMixin, GenericViewTestCase
):
    def test_user_mailer_create_view_no_permission(self):
        self.grant_permission(permission=permission_user_mailer_view)

        self._clear_events()

        response = self._request_test_user_mailer_create_view()
        self.assertNotContains(
            response=response, status_code=403, text=TestBackend.label
        )

        self.assertEqual(UserMailer.objects.count(), 0)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_user_mailer_create_view_with_permissions(self):
        self.grant_permission(permission=permission_user_mailer_create)
        self.grant_permission(permission=permission_user_mailer_view)

        self._clear_events()

        response = self._request_test_user_mailer_create_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(UserMailer.objects.count(), 1)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_user_mailer)
        self.assertEqual(events[0].verb, event_profile_created.id)

    def test_user_mailer_delete_view_no_permission(self):
        self._create_test_user_mailer()

        self._clear_events()

        response = self._request_test_user_mailer_delete_view()
        self.assertEqual(response.status_code, 404)

        self.assertQuerysetEqual(
            UserMailer.objects.all(), (repr(self._test_user_mailer),)
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_user_mailer_delete_view_with_access(self):
        self._create_test_user_mailer()

        self.grant_access(
            obj=self._test_user_mailer,
            permission=permission_user_mailer_delete
        )

        self._clear_events()

        response = self._request_test_user_mailer_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(UserMailer.objects.count(), 0)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_user_mailer_edit_view_no_permission(self):
        self._create_test_user_mailer()

        test_profile_label = self._test_user_mailer.label

        self._clear_events()

        response = self._request_test_user_mailer_edit_view()
        self.assertEqual(response.status_code, 404)

        self._test_user_mailer.refresh_from_db()
        self.assertEqual(
            self._test_user_mailer.label, test_profile_label
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_user_mailer_edit_view_with_access(self):
        self._create_test_user_mailer()

        self.grant_access(
            obj=self._test_user_mailer,
            permission=permission_user_mailer_edit
        )

        test_profile_label = self._test_user_mailer.label

        self._clear_events()

        response = self._request_test_user_mailer_edit_view()
        self.assertEqual(response.status_code, 302)

        self._test_user_mailer.refresh_from_db()
        self.assertNotEqual(
            self._test_user_mailer.label, test_profile_label
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_user_mailer)
        self.assertEqual(events[0].verb, event_profile_edited.id)

    def test_user_mailer_list_view_no_permission(self):
        self._create_test_user_mailer()

        self._clear_events()

        response = self._request_test_user_mailer_list_view()
        self.assertNotContains(
            response=response, status_code=200,
            text=self._test_user_mailer.label
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_user_mailer_list_view_with_access(self):
        self._create_test_user_mailer()

        self.grant_access(
            obj=self._test_user_mailer,
            permission=permission_user_mailer_view
        )

        self._clear_events()

        response = self._request_test_user_mailer_list_view()
        self.assertContains(
            response=response, status_code=200,
            text=self._test_user_mailer.label
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_user_mailer_list_bad_data_view_with_access(self):
        self._silence_logger(name='mayan.apps.databases.model_mixins')

        self._create_test_user_mailer()
        self._test_user_mailer.backend_path = 'bad.backend.path'
        self._test_user_mailer.backend_data = '{"bad_field": "bad_data"}'
        self._test_user_mailer.save()

        self.grant_access(
            obj=self._test_user_mailer,
            permission=permission_user_mailer_view
        )

        self._clear_events()

        response = self._request_test_user_mailer_list_view()
        self.assertContains(
            response=response, status_code=200,
            text=self._test_user_mailer.label
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_user_mailer_test_view_no_permission(self):
        self._create_test_user_mailer()

        self._clear_events()

        response = self._request_test_user_mailer_test_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(len(mail.outbox), 0)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_user_mailer_test_view_with_access(self):
        self._create_test_user_mailer()

        self.grant_access(
            obj=self._test_user_mailer, permission=permission_user_mailer_use
        )

        self._clear_events()

        response = self._request_test_user_mailer_test_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, TEST_EMAIL_FROM_ADDRESS)
        self.assertEqual(mail.outbox[0].to, [TEST_EMAIL_ADDRESS])

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_user_mailer)
        self.assertEqual(events[0].verb, event_email_sent.id)

    def test_send_multiple_recipients_comma(self):
        self._create_test_user_mailer()

        self.grant_access(
            obj=self._test_user_mailer, permission=permission_user_mailer_use
        )

        self._test_email_address = TEST_RECIPIENTS_MULTIPLE_COMMA

        self._clear_events()

        response = self._request_test_user_mailer_test_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, TEST_EMAIL_FROM_ADDRESS)
        self.assertEqual(
            mail.outbox[0].to, TEST_RECIPIENTS_MULTIPLE_COMMA_RESULT
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_user_mailer)
        self.assertEqual(events[0].verb, event_email_sent.id)

    def test_send_multiple_recipients_mixed(self):
        self._create_test_user_mailer()

        self.grant_access(
            obj=self._test_user_mailer, permission=permission_user_mailer_use
        )

        self._test_email_address = TEST_RECIPIENTS_MULTIPLE_MIXED

        self._clear_events()

        response = self._request_test_user_mailer_test_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, TEST_EMAIL_FROM_ADDRESS)
        self.assertEqual(
            mail.outbox[0].to, TEST_RECIPIENTS_MULTIPLE_MIXED_RESULT
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_user_mailer)
        self.assertEqual(events[0].verb, event_email_sent.id)

    def test_send_multiple_recipients_semicolon(self):
        self._create_test_user_mailer()

        self.grant_access(
            obj=self._test_user_mailer, permission=permission_user_mailer_use
        )

        self._test_email_address = TEST_RECIPIENTS_MULTIPLE_SEMICOLON

        self._clear_events()

        response = self._request_test_user_mailer_test_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, TEST_EMAIL_FROM_ADDRESS)
        self.assertEqual(
            mail.outbox[0].to, TEST_RECIPIENTS_MULTIPLE_SEMICOLON_RESULT
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_user_mailer)
        self.assertEqual(events[0].verb, event_email_sent.id)
