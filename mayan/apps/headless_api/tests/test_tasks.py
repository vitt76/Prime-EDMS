"""
Unit tests for Headless API Celery tasks.
"""
import io
from unittest.mock import Mock, patch, MagicMock

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from mayan.apps.documents.tests.base import GenericDocumentViewTestCase
from mayan.apps.storage.models import SharedUploadedFile
from mayan.apps.headless_api.tasks import process_editor_version_task, _convert_image

User = get_user_model()


class ProcessEditorVersionTaskTestCase(GenericDocumentViewTestCase):
    """Test cases for process_editor_version_task."""

    def setUp(self):
        super().setUp()
        self.test_file = ContentFile(
            b'fake image content',
            name='test.jpg'
        )
        self.shared_file = SharedUploadedFile.objects.create(
            file=self.test_file,
            filename='test.jpg'
        )

    def tearDown(self):
        # Очистка SharedUploadedFile
        SharedUploadedFile.objects.all().delete()
        super().tearDown()

    @patch('mayan.apps.headless_api.tasks.process_editor_version_task.retry')
    def test_process_editor_version_task_success(self, mock_retry):
        """Test successful processing of editor version task."""
        result = process_editor_version_task(
            shared_uploaded_file_id=self.shared_file.pk,
            document_id=self.test_document.pk,
            target_format='jpeg',
            comment='Test comment',
            user_id=self._test_case_user.pk
        )

        self.assertTrue(result['success'])
        self.assertEqual(result['document_id'], self.test_document.pk)
        self.assertIn('file_id', result)
        self.assertIn('version_id', result)

        # Проверка, что SharedUploadedFile удален
        self.assertFalse(
            SharedUploadedFile.objects.filter(pk=self.shared_file.pk).exists()
        )

    @patch('mayan.apps.headless_api.tasks.process_editor_version_task.retry')
    def test_process_editor_version_task_without_conversion(self, mock_retry):
        """Test processing without format conversion."""
        result = process_editor_version_task(
            shared_uploaded_file_id=self.shared_file.pk,
            document_id=self.test_document.pk,
            target_format=None,
            comment='Test comment',
            user_id=self._test_case_user.pk
        )

        self.assertTrue(result['success'])
        self.assertEqual(result['document_id'], self.test_document.pk)

    @patch('mayan.apps.headless_api.tasks.process_editor_version_task.retry')
    def test_process_editor_version_task_cleans_up_on_error(self, mock_retry):
        """Test that SharedUploadedFile is cleaned up even on error."""
        # Используем несуществующий document_id для вызова ошибки
        result = process_editor_version_task(
            shared_uploaded_file_id=self.shared_file.pk,
            document_id=99999,  # Несуществующий ID
            target_format=None,
            user_id=self._test_case_user.pk
        )

        self.assertFalse(result['success'])
        self.assertIn('error', result)

        # Проверка, что SharedUploadedFile удален даже при ошибке
        self.assertFalse(
            SharedUploadedFile.objects.filter(pk=self.shared_file.pk).exists()
        )

    def test_convert_image_function(self):
        """Test _convert_image helper function."""
        # Создаем простое изображение через PIL
        from PIL import Image
        
        # Создаем тестовое изображение
        test_image = Image.new('RGB', (100, 100), color='red')
        image_buffer = io.BytesIO()
        test_image.save(image_buffer, format='PNG')
        image_buffer.seek(0)

        # Конвертируем в JPEG
        output_buffer, content_type, extension = _convert_image(
            image_buffer, target_format='jpeg'
        )

        self.assertEqual(extension, 'jpeg')
        self.assertEqual(content_type, 'image/jpeg')
        self.assertIsInstance(output_buffer, io.BytesIO)
        self.assertGreater(len(output_buffer.getvalue()), 0)

