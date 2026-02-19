import logging
import os
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile

from PIL import Image, ImageEnhance, ImageOps, ImageDraw, ImageFont

from mayan.celery import app
from mayan.apps.documents.models import DocumentFile
from mayan.apps.converter_pipeline_extension.backends import RawImageConverter
from mayan.apps.converter_pipeline_extension.utils import (
    get_converter_for_mime_type, get_converter_class_for_info
)

logger = logging.getLogger(name=__name__)


@app.task(bind=True, ignore_result=True, queue='converter')
def generate_rendition_task(self, generated_rendition_id):
    logger.debug('generate_rendition_task queued with id %s', generated_rendition_id)
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

        # Org-level watermark (Sprint 3.3)
        org_watermark = {}
        try:
            pub = publication_item.publication
            if getattr(pub, 'organization_id', None):
                from mayan.apps.organizations.models import OrganizationWatermarkSettings
                ws = OrganizationWatermarkSettings.objects.filter(
                    organization_id=pub.organization_id
                ).first()
                if ws:
                    org_watermark = ws.to_watermark_dict()
        except Exception as e:
            logger.debug('Org watermark not applied: %s', e)

        # Генерируем файл с помощью converter_pipeline_extension
        converted_file = _convert_file_with_preset(document_file, preset, org_watermark=org_watermark)

        if converted_file:
            # Сохраняем файл через Django FileField
            filename = _generate_rendition_filename(document_file, preset)
            file_content = ContentFile(converted_file.getvalue(), name=filename)

            rendition.status = 'completed'
            rendition.file.save(filename, file_content, save=False)
            rendition.file_size = len(converted_file.getvalue())
            rendition.checksum = _calculate_checksum(converted_file)
            rendition.error_message = ''
            rendition.save(update_fields=['status', 'file', 'file_size', 'checksum', 'error_message', 'modified'])

            logger.info(f"Successfully generated rendition: {rendition}")
        else:
            rendition.status = 'failed'
            rendition.error_message = 'Failed to convert file'
            rendition.save(update_fields=['status', 'error_message', 'modified'])
            logger.error(f"Failed to generate rendition: {rendition}")

    except Exception as e:
        logger.exception(f"Error generating rendition {generated_rendition_id}: {e}")
        try:
            rendition = GeneratedRendition.objects.get(id=generated_rendition_id)
            rendition.status = 'failed'
            rendition.error_message = str(e)
            rendition.save(update_fields=['status', 'error_message', 'modified'])
        except Exception:
            pass


