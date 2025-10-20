from ..events import event_ocr_document_version_finished
from ..models import DocumentVersionPageOCRContent

from .literals import (
    TEST_DOCUMENT_VERSION_OCR_CONTENT,
    TEST_DOCUMENT_VERSION_PAGE_OCR_CONTENT_UPDATED
)


class DocumentTypeOCRSettingsAPIViewTestMixin:
    def _request_test_document_type_ocr_settings_details_api_view(self):
        return self.get(
            viewname='rest_api:document-type-ocr-settings-view',
            kwargs={'document_type_id': self._test_document_type.pk}
        )

    def _request_test_document_type_ocr_settings_patch_api_view(self):
        return self.patch(
            viewname='rest_api:document-type-ocr-settings-view',
            kwargs={'document_type_id': self._test_document_type.pk},
            data={'auto_ocr': True}
        )

    def _request_test_document_type_ocr_settings_put_api_view(self):
        return self.put(
            viewname='rest_api:document-type-ocr-settings-view',
            kwargs={'document_type_id': self._test_document_type.pk},
            data={'auto_ocr': True}
        )


class DocumentTypeOCRViewTestMixin:
    def _request_test_document_type_ocr_settings_view(self):
        return self.get(
            viewname='ocr:document_type_ocr_settings', kwargs={
                'document_type_id': self._test_document_type.pk
            }
        )

    def _request_document_type_ocr_submit_view(self):
        return self.post(
            viewname='ocr:document_type_submit', data={
                'document_type': [self._test_document_type.pk]
            }
        )


class DocumentOCRAPIViewTestMixin:
    def _request_test_document_ocr_submit_api_view(self):
        return self.post(
            viewname='rest_api:document-ocr-submit-view',
            kwargs={'document_id': self._test_document.pk}
        )


class DocumentVersionOCRAPIViewTestMixin:
    def _request_test_document_version_ocr_submit_api_view(self):
        return self.post(
            viewname='rest_api:document-version-ocr-submit-view', kwargs={
                'document_id': self._test_document.pk,
                'document_version_id': self._test_document_version.pk
            }
        )


class DocumentVersionPageOCRAPIViewTestMixin:
    def _request_test_document_version_page_ocr_content_detail_api_view_via_get(self):
        return self.get(
            viewname='rest_api:document-version-page-ocr-content-detail-view', kwargs={
                'document_id': self._test_document.pk,
                'document_version_id': self._test_document_version.pk,
                'document_version_page_id': self._test_document_version_page.pk
            }
        )

    def _request_test_document_version_page_ocr_content_edit_api_view_via_patch(self):
        return self.patch(
            viewname='rest_api:document-version-page-ocr-content-detail-view', kwargs={
                'document_id': self._test_document.pk,
                'document_version_id': self._test_document_version.pk,
                'document_version_page_id': self._test_document_version_page.pk
            }, data={
                'content': TEST_DOCUMENT_VERSION_PAGE_OCR_CONTENT_UPDATED
            }
        )

    def _request_test_document_version_page_ocr_content_edit_api_view_via_put(self):
        return self.put(
            viewname='rest_api:document-version-page-ocr-content-detail-view', kwargs={
                'document_id': self._test_document.pk,
                'document_version_id': self._test_document_version.pk,
                'document_version_page_id': self._test_document_version_page.pk
            }, data={
                'content': TEST_DOCUMENT_VERSION_PAGE_OCR_CONTENT_UPDATED
            }
        )


class DocumentVersionOCRTestMixin:
    auto_create_test_document_version_ocr_content = False

    def setUp(self):
        super().setUp()

        if self.auto_create_test_document_version_ocr_content:
            self._create_test_document_version_ocr_content()

    def _create_test_document_version_ocr_content(self):
        DocumentVersionPageOCRContent.objects.create(
            document_version_page=self._test_document_version_page,
            content=TEST_DOCUMENT_VERSION_OCR_CONTENT
        )
        event_ocr_document_version_finished.commit(
            action_object=self._test_document,
            target=self._test_document_version
        )

    def _do_test_document_version_ocr_content_delete(self):
        DocumentVersionPageOCRContent.objects.delete_content_for(
            document_version=self._test_document_version
        )


class DocumentVersionOCRViewTestMixin:
    def _request_test_document_version_ocr_content_detail_view(self):
        return self.get(
            viewname='ocr:document_version_ocr_content_view', kwargs={
                'document_version_id': self._test_document_version.pk
            }
        )

    def _request_test_document_version_ocr_content_single_delete_view(self):
        return self.post(
            viewname='ocr:document_version_ocr_content_single_delete',
            kwargs={
                'document_version_id': self._test_document_version.pk
            }
        )

    def _request_test_document_version_ocr_content_multiple_delete_view(self):
        return self.post(
            viewname='ocr:document_version_ocr_content_multiple_delete',
            data={
                'id_list': self._test_document_version.pk
            }
        )

    def _request_test_document_version_ocr_single_submit_view(self):
        return self.post(
            viewname='ocr:document_version_ocr_single_submit', kwargs={
                'document_version_id': self._test_document_version.pk
            }
        )

    def _request_test_document_version_ocr_multiple_submit_view(self):
        return self.post(
            viewname='ocr:document_version_ocr_multiple_submit', data={
                'id_list': self._test_document_version.pk,
            }
        )

    def _request_test_document_version_ocr_content_download_view(self):
        return self.get(
            viewname='ocr:document_version_ocr_content_download', kwargs={
                'document_version_id': self._test_document_version.pk
            }
        )


class DocumentVersionPageOCRViewTestMixin:
    def _request_test_document_version_page_ocr_content_detail_view(self):
        return self.get(
            viewname='ocr:document_version_page_ocr_content_detail_view', kwargs={
                'document_version_page_id': self._test_document_version_page.pk
            }
        )

    def _request_test_document_version_page_ocr_content_edit_view(self):
        return self.post(
            viewname='ocr:document_version_page_ocr_content_edit_view', kwargs={
                'document_version_page_id': self._test_document_version_page.pk
            }, data={
                'content': TEST_DOCUMENT_VERSION_PAGE_OCR_CONTENT_UPDATED
            }
        )
