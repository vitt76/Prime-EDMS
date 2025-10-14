import logging

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import RedirectView, View
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from stronghold.decorators import public

from mayan.apps.documents.models import DocumentFile
from mayan.apps.documents.permissions import permission_document_file_view
from mayan.apps.views.generics import SingleObjectDetailView
from mayan.apps.views.mixins import ExternalObjectViewMixin

# REST Framework imports
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from mayan.apps.rest_api import generics

logger = logging.getLogger(name=__name__)


class MediaConversionView(SingleObjectDetailView):
    """
    View for media conversion of document files.
    """
    model = DocumentFile
    pk_url_kwarg = 'document_file_id'
    template_name = 'converter_pipeline_extension/media_conversion.html'
    fields = []  # Empty fields list to satisfy ModelFormMixin

    def get_extra_context(self):
        context = super().get_extra_context()

        # Определяем поддерживаемые форматы
        mime_type = self.object.mimetype
        filename = self.object.filename or ''

        # Отладка MIME типа для .dng файлов
        if filename.lower().endswith('.dng'):
            mime_type = 'image/x-adobe-dng'  # Исправляем MIME тип для DNG

        supported_formats = self._get_supported_formats(mime_type)

        context.update({
            'title': _('Сконвертировать: %s') % self.object,
            'mime_type': mime_type,
            'supported_formats': supported_formats,
            'can_convert': len(supported_formats) > 0,
        })

        return context

    def _get_supported_formats(self, mime_type):
        """Получить список поддерживаемых выходных форматов для конвертации"""
        # Определяем поддерживаемые выходные форматы на основе типа входного файла

        # Для изображений (включая RAW)
        if mime_type.startswith('image/'):
            return [
                ('jpeg', 'JPEG'),
                ('png', 'PNG'),
                ('tiff', 'TIFF'),
                ('pdf', 'PDF'),
            ]

        # Для видео файлов (расширенная поддержка MIME типов)
        elif (mime_type.startswith('video/') or
              mime_type in ['application/mp4', 'application/x-mp4']):
            return [
                ('jpeg', 'JPEG (Превью)'),
                ('png', 'PNG (Превью)'),
                ('tiff', 'TIFF (Превью)'),
                ('pdf', 'PDF (Превью)'),
            ]

        # Для документов
        elif mime_type in ['application/pdf', 'application/msword',
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            return [
                ('pdf', 'PDF'),
                ('jpeg', 'JPEG'),
                ('png', 'PNG'),
            ]


        # Для аудио файлов
        elif mime_type.startswith('audio/'):
            return [
                ('jpeg', 'JPEG (Визуализация)'),
                ('png', 'PNG (Визуализация)'),
            ]

        # Для неизвестных форматов возвращаем пустой список
        return []

    def _generate_converted_filename(self, original_filename, output_format):
        """
        Генерирует имя файла для конвертированного файла.
        """
        import os

        if not original_filename:
            return f'converted.{output_format}'

        # Разделяем имя файла и расширение
        name_part, ext = os.path.splitext(original_filename)

        # Создаем новое имя с указанным расширением
        if output_format.lower() == 'jpeg':
            new_ext = '.jpg'
        elif output_format.lower() == 'tiff':
            new_ext = '.tif'
        else:
            new_ext = f'.{output_format.lower()}'

        return f'{name_part}_converted{new_ext}'

    def _convert_image_to_pdf(self, image):
        """Конвертирует изображение в PDF"""
        from io import BytesIO
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from PIL import Image
        import tempfile
        import os

        try:
            # Создаем PDF буфер
            pdf_buffer = BytesIO()

            # Создаем PDF документ
            c = canvas.Canvas(pdf_buffer, pagesize=letter)
            width, height = letter

            # Конвертируем изображение в RGB если нужно
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Масштабируем изображение чтобы поместилось на страницу
            img_width, img_height = image.size
            aspect_ratio = img_width / img_height

            if img_width > width * 0.8:
                img_width = width * 0.8
                img_height = img_width / aspect_ratio

            if img_height > height * 0.8:
                img_height = height * 0.8
                img_width = img_height * aspect_ratio

            # Сохраняем изображение во временный файл (reportlab лучше работает с файлами)
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_image_path = temp_file.name
                image.save(temp_file, format='JPEG', quality=85)

            try:
                # Добавляем изображение на PDF страницу
                c.drawImage(temp_image_path, (width - img_width) / 2, (height - img_height) / 2, img_width, img_height)

                # Сохраняем PDF
                c.save()
                pdf_buffer.seek(0)

                return pdf_buffer
            finally:
                # Удаляем временный файл
                try:
                    os.unlink(temp_image_path)
                except:
                    pass

        except Exception as e:
            logger.error(f'PDF conversion failed: {e}')
            return None

    def post(self, request, *args, **kwargs):
        """Обработка POST запроса на конвертацию"""
        self.object = self.get_object()

        # Получаем выбранный выходной формат
        output_format = request.POST.get('output_format', 'pdf')

        # Определяем правильный MIME тип
        mime_type = self.object.mimetype
        filename = self.object.filename or ''
        if filename.lower().endswith('.dng'):
            mime_type = 'image/x-adobe-dng'

        try:
            # Импортируем необходимые модели
            from mayan.apps.documents.models import DocumentVersion

            # Создаем новую версию документа с комментарием о конвертации
            comment = _('Media conversion from %(input_format)s to %(output_format)s') % {
                'input_format': mime_type,
                'output_format': output_format.upper()
            }

            # Создаем конвертированный файл
            converted_file = self._convert_file(self.object, output_format)

            if converted_file:
                # Используем метод file_new документа для создания нового файла
                from django.core.files.base import ContentFile

                # Создаем новый файл в документе
                new_filename = self._generate_converted_filename(self.object.filename, output_format)

                # Создаем file-like объект из конвертированных данных
                file_content = ContentFile(converted_file.getvalue(), name=new_filename)

                # Используем file_new метод документа
                from mayan.apps.documents.document_file_actions import DocumentFileActionUseNewPages

                new_document_file = self.object.document.file_new(
                    file_object=file_content,
                    action=DocumentFileActionUseNewPages.backend_id,  # Используем правильный backend_id
                    comment=comment,
                    filename=new_filename,
                    _user=request.user
                )
                # file_new уже выполнил нужные действия по созданию версии
            else:
                # Fallback: создаем версию с оригинальным файлом
                if not self.object.document.version_active:
                    document_version = DocumentVersion(
                        document=self.object.document,
                        comment=comment + _(' (conversion failed, using original file)')
                    )
                    document_version._event_actor = request.user
                    document_version.save()

                    document_version.pages_remap(
                        annotated_content_object_list=DocumentVersion.annotate_content_object_list(
                            content_object_list=self.object.pages.all()
                        ),
                        _user=request.user
                    )
                else:
                    from mayan.apps.documents.document_file_actions import DocumentFileActionAppendNewPages
                    DocumentFileActionAppendNewPages.execute(
                        document=self.object.document,
                        document_file=self.object,
                        comment=comment + _(' (conversion failed, using original file)'),
                        _user=request.user
                    )

            messages.success(
                request,
                _('Media conversion to %(format)s completed. New version created for document: %(document)s') % {
                    'format': output_format.upper(),
                    'document': self.object.document
                }
            )

            logger.info(f'Media conversion to {output_format} completed for file: {self.object}')

            # Перенаправляем на страницу версий документа
            return redirect(
                reverse(
                    'documents:document_version_list',
                    kwargs={'document_id': self.object.document.pk}
                )
            )

        except Exception as e:
            messages.error(
                request,
                _('Media conversion failed: %s') % str(e)
            )
            logger.error(f'Media conversion failed for file {self.object}: {e}')

            # Возвращаемся к странице конвертации
            return self.get(request, *args, **kwargs)

    def _convert_file(self, document_file, output_format):
        """
        Конвертирует файл в указанный формат.
        Возвращает BytesIO с конвертированным файлом или None при ошибке.
        """
        from io import BytesIO
        from PIL import Image
        import os

        try:
            # Читаем исходный файл
            with document_file.file.open() as f:
                file_content = f.read()

            input_buffer = BytesIO(file_content)

            # Определяем тип файла по MIME типу
            mime_type = document_file.mimetype
            filename = document_file.filename or ''

            # Конвертация изображений
            if mime_type.startswith('image/'):
                try:
                    # Открываем изображение
                    if mime_type in ['image/x-adobe-dng', 'image/x-canon-cr2', 'image/x-nikon-nef', 'image/x-sony-arw']:
                        # Для RAW файлов пытаемся использовать PIL (может не сработать для всех)
                        try:
                            image = Image.open(input_buffer)
                        except Exception:
                            # Если не можем открыть RAW, возвращаем None (нужны специальные инструменты)
                            return None
                    else:
                        image = Image.open(input_buffer)

                    # Конвертируем в RGB если нужно
                    if image.mode not in ('RGB', 'L'):
                        image = image.convert('RGB')

                    # Создаем выходной буфер
                    output_buffer = BytesIO()

                    # Сохраняем в выбранном формате
                    if output_format == 'jpeg':
                        image.save(output_buffer, format='JPEG', quality=85)
                    elif output_format == 'png':
                        image.save(output_buffer, format='PNG')
                    elif output_format == 'tiff':
                        image.save(output_buffer, format='TIFF')
                    elif output_format == 'pdf':
                        # Конвертируем изображение в PDF
                        output_buffer = self._convert_image_to_pdf(image)
                    else:
                        # По умолчанию JPEG
                        image.save(output_buffer, format='JPEG', quality=85)

                    output_buffer.seek(0)
                    return output_buffer

                except Exception as e:
                    logger.error(f'Image conversion failed: {e}')
                    return None

            # Конвертация видео файлов (извлекаем превью)
            elif (mime_type.startswith('video/') or
                  mime_type in ['application/mp4', 'application/x-mp4']):
                try:
                    logger.info(f'Converting video file: {filename}, size: {len(input_buffer.getvalue())} bytes')

                    # Сохраняем видео во временный файл
                    import tempfile
                    import subprocess
                    import os

                    # Определяем расширение файла
                    file_ext = os.path.splitext(filename)[1].lower() or '.mp4'  # по умолчанию .mp4

                    with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as temp_video:
                        temp_video.write(input_buffer.getvalue())
                        temp_video_path = temp_video.name

                    logger.info(f'Video saved to temporary file: {temp_video_path}')

                    try:
                        # Сначала проверим, может ли FFmpeg прочитать файл
                        probe_cmd = [
                            'ffprobe',
                            '-v', 'quiet',
                            '-print_format', 'json',
                            '-show_format',
                            '-show_streams',
                            temp_video_path
                        ]

                        logger.info(f'Probing video with ffprobe: {" ".join(probe_cmd)}')
                        probe_result = subprocess.run(
                            probe_cmd,
                            capture_output=True,
                            text=True,
                            timeout=10
                        )

                        if probe_result.returncode != 0:
                            logger.error(f'FFprobe failed: {probe_result.stderr}')
                            return None

                        logger.info('FFprobe successful, video is readable')

                        # Используем FFmpeg для извлечения первого кадра
                        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_image:
                            temp_image_path = temp_image.name

                        # Улучшенная команда FFmpeg с дополнительными опциями
                        cmd = [
                            'ffmpeg',
                            '-y',                    # перезаписывать выходные файлы без вопроса
                            '-i', temp_video_path,  # входной файл
                            '-ss', '0.5',          # начать с 0.5 секунды (пропустить возможные черные кадры)
                            '-vframes', '1',       # извлечь только первый кадр
                            '-q:v', '2',           # качество (2 = высокое)
                            '-vf', 'scale=800:-1', # масштабировать до ширины 800px, сохраняя пропорции
                            '-f', 'image2',        # формат вывода
                            temp_image_path        # выходной файл
                        ]

                        logger.info(f'Running FFmpeg command: {" ".join(cmd)}')

                        # Запускаем FFmpeg с увеличенным таймаутом
                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            timeout=60  # увеличенный таймаут до 60 секунд
                        )

                        if result.returncode != 0:
                            logger.error(f'FFmpeg failed with return code {result.returncode}')
                            logger.error(f'FFmpeg stderr: {result.stderr}')
                            logger.error(f'FFmpeg stdout: {result.stdout}')
                            return None

                        # Проверяем, создался ли файл
                        if not os.path.exists(temp_image_path) or os.path.getsize(temp_image_path) == 0:
                            logger.error(f'FFmpeg output file not created or empty: {temp_image_path}')
                            return None

                        logger.info(f'FFmpeg successfully created image: {temp_image_path}, size: {os.path.getsize(temp_image_path)} bytes')

                        # Читаем извлеченное изображение
                        with open(temp_image_path, 'rb') as f:
                            image_data = f.read()

                        # Конвертируем в выбранный формат
                        image_buffer = BytesIO(image_data)
                        image = Image.open(image_buffer)

                        # Конвертируем в RGB если нужно
                        if image.mode not in ('RGB', 'L'):
                            image = image.convert('RGB')

                        logger.info(f'Image loaded successfully, size: {image.size}, mode: {image.mode}')

                        # Создаем выходной буфер
                        output_buffer = BytesIO()

                        # Сохраняем в выбранном формате
                        if output_format == 'jpeg':
                            image.save(output_buffer, format='JPEG', quality=85)
                        elif output_format == 'png':
                            image.save(output_buffer, format='PNG')
                        elif output_format == 'tiff':
                            image.save(output_buffer, format='TIFF')
                        elif output_format == 'pdf':
                            # Конвертируем изображение в PDF
                            output_buffer = self._convert_image_to_pdf(image)
                        else:
                            # По умолчанию JPEG
                            image.save(output_buffer, format='JPEG', quality=85)

                        output_buffer.seek(0)
                        logger.info(f'Video conversion completed, output size: {len(output_buffer.getvalue())} bytes')
                        return output_buffer

                    finally:
                        # Удаляем временные файлы
                        try:
                            os.unlink(temp_video_path)
                            if 'temp_image_path' in locals():
                                os.unlink(temp_image_path)
                        except Exception as cleanup_error:
                            logger.warning(f'Failed to cleanup temporary files: {cleanup_error}')

                except subprocess.TimeoutExpired as e:
                    logger.error(f'FFmpeg command timed out after {e.timeout} seconds: {e}')
                    return None
                except Exception as e:
                    logger.error(f'Video conversion failed: {e}')
                    import traceback
                    logger.error(f'Traceback: {traceback.format_exc()}')
                    return None


            # For other file types, return None for now
            return None

        except Exception as e:
            logger.error(f'File conversion failed: {e}')
            return None


