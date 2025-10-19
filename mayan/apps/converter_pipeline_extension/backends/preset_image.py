import io
import logging
from pathlib import Path

from django.core.files.base import ContentFile

from PIL import Image, ImageEnhance, ImageOps, UnidentifiedImageError, ImageDraw, ImageFont

from .base import BaseMediaConverter

logger = logging.getLogger(name=__name__)


class PresetImageConverter(BaseMediaConverter):
    """Конвертер изображений для применения настроек пресетов."""

    SUPPORTED_MIME_TYPES = [
        'image/jpeg',
        'image/pjpeg',
        'image/png',
        'image/webp',
        'image/tiff',
        'image/bmp',
        'image/x-bmp',
        'image/x-ms-bmp',
        'image/gif',
    ]

    MAX_FILE_SIZE_MB = 200

    def __init__(self, file_obj=None, file_stream=None, mime_type=None):
        if file_obj is None and file_stream is None:
            raise ValueError('Either file_obj or file_stream must be provided.')

        if file_stream is not None and not hasattr(file_stream, 'read'):
            raise ValueError('file_stream must be a file-like object.')

        if file_stream is not None:
            # Обернуть поток в ContentFile для совместимости
            original_position = file_stream.tell() if hasattr(file_stream, 'tell') else None
            data = file_stream.read()
            if original_position is not None:
                file_stream.seek(original_position)
            file_obj = ContentFile(data)

        detected_mime = mime_type or getattr(file_obj, 'mime_type', None) or getattr(file_obj, 'mimetype', None)
        if detected_mime and detected_mime not in self.SUPPORTED_MIME_TYPES:
            detected_mime = self._infer_mime_from_name(file_obj, fallback=detected_mime)

        super().__init__(file_obj=file_obj, mime_type=detected_mime)

    def convert(
        self,
        *,
        width=None,
        height=None,
        format='jpeg',
        quality=85,
        crop=True,
        dpi=None,
        filters=None,
        brightness=None,
        contrast=None,
        color=None,
        sharpness=None,
        watermark=None
    ):
        """Конвертировать изображение согласно настройкам пресета."""
        self.validate_file()

        image = self._open_image()

        target_format = (format or 'jpeg').upper()
        if target_format == 'JPG':
            target_format = 'JPEG'

        if crop and width and height:
            image = ImageOps.fit(
                image,
                (int(width), int(height)),
                method=Image.LANCZOS,
                centering=(0.5, 0.5)
            )
        else:
            image = self._resize_without_crop(image, width=width, height=height)

        image = self._apply_adjustments(
            image=image,
            target_format=target_format,
            dpi=dpi,
            filters=filters,
            brightness=brightness,
            contrast=contrast,
            color=color,
            sharpness=sharpness,
            watermark=watermark
        )

        output = io.BytesIO()
        save_kwargs = self._build_save_kwargs(target_format, quality)
        image.save(output, format=target_format, **save_kwargs)
        output.seek(0)
        return output

    def convert_to_preview(self, **options):
        return ContentFile(
            self.convert(**options).getvalue(),
            name=self._build_preview_name(options.get('format', 'jpeg'))
        )

    def _open_image(self):
        try:
            if hasattr(self.file_obj, 'open'):
                self.file_obj.open('rb')
                data = self.file_obj.read()
                self.file_obj.close()
            else:
                data = self.file_obj.read()
                if hasattr(self.file_obj, 'seek'):
                    self.file_obj.seek(0)

            stream = io.BytesIO(data)
            image = Image.open(stream)
            image.load()
            return image
        except UnidentifiedImageError as exc:
            raise ValueError(f'Cannot process image: {exc}')

    @staticmethod
    def _resize_without_crop(image, *, width=None, height=None):
        width = int(width) if width else None
        height = int(height) if height else None

        if width and height:
            return image.resize((width, height), Image.LANCZOS)

        if width:
            ratio = width / image.width
            target_height = max(1, int(round(image.height * ratio)))
            return image.resize((width, target_height), Image.LANCZOS)

        if height:
            ratio = height / image.height
            target_width = max(1, int(round(image.width * ratio)))
            return image.resize((target_width, height), Image.LANCZOS)

        return image

    @staticmethod
    def _ensure_mode(image, target_format):
        if target_format == 'JPEG' and image.mode not in ('RGB', 'L'):
            return image.convert('RGB')
        return image

    @staticmethod
    def _build_save_kwargs(target_format, quality):
        if target_format == 'JPEG':
            return {'quality': int(quality or 85), 'optimize': True}
        if target_format == 'PNG':
            return {'optimize': True}
        if target_format == 'WEBP':
            return {'quality': int(quality or 85)}
        return {}

    @staticmethod
    def _infer_mime_from_name(file_obj, fallback):
        name = getattr(file_obj, 'name', '') or ''
        suffix = Path(name).suffix.lower()
        mapping = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff',
            '.bmp': 'image/bmp',
            '.gif': 'image/gif',
        }
        return mapping.get(suffix, fallback)

    def _build_preview_name(self, fmt):
        suffix = (fmt or 'jpeg').lower().replace('jpg', 'jpeg')
        return f'preview.{suffix}'

    def _apply_adjustments(
        self,
        *,
        image,
        target_format,
        dpi,
        filters,
        brightness,
        contrast,
        color,
        sharpness,
        watermark
    ):
        image = self._ensure_mode(image, target_format)

        if dpi and isinstance(dpi, (list, tuple)) and len(dpi) == 2:
            image.info['dpi'] = (int(dpi[0]), int(dpi[1]))

        if brightness is not None and brightness != 1.0:
            image = ImageEnhance.Brightness(image).enhance(float(brightness))

        if contrast is not None and contrast != 1.0:
            image = ImageEnhance.Contrast(image).enhance(float(contrast))

        if color is not None and color != 1.0:
            image = ImageEnhance.Color(image).enhance(float(color))

        if sharpness is not None and sharpness != 1.0:
            image = ImageEnhance.Sharpness(image).enhance(float(sharpness))

        if filters:
            for filter_name in filters:
                try:
                    image = self._apply_filter(image=image, filter_name=filter_name)
                except Exception as exc:
                    logger.warning('Filter %s failed: %s', filter_name, exc)

        if watermark:
            try:
                image = self._apply_watermark(image=image, watermark=watermark)
            except Exception as exc:
                logger.warning('Watermark application failed: %s', exc)

        return image

    @staticmethod
    def _apply_filter(*, image, filter_name):
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

        raise ValueError(f'Unsupported filter: {filter_name}')

    @staticmethod
    def _apply_watermark(*, image, watermark):
        text = watermark.get('text') if isinstance(watermark, dict) else None
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
