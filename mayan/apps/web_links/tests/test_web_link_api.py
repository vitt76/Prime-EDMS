from rest_framework import status

from mayan.apps.documents.permissions import (
    permission_document_type_edit, permission_document_type_view
)
from mayan.apps.documents.tests.mixins.document_mixins import DocumentTestMixin
from mayan.apps.rest_api.tests.base import BaseAPITestCase

from ..events import event_web_link_created, event_web_link_edited
from ..models import WebLink
from ..permissions import (
    permission_web_link_create, permission_web_link_delete,
    permission_web_link_edit, permission_web_link_view
)

from .literals import TEST_WEB_LINK_LABEL_EDITED, TEST_WEB_LINK_LABEL
from .mixins import (
    WebLinkDocumentTypeAPIViewMixin, WebLinkAPIViewTestMixin,
    WebLinkTestMixin
)


class WebLinkAPIViewTestCase(
    WebLinkTestMixin, WebLinkAPIViewTestMixin, BaseAPITestCase
):
    def test_web_link_create_api_view_no_permission(self):
        self._clear_events()

        response = self._request_test_web_link_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(WebLink.objects.count(), 0)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_web_link_create_api_view_with_permission(self):
        self.grant_permission(permission=permission_web_link_create)

        self._clear_events()

        response = self._request_test_web_link_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        web_link = WebLink.objects.first()
        self.assertEqual(response.data['id'], web_link.pk)
        self.assertEqual(response.data['label'], TEST_WEB_LINK_LABEL)

        self.assertEqual(WebLink.objects.count(), 1)
        self.assertEqual(web_link.label, TEST_WEB_LINK_LABEL)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_web_link)
        self.assertEqual(events[0].verb, event_web_link_created.id)

    def test_web_link_delete_api_view_no_permission(self):
        self._create_test_web_link()

        self._clear_events()

        response = self._request_test_web_link_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(WebLink.objects.count(), 1)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_web_link_delete_api_view_with_access(self):
        self._create_test_web_link()
        self.grant_access(
            obj=self._test_web_link, permission=permission_web_link_delete
        )

        self._clear_events()

        response = self._request_test_web_link_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(WebLink.objects.count(), 0)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_web_link_detail_api_view_no_permission(self):
        self._create_test_web_link()

        self._clear_events()

        response = self._request_test_web_link_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertFalse('label' in response.data)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_web_link_detail_api_view_with_access(self):
        self._create_test_web_link()
        self.grant_access(
            obj=self._test_web_link, permission=permission_web_link_view
        )

        self._clear_events()

        response = self._request_test_web_link_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.data['label'], TEST_WEB_LINK_LABEL
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_web_link_edit_api_view_via_patch_no_permission(self):
        self._create_test_web_link()

        self._clear_events()

        response = self._request_test_web_link_edit_via_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self._test_web_link.refresh_from_db()
        self.assertEqual(self._test_web_link.label, TEST_WEB_LINK_LABEL)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_web_link_edit_api_view_via_patch_with_access(self):
        self._create_test_web_link()
        self.grant_access(
            obj=self._test_web_link, permission=permission_web_link_edit
        )

        self._clear_events()

        response = self._request_test_web_link_edit_via_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self._test_web_link.refresh_from_db()
        self.assertEqual(
            self._test_web_link.label, TEST_WEB_LINK_LABEL_EDITED
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_web_link)
        self.assertEqual(events[0].verb, event_web_link_edited.id)

    def test_web_link_edit_api_view_via_put_no_permission(self):
        self._create_test_web_link()

        self._clear_events()

        response = self._request_test_web_link_edit_via_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self._test_web_link.refresh_from_db()
        self.assertEqual(self._test_web_link.label, TEST_WEB_LINK_LABEL)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_web_link_edit_api_view_via_put_with_access(self):
        self._create_test_web_link()
        self.grant_access(
            obj=self._test_web_link, permission=permission_web_link_edit
        )

        self._clear_events()

        response = self._request_test_web_link_edit_via_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self._test_web_link.refresh_from_db()
        self.assertEqual(
            self._test_web_link.label, TEST_WEB_LINK_LABEL_EDITED
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_web_link)
        self.assertEqual(events[0].verb, event_web_link_edited.id)


