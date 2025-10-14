import logging

from django.apps import apps
from django.core.files.base import ContentFile

from mayan.celery import app

from .backends import RawImageConverter, VideoConverter
from .utils import get_converter_for_mime_type

logger = logging.getLogger(name=__name__)


@app.task(bind=True, max_retries=3, retry_backoff=True)
def task_convert_document_media(self, document_id, force=False):
    """
    Асинхронная конвертация медиа файла документа.

    Args:
        document_id (int): ID документа
        force (bool): Принудительно переконвертировать даже если уже есть preview
    """
    Document = apps.get_model('documents', 'Document')

    try:
        document = Document.objects.get(pk=document_id)
    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found")
        return

    # Проверить поддерживается ли формат
    from .utils import is_media_format_supported
    if not is_media_format_supported(document.file.mime_type):
        logger.info(f"Format {document.file.mime_type} not supported for document {document_id}")
        return

    # Проверить нужно ли конвертировать
    if not force and document.conversion_metadata.filter(
        conversion_status__in=['completed', 'processing']
    ).exists():
        logger.info(f"Document {document_id} already processed or processing")
        return

    # Создать/обновить метаданные конвертации
    metadata = document.get_conversion_metadata()
    metadata.mark_as_processing('converter_pipeline_extension')

    try:
        # Получить подходящий конвертер
        converter_class = get_converter_class_for_mime_type(document.file.mime_type)
        if not converter_class:
            raise ValueError(f"No converter found for {document.file.mime_type}")

        # Создать конвертер и выполнить конвертацию
        with converter_class(document.file.file) as converter:
            # Получить количество страниц/кадров
            total_pages = converter.get_page_count()

            for page_num in range(total_pages):
                try:
                    # Конвертировать страницу
                    preview_image = converter.get_page(page_number=page_num)

                    # Сохранить превью
                    save_preview_to_document(
                        document,
                        preview_image,
                        f'page_{page_num}',
                        converter_class.__name__
                    )

                    logger.info(f'Generated preview for document {document_id}, page {page_num + 1}')

                except Exception as page_e:
                    logger.error(f'Failed to generate preview for document {document_id}, page {page_num + 1}: {page_e}')
                    continue

        # Отметить как завершенное
        metadata.mark_as_completed()

    except Exception as e:
        metadata.mark_as_failed()
        logger.error(f'Document media conversion failed for {document_id}: {e}')
        raise


@app.task(bind=True, max_retries=3, retry_backoff=True)
def task_generate_video_preview(self, document_file_id):
    """
    Генерирует превью (первый кадр) для видео файла.

    Args:
        document_file_id (int): ID файла документа
    """
    DocumentFile = apps.get_model('documents', 'DocumentFile')

    try:
        document_file = DocumentFile.objects.get(pk=document_file_id)
    except DocumentFile.DoesNotExist:
        logger.error(f"DocumentFile {document_file_id} not found")
        return

    # Проверить что это видео файл
    if not document_file.mimetype or not document_file.mimetype.startswith('video/'):
        logger.warning(f"DocumentFile {document_file_id} is not a video file")
        return

    logger.info(f"Generating video preview for file {document_file_id}: {document_file.filename}")

    try:
        # Извлечь превью из видео
        preview_image = _extract_video_preview(document_file)

        if preview_image:
            # Сохранить превью в системе кеширования Mayan
            _save_video_preview_to_cache(document_file.document, preview_image, 'video_preview')

            logger.info(f"Successfully generated video preview for file {document_file_id}")
        else:
            logger.error(f"Failed to extract video preview for file {document_file_id}")

    except Exception as e:
        logger.error(f"Failed to generate video preview for file {document_file_id}: {e}")


