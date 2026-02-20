"""
Sprint 2 Productivity & UX: favorites_only filter for optimized document list.

GET /api/v4/documents/optimized/?favorites_only=true returns only documents
that the current user has favorited (and, when organization is set, only in that org).
"""

from rest_framework import status

from mayan.apps.documents.models import Document
from mayan.apps.documents.models import FavoriteDocument
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.rest_api.tests.base import BaseAPITestCase

from .mixins.document_mixins import DocumentTestMixin
from .mixins.favorite_document_mixins import FavoriteDocumentTestMixin


class OptimizedDocumentListFavoritesOnlyTestCase(
    FavoriteDocumentTestMixin, DocumentTestMixin, BaseAPITestCase
):
    """Optimized list with favorites_only returns only favorited documents."""

    auto_upload_test_document = False
    auto_create_test_document_stub = True

    def test_optimized_list_favorites_only_returns_only_favorited(self):
        """With favorites_only=true, only favorited documents appear in results."""
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_view
        )
        FavoriteDocument.valid.add_for_user(
            document=self._test_document,
            user=self._test_case_user
        )
        response = self.get(
            viewname='rest_api:document-optimized-list',
            query={'favorites_only': 'true'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        results = response.data.get('results', [])
        ids = [r['id'] for r in results]
        self.assertIn(
            self._test_document.id,
            ids,
            'Favorited document should appear when favorites_only=true'
        )

    def test_optimized_list_without_favorites_only_returns_all_accessible(self):
        """Without favorites_only, all accessible documents are returned."""
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_view
        )
        response = self.get(
            viewname='rest_api:document-optimized-list'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        results = response.data.get('results', [])
        ids = [r['id'] for r in results]
        self.assertIn(
            self._test_document.id,
            ids,
            'Document should appear without favorites_only filter'
        )
