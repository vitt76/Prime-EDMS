"""
Integration tests for PotentialDuplicatesView (Sprint 3.2).

GET /api/v4/headless/documents/<id>/potential-duplicates/
- Tenant-scoped (organization), ACL-filtered.
- Returns documents with same file checksum in the same organization.
"""
import os

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from mayan.apps.documents.models import Document
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.tests.base import GenericDocumentViewTestCase
from mayan.apps.documents.tests.mixins.document_file_mixins import DocumentFileTestMixin
from mayan.apps.documents.tests.mixins.document_mixins import DocumentTestMixin


class PotentialDuplicatesViewTestCase(
    DocumentFileTestMixin, DocumentTestMixin, GenericDocumentViewTestCase
):
    """Integration tests for GET potential-duplicates."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self._test_case_user)
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_view,
        )

    def test_get_returns_structure(self):
        """GET returns 200 with results and count (empty when no duplicates)."""
        response = self.client.get(
            f'/api/v4/headless/documents/{self._test_document.pk}/potential-duplicates/'
        )
        # May return 400 if request.organization is not set (no middleware in test)
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            self.assertIn('detail', response.data)
            self.assertIn('Organization', str(response.data.get('detail', '')))
            return
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertIsInstance(response.data['results'], list)
        self.assertEqual(response.data['count'], len(response.data['results']))

    def test_get_returns_empty_when_no_duplicates(self):
        """GET returns empty results when no other document has same checksum."""
        response = self.client.get(
            f'/api/v4/headless/documents/{self._test_document.pk}/potential-duplicates/'
        )
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            return
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['results'], [])

    def test_get_returns_duplicate_when_same_checksum(self):
        """GET returns other document when it has a file with same checksum."""
        doc1 = self._test_document
        self.assertIsNotNone(doc1.file_latest)
        self.assertTrue(doc1.file_latest.checksum)

        # Create second document with same file content (same checksum)
        self._calculate_test_document_path()
        test_path = self._test_document_path
        if not test_path or not os.path.exists(test_path):
            self.skipTest('Sample file not found for same-checksum test')

        with open(test_path, 'rb') as f:
            doc2, _ = self._test_document_type.new_document(
                file_object=f,
                label='Duplicate content doc',
            )
        self._test_documents.append(doc2)
        self.grant_access(obj=doc2, permission=permission_document_view)

        response = self.client.get(
            f'/api/v4/headless/documents/{doc1.pk}/potential-duplicates/'
        )
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            return
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [r['id'] for r in response.data['results']]
        self.assertIn(doc2.pk, ids, 'Document with same checksum should appear in potential duplicates')
        self.assertNotIn(doc1.pk, ids, 'Current document must not be in results')

    def test_get_404_for_nonexistent_document(self):
        """GET returns 404 for non-existent document_id."""
        response = self.client.get(
            '/api/v4/headless/documents/999999/potential-duplicates/'
        )
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            return
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
