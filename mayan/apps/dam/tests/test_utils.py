"""
Тесты для утилит работы с лимитами размеров файлов.
"""
from django.test import TestCase, override_settings

from mayan.apps.dam.utils import get_max_file_size_for_mime_type, format_file_size


class FileSizeUtilsTestCase(TestCase):
    """Тесты для функций работы с размерами файлов."""

    def test_format_file_size_bytes(self):
        """Тест форматирования размера в байтах."""
        self.assertEqual(format_file_size(512), "512 B")
        self.assertEqual(format_file_size(0), "0 B")
        self.assertEqual(format_file_size(1023), "1023 B")

    def test_format_file_size_kilobytes(self):
        """Тест форматирования размера в килобайтах."""
        self.assertEqual(format_file_size(1024), "1.0 KB")
        self.assertEqual(format_file_size(2048), "2.0 KB")
        self.assertEqual(format_file_size(1536), "1.5 KB")
        self.assertEqual(format_file_size(1024 * 1024 - 1), "1024.0 KB")

    def test_format_file_size_megabytes(self):
        """Тест форматирования размера в мегабайтах."""
        self.assertEqual(format_file_size(1024 * 1024), "1.0 MB")
        self.assertEqual(format_file_size(20 * 1024 * 1024), "20.0 MB")
        self.assertEqual(format_file_size(15.5 * 1024 * 1024), "15.5 MB")

    def test_get_max_file_size_for_mime_type_default(self):
        """Тест получения лимита по умолчанию."""
        # Пустой MIME тип
        self.assertEqual(
            get_max_file_size_for_mime_type(''),
            15 * 1024 * 1024
        )
        self.assertEqual(
            get_max_file_size_for_mime_type(None),
            15 * 1024 * 1024
        )
        # Неизвестный тип
        self.assertEqual(
            get_max_file_size_for_mime_type('application/unknown'),
            15 * 1024 * 1024
        )

    def test_get_max_file_size_for_mime_type_images(self):
        """Тест получения лимита для обычных изображений."""
        self.assertEqual(
            get_max_file_size_for_mime_type('image/jpeg'),
            20 * 1024 * 1024
        )
        self.assertEqual(
            get_max_file_size_for_mime_type('image/png'),
            20 * 1024 * 1024
        )
        self.assertEqual(
            get_max_file_size_for_mime_type('image/gif'),
            20 * 1024 * 1024
        )
        self.assertEqual(
            get_max_file_size_for_mime_type('image/webp'),
            20 * 1024 * 1024
        )
        self.assertEqual(
            get_max_file_size_for_mime_type('image/bmp'),
            20 * 1024 * 1024
        )

    def test_get_max_file_size_for_mime_type_raw(self):
        """Тест получения лимита для RAW файлов."""
        self.assertEqual(
            get_max_file_size_for_mime_type('image/x-canon-cr2'),
            50 * 1024 * 1024
        )
        self.assertEqual(
            get_max_file_size_for_mime_type('image/x-adobe-dng'),
            50 * 1024 * 1024
        )
        self.assertEqual(
            get_max_file_size_for_mime_type('image/x-nikon-nef'),
            50 * 1024 * 1024
        )
        self.assertEqual(
            get_max_file_size_for_mime_type('image/tiff'),
            50 * 1024 * 1024
        )
        self.assertEqual(
            get_max_file_size_for_mime_type('image/tif'),
            50 * 1024 * 1024
        )

    def test_get_max_file_size_for_mime_type_pdf(self):
        """Тест получения лимита для PDF."""
        self.assertEqual(
            get_max_file_size_for_mime_type('application/pdf'),
            30 * 1024 * 1024
        )

    def test_get_max_file_size_for_mime_type_documents(self):
        """Тест получения лимита для документов."""
        self.assertEqual(
            get_max_file_size_for_mime_type('application/msword'),
            15 * 1024 * 1024
        )
        self.assertEqual(
            get_max_file_size_for_mime_type(
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ),
            15 * 1024 * 1024
        )
        self.assertEqual(
            get_max_file_size_for_mime_type('text/plain'),
            15 * 1024 * 1024
        )
        self.assertEqual(
            get_max_file_size_for_mime_type('application/rtf'),
            15 * 1024 * 1024
        )

    def test_get_max_file_size_for_mime_type_video(self):
        """Тест получения лимита для видео."""
        self.assertEqual(
            get_max_file_size_for_mime_type('video/mp4'),
            500 * 1024 * 1024
        )
        self.assertEqual(
            get_max_file_size_for_mime_type('video/avi'),
            500 * 1024 * 1024
        )

    def test_get_max_file_size_for_mime_type_audio(self):
        """Тест получения лимита для аудио."""
        self.assertEqual(
            get_max_file_size_for_mime_type('audio/mpeg'),
            100 * 1024 * 1024
        )
        self.assertEqual(
            get_max_file_size_for_mime_type('audio/wav'),
            100 * 1024 * 1024
        )

    @override_settings(DAM_AI_MAX_FILE_SIZE_IMAGES=25 * 1024 * 1024)
    def test_get_max_file_size_custom_settings(self):
        """Тест использования кастомных настроек."""
        self.assertEqual(
            get_max_file_size_for_mime_type('image/jpeg'),
            25 * 1024 * 1024
        )

    def test_get_max_file_size_case_insensitive(self):
        """Тест нечувствительности к регистру."""
        self.assertEqual(
            get_max_file_size_for_mime_type('IMAGE/JPEG'),
            20 * 1024 * 1024
        )
        self.assertEqual(
            get_max_file_size_for_mime_type('Application/PDF'),
            30 * 1024 * 1024
        )