class WebLinkDocumentTypeAPIViewTestCase(
    DocumentTestMixin, WebLinkDocumentTypeAPIViewMixin, WebLinkTestMixin,
    BaseAPITestCase
):
    auto_upload_test_document = False

    def test_web_link_document_type_add_api_view_no_permission(self):
        self._create_test_web_link()
        self.grant_access(
            obj=self._test_document_type,
            permission=permission_document_type_edit
        )

        test_web_link_document_types_count = self._test_web_link.document_types.count()

        self._clear_events()

        response = self._request_test_web_link_document_type_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self._test_web_link.refresh_from_db()

        self.assertEqual(
            self._test_web_link.document_types.count(),
            test_web_link_document_types_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_web_link_document_type_add_api_view_with_document_type_access(self):
        self._create_test_web_link()
        self.grant_access(
            obj=self._test_document_type,
            permission=permission_document_type_edit
        )

        test_web_link_document_types_count = self._test_web_link.document_types.count()

        self._clear_events()

        response = self._request_test_web_link_document_type_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self._test_web_link.refresh_from_db()

        self.assertEqual(
            self._test_web_link.document_types.count(),
            test_web_link_document_types_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_web_link_document_type_add_api_view_with_web_link_access(self):
        self._create_test_web_link()

        self.grant_access(
            obj=self._test_web_link, permission=permission_web_link_edit
        )

        test_web_link_document_types_count = self._test_web_link.document_types.count()

        self._clear_events()

        response = self._request_test_web_link_document_type_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self._test_web_link.refresh_from_db()

        self.assertEqual(
            self._test_web_link.document_types.count(),
            test_web_link_document_types_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_web_link_document_type_add_api_view_with_full_access(self):
        self._create_test_web_link()
        self.grant_access(
            obj=self._test_document_type,
            permission=permission_document_type_edit
        )
        self.grant_access(
            obj=self._test_web_link, permission=permission_web_link_edit
        )

        test_web_link_document_types_count = self._test_web_link.document_types.count()

        self._clear_events()

        response = self._request_test_web_link_document_type_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self._test_web_link.refresh_from_db()

        self.assertEqual(
            self._test_web_link.document_types.count(),
            test_web_link_document_types_count + 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, self._test_document_type)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_web_link)
        self.assertEqual(events[0].verb, event_web_link_edited.id)

    def test_web_link_permission_list_api_view_no_permission(self):
        self._create_test_web_link()
        self._test_web_link.document_types.add(self._test_document_type)

        self._clear_events()

        response = self._request_test_web_link_document_type_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_web_link_permission_list_api_view_with_document_type_access(self):
        self._create_test_web_link()
        self._test_web_link.document_types.add(self._test_document_type)

        self.grant_access(
            obj=self._test_document_type,
            permission=permission_document_type_view
        )

        self._clear_events()

        response = self._request_test_web_link_document_type_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_web_link_permission_list_api_view_with_web_link_access(self):
        self._create_test_web_link()
        self._test_web_link.document_types.add(self._test_document_type)

        self.grant_access(
            obj=self._test_web_link, permission=permission_web_link_view
        )

        self._clear_events()

        response = self._request_test_web_link_document_type_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_web_link_permission_list_api_view_with_full_access(self):
        self._create_test_web_link()
        self._test_web_link.document_types.add(self._test_document_type)

        self.grant_access(
            obj=self._test_document_type,
            permission=permission_document_type_view
        )
        self.grant_access(
            obj=self._test_web_link, permission=permission_web_link_view
        )

        self._clear_events()

        response = self._request_test_web_link_document_type_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['id'],
            self._test_document_type.pk
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_web_link_document_type_remove_api_view_no_permission(self):
        self._create_test_web_link(add_test_document_type=True)
        self.grant_access(
            obj=self._test_document_type,
            permission=permission_document_type_edit
        )

        test_web_link_document_types_count = self._test_web_link.document_types.count()

        self._clear_events()

        response = self._request_test_web_link_document_type_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self._test_web_link.refresh_from_db()

        self.assertEqual(
            self._test_web_link.document_types.count(),
            test_web_link_document_types_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_web_link_document_type_remove_api_view_with_document_type_access(self):
        self._create_test_web_link(add_test_document_type=True)
        self.grant_access(
            obj=self._test_document_type,
            permission=permission_document_type_edit
        )

        test_web_link_document_types_count = self._test_web_link.document_types.count()

        self._clear_events()

        response = self._request_test_web_link_document_type_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self._test_web_link.refresh_from_db()

        self.assertEqual(
            self._test_web_link.document_types.count(),
            test_web_link_document_types_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_web_link_document_type_remove_api_view_with_web_link_access(self):
        self._create_test_web_link(add_test_document_type=True)

        self.grant_access(
            obj=self._test_web_link, permission=permission_web_link_edit
        )

        test_web_link_document_types_count = self._test_web_link.document_types.count()

        self._clear_events()

        response = self._request_test_web_link_document_type_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self._test_web_link.refresh_from_db()

        self.assertEqual(
            self._test_web_link.document_types.count(),
            test_web_link_document_types_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_web_link_document_type_remove_api_view_with_full_access(self):
        self._create_test_web_link(add_test_document_type=True)
        self.grant_access(
            obj=self._test_document_type,
            permission=permission_document_type_edit
        )
        self.grant_access(
            obj=self._test_web_link, permission=permission_web_link_edit
        )

        test_web_link_document_types_count = self._test_web_link.document_types.count()

        self._clear_events()

        response = self._request_test_web_link_document_type_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self._test_web_link.refresh_from_db()

        self.assertEqual(
            self._test_web_link.document_types.count(),
            test_web_link_document_types_count - 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, self._test_document_type)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_web_link)
        self.assertEqual(events[0].verb, event_web_link_edited.id)
