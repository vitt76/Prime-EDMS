#!/usr/bin/env python3
"""
Video Converter Service
Извлекает кадры из видео файлов для создания preview изображений.

Поддерживает:
- Извлечение кадров по timestamp
- Определение длительности видео
- Создание миниатюр оптимального размера
"""

import sys
import os
import json
import logging
import subprocess
from pathlib import Path
from io import BytesIO

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("PIL not available, image processing disabled")


class VideoConverter:
    """Конвертер видео файлов"""

    def __init__(self):
        self.temp_dir = Path("/tmp/converter")
        self.temp_dir.mkdir(exist_ok=True)

    def extract_frame(self, input_path, timestamp=1.0, output_path=None,
                     quality=90, max_size=(640, 360)):
        """
        Извлечь кадр из видео по timestamp.

        Args:
            input_path (str): Путь к видео файлу
            timestamp (float): Время в секундах для извлечения кадра
            output_path (str): Путь для сохранения изображения (опционально)
            quality (int): Качество JPEG (1-100)
            max_size (tuple): Максимальный размер (width, height)

        Returns:
            str: Путь к созданному изображению
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Создать output path если не указан
        if output_path is None:
            timestamp_str = "02d"
            output_path = self.temp_dir / f"{input_path.stem}_frame_{timestamp_str}.jpg"
        else:
            output_path = Path(output_path)

        logger.info(f"Extracting frame at {timestamp}s from {input_path} to {output_path}")

        # Извлечь кадр с помощью FFmpeg
        self._extract_frame_ffmpeg(input_path, output_path, timestamp)

        # Обработать изображение если PIL доступен
        if PIL_AVAILABLE:
            self._process_image(output_path, quality, max_size)

        logger.info(f"Successfully extracted frame: {output_path}")
        return str(output_path)

    def _extract_frame_ffmpeg(self, input_path, output_path, timestamp):
        """Извлечь кадр с помощью FFmpeg"""
        # Форматировать timestamp
        timestamp_str = "02d"

        cmd = [
            'ffmpeg',
            '-ss', str(timestamp),          # Позиция в секундах
            '-i', str(input_path),          # Входной файл
            '-vframes', '1',                # Один кадр
            '-q:v', '2',                    # Качество (2 = высокое)
            '-f', 'image2',                 # Формат вывода - изображение
            '-y',                           # Перезаписать выходной файл
            str(output_path)                # Выходной файл
        ]

        logger.debug(f"Running FFmpeg command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=30  # 30 секунд таймаут
        )

        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='ignore')
            logger.error(f"FFmpeg failed: {error_msg}")

            # Попробовать альтернативный подход
            self._extract_frame_alternative(input_path, output_path, timestamp)
            return

        # Проверить что файл создался
        if not output_path.exists():
            raise RuntimeError("FFmpeg completed but output file not found")

    def _extract_frame_alternative(self, input_path, output_path, timestamp):
        """Альтернативный метод извлечения кадра"""
        logger.info("Trying alternative frame extraction method")

        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-ss', str(timestamp),
            '-vcodec', 'mjpeg',
            '-vframes', '1',
            '-an',                          # Без аудио
            '-y',
            str(output_path)
        ]

        result = subprocess.run(cmd, capture_output=True, timeout=30)

        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='ignore')
            raise RuntimeError(f"Alternative FFmpeg extraction failed: {error_msg}")

    def _process_image(self, image_path, quality, max_size):
        """Обработать извлеченное изображение"""
        try:
            with Image.open(image_path) as img:
                # Конвертировать в RGB если нужно
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')

                # Изменить размер если нужно
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.LANCZOS)

                # Сохранить с оптимизацией
                img.save(image_path, 'JPEG', quality=quality, optimize=True)

        except Exception as e:
            logger.warning(f"Image processing failed: {e}")

    def get_video_info(self, input_path):
        """
        Получить информацию о видео файле.

        Args:
            input_path (str): Путь к видео файлу

        Returns:
            dict: Информация о видео
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Получить информацию с помощью ffprobe
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            str(input_path)
        ]

        result = subprocess.run(cmd, capture_output=True, timeout=30)

        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='ignore')
            raise RuntimeError(f"ffprobe failed: {error_msg}")

        try:
            data = json.loads(result.stdout.decode('utf-8'))

            # Извлечь основную информацию
            format_info = data.get('format', {})
            duration = float(format_info.get('duration', 0))
            size = int(format_info.get('size', 0))

            # Найти видео поток
            video_stream = None
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                    break

            width = height = None
            if video_stream:
                width = video_stream.get('width')
                height = video_stream.get('height')

            return {
                'duration': duration,
                'duration_formatted': self._format_duration(duration),
                'size': size,
                'size_mb': round(size / (1024 * 1024), 2),
                'width': width,
                'height': height,
                'format': format_info.get('format_name', 'unknown')
            }

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse ffprobe output: {e}")
            return {'error': 'Failed to parse video info'}

    def _format_duration(self, seconds):
        """Форматировать длительность в читаемый вид"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)

        if hours > 0:
            return "02d"
        else:
            return "02d"

    def create_multiple_thumbnails(self, input_path, output_dir, count=5, max_size=(320, 180)):
        """
        Создать несколько миниатюр видео.

        Args:
            input_path (str): Путь к видео файлу
            output_dir (str): Директория для сохранения миниатюр
            count (int): Количество миниатюр
            max_size (tuple): Максимальный размер миниатюр

        Returns:
            list: Список путей к созданным миниатюрам
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)

        # Получить длительность видео
        info = self.get_video_info(input_path)
        duration = info.get('duration', 60)

        # Создать timestamps для миниатюр
        timestamps = [duration * i / (count - 1) for i in range(count)]

        thumbnails = []
        for i, timestamp in enumerate(timestamps):
            try:
                output_path = output_dir / "03d"
                thumbnail_path = self.extract_frame(
                    input_path, timestamp, output_path, max_size=max_size
                )
                thumbnails.append(thumbnail_path)
            except Exception as e:
                logger.warning(f"Failed to create thumbnail {i+1}: {e}")
                continue

        return thumbnails


