import logging
from pathlib import Path

logger = logging.getLogger(name=__name__)

# Справочник поддерживаемых форматов с их конвертерами
MEDIA_FORMAT_REGISTRY = {
    # RAW изображения (dcraw/libraw)
    'image/x-canon-cr2': {'converter': 'raw_image', 'backend': 'dcraw', 'priority': 10},
    'image/x-canon-crw': {'converter': 'raw_image', 'backend': 'dcraw', 'priority': 10},
    'image/x-nikon-nef': {'converter': 'raw_image', 'backend': 'libraw', 'priority': 10},
    'image/x-nikon-nrw': {'converter': 'raw_image', 'backend': 'libraw', 'priority': 10},
    'image/x-sony-arw': {'converter': 'raw_image', 'backend': 'libraw', 'priority': 10},
    'image/x-sony-srf': {'converter': 'raw_image', 'backend': 'libraw', 'priority': 10},
    'image/x-pentax-pef': {'converter': 'raw_image', 'backend': 'dcraw', 'priority': 10},
    'image/x-pentax-raw': {'converter': 'raw_image', 'backend': 'dcraw', 'priority': 10},
    'image/x-olympus-orf': {'converter': 'raw_image', 'backend': 'libraw', 'priority': 10},
    'image/x-fuji-raf': {'converter': 'raw_image', 'backend': 'libraw', 'priority': 10},
    'image/x-panasonic-rw2': {'converter': 'raw_image', 'backend': 'libraw', 'priority': 10},
    'image/x-adobe-dng': {'converter': 'raw_image', 'backend': 'libraw', 'priority': 10},
    'image/x-kodak-dcr': {'converter': 'raw_image', 'backend': 'dcraw', 'priority': 10},
    'image/x-kodak-k25': {'converter': 'raw_image', 'backend': 'dcraw', 'priority': 10},
    'image/x-kodak-kdc': {'converter': 'raw_image', 'backend': 'dcraw', 'priority': 10},
    'image/x-minolta-mrw': {'converter': 'raw_image', 'backend': 'dcraw', 'priority': 10},
    'image/x-samsung-srw': {'converter': 'raw_image', 'backend': 'libraw', 'priority': 10},
    'image/x-sigma-sd9': {'converter': 'raw_image', 'backend': 'dcraw', 'priority': 10},
    'image/x-sigma-sd14': {'converter': 'raw_image', 'backend': 'dcraw', 'priority': 10},
    'image/x-sigma-sd15': {'converter': 'raw_image', 'backend': 'dcraw', 'priority': 10},
    'image/x-sigma-sd1': {'converter': 'raw_image', 'backend': 'dcraw', 'priority': 10},
    'image/x-sigma-sd1m': {'converter': 'raw_image', 'backend': 'dcraw', 'priority': 10},

    # Видео форматы (FFmpeg)
    'video/mp4': {'converter': 'video', 'backend': 'ffmpeg', 'priority': 20},
    'video/avi': {'converter': 'video', 'backend': 'ffmpeg', 'priority': 20},
    'video/mov': {'converter': 'video', 'backend': 'ffmpeg', 'priority': 20},
    'video/mkv': {'converter': 'video', 'backend': 'ffmpeg', 'priority': 20},
    'video/webm': {'converter': 'video', 'backend': 'ffmpeg', 'priority': 20},
    'video/flv': {'converter': 'video', 'backend': 'ffmpeg', 'priority': 20},
    'video/wmv': {'converter': 'video', 'backend': 'ffmpeg', 'priority': 20},
    'video/m4v': {'converter': 'video', 'backend': 'ffmpeg', 'priority': 20},
    'video/3gp': {'converter': 'video', 'backend': 'ffmpeg', 'priority': 20},
    'video/quicktime': {'converter': 'video', 'backend': 'ffmpeg', 'priority': 20},
    'video/x-msvideo': {'converter': 'video', 'backend': 'ffmpeg', 'priority': 20},
    'video/x-flv': {'converter': 'video', 'backend': 'ffmpeg', 'priority': 20},
    'video/x-ms-wmv': {'converter': 'video', 'backend': 'ffmpeg', 'priority': 20},
    'video/x-matroska': {'converter': 'video', 'backend': 'ffmpeg', 'priority': 20},

    # Аудио форматы (FFmpeg)
    'audio/mp3': {'converter': 'audio', 'backend': 'ffmpeg', 'priority': 30},
    'audio/wav': {'converter': 'audio', 'backend': 'ffmpeg', 'priority': 30},
    'audio/flac': {'converter': 'audio', 'backend': 'ffmpeg', 'priority': 30},
    'audio/ogg': {'converter': 'audio', 'backend': 'ffmpeg', 'priority': 30},
    'audio/m4a': {'converter': 'audio', 'backend': 'ffmpeg', 'priority': 30},
    'audio/aac': {'converter': 'audio', 'backend': 'ffmpeg', 'priority': 30},

    # Профессиональные форматы изображений
    'image/vnd.adobe.photoshop': {'converter': 'pro_image', 'backend': 'imagemagick', 'priority': 15},
    'image/x-coreldraw': {'converter': 'pro_image', 'backend': 'libcdr', 'priority': 15},
    'image/x-gimp-xcf': {'converter': 'pro_image', 'backend': 'gimp', 'priority': 15},
    'application/postscript': {'converter': 'pro_image', 'backend': 'ghostscript', 'priority': 15},
    'application/pdf': {'converter': 'pro_image', 'backend': 'poppler', 'priority': 15},

    # Архивы
    'application/x-rar': {'converter': 'archive', 'backend': 'unrar', 'priority': 40},
    'application/x-rar-compressed': {'converter': 'archive', 'backend': 'unrar', 'priority': 40},
    'application/x-7z-compressed': {'converter': 'archive', 'backend': '7z', 'priority': 40},
    'application/zip': {'converter': 'archive', 'backend': 'zip', 'priority': 40},
    'application/x-tar': {'converter': 'archive', 'backend': 'tar', 'priority': 40},
    'application/x-gzip': {'converter': 'archive', 'backend': 'gzip', 'priority': 40},
    'application/x-bzip2': {'converter': 'archive', 'backend': 'bzip2', 'priority': 40},
}


