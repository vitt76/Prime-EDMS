"""
Celery tasks for Headless API.

Handles asynchronous processing of editor operations (image conversion, version creation).
"""
import io
import logging
from typing import Dict, Any, Optional, Tuple

from celery import shared_task
from django.apps import apps
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.db import OperationalError

logger = logging.getLogger(__name__)


def _convert_image(file_obj, target_format: str) -> Tuple[io.BytesIO, str, str]:
    """
    Convert uploaded image to target format using Pillow.
    
    Args:
        file_obj: File-like object to convert
        target_format: Target format (jpeg, png, webp, etc.)
    
    Returns:
        Tuple of (output_buffer, content_type, extension)
    """
    from PIL import Image

    image = Image.open(file_obj)
    output_buffer = io.BytesIO()

    fmt = target_format.upper() if target_format else 'JPEG'
    if fmt == 'JPG':
        fmt = 'JPEG'

    image.save(output_buffer, format=fmt)
    output_buffer.seek(0)

    content_type = f"image/{fmt.lower()}"
    extension = fmt.lower()
    return output_buffer, content_type, extension


@shared_task(bind=True, max_retries=3, default_retry_delay=60, queue='converter')
def process_editor_version_task(
    self,
    shared_uploaded_file_id: int,
    document_id: int,
    target_format: Optional[str] = None,
    comment: Optional[str] = None,
    action_id: Optional[int] = None,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Celery task для асинхронной обработки изображения из редактора.
    
    Выполняет конвертацию изображения (если требуется) и создает новую версию документа.
    Постобработка (OCR, AI-анализ) запускается автоматически через сигналы Mayan EDMS.
    
    Args:
        shared_uploaded_file_id: ID временного файла в SharedUploadedFile
        document_id: ID документа для создания версии
        target_format: Целевой формат (jpeg, png, webp, etc.) или None для сохранения оригинала
        comment: Комментарий для версии
        action_id: ID действия DocumentFileAction (по умолчанию DocumentFileActionUseNewPages)
        user_id: ID пользователя, создавшего версию
    
    Returns:
        dict: {
            'success': bool,
            'document_id': int,
            'file_id': int,
            'version_id': int (optional),
            'error': str (optional, только при success=False)
        }
    """
    # Импорты внутри функции для избежания circular dependencies
    SharedUploadedFile = apps.get_model('storage', 'SharedUploadedFile')
    Document = apps.get_model('documents', 'Document')
    DocumentFileActionUseNewPages = apps.get_model(
        'documents', 'DocumentFileActionUseNewPages'
    )
    User = get_user_model()
    
    shared_file = None
    try:
        # Получение объектов
        shared_file = SharedUploadedFile.objects.get(pk=shared_uploaded_file_id)
        document = Document.objects.get(pk=document_id)
        user = User.objects.get(pk=user_id) if user_id else None
        
        if not action_id:
            action_id = DocumentFileActionUseNewPages.backend_id
        
        # Конвертация (если требуется)
        file_to_save = shared_file
        filename = shared_file.filename or 'edited-image'
        
        if target_format:
            logger.debug(
                f'Converting image to {target_format} for document {document_id}'
            )
            with shared_file.open() as file_obj:
                buffer, _content_type, extension = _convert_image(
                    file_obj, target_format=target_format
                )
                filename_parts = filename.rsplit('.', 1)
                base_name = filename_parts[0] if len(filename_parts) > 1 else filename
                filename = f'{base_name}.{extension}'
                file_to_save = ContentFile(buffer.read(), name=filename)
        
        # Создание версии документа
        # Это автоматически триггерит сигналы для OCR, AI-анализа и других постобработок
        logger.debug(f'Creating new version for document {document_id}')
        new_file = document.file_new(
            file_object=file_to_save,
            filename=filename,
            action=action_id,
            comment=comment or 'Edited via Web Editor',
            _user=user,
        )
        
        # Получение созданной версии
        version = document.versions.order_by('-timestamp').first()
        
        # Очистка временного файла
        shared_file.delete()
        shared_file = None
        
        logger.info(
            f'Successfully created version {version.pk if version else None} '
            f'for document {document_id} (file_id: {new_file.pk})'
        )
        
        return {
            'success': True,
            'document_id': document.pk,
            'file_id': new_file.pk,
            'version_id': version.pk if version else None,
        }
        
    except OperationalError as exc:
        logger.warning(
            f'Operational error processing editor version for document {document_id}: {exc}. '
            f'Retrying...'
        )
        # Retry при операционных ошибках БД
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        else:
            # Очистка при окончательной ошибке
            if shared_file:
                try:
                    shared_file.delete()
                except Exception:
                    pass
            return {
                'success': False,
                'error': f'Database operational error: {str(exc)}',
                'document_id': document_id,
            }
            
    except Exception as exc:
        logger.exception(
            f'Error processing editor version for document {document_id}: {exc}'
        )
        
        # Очистка временного файла при ошибке
        if shared_file:
            try:
                shared_file.delete()
            except Exception:
                pass
        
        # Retry логика для других ошибок
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        
        return {
            'success': False,
            'error': str(exc),
            'document_id': document_id,
        }

