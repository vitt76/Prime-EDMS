from django.contrib.contenttypes.models import ContentType

from mayan.apps.documents.tests.base import GenericDocumentViewTestCase

from ..permissions import permission_events_view

from .mixins import (
    EventTestMixin, EventTypeTestMixin, EventViewTestMixin
)


class EventsViewTestCase(
    EventTestMixin, EventTypeTestMixin, EventViewTestMixin,
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

    def test_event_list_view_no_permission(self):
        self._create_test_event(target=self._test_object)

        response = self._request_test_event_list_view()

        self.assertNotContains(
            response=response, status_code=200,
            text=self._test_event_type.label
        )

    def test_event_list_view_with_access(self):
        self._create_test_event(target=self._test_object)

        self.grant_access(
            obj=self._test_object, permission=permission_events_view
        )

        response = self._request_test_event_list_view()

        self.assertContains(
            response=response, status_code=200,
            text=self._test_event_type.label
        )

    def test_object_event_list_view_no_permission(self):
        self._create_test_event(
            actor=self._test_user, action_object=self._test_object
        )

        response = self._request_test_object_event_list_view()
        self.assertNotContains(
            response=response, status_code=200,
            text=self._test_event_type.label
        )

    def test_object_event_list_view_with_access(self):
        self._create_test_event(
            actor=self._test_user, action_object=self._test_object
        )

        self.grant_access(
            obj=self._test_object, permission=permission_events_view
        )

        response = self._request_test_object_event_list_view()
        self.assertContains(
            response=response, status_code=200,
            text=self._test_event_type.label
        )

    def test_verb_event_list_view_no_permission(self):
        self._create_test_event(
            actor=self._test_user, action_object=self._test_object
        )

        response = self._request_test_verb_event_list_view()
        self.assertContains(
            count=2, response=response, status_code=200,
            text=self._test_event_type.label
        )

    def test_verb_event_list_view_with_access(self):
        self._create_test_event(
            actor=self._test_user, action_object=self._test_object
        )

        self.grant_access(
            obj=self._test_object, permission=permission_events_view
        )

        response = self._request_test_verb_event_list_view()
        self.assertContains(
            count=3, response=response, status_code=200,
            text=self._test_event_type.label
        )


class CurrentUserEventsViewTestCase(
    EventTestMixin, EventTypeTestMixin, EventViewTestMixin,
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

    def test_current_user_events_view_no_permission(self):
        self._create_test_event(
            actor=self._test_case_user, action_object=self._test_object
        )

        response = self._request_test_object_event_list_view()
        self.assertNotContains(
            response=response, status_code=200,
            text=self._test_event_type.label
        )

    def test_current_user_events_view_with_access(self):
        self._create_test_event(
            actor=self._test_case_user, action_object=self._test_object
        )

        self.grant_access(
            obj=self._test_case_user, permission=permission_events_view
        )

        response = self._request_test_object_event_list_view()
        self.assertContains(
            response=response, status_code=200,
            text=self._test_event_type.label
        )
