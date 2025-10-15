from mayan.apps.dynamic_search.tests.mixins import SearchTestMixin

from ..permissions import permission_document_view

from .base import GenericDocumentViewTestCase
from .mixins.document_mixins import DocumentViewTestMixin


class DocumentPreviewWidgetViewTestCase(
    DocumentViewTestMixin, SearchTestMixin, GenericDocumentViewTestCase
):
    def test_document_preview_page_carousel_widget_render(self):
        self.grant_access(
            obj=self._test_document, permission=permission_document_view
        )

        response = self._request_test_document_preview_view()
        self.assertContains(
            response=response, status_code=200, text='carousel-container'
        )
