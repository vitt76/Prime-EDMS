import logging
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image

from .base import BaseMediaConverter

logger = logging.getLogger(name=__name__)


class RawImageConverter(BaseMediaConverter):
    """
    Конвертер для RAW изображений камер.

    Использует dcraw и libraw для конвертации RAW форматов
    (CR2, NEF, ARW, DNG, ORF, RAF, RW2, и др.) в JPEG/PNG.
    """

    # Поддерживаемые RAW форматы
    SUPPORTED_MIME_TYPES = [
        'image/x-canon-cr2',      # Canon CR2
        'image/x-canon-crw',      # Canon CRW
        'image/x-nikon-nef',      # Nikon NEF
        'image/x-nikon-nrw',      # Nikon NRW
        'image/x-sony-arw',       # Sony ARW
        'image/x-sony-srf',       # Sony SRF
        'image/x-pentax-pef',     # Pentax PEF
        'image/x-pentax-raw',     # Pentax RAW
        'image/x-olympus-orf',    # Olympus ORF
        'image/x-fuji-raf',       # Fuji RAF
        'image/x-panasonic-rw2',  # Panasonic RW2
        'image/x-adobe-dng',      # Adobe DNG
        'image/x-kodak-dcr',      # Kodak DCR
        'image/x-kodak-k25',      # Kodak K25
        'image/x-kodak-kdc',      # Kodak KDC
        'image/x-minolta-mrw',    # Minolta MRW
        'image/x-samsung-srw',    # Samsung SRW
        'image/x-sigma-sd9',      # Sigma SD9
        'image/x-sigma-sd14',     # Sigma SD14
        'image/x-sigma-sd15',     # Sigma SD15
        'image/x-sigma-sd1',      # Sigma SD1
        'image/x-sigma-sd1m',     # Sigma SD1 Merrill
    ]

    # Максимальный размер RAW файла - 100MB (RAW файлы могут быть большими)
    MAX_FILE_SIZE_MB = 100

    def convert_to_preview(self, quality=90, format='JPEG', max_size=(1920, 1080)):
        """
        Конвертировать RAW изображение в preview формат.

        Args:
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
            # Создать временный файл для входного RAW файла
            temp_input = self.create_temp_file(suffix='.raw')

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

            # Создать временный файл для выхода
            temp_output = self._get_temp_output_path(output_suffix)

            # Конвертировать с помощью dcraw
            self._convert_with_dcraw(temp_input, temp_output)

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
                    name=f'preview_{Path(temp_input).stem}.{output_format.lower()}'
                )

        except Exception as e:
            logger.error(f"RAW conversion failed: {e}")
            raise
        finally:
            # Очистить временные файлы
            if temp_input:
                self.cleanup_temp_file(temp_input)
            if temp_output:
                self.cleanup_temp_file(temp_output)

    def _convert_with_dcraw(self, input_path, output_path):
        """
        Конвертировать RAW файл с помощью dcraw.

        Args:
            input_path (str): Путь к входному файлу
            output_path (str): Путь к выходному файлу
        """
        # dcraw параметры:
        # -c: вывести на stdout
        # -q 3: качество интерполяции (3 = AHD)
        # -w: использовать white balance из камеры
        # -H 2: выделять горячие пиксели (2 = средне)
        # -o 1: цветовое пространство (1 = sRGB)
        # -6: 16-битный вывод (для лучшего качества)

        command = [
            'dcraw',
            '-c',      # Вывести на stdout
            '-q', '3', # Качество интерполяции AHD
            '-w',      # White balance из камеры
            '-H', '2', # Выделение горячих пикселей
            '-o', '1', # sRGB цветовое пространство
            '-T',      # TIFF вывод (лучше для дальнейшей обработки)
            input_path
        ]

        try:
            # Запустить dcraw
            stdout, stderr, return_code = self.execute_command(command)

            if return_code != 0:
                # Если dcraw не сработал, попробовать libraw
                logger.warning(f"dcraw failed, trying libraw: {stderr}")
                self._convert_with_libraw(input_path, output_path)
                return

            # dcraw выводит TIFF на stdout, конвертировать в JPEG
            with io.BytesIO(stdout) as tiff_buffer:
                with Image.open(tiff_buffer) as img:
                    # Конвертировать TIFF в JPEG
                    if img.mode == 'I':
                        # 16-bit image, конвертировать в 8-bit
                        img = img.point(lambda x: x * (255 / 65535)).convert('L')
                    elif img.mode not in ('RGB', 'L'):
                        img = img.convert('RGB')

                    img.save(output_path, 'JPEG', quality=95)

        except Exception as e:
            logger.warning(f"dcraw conversion failed, trying libraw: {e}")
            self._convert_with_libraw(input_path, output_path)

    def _convert_with_libraw(self, input_path, output_path):
        """
        Конвертировать RAW файл с помощью libraw/dcraw_emu.

        Args:
            input_path (str): Путь к входному файлу
            output_path (str): Путь к выходному файлу
        """
        # Использовать dcraw_emu из libraw
        command = [
            'dcraw_emu',
            '-c',      # Вывести на stdout
            '-q', '3', # Качество интерполяции
            '-w',      # White balance
            '-H', '2', # Выделение горячих пикселей
            '-o', '1', # sRGB
            '-T',      # TIFF вывод
            input_path
        ]

        stdout, stderr, return_code = self.execute_command(command)

        if return_code != 0:
            raise RuntimeError(f"libraw conversion failed: {stderr}")

        # Обработать вывод аналогично dcraw
        with io.BytesIO(stdout) as tiff_buffer:
            with Image.open(tiff_buffer) as img:
                if img.mode == 'I':
                    img = img.point(lambda x: x * (255 / 65535)).convert('L')
                elif img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')

                img.save(output_path, 'JPEG', quality=95)

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

