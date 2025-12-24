"""
Утилиты для работы с лимитами размеров файлов в DAM системе.
"""
from typing import Optional
from django.conf import settings
from mayan.apps.tags.models import Tag


def get_max_file_size_for_mime_type(mime_type: str) -> int:
    """
    Получить максимальный размер файла для AI-анализа на основе MIME типа.
    
    Args:
        mime_type: MIME тип файла (например, 'image/jpeg', 'application/pdf')
        
    Returns:
        Максимальный размер в байтах
    """
    if not mime_type:
        return getattr(settings, 'DAM_AI_MAX_FILE_SIZE_DEFAULT', 15 * 1024 * 1024)
    
    mime_type_lower = mime_type.lower()
    
    # Изображения (обычные форматы)
    if mime_type_lower.startswith('image/'):
        # RAW и TIFF - специальная обработка
        if any(raw_type in mime_type_lower for raw_type in [
            'raw', 'dng', 'cr2', 'nef', 'orf', 'arw', 'rw2', 'raf', 'srw'
        ]):
            return getattr(settings, 'DAM_AI_MAX_FILE_SIZE_RAW', 50 * 1024 * 1024)
        
        # TIFF может быть очень большим
        if 'tiff' in mime_type_lower or 'tif' in mime_type_lower:
            return getattr(settings, 'DAM_AI_MAX_FILE_SIZE_RAW', 50 * 1024 * 1024)
        
        # Обычные изображения (JPEG, PNG, GIF, WebP, BMP)
        return getattr(settings, 'DAM_AI_MAX_FILE_SIZE_IMAGES', 20 * 1024 * 1024)
    
    # PDF документы
    elif mime_type_lower == 'application/pdf':
        return getattr(settings, 'DAM_AI_MAX_FILE_SIZE_PDF', 30 * 1024 * 1024)
    
    # Документы (DOCX, DOC, TXT)
    elif any(doc_type in mime_type_lower for doc_type in [
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
        'application/rtf'
    ]):
        return getattr(settings, 'DAM_AI_MAX_FILE_SIZE_DOCUMENTS', 15 * 1024 * 1024)
    
    # Видео (для будущей поддержки)
    elif mime_type_lower.startswith('video/'):
        return getattr(settings, 'DAM_AI_MAX_FILE_SIZE_VIDEO', 500 * 1024 * 1024)
    
    # Аудио (для будущей поддержки)
    elif mime_type_lower.startswith('audio/'):
        return getattr(settings, 'DAM_AI_MAX_FILE_SIZE_AUDIO', 100 * 1024 * 1024)
    
    # По умолчанию - безопасный лимит
    return getattr(settings, 'DAM_AI_MAX_FILE_SIZE_DEFAULT', 15 * 1024 * 1024)


def format_file_size(size_bytes: int) -> str:
    """
    Форматировать размер файла в читаемый вид.
    
    Args:
        size_bytes: Размер в байтах
        
    Returns:
        Строка вида "15.5 MB"
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def get_or_create_tag(label: str, color: Optional[str] = None) -> Optional[Tag]:
    """
    Get or create a Tag by label.
    
    Args:
        label: Tag label (will be trimmed and validated)
        color: Optional tag color (default from settings)
    
    Returns:
        Tag instance or None if label is invalid
    """
    from . import settings as dam_settings
    
    label = label.strip()[:128]  # Tag.label max_length=128
    if not label:
        return None
    
    color = color or dam_settings.setting_ai_tag_default_color.value or '#3c8dbc'
    
    tag, created = Tag.objects.get_or_create(
        label=label,
        defaults={'color': color}
    )
    return tag

