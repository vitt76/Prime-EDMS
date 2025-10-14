import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from mayan.apps.documents.models import Document, DocumentFile, DocumentVersion

logger = logging.getLogger(name=__name__)


@receiver(post_save, sender=Document)
def handle_document_saved(sender, instance, created, **kwargs):
    """
    Обработчик сохранения документа.
    Запускает автоматическую конвертацию для новых медиа файлов.
    """
    from .tasks import task_convert_document_media

    if created and instance.file:
        # Новый документ с файлом - проверить на необходимость конвертации
        mime_type = instance.file.mime_type
        from .utils import is_media_format_supported

        if is_media_format_supported(mime_type):
            logger.info(f'Scheduling automatic conversion for document {instance.pk} ({mime_type})')
            task_convert_document_media.delay(instance.pk)


@receiver(post_save, sender=DocumentVersion)
def handle_document_version_saved(sender, instance, created, **kwargs):
    """
    Обработчик сохранения версии документа.
    Для видео файлов создает превью.
    """
    if created and instance.document.file_latest and instance.document.file_latest.mimetype and instance.document.file_latest.mimetype.startswith('video/'):
        logger.info(f'New document version created for video file: {instance.pk}, MIME: {instance.document.file_latest.mimetype}')
        # Запускаем задачу генерации превью
        from .tasks import task_generate_video_preview
        task_generate_video_preview.delay(instance.document.file_latest.pk)


@receiver(post_save, sender=DocumentFile)
def handle_document_file_saved(sender, instance, created, **kwargs):
    """
    Обработчик сохранения файла документа.
    Автоматически генерирует превью для видео файлов и извлекает архивы.
    """
    if created and instance.mimetype:
        # Обработка видео файлов
        if instance.mimetype.startswith('video/'):
            logger.info(f'New video file uploaded: {instance.pk}, MIME: {instance.mimetype}')
            # Запускаем задачу генерации превью
            from .tasks import task_generate_video_preview
            task_generate_video_preview.delay(instance.pk)





@receiver(post_delete, sender=Document)
def handle_document_deleted(sender, instance, **kwargs):
    """
    Обработчик удаления документа.
    Очищает связанные метаданные конвертации.
    """
    from .models import DocumentConversionMetadata

    try:
        metadata = DocumentConversionMetadata.objects.get(document=instance)
        metadata.delete()
        logger.info(f'Cleaned up conversion metadata for deleted document {instance.pk}')
    except DocumentConversionMetadata.DoesNotExist:
        pass

