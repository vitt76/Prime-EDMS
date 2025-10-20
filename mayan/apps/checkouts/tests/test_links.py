from mayan.apps.documents.permissions import permission_document_file_new
from mayan.apps.documents.tests.base import GenericDocumentViewTestCase
from mayan.apps.sources.links import link_document_file_upload
from mayan.apps.sources.tests.mixins.base_mixins import SourceTestMixin


from ..links import link_check_out_document, link_check_out_info
from ..permissions import (
    permission_document_check_out, permission_document_check_out_detail_view
)

from .mixins import DocumentCheckoutTestMixin


class CheckoutLinksTestCase(
    DocumentCheckoutTestMixin, GenericDocumentViewTestCase
):
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()
        self._create_test_document_stub()

    def _resolve_document_check_out_link(self):
        self.add_test_view(test_object=self._test_document)
        context = self.get_test_view()
        context['user'] = self._test_case_user
        return link_check_out_document.resolve(context=context)

    def _resolve_document_check_out_info_link(self):
        self.add_test_view(test_object=self._test_document)
        context = self.get_test_view()
        context['user'] = self._test_case_user
        return link_check_out_info.resolve(context=context)

    def test_document_check_out_link_no_permission(self):
        resolved_link = self._resolve_document_check_out_link()
        self.assertEqual(resolved_link, None)

    def test_document_check_out_link_with_access(self):
        self.grant_access(
            obj=self._test_document, permission=permission_document_check_out
        )
        resolved_link = self._resolve_document_check_out_link()
        self.assertNotEqual(resolved_link, None)

    def test_document_check_out_info_link_no_permission(self):
        resolved_link = self._resolve_document_check_out_info_link()
        self.assertEqual(resolved_link, None)

    def test_document_check_out_info_link_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_check_out_detail_view
        )
        resolved_link = self._resolve_document_check_out_info_link()
        self.assertNotEqual(resolved_link, None)


class DocumentFileListViewTestCase(
    DocumentCheckoutTestMixin, SourceTestMixin, GenericDocumentViewTestCase
):
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()
        self._create_test_document_stub()

    def _get_document_new_file_link(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_file_new
        )
        self.grant_access(
            obj=self._test_source, permission=permission_document_file_new
        )

        self.add_test_view(test_object=self._test_document)
        context = self.get_test_view()
        return link_document_file_upload.resolve(context=context)

    def test_document_file_new_not_blocked(self):
        resolved_link = self._get_document_new_file_link()
        self.assertNotEqual(resolved_link, None)

    def test_document_file_new_blocked_different_user(self):
        self._silence_logger(name='mayan.apps.sources.links')

        self._create_test_user()
        self._check_out_test_document(user=self._test_user)

        resolved_link = self._get_document_new_file_link()
        self.assertEqual(resolved_link, None)

    def test_document_file_new_blocked_same_user(self):
        self._check_out_test_document()

        resolved_link = self._get_document_new_file_link()
        self.assertNotEqual(resolved_link, None)
