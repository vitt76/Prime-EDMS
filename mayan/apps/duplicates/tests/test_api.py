from rest_framework import status

from mayan.apps.documents.tests.mixins.document_mixins import DocumentTestMixin
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.rest_api.tests.base import BaseAPITestCase

from .mixins import (
    DuplicatedDocumentAPIViewTestMixin, DuplicatedDocumentTestMixin
)


class DuplicatedDocumentAPIViewTestCase(
    DocumentTestMixin, DuplicatedDocumentAPIViewTestMixin,
    DuplicatedDocumentTestMixin, BaseAPITestCase
):
    def setUp(self):
        super().setUp()
        self._upload_duplicate_document()

    def test_duplicated_document_list_api_view_no_permission(self):
        self._clear_events()

        response = self._request_test_duplicated_document_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_duplicated_document_list_api_view_with_access(self):
        self.grant_access(
            obj=self._test_document, permission=permission_document_view
        )

        self._clear_events()

        response = self._request_test_duplicated_document_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['results'][0]['id'],
            self._test_document.pk
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)


class DocumentDuplicatesAPIViewTestCase(
    DocumentTestMixin, DuplicatedDocumentAPIViewTestMixin,
    DuplicatedDocumentTestMixin, BaseAPITestCase
):
    def setUp(self):
        super().setUp()
        self._upload_duplicate_document()

    def test_document_duplicates_list_api_view_no_permission(self):
        self._clear_events()

        response = self._request_test_document_duplicates_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_duplicates_list_api_view_with_source_document_access(self):
        self.grant_access(
            obj=self._test_documents[0], permission=permission_document_view
        )

        self._clear_events()

        response = self._request_test_document_duplicates_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_duplicates_list_api_view_with_target_document_access(self):
        self.grant_access(
            obj=self._test_documents[1], permission=permission_document_view
        )

        self._clear_events()

        response = self._request_test_document_duplicates_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_duplicates_list_api_view_with_full_access(self):
        self.grant_access(
            obj=self._test_documents[0], permission=permission_document_view
        )
        self.grant_access(
            obj=self._test_documents[1], permission=permission_document_view
        )

        self._clear_events()

        response = self._request_test_document_duplicates_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['results'][0]['id'],
            self._test_documents[1].pk
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_trashed_source_document_duplicates_list_api_view_with_full_access(self):
        self.grant_access(
            obj=self._test_documents[0], permission=permission_document_view
        )
        self.grant_access(
            obj=self._test_documents[1], permission=permission_document_view
        )

        self._test_documents[0].delete()

        self._clear_events()

        response = self._request_test_document_duplicates_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_trashed_target_document_duplicates_list_api_view_with_full_access(self):
        self.grant_access(
            obj=self._test_documents[0], permission=permission_document_view
        )
        self.grant_access(
            obj=self._test_documents[1], permission=permission_document_view
        )

        self._test_documents[1].delete()

        self._clear_events()

        response = self._request_test_document_duplicates_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)