def _convert_file_with_preset(document_file, preset, org_watermark=None):
    """
    Конвертирует файл с использованием заданного пресета.
    org_watermark: optional dict from OrganizationWatermarkSettings.to_watermark_dict().
    Возвращает BytesIO с конвертированным файлом или None при ошибке.
    """
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

        if not mime_type:
            logger.warning('DocumentFile %s has no mimetype; skipping conversion.', document_file.pk)
            return None

        converter_info = get_converter_for_mime_type(mime_type)
        if converter_info:
            converter_class = get_converter_class_for_info(converter_info['converter'])
            if converter_class:
                target_format = (preset.format or 'jpeg').lower()
                try:
                    storage_file = document_file.file
                    with storage_file.storage.open(name=storage_file.name, mode='rb') as source_stream:
                        converter = converter_class(file_stream=source_stream, mime_type=mime_type)

                    filters_value = preset.filters or []
                    if isinstance(filters_value, str):
                        filters_value = [filters_value]

                    convert_kwargs = {
                        'width': preset.width,
                        'height': preset.height,
                        'format': target_format,
                        'quality': preset.quality or 85,
                        'crop': bool(preset.crop and preset.width and preset.height),
                        'dpi': (preset.dpi_x, preset.dpi_y) if preset.dpi_x and preset.dpi_y else None,
                        'filters': filters_value or None,
                        'brightness': preset.adjust_brightness,
                        'contrast': preset.adjust_contrast,
                        'color': preset.adjust_color,
                        'sharpness': preset.adjust_sharpness,
                        'watermark': preset.watermark or None,
                    }

                    if hasattr(converter, 'convert'):
                        output_buffer = converter.convert(**convert_kwargs)
                        if isinstance(output_buffer, ContentFile):
                            buffer = BytesIO(output_buffer.read())
                        elif isinstance(output_buffer, BytesIO):
                            buffer = output_buffer
                        else:
                            buffer = BytesIO(output_buffer)
                        buffer.seek(0)
                        return buffer
                    else:
                        preview = converter.convert_to_preview(
                            format=target_format.upper(),
                            quality=preset.quality or 85,
                            max_size=(preset.width or 1920, preset.height or 1080)
                        )
                        buffer = BytesIO(preview.read())
                        buffer.seek(0)
                        return buffer
                except Exception as exc:
                    logger.warning('Preset converter failed for document_file %s: %s', document_file.pk, exc)

        # Конвертация изображений
        if mime_type.startswith('image/'):
            try:
                # Открываем изображение
                if mime_type in ['image/x-adobe-dng', 'image/x-canon-cr2', 'image/x-nikon-nef', 'image/x-sony-arw']:
                    try:
                        image = Image.open(input_buffer)
                    except Exception:
                        # Попробовать конвертировать через RawImageConverter
                        try:
                            converter = RawImageConverter(file_object=document_file.file)
                            preview = converter.convert_to_preview(format=preset.format.upper())
                            if preview:
                                return BytesIO(preview.read())
                        except Exception as raw_error:
                            logger.error('Raw conversion failed for %s: %s', document_file.pk, raw_error)
                        return None
                else:
                    image = Image.open(input_buffer)

                # Коррекция режима под целевой формат
                if preset.format == 'jpeg' and image.mode not in ('RGB', 'L'):
                    image = image.convert('RGB')

                # Масштабирование / обрезка
                if preset.crop and preset.width and preset.height:
                    image = ImageOps.fit(
                        image,
                        (int(preset.width), int(preset.height)),
                        method=Image.LANCZOS,
                        centering=(0.5, 0.5)
                    )
                elif preset.width or preset.height:
                    target_width = preset.width or image.width
                    target_height = preset.height or image.height
                    image.thumbnail((int(target_width), int(target_height)), Image.LANCZOS)

                # Тоновые корректировки
                if preset.adjust_brightness is not None and preset.adjust_brightness != 1.0:
                    image = ImageEnhance.Brightness(image).enhance(float(preset.adjust_brightness))

                if preset.adjust_contrast is not None and preset.adjust_contrast != 1.0:
                    image = ImageEnhance.Contrast(image).enhance(float(preset.adjust_contrast))

                if preset.adjust_color is not None and preset.adjust_color != 1.0:
                    image = ImageEnhance.Color(image).enhance(float(preset.adjust_color))

                if preset.adjust_sharpness is not None and preset.adjust_sharpness != 1.0:
                    image = ImageEnhance.Sharpness(image).enhance(float(preset.adjust_sharpness))

                # Фильтры
                if preset.filters and image.mode in ('RGB', 'RGBA', 'L'):
                    for filter_name in preset.filters:
                        image = _apply_image_filter(image=image, filter_name=filter_name)

                # Водяной знак (пресет)
                if preset.watermark and image.mode in ('RGB', 'RGBA'):
                    image = _apply_watermark(image=image, watermark=preset.watermark)
                # Водяной знак организации (Sprint 3.3)
                if org_watermark and image.mode in ('RGB', 'RGBA'):
                    image = _apply_watermark(image=image, watermark=org_watermark)

                # Создаем выходной буфер
                output_buffer = BytesIO()

                target_format = (preset.format or 'jpeg').upper()
                save_kwargs = {}
                if preset.dpi_x and preset.dpi_y:
                    save_kwargs['dpi'] = (int(preset.dpi_x), int(preset.dpi_y))

                if target_format == 'JPEG':
                    save_kwargs['quality'] = int(preset.quality or 85)
                    save_kwargs['optimize'] = True
                elif target_format == 'PNG':
                    save_kwargs['optimize'] = True
                elif target_format == 'TIFF':
                    pass
                else:
                    logger.warning('Unsupported target format for fallback conversion: %s', preset.format)
                    return None

                image.save(output_buffer, format=target_format, **save_kwargs)

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
    checksum = hashlib.md5(file_buffer.read()).hexdigest()
    file_buffer.seek(0)
    return checksum


