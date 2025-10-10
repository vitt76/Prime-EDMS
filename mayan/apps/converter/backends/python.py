import io
import logging
import os
import shutil
import struct
import subprocess
import tempfile

from PIL import Image
import PyPDF2
import sh

from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from mayan.apps.storage.utils import NamedTemporaryFile

from ..classes import ConverterBase
from ..exceptions import AppImageError, PageCountError
from ..settings import setting_graphics_backend_arguments

from ..literals import (
    DEFAULT_PDFTOPPM_DPI, DEFAULT_PDFTOPPM_FORMAT, DEFAULT_PDFTOPPM_PATH,
    DEFAULT_PDFINFO_PATH, DEFAULT_PILLOW_MAXIMUM_IMAGE_PIXELS
)

logger = logging.getLogger(name=__name__)
pdftoppm_path = setting_graphics_backend_arguments.value.get(
    'pdftoppm_path', DEFAULT_PDFTOPPM_PATH
)

try:
    pdftoppm = sh.Command(path=pdftoppm_path)
except sh.CommandNotFound:
    pdftoppm = None
else:
    pdftoppm_format = '-{}'.format(
        setting_graphics_backend_arguments.value.get(
            'pdftoppm_format', DEFAULT_PDFTOPPM_FORMAT
        )
    )

    pdftoppm_dpi = format(
        setting_graphics_backend_arguments.value.get(
            'pdftoppm_dpi', DEFAULT_PDFTOPPM_DPI
        )
    )

    pdftoppm = pdftoppm.bake(pdftoppm_format, '-r', pdftoppm_dpi)

pdfinfo_path = setting_graphics_backend_arguments.value.get(
    'pdfinfo_path', DEFAULT_PDFINFO_PATH
)

try:
    pdfinfo = sh.Command(path=pdfinfo_path)
except sh.CommandNotFound:
    pdfinfo = None


pillow_maximum_image_pixels = setting_graphics_backend_arguments.value.get(
    'pillow_maximum_image_pixels', DEFAULT_PILLOW_MAXIMUM_IMAGE_PIXELS
)
Image.MAX_IMAGE_PIXELS = pillow_maximum_image_pixels


