from ..permissions import permission_document_view

from .base import GenericDocumentViewTestCase
from .mixins.recently_accessed_document_mixins import RecentlyAccessedDocumentViewTestMixin


class RecentlyAccessedDocumentViewTestCase(
    RecentlyAccessedDocumentViewTestMixin, GenericDocumentViewTestCase
):
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()
        self._create_test_document_stub()

    def test_recently_accessed_document_list_view_no_permission(self):
        self._test_document.add_as_recent_document_for_user(
            user=self._test_case_user
        )

        self._clear_events()

        response = self._request_test_recently_accessed_document_list_view()
        self.assertNotContains(
            response=response, text=self._test_document.label, status_code=200
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_recently_accessed_document_list_view_with_access(self):
        self._test_document.add_as_recent_document_for_user(
            user=self._test_case_user
        )

        self.grant_access(
            obj=self._test_document, permission=permission_document_view
        )

        self._clear_events()

        response = self._request_test_recently_accessed_document_list_view()
        self.assertContains(
            response=response, text=self._test_document.label, status_code=200
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_trashed_recently_accessed_document_list_view_with_access(self):
        self._test_document.add_as_recent_document_for_user(
            user=self._test_case_user
        )
        self._test_document.delete()

        self.grant_access(
            obj=self._test_document, permission=permission_document_view
        )

        self._clear_events()

        response = self._request_test_recently_accessed_document_list_view()
        self.assertNotContains(
            response=response, text=self._test_document.label, status_code=200
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)