def main():
    """Основная функция для обработки запросов"""
    if len(sys.argv) < 2:
        print("Usage: python convert_video.py <command> [args...]")
        print("Commands:")
        print("  extract <input_file> [timestamp] [output_file] [quality] [max_width] [max_height]")
        print("  info <input_file>")
        print("  thumbnails <input_file> <output_dir> [count] [max_width] [max_height]")
        sys.exit(1)

    command = sys.argv[1]
    converter = VideoConverter()

    try:
        if command == 'extract':
            if len(sys.argv) < 3:
                print("Error: input file required")
                sys.exit(1)

            input_file = sys.argv[2]
            timestamp = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
            output_file = sys.argv[4] if len(sys.argv) > 4 else None
            quality = int(sys.argv[5]) if len(sys.argv) > 5 else 90
            max_width = int(sys.argv[6]) if len(sys.argv) > 6 else 640
            max_height = int(sys.argv[7]) if len(sys.argv) > 7 else 360

            result_path = converter.extract_frame(
                input_file, timestamp, output_file, quality, (max_width, max_height)
            )

            result = {
                'success': True,
                'output_path': result_path,
                'input_file': input_file,
                'timestamp': timestamp
            }
            print(json.dumps(result))

        elif command == 'info':
            if len(sys.argv) < 3:
                print("Error: input file required")
                sys.exit(1)

            input_file = sys.argv[2]
            info = converter.get_video_info(input_file)

            result = {
                'success': True,
                'input_file': input_file,
                'info': info
            }
            print(json.dumps(result))

        elif command == 'thumbnails':
            if len(sys.argv) < 4:
                print("Error: input file and output dir required")
                sys.exit(1)

            input_file = sys.argv[2]
            output_dir = sys.argv[3]
            count = int(sys.argv[4]) if len(sys.argv) > 4 else 5
            max_width = int(sys.argv[5]) if len(sys.argv) > 5 else 320
            max_height = int(sys.argv[6]) if len(sys.argv) > 6 else 180

            thumbnails = converter.create_multiple_thumbnails(
                input_file, output_dir, count, (max_width, max_height)
            )

            result = {
                'success': True,
                'input_file': input_file,
                'thumbnails': thumbnails,
                'count': len(thumbnails)
            }
            print(json.dumps(result))

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }
        print(json.dumps(error_result))
        sys.exit(1)


if __name__ == '__main__':
    main()