def _extract_video_preview(document_file):
    """
    Извлекает первый кадр из видео файла.

    Args:
        document_file: объект DocumentFile

    Returns:
        BytesIO: изображение превью или None при ошибке
    """
    import tempfile
    import subprocess
    import os
    from io import BytesIO

    with document_file.file.open() as video_file:
        video_data = video_file.read()

    # Сохранить видео во временный файл
    file_ext = os.path.splitext(document_file.filename or '')[1].lower() or '.mp4'

    with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as temp_video:
        temp_video.write(video_data)
        temp_video_path = temp_video.name

    try:
        # Проверить видео с ffprobe
        probe_cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            temp_video_path
        ]

        probe_result = subprocess.run(
            probe_cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        if probe_result.returncode != 0:
            logger.error(f'FFprobe failed for {document_file.pk}: {probe_result.stderr}')
            return None

        # Извлечь первый кадр
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_image:
            temp_image_path = temp_image.name

        cmd = [
            'ffmpeg',
            '-y',
            '-i', temp_video_path,
            '-ss', '0.5',          # начать с 0.5 секунды
            '-vframes', '1',       # извлечь только первый кадр
            '-q:v', '2',           # качество
            '-vf', 'scale=800:-1', # масштабировать до ширины 800px
            '-f', 'image2',
            temp_image_path
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            logger.error(f'FFmpeg failed for {document_file.pk}: {result.stderr}')
            return None

        # Прочитать изображение
        with open(temp_image_path, 'rb') as f:
            image_data = f.read()

        return BytesIO(image_data)

    except subprocess.TimeoutExpired:
        logger.error(f'Video preview extraction timed out for file {document_file.pk}')
        return None
    except Exception as e:
        logger.error(f'Error extracting video preview for file {document_file.pk}: {e}')
        return None
    finally:
        # Очистить временные файлы
        try:
            os.unlink(temp_video_path)
            if 'temp_image_path' in locals():
                os.unlink(temp_image_path)
        except:
            pass


def _save_video_preview_to_cache(document, preview_image, preview_name):
    """
    Сохраняет превью видео в систему кеширования Mayan.

    Args:
        document: объект Document
        preview_image: BytesIO с изображением превью
        preview_name: имя превью
    """
    from mayan.apps.file_caching.models import Cache

    try:
        # Получить или создать кэш для превью
        cache, created = Cache.objects.get_or_create(
            defined_storage_name='converter_pipeline_preview',
            defaults={
                'maximum_size': 1024 * 1024 * 1024,  # 1GB
            }
        )

        # Создать partition для документа
        partition, created = cache.partitions.get_or_create(
            name=f'document_{document.pk}'
        )

        # Сохранить превью
        filename = f'{preview_name}.png'
        partition.set_file(
            filename=filename,
            content=preview_image
        )

        logger.info(f"Saved video preview for document {document.pk}: {filename}")

    except Exception as e:
        logger.error(f"Failed to save video preview for document {document.pk}: {e}")
        raise


def get_converter_class_for_mime_type(mime_type):
    """
    Возвращает класс конвертера для заданного MIME типа.
    """
    from .utils import get_supported_formats

    format_info = get_supported_formats(mime_type)
    if not format_info:
        return None

    converter_type = format_info.get('converter')
    if converter_type == 'raw_image':
        return RawImageConverter
    elif converter_type == 'video':
        return VideoConverter

    return None


def save_preview_to_document(document, preview_content, preview_name, converter_name):
    """
    Сохраняет превью в документ Mayan.

    Args:
        document: объект Document
        preview_content: содержимое превью (BytesIO или bytes)
        preview_name: имя превью
        converter_name: имя конвертера
    """
    from mayan.apps.file_caching.models import Cache

    try:
        # Получить или создать кэш
        cache, created = Cache.objects.get_or_create(
            defined_storage_name='converter_pipeline_preview',
            defaults={
                'maximum_size': 1024 * 1024 * 1024,  # 1GB
            }
        )

        # Создать partition для документа
        partition, created = cache.partitions.get_or_create(
            name=f'document_{document.pk}'
        )

        # Сохранить превью
        filename = f'{preview_name}.png'
        partition.set_file(
            filename=filename,
            content=preview_content
        )

        logger.info(f"Saved preview for document {document.pk}: {filename}")

    except Exception as e:
        logger.error(f"Failed to save preview for document {document.pk}: {e}")
        raise