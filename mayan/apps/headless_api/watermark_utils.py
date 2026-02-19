"""
Sprint 5.1: Shared watermark logic for image editor and watermarked download/rendition.

Reused by:
- headless_api.views.image_editor_views (preview/commit)
- Celery task apply_watermark (WatermarkedRendition generation)
"""
from typing import Any, Dict, Tuple

from PIL import Image, ImageDraw, ImageFont, ImageOps


def load_image_from_document_file(document_file) -> Image.Image:
    """
    Load a raster image from a DocumentFile (for use in Celery task).
    Uses first page pipeline or raw file open; normalizes to RGBA for watermarking.
    """
    page = document_file.pages_first
    if page:
        image_buffer = page.get_image(transformation_instance_list=())
        image = Image.open(fp=image_buffer)
        image.load()
    else:
        with document_file.open() as file_object:
            image = Image.open(fp=file_object)
            image.load()
    image = ImageOps.exif_transpose(image)
    if image.mode not in ('RGB', 'RGBA'):
        image = image.convert('RGBA')
    return image



def _coerce_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def watermark_position_to_xy(
    position: str,
    base_size: Tuple[int, int],
    wm_size: Tuple[int, int],
    offset_x: int = 0,
    offset_y: int = 0
) -> Tuple[int, int]:
    """
    Map 9-grid position string to (x, y) coordinates for watermark placement.

    Position format from editor state: 'top-left', 'bottom-right', 'middle-center', etc.
    """
    base_w, base_h = base_size
    wm_w, wm_h = wm_size
    pos = (position or 'bottom-right').lower().replace('_', '-')

    mapping = {
        'top-left': (0, 0),
        'top-center': ((base_w - wm_w) // 2, 0),
        'top-right': (base_w - wm_w, 0),
        'middle-left': (0, (base_h - wm_h) // 2),
        'middle-center': ((base_w - wm_w) // 2, (base_h - wm_h) // 2),
        'middle-right': (base_w - wm_w, (base_h - wm_h) // 2),
        'bottom-left': (0, base_h - wm_h),
        'bottom-center': ((base_w - wm_w) // 2, base_h - wm_h),
        'bottom-right': (base_w - wm_w, base_h - wm_h),
    }
    x, y = mapping.get(pos, mapping['bottom-right'])
    x += offset_x
    y += offset_y
    return max(0, min(x, base_w - wm_w)), max(0, min(y, base_h - wm_h))


def apply_watermark(image: Image.Image, state: Dict[str, Any]) -> Image.Image:
    """
    Apply watermark from editor-format state['watermark'] to image.

    state: dict with key 'watermark' (enabled, type text|image, position, opacity,
            text/fontSize/color or assetId). Same format as MediaEditorModal / editorStore.
    """
    watermark = state.get('watermark') or {}
    if not watermark.get('enabled'):
        return image

    opacity = _coerce_float(watermark.get('opacity'), 50.0)
    opacity = max(0.0, min(opacity, 100.0)) / 100.0
    position = watermark.get('position') or 'bottom-right'
    offset_x = _coerce_int(watermark.get('offsetX'), 0)
    offset_y = _coerce_int(watermark.get('offsetY'), 0)
    scale_pct = _coerce_float(watermark.get('scale'), 100.0)
    scale_pct = max(10.0, min(scale_pct, 400.0)) / 100.0

    base = image.convert('RGBA')
    overlay = Image.new('RGBA', base.size, (0, 0, 0, 0))

    wm_type = (watermark.get('type') or 'text').lower()
    if wm_type == 'image':
        from mayan.apps.converter.models import Asset
        asset_id = watermark.get('assetId') or watermark.get('asset_id')
        if not asset_id:
            return image
        asset = Asset.objects.filter(category='watermark', pk=asset_id).first()
        if not asset:
            return image
        wm = asset.get_image()

        wm_w = max(1, int(wm.width * scale_pct))
        wm_h = max(1, int(wm.height * scale_pct))
        wm = wm.resize((wm_w, wm_h), resample=Image.Resampling.LANCZOS)

        if opacity < 1.0:
            alpha = wm.getchannel('A')
            alpha = alpha.point(lambda a: int(a * opacity))
            wm.putalpha(alpha)

        x, y = watermark_position_to_xy(
            position=position, base_size=base.size, wm_size=wm.size,
            offset_x=offset_x, offset_y=offset_y
        )
        overlay.alpha_composite(wm, dest=(x, y))
    else:
        text = watermark.get('text') or ''
        if not text:
            return image
        font_size = _coerce_int(watermark.get('fontSize'), 24)
        font_size = max(8, min(font_size, 256))
        color = watermark.get('color') or '#ffffff'

        try:
            font = ImageFont.truetype('arial.ttf', font_size)
        except Exception:
            font = ImageFont.load_default()

        draw = ImageDraw.Draw(overlay)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x, y = watermark_position_to_xy(
            position=position, base_size=base.size, wm_size=(text_w, text_h),
            offset_x=offset_x, offset_y=offset_y
        )

        try:
            r = int(color.lstrip('#')[0:2], 16)
            g = int(color.lstrip('#')[2:4], 16)
            b = int(color.lstrip('#')[4:6], 16)
        except Exception:
            r, g, b = 255, 255, 255
        a = int(255 * opacity)
        draw.text((x, y), text, font=font, fill=(r, g, b, a))

    result = Image.alpha_composite(base, overlay)
    return result


def organization_watermark_to_editor_state(org_settings) -> Dict[str, Any]:
    """
    Convert OrganizationWatermarkSettings to editor-format state['watermark'].

    Used when generating WatermarkedRendition so organization watermark
    looks the same as in the image editor (same position grid, opacity, etc.).
    """
    if not org_settings or not getattr(org_settings, 'enabled', False):
        return {'enabled': False}
    text = (org_settings.text or '').strip()
    if not text:
        return {'enabled': False}

    # Org uses top_left, bottom_right, center -> editor uses top-left, bottom-right, middle-center
    pos_map = {
        'top_left': 'top-left',
        'top_right': 'top-right',
        'bottom_left': 'bottom-left',
        'bottom_right': 'bottom-right',
        'center': 'middle-center',
    }
    position = pos_map.get(
        (org_settings.position or 'bottom_right').strip(),
        'bottom-right'
    )
    opacity_pct = int((getattr(org_settings, 'opacity', 0.5) or 0.5) * 100)
    opacity_pct = max(0, min(100, opacity_pct))
    font_size = _coerce_int(getattr(org_settings, 'font_size', None), 24)
    font_size = max(8, min(256, font_size))

    return {
        'enabled': True,
        'type': 'text',
        'text': text,
        'position': position,
        'opacity': opacity_pct,
        'fontSize': font_size,
        'color': '#ffffff',
        'offsetX': 0,
        'offsetY': 0,
        'scale': 100.0,
    }