def is_media_format_supported(mime_type):
    """
    Проверить, поддерживается ли формат для конвертации.

    Args:
        mime_type (str): MIME тип файла

    Returns:
        bool: True если формат поддерживается
    """
    return mime_type in MEDIA_FORMAT_REGISTRY


def get_supported_formats_for_document(document):
    """
    Получить список поддерживаемых форматов для документа.

    Args:
        document: Экземпляр Document

    Returns:
        list: Список словарей с информацией о поддерживаемых форматах
    """
    if not document.file:
        return []

    mime_type = document.file.mime_type
    format_info = MEDIA_FORMAT_REGISTRY.get(mime_type)

    if format_info:
        return [format_info]
    else:
        return []


def get_converter_for_mime_type(mime_type):
    """
    Получить подходящий конвертер для MIME типа.

    Args:
        mime_type (str): MIME тип файла

    Returns:
        dict or None: Информация о конвертере или None
    """
    return MEDIA_FORMAT_REGISTRY.get(mime_type)


def get_all_supported_formats():
    """
    Получить все поддерживаемые форматы.

    Returns:
        dict: Словарь всех поддерживаемых форматов
    """
    return MEDIA_FORMAT_REGISTRY.copy()


def get_formats_by_category(category):
    """
    Получить форматы по категории.

    Args:
        category (str): Категория форматов ('image', 'video', etc.)

    Returns:
        dict: Форматы указанной категории
    """
    return {
        mime_type: info
        for mime_type, info in MEDIA_FORMAT_REGISTRY.items()
        if info['converter'] == category
    }


def get_file_extension_from_mime_type(mime_type):
    """
    Получить расширение файла по MIME типу.

    Args:
        mime_type (str): MIME тип

    Returns:
        str: Расширение файла или пустая строка
    """
    # Простое отображение MIME типов на расширения
    mime_to_ext = {
        'image/x-canon-cr2': '.cr2',
        'image/x-nikon-nef': '.nef',
        'image/x-sony-arw': '.arw',
        'video/mp4': '.mp4',
        'video/avi': '.avi',
        'video/mov': '.mov',
        'video/mkv': '.mkv',
        'application/x-rar': '.rar',
        'application/x-7z-compressed': '.7z',
        'application/zip': '.zip',
    }

    return mime_to_ext.get(mime_type, '')


def validate_file_size(file_obj, max_size_mb=500):
    """
    Проверить размер файла.

    Args:
        file_obj: File объект
        max_size_mb (int): Максимальный размер в MB

    Returns:
        bool: True если файл допустимого размера
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    file_obj.seek(0, 2)  # Перейти в конец файла
    size = file_obj.tell()
    file_obj.seek(0)  # Вернуться в начало

    return size <= max_size_bytes


def get_file_info(file_obj):
    """
    Получить информацию о файле.

    Args:
        file_obj: File объект

    Returns:
        dict: Информация о файле
    """
    file_obj.seek(0, 2)
    size = file_obj.tell()
    file_obj.seek(0)

    return {
        'size': size,
        'size_mb': round(size / (1024 * 1024), 2),
        'mime_type': getattr(file_obj, 'mime_type', 'unknown'),
    }