def _apply_image_filter(*, image, filter_name):
    filter_name = (filter_name or '').lower()

    if filter_name == 'grayscale':
        return ImageOps.grayscale(image)
    if filter_name == 'invert':
        return ImageOps.invert(image)
    if filter_name == 'autocontrast':
        return ImageOps.autocontrast(image)
    if filter_name == 'equalize':
        return ImageOps.equalize(image)
    if filter_name == 'posterize':
        return ImageOps.posterize(image, bits=4)
    if filter_name == 'solarize':
        return ImageOps.solarize(image)

    logger.warning('Unsupported image filter requested: %s', filter_name)
    return image


def _apply_watermark(*, image, watermark):
    if not isinstance(watermark, dict):
        return image

    text = watermark.get('text')
    if not text:
        return image

    position = watermark.get('position', (10, 10))
    font_size = watermark.get('font_size', 24)
    font_color = watermark.get('font_color', (255, 255, 255, 128))

    drawable = image.convert('RGBA') if image.mode != 'RGBA' else image.copy()
    overlay = Image.new('RGBA', drawable.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    try:
        font_path = watermark.get('font_path')
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.truetype('arial.ttf', font_size)
    except Exception:
        font = ImageFont.load_default()

    draw.text(position, text, font=font, fill=font_color)
    combined = Image.alpha_composite(drawable, overlay)
    return combined.convert(image.mode) if image.mode != 'RGBA' else combined


@app.task(bind=True, ignore_result=True, queue='documents')
def apply_watermark_task(document_file_id, organization_id, **kwargs):
    """
    Sprint 5.1: Generate WatermarkedRendition for a document file using organization watermark settings.
    Uses shared watermark logic from headless_api.watermark_utils (same as image editor).
    """
    from mayan.apps.organizations.models import Organization
    from mayan.apps.headless_api.watermark_utils import (
        apply_watermark,
        organization_watermark_to_editor_state,
        load_image_from_document_file,
    )
    from .models import WatermarkedRendition

    try:
        document_file = DocumentFile.objects.filter(pk=document_file_id).select_related('document').first()
        if not document_file:
            logger.warning('apply_watermark_task: document_file_id=%s not found', document_file_id)
            return
        organization = Organization.objects.filter(pk=organization_id).first()
        if not organization:
            logger.warning('apply_watermark_task: organization_id=%s not found', organization_id)
            return
        from mayan.apps.organizations.models import OrganizationWatermarkSettings
        ws = OrganizationWatermarkSettings.objects.filter(organization=organization).first()
        if not ws or not ws.enabled or not (ws.text or '').strip():
            logger.debug('apply_watermark_task: no watermark settings or disabled for org %s', organization_id)
            rendition, _ = WatermarkedRendition.objects.get_or_create(
                document_file_id=document_file_id,
                organization_id=organization_id,
                defaults={'status': 'failed', 'error_message': 'Watermark not enabled or no text'}
            )
            rendition.status = 'failed'
            rendition.error_message = 'Watermark not enabled or no text'
            rendition.save(update_fields=['status', 'error_message', 'modified'])
            return

        rendition, created = WatermarkedRendition.objects.get_or_create(
            document_file_id=document_file_id,
            organization_id=organization_id,
            defaults={'status': 'pending'}
        )
        rendition.status = 'processing'
        rendition.save(update_fields=['status', 'modified'])

        state = {'watermark': organization_watermark_to_editor_state(ws)}
        image = load_image_from_document_file(document_file)
        image = apply_watermark(image, state)
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        buffer = BytesIO()
        image.save(buffer, format='JPEG', quality=85, optimize=True)
        buffer.seek(0)
        filename = 'watermarked_df_{}_org_{}.jpg'.format(document_file_id, organization_id)
        rendition.file.save(filename, ContentFile(buffer.getvalue()), save=False)
        rendition.status = 'completed'
        rendition.error_message = ''
        rendition.save(update_fields=['status', 'file', 'error_message', 'modified'])
        logger.info('apply_watermark_task: completed for document_file_id=%s org_id=%s', document_file_id, organization_id)
    except Exception as exc:
        logger.exception('apply_watermark_task failed: document_file_id=%s org_id=%s: %s', document_file_id, organization_id, exc)
        try:
            rendition = WatermarkedRendition.objects.get(
                document_file_id=document_file_id,
                organization_id=organization_id
            )
            rendition.status = 'failed'
            rendition.error_message = str(exc)[:500]
            rendition.save(update_fields=['status', 'error_message', 'modified'])
        except Exception:
            pass