class Python(ConverterBase):
    def convert(self, *args, **kwargs):
        super().convert(*args, **kwargs)

        if self.mime_type == 'application/pdf' and pdftoppm:
            with NamedTemporaryFile() as new_file_object:
                self.file_object.seek(0)
                shutil.copyfileobj(fsrc=self.file_object, fdst=new_file_object)
                self.file_object.seek(0)
                new_file_object.seek(0)

                image_buffer = io.BytesIO()
                pdftoppm(
                    new_file_object.name, f=self.page_number + 1,
                    l=self.page_number + 1, _out=image_buffer
                )
                image_buffer.seek(0)
                return Image.open(fp=image_buffer)

        # Поддержка видео файлов - извлечение превью
        elif self.mime_type and self.mime_type.startswith('video/'):
            return self._convert_video_to_preview()

        # Поддержка архивных файлов - превью содержимого
        elif self.mime_type and self.mime_type in [
            'application/zip', 'application/x-zip-compressed', 'application/x-rar',
            'application/x-rar-compressed', 'application/x-7z-compressed',
            'application/x-tar', 'application/x-gzip', 'application/x-bzip2', 'application/x-xz'
        ]:
            return self._convert_archive_to_preview()

    def get_page_count(self):
        super().get_page_count()

        page_count = 1

        # Для видео файлов возвращаем 1 страницу (превью)
        if self.mime_type and self.mime_type.startswith('video/'):
            logger.debug('Video file detected, returning 1 page (preview)')
            return 1

        # Для архивных файлов возвращаем 1 страницу (превью содержимого)
        archive_mimetypes = [
            'application/zip', 'application/x-zip-compressed', 'application/x-rar',
            'application/x-rar-compressed', 'application/x-7z-compressed',
            'application/x-tar', 'application/x-gzip', 'application/x-bzip2', 'application/x-xz'
        ]
        if self.mime_type and self.mime_type in archive_mimetypes:
            logger.debug('Archive file detected, returning 1 page (preview)')
            return 1

        if self.mime_type == 'application/pdf' or self.soffice_file:
            if self.soffice_file:
                file_object = self.soffice_file
            else:
                file_object = self.file_object

            try:
                # Try PyPDF to determine the page number
                pdf_reader = PyPDF2.PdfFileReader(
                    stream=file_object, strict=False
                )
                page_count = pdf_reader.getNumPages()
            except Exception as exception:
                if force_text(s=exception) == 'File has not been decrypted':
                    # File is encrypted, try to decrypt using a blank
                    # password.
                    file_object.seek(0)
                    pdf_reader = PyPDF2.PdfFileReader(
                        stream=file_object, strict=False
                    )
                    try:
                        pdf_reader.decrypt(password=b'')
                        page_count = pdf_reader.getNumPages()
                    except Exception as exception:
                        file_object.seek(0)
                        if force_text(s=exception) == 'only algorithm code 1 and 2 are supported':
                            # PDF uses an unsupported encryption
                            # Try poppler-util's pdfinfo
                            page_count = self.get_pdfinfo_page_count(
                                file_object=file_object
                            )
                            return page_count
                        else:
                            error_message = _(
                                'Exception determining PDF page count; %s'
                            ) % exception
                            logger.error(error_message, exc_info=True)
                            raise PageCountError(error_message)
                elif force_text(s=exception) == 'EOF marker not found':
                    # PyPDF2 issue: https://github.com/mstamy2/PyPDF2/issues/177
                    # Try poppler-util's pdfinfo
                    logger.debug('PyPDF2 GitHub issue #177 : EOF marker not found')
                    file_object.seek(0)
                    page_count = self.get_pdfinfo_page_count(file_object)
                    return page_count
                else:
                    error_message = _(
                        'Exception determining PDF page count; %s'
                    ) % exception
                    logger.error(error_message, exc_info=True)
                    raise PageCountError(error_message)
            else:
                logger.debug('Document contains %d pages', page_count)
                return page_count
            finally:
                file_object.seek(0)
        else:
            try:
                image = Image.open(fp=self.file_object)
            except IOError as exception:
                error_message = _(
                    'Exception determining page count using Pillow; %s'
                ) % exception
                logger.error(error_message)
                raise PageCountError(error_message)
            finally:
                self.file_object.seek(0)

            # Get total page count by attempting to seek to an increasing
            # page count number until an EOFError or struct.error exception
            # are raised.
            while True:
                try:
                    image.seek(image.tell() + 1)
                except EOFError:
                    """End of sequence"""
                    break
                except struct.error:
                    """
                    struct.error was raise for a TIFF file converted to JPEG
                    GitLab issue #767 "Upload Error: unpack_from requires a
                    buffer of at least 2 bytes"
                    """
                    logger.debug(
                        'image page count detection raised struct.error'
                    )
                    break
                else:
                    try:
                        # Even if the image reports multiple frames,
                        # test it to make sure it is valid and supported
                        # before counting it as a valid page.
                        image.getim()
                    except OSError as exception:
                        logger.error(
                            'Multi image element not supported; %s',
                            exception
                        )
                        break
                    else:
                        page_count += 1

            self.file_object.seek(0)
            return page_count

    def _convert_video_to_preview(self):
        """
        Конвертирует видео файл в превью изображение (первый кадр).
        """
        logger.info(f'Converting video to preview: {self.mime_type}')

        # Сохраняем видео во временный файл
        with NamedTemporaryFile(delete=False) as temp_video:
            self.file_object.seek(0)
            shutil.copyfileobj(fsrc=self.file_object, fdst=temp_video)
            temp_video_path = temp_video.name

        try:
            # Создаем временный файл для превью
            with NamedTemporaryFile(suffix='.png', delete=False) as temp_image:
                temp_image_path = temp_image.name

            # Команда FFmpeg для извлечения превью
            cmd = [
                'ffmpeg',
                '-y',                    # перезаписывать файлы
                '-i', temp_video_path,  # входной файл
                '-ss', '0.5',          # начать с 0.5 секунды
                '-vframes', '1',       # извлечь только первый кадр
                '-q:v', '2',           # качество
                '-vf', 'scale=800:-1', # масштабировать до ширины 800px
                '-f', 'image2',        # формат вывода
                temp_image_path        # выходной файл
            ]

            logger.debug(f'Running FFmpeg command: {" ".join(cmd)}')

            # Запускаем FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                logger.error(f'FFmpeg failed: {result.stderr}')
                raise AppImageError(_('Video preview extraction failed'))

            # Проверяем, создался ли файл
            if not os.path.exists(temp_image_path) or os.path.getsize(temp_image_path) == 0:
                logger.error(f'FFmpeg output file not created or empty: {temp_image_path}')
                raise AppImageError(_('Video preview file not created'))

            # Читаем изображение
            with open(temp_image_path, 'rb') as f:
                image_data = f.read()

            image_buffer = io.BytesIO(image_data)
            image = Image.open(image_buffer)

            logger.info(f'Video preview extracted successfully, size: {image.size}')
            return image

        except subprocess.TimeoutExpired:
            logger.error('FFmpeg command timed out')
            raise AppImageError(_('Video preview extraction timed out'))
        except Exception as e:
            logger.error(f'Error extracting video preview: {e}')
            raise AppImageError(_('Video preview extraction failed'))
        finally:
            # Очистка временных файлов
            try:
                os.unlink(temp_video_path)
                if 'temp_image_path' in locals():
                    os.unlink(temp_image_path)
            except:
                pass

    def _convert_archive_to_preview(self):
        """
        Создает превью для архива, показывая информацию о содержимом.

        Returns:
            PIL.Image: изображение превью
        """
        logger.info(f'Creating archive preview for: {self.mime_type}')

        try:
            # Импортировать необходимые модули
            import zipfile
            import tarfile

            # Создать изображение превью
            img_width, img_height = 800, 600
            img = Image.new('RGB', (img_width, img_height), color='white')
            draw = ImageDraw.Draw(img)

            # Попробовать загрузить шрифт
            try:
                # В контейнере Mayan могут быть другие пути к шрифтам
                font_title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
                font_text = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
            except:
                font_title = ImageFont.load_default()
                font_text = ImageFont.load_default()

            # Получить информацию об архиве
            archive_info = self._get_archive_info_for_preview()

            # Заголовок
            title = f"📦 Archive Preview"
            draw.text((20, 20), title, fill='black', font=font_title)

            # Информация об архиве
            y_pos = 70
            info_lines = [
                f"Files: {archive_info.get('file_count', 'Unknown')}",
                f"Total size: {archive_info.get('total_size', 'Unknown')}",
                f"Format: {archive_info.get('format', 'Unknown')}",
            ]

            for line in info_lines:
                draw.text((20, y_pos), line, fill='black', font=font_text)
                y_pos += 25

            # Список файлов (первые 10)
            if archive_info.get('files'):
                draw.text((20, y_pos + 20), "Contents:", fill='black', font=font_text)
                y_pos += 50

                for i, filename in enumerate(archive_info['files'][:10]):
                    if y_pos > img_height - 30:
                        break
                    truncated_name = filename[:50] + '...' if len(filename) > 50 else filename
                    draw.text((30, y_pos), f"• {truncated_name}", fill='black', font=font_text)
                    y_pos += 20

                if len(archive_info['files']) > 10:
                    draw.text((30, y_pos), f"... and {len(archive_info['files']) - 10} more files", fill='gray', font=font_text)

            return img

        except Exception as e:
            logger.error(f'Error creating archive preview: {e}')
            raise AppImageError(_('Archive preview creation failed'))

    def _get_archive_info_for_preview(self):
        """
        Получает информацию о содержимом архива для превью.

        Returns:
            dict: информация об архиве
        """
        import zipfile
        import tarfile

        info = {
            'file_count': 0,
            'total_size': 0,
            'files': [],
            'format': 'Unknown'
        }

        try:
            mimetype = self.mime_type

            if mimetype in ['application/zip', 'application/x-zip-compressed']:
                info['format'] = 'ZIP'
                with NamedTemporaryFile() as temp_file:
                    shutil.copyfileobj(self.file_object, temp_file)
                    temp_file.seek(0)
                    self.file_object.seek(0)

                    with zipfile.ZipFile(temp_file, 'r') as zip_ref:
                        for file_info in zip_ref.filelist:
                            if not file_info.is_dir():
                                filename = os.path.basename(file_info.filename)
                                if filename:
                                    info['files'].append(filename)
                                    info['total_size'] += file_info.file_size
                                    info['file_count'] += 1

            elif mimetype in ['application/x-tar']:
                info['format'] = 'TAR'
                with NamedTemporaryFile() as temp_file:
                    shutil.copyfileobj(self.file_object, temp_file)
                    temp_file.seek(0)
                    self.file_object.seek(0)

                    with tarfile.open(fileobj=temp_file, mode='r') as tar_ref:
                        for member in tar_ref.getmembers():
                            if member.isfile():
                                filename = os.path.basename(member.name)
                                if filename:
                                    info['files'].append(filename)
                                    info['total_size'] += member.size
                                    info['file_count'] += 1

            # Форматировать размер
            if info['total_size'] > 1024 * 1024 * 1024:
                info['total_size'] = f"{info['total_size'] / (1024 * 1024 * 1024):.1f} GB"
            elif info['total_size'] > 1024 * 1024:
                info['total_size'] = f"{info['total_size'] / (1024 * 1024):.1f} MB"
            elif info['total_size'] > 1024:
                info['total_size'] = f"{info['total_size'] / 1024:.1f} KB"
            else:
                info['total_size'] = f"{info['total_size']} B"

        except Exception as e:
            logger.error(f'Failed to get archive info for preview: {e}')

        return info

    def get_pdfinfo_page_count(self, file_object):
        process = pdfinfo('-', _in=file_object)
        page_count = int(
            list(filter(
                lambda line: line.startswith('Pages:'),
                force_text(s=process.stdout).split('\n')
            ))[0].replace('Pages:', '')
        )
        file_object.seek(0)
        logger.debug(
            'Document contains %d pages', page_count
        )
        return page_count
