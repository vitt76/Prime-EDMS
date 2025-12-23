"""
Integration tests for HeadlessEditView with asynchronous processing.
"""
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from mayan.apps.documents.tests.base import GenericDocumentViewTestCase
from mayan.apps.storage.models import SharedUploadedFile


class HeadlessEditViewAsyncTestCase(GenericDocumentViewTestCase):
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
            f'/api/v4/headless/documents/{self.test_document.pk}/versions/new_from_edit/',
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
            f'/api/v4/headless/documents/{self.test_document.pk}/versions/new_from_edit/',
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
            f'/api/v4/headless/documents/{self.test_document.pk}/versions/new_from_edit/',
            {'file': test_file},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        # SharedUploadedFile должен быть создан
        self.assertEqual(SharedUploadedFile.objects.count(), initial_count + 1)

    def test_post_requires_file(self):
        """Test that POST returns 400 if file is missing."""
        response = self.client.post(
            f'/api/v4/headless/documents/{self.test_document.pk}/versions/new_from_edit/',
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
            f'/api/v4/headless/documents/{self.test_document.pk}/versions/new_from_edit/',
            {'file': test_file, 'format': 'jpeg'},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('task_id', response.data)

