import io
import logging
import tempfile
from pathlib import Path

from django.core.files.base import ContentFile

logger = logging.getLogger(name=__name__)


class BaseMediaConverter:
    """
    Базовый класс для конвертеров медиа файлов.

    Определяет интерфейс для всех конвертеров и предоставляет
    общую функциональность.
    """

    # Список поддерживаемых MIME типов
    SUPPORTED_MIME_TYPES = []

    # Максимальный размер файла в MB
    MAX_FILE_SIZE_MB = 500

    # Таймаут конвертации в секундах
    CONVERSION_TIMEOUT = 300

    def __init__(self, file_obj, mime_type=None):
        """
        Инициализация конвертера.

        Args:
            file_obj: File объект Django
            mime_type (str): MIME тип файла
        """
        self.file_obj = file_obj
        self.mime_type = mime_type or getattr(file_obj, 'mime_type', 'application/octet-stream')

        if self.mime_type not in self.SUPPORTED_MIME_TYPES:
            raise ValueError(f"MIME type {self.mime_type} not supported by {self.__class__.__name__}")

    @classmethod
    def can_handle(cls, mime_type):
        """
        Проверить, может ли конвертер обработать данный MIME тип.

        Args:
            mime_type (str): MIME тип файла

        Returns:
            bool: True если конвертер поддерживает тип
        """
        return mime_type in cls.SUPPORTED_MIME_TYPES

    def validate_file(self):
        """
        Валидация файла перед конвертацией.

        Returns:
            bool: True если файл валиден

        Raises:
            ValueError: Если файл не валиден
        """
        from ..utils import validate_file_size

        if not validate_file_size(self.file_obj, self.MAX_FILE_SIZE_MB):
            raise ValueError(f"File size exceeds maximum allowed size of {self.MAX_FILE_SIZE_MB}MB")

        return True

    def convert_to_preview(self, **options):
        """
        Конвертировать файл в формат preview.

        Args:
            **options: Дополнительные опции конвертации

        Returns:
            ContentFile: Django ContentFile с preview изображением

        Raises:
            NotImplementedError: Должен быть реализован в подклассах
        """
        raise NotImplementedError("Subclasses must implement convert_to_preview method")

    def get_file_info(self):
        """
        Получить информацию о файле.

        Returns:
            dict: Информация о файле
        """
        from ..utils import get_file_info
        return get_file_info(self.file_obj)

    def create_temp_file(self, suffix=''):
        """
        Создать временный файл с содержимым исходного файла.

        Args:
            suffix (str): Суффикс для временного файла

        Returns:
            str: Путь к временному файлу
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            self.file_obj.seek(0)
            for chunk in self.file_obj.chunks():
                temp_file.write(chunk)
            return temp_file.name

    def cleanup_temp_file(self, file_path):
        """
        Очистить временный файл.

        Args:
            file_path (str): Путь к файлу для удаления
        """
        try:
            Path(file_path).unlink(missing_ok=True)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {file_path}: {e}")

    def execute_command(self, command, timeout=None, **kwargs):
        """
        Выполнить системную команду с таймаутом.

        Args:
            command (list): Команда для выполнения
            timeout (int): Таймаут в секундах
            **kwargs: Дополнительные аргументы для subprocess

        Returns:
            tuple: (stdout, stderr, return_code)

        Raises:
            TimeoutError: При превышении таймаута
            Exception: При ошибке выполнения
        """
        import subprocess
        import shlex

        if isinstance(command, str):
            command = shlex.split(command)

        timeout = timeout or self.CONVERSION_TIMEOUT

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                timeout=timeout,
                **kwargs
            )

            stdout = result.stdout.decode('utf-8', errors='ignore')
            stderr = result.stderr.decode('utf-8', errors='ignore')

            return stdout, stderr, result.returncode

        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Command execution timed out after {timeout} seconds")
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            raise

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        # Здесь можно добавить очистку ресурсов
        pass

