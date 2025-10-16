import logging
import os
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile

from mayan.celery import app
from mayan.apps.documents.models import DocumentFile

logger = logging.getLogger(name=__name__)


@app.task(bind=True, ignore_result=True)
def generate_rendition_task(self, generated_rendition_id):
    """
    Celery задача для генерации rendition'а.
    """
    from .models import GeneratedRendition, RenditionPreset

    try:
        rendition = GeneratedRendition.objects.get(id=generated_rendition_id)
        rendition.status = 'processing'
        rendition.save(update_fields=['status'])

        logger.info(f"Starting rendition generation for {rendition}")

        # Получаем данные для конвертации
        publication_item = rendition.publication_item
        preset = rendition.preset
        document_file = publication_item.document_file

        # Генерируем файл с помощью converter_pipeline_extension
        converted_file = _convert_file_with_preset(document_file, preset)

        if converted_file:
            # Сохраняем файл через Django FileField
            filename = _generate_rendition_filename(document_file, preset)
            file_content = ContentFile(converted_file.getvalue(), name=filename)

            # Обновляем модель
            rendition.status = 'completed'
            rendition.file = file_content
            rendition.file_size = converted_file.tell()
            rendition.checksum = _calculate_checksum(converted_file)
            rendition.save()

            logger.info(f"Successfully generated rendition: {rendition}")
        else:
            rendition.status = 'failed'
            rendition.error_message = 'Failed to convert file'
            rendition.save()
            logger.error(f"Failed to generate rendition: {rendition}")

    except Exception as e:
        logger.exception(f"Error generating rendition {generated_rendition_id}: {e}")
        try:
            rendition = GeneratedRendition.objects.get(id=generated_rendition_id)
            rendition.status = 'failed'
            rendition.error_message = str(e)
            rendition.save()
        except Exception:
            pass


def _convert_file_with_preset(document_file, preset):
    """
    Конвертирует файл с использованием заданного пресета.
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

        # Исправляем MIME тип для DNG файлов
        if filename.lower().endswith('.dng'):
            mime_type = 'image/x-adobe-dng'

        # Конвертация изображений
        if mime_type.startswith('image/'):
            try:
                # Открываем изображение
                if mime_type in ['image/x-adobe-dng', 'image/x-canon-cr2', 'image/x-nikon-nef', 'image/x-sony-arw']:
                    try:
                        image = Image.open(input_buffer)
                    except Exception:
                        return None
                else:
                    image = Image.open(input_buffer)

                # Конвертируем в RGB если нужно
                if image.mode not in ('RGB', 'L'):
                    image = image.convert('RGB')

                # Применяем размеры если указаны
                if preset.width or preset.height:
                    image.thumbnail((preset.width or image.width, preset.height or image.height), Image.ANTIALIAS)

                # Создаем выходной буфер
                output_buffer = BytesIO()

                # Сохраняем в выбранном формате
                if preset.format == 'jpeg':
                    quality = preset.quality or 85
                    image.save(output_buffer, format='JPEG', quality=quality)
                elif preset.format == 'png':
                    image.save(output_buffer, format='PNG')
                elif preset.format == 'tiff':
                    image.save(output_buffer, format='TIFF')
                else:
                    # Неизвестный формат
                    return None

                output_buffer.seek(0)
                return output_buffer

            except Exception as e:
                logger.error(f"Error converting image: {e}")
                return None

        # Для видео и документов пока возвращаем None (нужна дополнительная интеграция)
        else:
            logger.warning(f"Unsupported file type for conversion: {mime_type}")
            return None

    except Exception as e:
        logger.error(f"Error in file conversion: {e}")
        return None


def _generate_rendition_filename(document_file, preset):
    """
    Генерирует имя файла для rendition'а.
    """
    base_name = os.path.splitext(document_file.filename or 'file')[0]
    return f"{base_name}_{preset.id}.{preset.format}"




def _calculate_checksum(file_buffer):
    """
    Вычисляет checksum файла.
    """
    import hashlib

    file_buffer.seek(0)
    return hashlib.md5(file_buffer.read()).hexdigest()
