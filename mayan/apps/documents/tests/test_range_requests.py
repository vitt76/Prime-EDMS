from django.http import StreamingHttpResponse

from rest_framework import status

from ..permissions import permission_document_file_download

from .mixins.document_file_mixins import DocumentFileAPIViewTestMixin
from .mixins.document_mixins import DocumentTestMixin
from .base import GenericDocumentAPIViewTestCase


class DocumentFileDownloadRangeRequestsTestCase(
    DocumentFileAPIViewTestMixin, DocumentTestMixin, GenericDocumentAPIViewTestCase
):
    auto_upload_test_document = True

    def _request_download_with_range(self, range_header):
        return self.get(
            viewname='rest_api:documentfile-download',
            kwargs={
                'document_id': self._test_document.pk,
                'document_file_id': self._test_document.file_latest.pk,
            },
            headers={'HTTP_RANGE': range_header}
        )

    def test_document_file_download_range_no_permission(self):
        response = self._request_download_with_range(range_header='bytes=0-9')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_document_file_download_range_with_access_bytes_0_9(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_file_download
        )

        with self._test_document.file_latest.open(mode='rb') as file_object:
            full_content = file_object.read()

        response = self._request_download_with_range(range_header='bytes=0-9')
        self.assertEqual(response.status_code, 206)
        self.assertTrue(isinstance(response, StreamingHttpResponse))
        self.assertEqual(response['Accept-Ranges'], 'bytes')
        self.assertEqual(response['Content-Range'], f'bytes 0-9/{len(full_content)}')
        self.assertEqual(int(response['Content-Length']), 10)
        self.assertEqual(b''.join(response), full_content[:10])

    def test_document_file_download_range_with_access_bytes_suffix(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_file_download
        )

        with self._test_document.file_latest.open(mode='rb') as file_object:
            full_content = file_object.read()

        response = self._request_download_with_range(range_header='bytes=-10')
        self.assertEqual(response.status_code, 206)
        self.assertTrue(isinstance(response, StreamingHttpResponse))
        self.assertEqual(
            response['Content-Range'],
            f'bytes {len(full_content) - 10}-{len(full_content) - 1}/{len(full_content)}'
        )
        self.assertEqual(b''.join(response), full_content[-10:])

    def test_document_file_download_range_invalid_returns_416(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_file_download
        )

        with self._test_document.file_latest.open(mode='rb') as file_object:
            full_content = file_object.read()

        response = self._request_download_with_range(
            range_header='bytes=999999999-999999999'
        )
        self.assertEqual(response.status_code, 416)
        self.assertEqual(response['Accept-Ranges'], 'bytes')
        self.assertEqual(response['Content-Range'], f'bytes */{len(full_content)}')

