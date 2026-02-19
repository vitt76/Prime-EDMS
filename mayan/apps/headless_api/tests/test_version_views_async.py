"""
Integration tests for HeadlessEditView, HeadlessVersionActivateView, HeadlessVersionRevertView.
"""
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from mayan.apps.documents.document_file_actions import DocumentFileActionUseNewPages
from mayan.apps.documents.permissions import permission_document_version_create
from mayan.apps.documents.tests.base import GenericDocumentViewTestCase
from mayan.apps.documents.tests.mixins.document_file_mixins import DocumentFileTestMixin
from mayan.apps.storage.models import SharedUploadedFile


class HeadlessEditViewAsyncTestCase(DocumentFileTestMixin, GenericDocumentViewTestCase):
    """Integration tests for HeadlessEditView asynchronous processing."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self._test_case_user)

    def test_post_returns_202_accepted_with_task_id(self):
        """Test that POST returns 202 Accepted with task_id."""
        # Создаем тестовый файл
        test_file = SimpleUploadedFile(
            'test.jpg',
            b'fake image content',
            content_type='image/jpeg'
        )

        response = self.client.post(
            f'/api/v4/headless/documents/{self._test_document.pk}/versions/new_from_edit/',
            {'file': test_file, 'format': 'jpeg'},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('task_id', response.data)
        self.assertEqual(response.data['status'], 'processing')
        self.assertIn('message', response.data)

    def test_post_validates_file_size(self):
        """Test that POST validates file size and returns 413 if exceeded."""
        # Создаем файл больше лимита (500MB)
        large_file = SimpleUploadedFile(
            'large.jpg',
            b'x' * (501 * 1024 * 1024),  # 501MB
            content_type='image/jpeg'
        )

        response = self.client.post(
            f'/api/v4/headless/documents/{self._test_document.pk}/versions/new_from_edit/',
            {'file': large_file},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'file_too_large')
        self.assertIn('max_size', response.data)
        self.assertIn('file_size', response.data)

    def test_post_creates_shared_uploaded_file(self):
        """Test that POST creates SharedUploadedFile for temporary storage."""
        test_file = SimpleUploadedFile(
            'test.jpg',
            b'fake image content',
            content_type='image/jpeg'
        )

        initial_count = SharedUploadedFile.objects.count()

        response = self.client.post(
            f'/api/v4/headless/documents/{self._test_document.pk}/versions/new_from_edit/',
            {'file': test_file},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        # SharedUploadedFile должен быть создан
        self.assertEqual(SharedUploadedFile.objects.count(), initial_count + 1)

    def test_post_requires_file(self):
        """Test that POST returns 400 if file is missing."""
        response = self.client.post(
            f'/api/v4/headless/documents/{self._test_document.pk}/versions/new_from_edit/',
            {},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'file_required')

    def test_post_with_format_conversion(self):
        """Test that POST accepts format parameter for conversion."""
        test_file = SimpleUploadedFile(
            'test.png',
            b'fake image content',
            content_type='image/png'
        )

        response = self.client.post(
            f'/api/v4/headless/documents/{self._test_document.pk}/versions/new_from_edit/',
            {'file': test_file, 'format': 'jpeg'},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('task_id', response.data)


class HeadlessVersionActivateTestCase(DocumentFileTestMixin, GenericDocumentViewTestCase):
    """Integration tests for HeadlessVersionActivateView (revert / make current)."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self._test_case_user)
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_create
        )

    def test_activate_with_version_id_returns_200(self):
        """POST activate with version_id activates that version."""
        doc = self._test_document
        version = doc.version_active
        self.assertIsNotNone(version)

        response = self.client.post(
            f'/api/v4/headless/documents/{doc.pk}/versions/activate/',
            {'version_id': version.pk},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('success'))
        self.assertEqual(response.data.get('version_id'), version.pk)
        self.assertIn('data', response.data)

    def test_activate_with_file_id_returns_200(self):
        """POST activate with file_id activates the version that corresponds to that file."""
        doc = self._test_document
        latest_file = doc.file_latest
        self.assertIsNotNone(latest_file)

        response = self.client.post(
            f'/api/v4/headless/documents/{doc.pk}/versions/activate/',
            {'file_id': latest_file.pk},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('success'))
        self.assertIn('data', response.data)

    def test_activate_requires_version_or_file_id(self):
        """POST activate without version_id or file_id returns 400."""
        response = self.client.post(
            f'/api/v4/headless/documents/{self._test_document.pk}/versions/activate/',
            {},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class HeadlessVersionRevertTestCase(DocumentFileTestMixin, GenericDocumentViewTestCase):
    """Integration tests for HeadlessVersionRevertView (revert by version_id in URL)."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self._test_case_user)
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_create
        )

    def test_revert_returns_200(self):
        """POST .../versions/{version_id}/revert/ activates that version."""
        doc = self._test_document
        version = doc.version_active
        self.assertIsNotNone(version)

        response = self.client.post(
            f'/api/v4/headless/documents/{doc.pk}/versions/{version.pk}/revert/',
            {},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('success'))
        self.assertEqual(response.data.get('version_id'), version.pk)

    def test_revert_unknown_version_returns_404(self):
        """POST revert with non-existent version_id returns 404."""
        response = self.client.post(
            f'/api/v4/headless/documents/{self._test_document.pk}/versions/999999/revert/',
            {},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

