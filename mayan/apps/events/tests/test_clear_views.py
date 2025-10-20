from django.contrib.contenttypes.models import ContentType

from mayan.apps.acls.classes import ModelPermission
from mayan.apps.documents.tests.base import GenericDocumentViewTestCase

from ..events import event_events_cleared
from ..permissions import permission_events_clear

from .mixins import (
    EventsClearViewTestMixin, EventTestMixin, EventTypeTestMixin
)


class EventClearViewTestCase(
    EventTestMixin, EventTypeTestMixin, EventsClearViewTestMixin,
    GenericDocumentViewTestCase
):
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()
        self._create_test_event_type()
        self._create_test_user()
        self._test_object = self._test_document_type

        content_type = ContentType.objects.get_for_model(
            model=self._test_object
        )

        self.view_arguments = {
            'app_label': content_type.app_label,
            'model_name': content_type.model,
            'object_id': self._test_object.pk
        }

        ModelPermission.register(
            model=self._test_object._meta.model, permissions=(
                permission_events_clear,
            )
        )

        self._clear_events()

    def test_event_list_clear_view_no_permission(self):
        self._clear_events()

        self._create_test_event(target=self._test_object)

        response = self._request_test_event_list_clear_view()
        self.assertEqual(response.status_code, 302)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0], self._test_event)

    def test_event_list_clear_view_with_access(self):
        self.grant_access(
            obj=self._test_object, permission=permission_events_clear
        )

        self._clear_events()

        self._create_test_event(target=self._test_object)

        response = self._request_test_event_list_clear_view()
        self.assertEqual(response.status_code, 302)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_case_user)
        self.assertEqual(events[0].verb, event_events_cleared.id)

    def test_object_event_list_clear_view_no_permission(self):
        self._clear_events()

        self._create_test_event(
            actor=self._test_user, action_object=self._test_object
        )

        response = self._request_object_event_list_clear_view()
        self.assertEqual(response.status_code, 302)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0], self._test_event)

    def test_object_event_list_clear_view_with_access(self):
        self.grant_access(
            obj=self._test_object, permission=permission_events_clear
        )

        self._clear_events()

        self._create_test_event(
            actor=self._test_user, action_object=self._test_object
        )

        response = self._request_object_event_list_clear_view()
        self.assertEqual(response.status_code, 302)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_object)
        self.assertEqual(events[0].verb, event_events_cleared.id)

    def test_verb_event_list_clear_view_no_permission(self):
        self._clear_events()

        self._create_test_event(
            actor=self._test_user, action_object=self._test_object
        )

        response = self._request_test_verb_event_list_clear_view()
        self.assertEqual(response.status_code, 302)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0], self._test_event)

    def test_verb_event_list_view_clear_with_access(self):
        self.grant_access(
            obj=self._test_object, permission=permission_events_clear
        )

        self._clear_events()

        self._create_test_event(
            actor=self._test_user, action_object=self._test_object
        )

        response = self._request_test_verb_event_list_clear_view()
        self.assertEqual(response.status_code, 302)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_case_user)
        self.assertEqual(events[0].verb, event_events_cleared.id)


class CurrentUserEventClearViewTestCase(
    EventTestMixin, EventTypeTestMixin, EventsClearViewTestMixin,
    GenericDocumentViewTestCase
):
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()
        self._create_test_event_type()
        self._create_test_user()
        self._test_object = self._test_case_user

        content_type = ContentType.objects.get_for_model(
            model=self._test_object
        )

        self.view_arguments = {
            'app_label': content_type.app_label,
            'model_name': content_type.model,
            'object_id': self._test_object.pk
        }

    def test_current_user_events_clear_view_no_permission(self):
        self._clear_events()

        self._create_test_event(
            actor=self._test_case_user, action_object=self._test_object
        )

        response = self._request_object_event_list_clear_view()
        self.assertEqual(response.status_code, 302)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0], self._test_event)

    def test_current_user_events_clear_view_with_access(self):
        self.grant_access(
            obj=self._test_object, permission=permission_events_clear
        )

        self._clear_events()

        self._create_test_event(
            actor=self._test_case_user, action_object=self._test_object
        )

        response = self._request_object_event_list_clear_view()
        self.assertEqual(response.status_code, 302)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_case_user)
        self.assertEqual(events[0].verb, event_events_cleared.id)
