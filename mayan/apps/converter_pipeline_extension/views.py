import logging

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import RedirectView
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

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
                # Создаем новый DocumentFile с конвертированным файлом
                from mayan.apps.documents.models import DocumentFile
                from django.core.files.base import ContentFile

                # Создаем новый файл в документе
                new_document_file = DocumentFile(
                    document=self.object.document,
                    filename=self._generate_converted_filename(self.object.filename, output_format)
                )

                # Сохраняем конвертированный файл
                file_content = ContentFile(converted_file.getvalue(), name=new_document_file.filename)
                new_document_file.file.save(new_document_file.filename, file_content, save=False)
                new_document_file.save()

                # Создаем версию с новым файлом
                if not self.object.document.version_active:
                    # Если нет активной версии, создаем первую версию
                    document_version = DocumentVersion(
                        document=self.object.document,
                        comment=comment
                    )
                    document_version._event_actor = request.user
                    document_version.save()

                    # Добавляем страницы из нового файла
                    document_version.pages_remap(
                        annotated_content_object_list=DocumentVersion.annotate_content_object_list(
                            content_object_list=new_document_file.pages.all()
                        ),
                        _user=request.user
                    )
                else:
                    # Используем новый файл для создания версии
                    from mayan.apps.documents.document_file_actions import DocumentFileActionAppendNewPages
                    DocumentFileActionAppendNewPages.execute(
                        document=self.object.document,
                        document_file=new_document_file,
                        comment=comment,
                        _user=request.user
                    )
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


class DocumentFileConvertRedirectView(RedirectView):
    """
    View that analyzes the return URL and redirects to the appropriate media conversion page.
    """

    def get_redirect_url(self, *args, **kwargs):
        return_url = self.request.GET.get('return', '')

        if not return_url:
            # Если нет return URL, показываем ошибку
            from django.contrib import messages
            messages.error(self.request, _('Не удалось определить файл для конвертации.'))
            return '/'

        # Извлекаем file ID из return URL
        file_id = self._extract_file_id_from_url(return_url)

        if file_id:
            # Перенаправляем на страницу конвертации
            return f"/converter-pipeline/media-conversion/{file_id}/"
                    else:
            # Если не удалось извлечь file ID, показываем ошибку
            from django.contrib import messages
            messages.error(self.request, _('Не удалось определить файл для конвертации.'))
            return return_url

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
