#!/usr/bin/env python3
"""
RAW Image Converter Service
Конвертирует RAW изображения в JPEG/PNG форматы для preview.

Поддерживает:
- dcraw для базовой обработки RAW
- libraw/rawpy для продвинутой обработки
- Автоматическое определение оптимальных параметров
"""

import sys
import os
import json
import logging
from pathlib import Path
import tempfile
import subprocess
from io import BytesIO

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import rawpy
    import imageio
    from PIL import Image
    RAWPY_AVAILABLE = True
except ImportError:
    RAWPY_AVAILABLE = False
    logger.warning("rawpy not available, falling back to dcraw only")


class RawImageConverter:
    """Конвертер RAW изображений"""

    def __init__(self):
        self.temp_dir = Path("/tmp/converter")
        self.temp_dir.mkdir(exist_ok=True)

    def convert_raw_to_jpeg(self, input_path, output_path=None, quality=90, max_size=None):
        """
        Конвертировать RAW файл в JPEG.

        Args:
            input_path (str): Путь к RAW файлу
            output_path (str): Путь для сохранения JPEG (опционально)
            quality (int): Качество JPEG (1-100)
            max_size (tuple): Максимальный размер (width, height)

        Returns:
            str: Путь к созданному JPEG файлу
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Создать output path если не указан
        if output_path is None:
            output_path = self.temp_dir / f"{input_path.stem}_converted.jpg"
        else:
            output_path = Path(output_path)

        logger.info(f"Converting {input_path} to {output_path}")

        try:
            # Сначала попробовать rawpy (более качественный)
            if RAWPY_AVAILABLE:
                return self._convert_with_rawpy(input_path, output_path, quality, max_size)
            else:
                # Fallback на dcraw
                return self._convert_with_dcraw(input_path, output_path, quality, max_size)

        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            # Последний шанс с dcraw
            return self._convert_with_dcraw(input_path, output_path, quality, max_size)

    def _convert_with_rawpy(self, input_path, output_path, quality, max_size):
        """Конвертация с помощью rawpy (высокое качество)"""
        logger.info("Using rawpy for conversion")

        with rawpy.imread(str(input_path)) as raw:
            # Автоматическая обработка
            rgb = raw.postprocess(
                use_camera_wb=True,  # White balance из камеры
                use_auto_wb=False,
                half_size=False,     # Полный размер
                output_bps=8         # 8-bit output
            )

        # Создать PIL изображение
        image = Image.fromarray(rgb)

        # Изменить размер если нужно
        if max_size:
            image.thumbnail(max_size, Image.LANCZOS)

        # Сохранить как JPEG
        image.save(output_path, 'JPEG', quality=quality, optimize=True)

        logger.info(f"Successfully converted with rawpy: {output_path}")
        return str(output_path)

    def _convert_with_dcraw(self, input_path, output_path, quality, max_size):
        """Конвертация с помощью dcraw (fallback)"""
        logger.info("Using dcraw for conversion")

        # dcraw параметры для оптимального качества
        dcraw_cmd = [
            'dcraw',
            '-c',              # Вывести на stdout
            '-q', '3',         # Качество интерполяции AHD (высокое)
            '-w',              # White balance из камеры
            '-H', '2',         # Выделение горячих пикселей (средне)
            '-o', '1',         # Цветовое пространство sRGB
            '-6',              # 16-bit линейный выход (для лучшей обработки)
            '-T',              # Выход в TIFF формате
            str(input_path)
        ]

        # Запустить dcraw
        result = subprocess.run(dcraw_cmd, capture_output=True, timeout=60)

        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='ignore')
            raise RuntimeError(f"dcraw failed: {error_msg}")

        # Обработать TIFF выход dcraw с помощью PIL
        tiff_data = BytesIO(result.stdout)

        try:
            with Image.open(tiff_data) as img:
                # Конвертировать в RGB если нужно
                if img.mode == 'I':
                    # 16-bit image, конвертировать в 8-bit
                    img = img.point(lambda x: x * (255 / 65535)).convert('L')
                elif img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')

                # Изменить размер если нужно
                if max_size:
                    img.thumbnail(max_size, Image.LANCZOS)

                # Сохранить как JPEG
                img.save(output_path, 'JPEG', quality=quality, optimize=True)

        except Exception as e:
            raise RuntimeError(f"PIL processing failed: {e}")

        logger.info(f"Successfully converted with dcraw: {output_path}")
        return str(output_path)


def main():
    """Основная функция для обработки запросов на конвертацию"""
    if len(sys.argv) < 2:
        print("Usage: python convert_raw.py <command> [args...]")
        print("Commands:")
        print("  convert <input_file> [output_file] [quality] [max_width] [max_height]")
        print("  info <input_file>")
        sys.exit(1)

    command = sys.argv[1]
    converter = RawImageConverter()

    try:
        if command == 'convert':
            if len(sys.argv) < 3:
                print("Error: input file required")
                sys.exit(1)

            input_file = sys.argv[2]
            output_file = sys.argv[3] if len(sys.argv) > 3 else None
            quality = int(sys.argv[4]) if len(sys.argv) > 4 else 90
            max_width = int(sys.argv[5]) if len(sys.argv) > 5 else None
            max_height = int(sys.argv[6]) if len(sys.argv) > 6 else None

            max_size = (max_width, max_height) if max_width and max_height else None

            result_path = converter.convert_raw_to_jpeg(
                input_file, output_file, quality, max_size
            )

            # Вывести результат как JSON для обработки вызывающим кодом
            result = {
                'success': True,
                'output_path': result_path,
                'input_file': input_file
            }
            print(json.dumps(result))

        elif command == 'info':
            if len(sys.argv) < 3:
                print("Error: input file required")
                sys.exit(1)

            input_file = sys.argv[2]

            # Получить информацию о RAW файле
            info_cmd = ['dcraw', '-i', '-v', input_file]
            result = subprocess.run(info_cmd, capture_output=True, timeout=30)

            if result.returncode == 0:
                info = {
                    'success': True,
                    'info': result.stdout.decode('utf-8', errors='ignore')
                }
            else:
                info = {
                    'success': False,
                    'error': result.stderr.decode('utf-8', errors='ignore')
                }

            print(json.dumps(info))

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

