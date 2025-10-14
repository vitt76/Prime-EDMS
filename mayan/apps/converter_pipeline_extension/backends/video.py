import io
import logging
import json
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image

from .base import BaseMediaConverter

logger = logging.getLogger(name=__name__)


class VideoConverter(BaseMediaConverter):
    """
    Конвертер для видео файлов.

    Использует FFmpeg для извлечения кадров из видео
    и создания thumbnail изображений.
    """

    # Поддерживаемые видео форматы
    SUPPORTED_MIME_TYPES = [
        'video/mp4',           # MP4
        'video/avi',           # AVI
        'video/mov',           # QuickTime MOV
        'video/mkv',           # Matroska MKV
        'video/webm',          # WebM
        'video/flv',           # Flash Video
        'video/wmv',           # Windows Media Video
        'video/m4v',           # M4V
        'video/3gp',           # 3GP
        'video/quicktime',     # QuickTime
        'video/x-msvideo',     # AVI (альтернативный MIME)
        'video/x-flv',         # FLV (альтернативный)
        'video/x-ms-wmv',      # WMV (альтернативный)
        'video/x-matroska',    # MKV (альтернативный)
    ]

    # Максимальный размер видео файла - 2GB
    MAX_FILE_SIZE_MB = 2048

    def convert_to_preview(self, timestamp=None, quality=90, format='JPEG', max_size=(640, 360)):
        """
        Извлечь кадр из видео для preview.

        Args:
            timestamp (float): Время в секундах для извлечения кадра (None = середина видео)
            quality (int): Качество JPEG (1-100)
            format (str): Формат вывода ('JPEG', 'PNG')
            max_size (tuple): Максимальный размер (width, height)

        Returns:
            ContentFile: Preview изображение
        """
        self.validate_file()

        temp_input = None
        temp_output = None

        try:
            # Создать временный файл для видео
            temp_input = self.create_temp_file()

            # Определить timestamp для извлечения кадра
            if timestamp is None:
                # Получить длительность видео и взять кадр из середины
                duration = self._get_video_duration(temp_input)
                timestamp = duration / 2 if duration > 0 else 1.0

            # Определить выходной формат
            if format.upper() == 'JPEG':
                output_suffix = '.jpg'
                output_format = 'JPEG'
            elif format.upper() == 'PNG':
                output_suffix = '.png'
                output_format = 'PNG'
            else:
                output_suffix = '.jpg'
                output_format = 'JPEG'

            # Создать временный файл для thumbnail
            temp_output = self._get_temp_output_path(output_suffix)

            # Извлечь кадр с помощью FFmpeg
            self._extract_frame_with_ffmpeg(temp_input, temp_output, timestamp)

            # Обработать изображение с помощью PIL
            with Image.open(temp_output) as img:
                # Конвертировать в RGB если нужно
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')

                # Изменить размер если нужно
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.LANCZOS)

                # Сохранить в буфер
                output_buffer = io.BytesIO()

                if output_format == 'JPEG':
                    img.save(output_buffer, format=output_format, quality=quality, optimize=True)
                else:
                    img.save(output_buffer, format=output_format, optimize=True)

                output_buffer.seek(0)

                return ContentFile(
                    output_buffer.getvalue(),
                    name=f'video_preview_{Path(temp_input).stem}_{int(timestamp)}s.{output_format.lower()}'
                )

        except Exception as e:
            logger.error(f"Video conversion failed: {e}")
            raise
        finally:
            # Очистить временные файлы
            if temp_input:
                self.cleanup_temp_file(temp_input)
            if temp_output:
                self.cleanup_temp_file(temp_output)

    def _extract_frame_with_ffmpeg(self, input_path, output_path, timestamp):
        """
        Извлечь кадр из видео с помощью FFmpeg.

        Args:
            input_path (str): Путь к видео файлу
            output_path (str): Путь к выходному изображению
            timestamp (float): Время в секундах
        """
        # FFmpeg команда для извлечения одного кадра
        # -ss: позиция в секундах
        # -vframes 1: извлечь только один кадр
        # -q:v 2: качество (2 = высокое)
        # -f image2: формат вывода - изображение

        command = [
            'ffmpeg',
            '-ss', str(timestamp),     # Позиция в секундах
            '-i', input_path,          # Входной файл
            '-vframes', '1',           # Один кадр
            '-q:v', '2',               # Качество (2 = высокое)
            '-f', 'image2',            # Формат вывода
            '-y',                      # Перезаписать выходной файл
            output_path                # Выходной файл
        ]

        stdout, stderr, return_code = self.execute_command(command)

        if return_code != 0:
            # Попробовать альтернативный подход
            logger.warning(f"FFmpeg frame extraction failed, trying alternative: {stderr}")
            self._extract_frame_alternative(input_path, output_path, timestamp)
            return

        # Проверить что файл создался
        if not Path(output_path).exists():
            raise RuntimeError(f"FFmpeg failed to create output file: {stderr}")

    def _extract_frame_alternative(self, input_path, output_path, timestamp):
        """
        Альтернативный метод извлечения кадра.

        Args:
            input_path (str): Путь к видео файлу
            output_path (str): Путь к выходному изображению
            timestamp (float): Время в секундах
        """
        # Использовать более простой подход с конвертацией
        command = [
            'ffmpeg',
            '-i', input_path,
            '-ss', str(timestamp),
            '-vcodec', 'mjpeg',
            '-vframes', '1',
            '-an',                      # Без аудио
            '-y',
            output_path
        ]

        stdout, stderr, return_code = self.execute_command(command)

        if return_code != 0:
            raise RuntimeError(f"Alternative FFmpeg extraction failed: {stderr}")

    def _get_video_duration(self, video_path):
        """
        Получить длительность видео с помощью ffprobe.

        Args:
            video_path (str): Путь к видео файлу

        Returns:
            float: Длительность в секундах
        """
        try:
            # ffprobe для получения информации о видео
            command = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                video_path
            ]

            stdout, stderr, return_code = self.execute_command(command)

            if return_code == 0:
                data = json.loads(stdout)
                duration = float(data['format']['duration'])
                return duration
            else:
                logger.warning(f"ffprobe failed, using fallback: {stderr}")
                return self._get_duration_fallback(video_path)

        except Exception as e:
            logger.warning(f"Failed to get video duration: {e}")
            return 10.0  # Значение по умолчанию

    def _get_duration_fallback(self, video_path):
        """
        Fallback метод для получения длительности видео.

        Args:
            video_path (str): Путь к видео файлу

        Returns:
            float: Длительность в секундах
        """
        try:
            # Использовать ffmpeg для получения длительности
            command = [
                'ffmpeg',
                '-i', video_path,
                '-f', 'null',
                '-'
            ]

            stdout, stderr, return_code = self.execute_command(command, timeout=10)

            # Найти duration в stderr
            for line in stderr.split('\n'):
                if 'Duration:' in line:
                    # Парсинг строки типа "Duration: 00:01:23.45"
                    duration_str = line.split('Duration:')[1].split(',')[0].strip()
                    h, m, s = duration_str.split(':')
                    duration = float(h) * 3600 + float(m) * 60 + float(s)
                    return duration

        except Exception as e:
            logger.warning(f"Fallback duration detection failed: {e}")

        return 10.0  # Значение по умолчанию

    def get_video_info(self):
        """
        Получить информацию о видео файле.

        Returns:
            dict: Информация о видео
        """
        temp_input = None

        try:
            temp_input = self.create_temp_file()
            duration = self._get_video_duration(temp_input)

            info = self.get_file_info()
            info.update({
                'duration': duration,
                'duration_formatted': self._format_duration(duration),
            })

            return info

        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            return self.get_file_info()
        finally:
            if temp_input:
                self.cleanup_temp_file(temp_input)

    def _format_duration(self, seconds):
        """
        Форматировать длительность в читаемый вид.

        Args:
            seconds (float): Длительность в секундах

        Returns:
            str: Отформатированная длительность
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

    def _get_temp_output_path(self, suffix):
        """
        Получить путь для временного выходного файла.

        Args:
            suffix (str): Расширение файла

        Returns:
            str: Путь к временному файлу
        """
        import tempfile
        import os

        fd, path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)  # Закрыть дескриптор, оставить файл
        return path