class DocumentFileConversionAPIView(generics.RetrieveAPIView):
    """
    API endpoint for converting document files.
    """
    queryset = DocumentFile.objects.all()

    def retrieve(self, request, *args, **kwargs):
        document_file = self.get_object()
        # Здесь будет логика конвертации
        return Response({"message": f"Convert document file {document_file.pk}"})


@public
class DocumentFileConvertRedirectView(View):
    """
    View that redirects to the media conversion page.
    Works with Mayan EDMS hash-based routing.
    """
    # public = True  # Mark as public view - now using decorator

    def get(self, request, *args, **kwargs):
        # Сначала проверяем, есть ли document_file_id в URL параметрах
        document_file_id = kwargs.get('document_file_id')

        if document_file_id:
            # Если есть ID файла в URL, формируем правильный URL (hash-based для Vue.js)
            redirect_url = f"#/converter-pipeline/media-conversion/{document_file_id}/"
        else:
            # Иначе используем старый способ с GET параметром return
            return_url = request.GET.get('return', '')

            if not return_url:
                # Если нет return URL, перенаправляем на home
                redirect_url = "/documents/"
            else:
                # Извлекаем file ID из return URL
                file_id = self._extract_file_id_from_url(return_url)

                if file_id:
                    # Перенаправляем на страницу конвертации (hash-based для Vue.js)
                    redirect_url = f"#/converter-pipeline/media-conversion/{file_id}/"
                else:
                    # Если не удалось извлечь file ID, перенаправляем на документы
                    redirect_url = "/documents/"

        # Используем Django redirect, который Mayan EDMS преобразует в hash-based URL
        return redirect(redirect_url)

    def _extract_file_id_from_url(self, url):
        """
        Извлекает file ID из URL.
        Поддерживает различные форматы URL Mayan EDMS.
        """
        import re

        # Паттерны для поиска file ID в URL
        patterns = [
            r'/documents/\d+/files/(\d+)/',  # /documents/1/files/123/
            r'/files/(\d+)/',                # /files/123/
            r'document_file_id=(\d+)',       # параметр document_file_id=123
            r'file_id=(\d+)',                # параметр file_id=123
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None
