import io
import logging
from typing import Any, Dict, Optional, Tuple

from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from mayan.apps.acls.models import AccessControlList
from mayan.apps.converter.models import Asset
from mayan.apps.converter.permissions import permission_asset_view
from mayan.apps.documents.document_file_actions import DocumentFileActionUseNewPages
from mayan.apps.documents.models import Document
from mayan.apps.documents.models.document_file_models import DocumentFile
from mayan.apps.documents.permissions import permission_document_version_create
from mayan.apps.image_editor.models import ImageEditSession
from mayan.apps.image_editor.permissions import permission_image_edit
from mayan.apps.headless_api.serializers.image_editor import (
    HeadlessImageEditorSessionCreateSerializer,
    HeadlessImageEditorSessionStateSerializer
)
from mayan.apps.headless_api.serializers.version import HeadlessDocumentVersionSerializer

logger = logging.getLogger(__name__)


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


def _map_format_to_pillow(fmt: str) -> Tuple[str, str]:
    fmt = (fmt or 'jpg').lower()
    if fmt in ('jpg', 'jpeg'):
        return 'JPEG', 'image/jpeg'
    if fmt == 'png':
        return 'PNG', 'image/png'
    if fmt == 'webp':
        return 'WEBP', 'image/webp'
    if fmt == 'tiff':
        return 'TIFF', 'image/tiff'
    if fmt == 'gif':
        return 'GIF', 'image/gif'
    return 'JPEG', 'image/jpeg'


def _load_document_file_image(document_file: DocumentFile) -> Image.Image:
    """
    Load a raster image for a document file.
    Uses the converter pipeline via DocumentFilePage.get_image when possible.
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

    # Respect EXIF orientation for camera images
    image = ImageOps.exif_transpose(image)
    if image.mode not in ('RGB', 'RGBA'):
        image = image.convert('RGBA')
    return image


def _apply_transformations(image: Image.Image, state: Dict[str, Any]) -> Image.Image:
    transform = state.get('transform') or {}
    rotation = _coerce_int(transform.get('rotation'), 0) % 360
    flip_h = bool(transform.get('flipHorizontal'))
    flip_v = bool(transform.get('flipVertical'))

    if rotation:
        # Expand to avoid cropping
        image = image.rotate(angle=-rotation, expand=True)
    if flip_h:
        image = ImageOps.mirror(image)
    if flip_v:
        image = ImageOps.flip(image)
    return image


def _apply_crop(image: Image.Image, state: Dict[str, Any]) -> Image.Image:
    crop = state.get('crop') or {}

    # Не обрезаем изображение, пока фронтенд явно не включил crop (crop.enabled),
    # иначе при одном лишь повороте можно непреднамеренно отрезать часть кадра.
    if not bool(crop.get('enabled')):
        return image
    x = _coerce_int(crop.get('x'), 0)
    y = _coerce_int(crop.get('y'), 0)
    w = _coerce_int(crop.get('width'), image.width)
    h = _coerce_int(crop.get('height'), image.height)

    # Clamp
    x = max(0, min(x, image.width - 1))
    y = max(0, min(y, image.height - 1))
    w = max(1, min(w, image.width - x))
    h = max(1, min(h, image.height - y))

    return image.crop((x, y, x + w, y + h))


def _apply_resize(image: Image.Image, state: Dict[str, Any]) -> Image.Image:
    resize = state.get('resize') or {}

    # По умолчанию resize выключен. Включаем его только если фронтенд
    # явно установил флаг enabled. Это позволяет не портить пропорции
    # при простом повороте изображения без изменения размера.
    if not bool(resize.get('enabled')):
        return image
    target_w = _coerce_int(resize.get('width'), image.width)
    target_h = _coerce_int(resize.get('height'), image.height)

    target_w = max(1, min(target_w, 20000))
    target_h = max(1, min(target_h, 20000))

    if (target_w, target_h) == (image.width, image.height):
        return image
    return image.resize((target_w, target_h), resample=Image.Resampling.LANCZOS)


def _apply_filters(image: Image.Image, state: Dict[str, Any]) -> Image.Image:
    filters = state.get('filters') or {}

    brightness = _coerce_float(filters.get('brightness'), 0.0)
    contrast = _coerce_float(filters.get('contrast'), 0.0)
    saturation = _coerce_float(filters.get('saturation'), 0.0)
    blur_px = _coerce_float(filters.get('blur'), 0.0)
    sharpen = _coerce_float(filters.get('sharpen'), 0.0)

    # Map -100..100 -> factor 0..2
    def _factor(v: float) -> float:
        v = max(-100.0, min(100.0, v))
        return 1.0 + (v / 100.0)

    if brightness:
        image = ImageEnhance.Brightness(image).enhance(_factor(brightness))
    if contrast:
        image = ImageEnhance.Contrast(image).enhance(_factor(contrast))
    if saturation:
        image = ImageEnhance.Color(image).enhance(_factor(saturation))
    if blur_px and blur_px > 0:
        image = image.filter(ImageFilter.GaussianBlur(radius=max(0.0, min(blur_px, 50.0))))
    if sharpen and sharpen > 0:
        # 0..100 -> apply mild unsharp mask
        amount = max(0.0, min(sharpen, 100.0))
        image = image.filter(ImageFilter.UnsharpMask(radius=2, percent=int(50 + amount * 2), threshold=3))
    return image


def _watermark_position_to_xy(
    position: str,
    base_size: Tuple[int, int],
    wm_size: Tuple[int, int],
    offset_x: int,
    offset_y: int
) -> Tuple[int, int]:
    base_w, base_h = base_size
    wm_w, wm_h = wm_size
    pos = (position or 'bottom-right').lower()

    # 9-grid positions from frontend store
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


def _apply_watermark(image: Image.Image, state: Dict[str, Any]) -> Image.Image:
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
        asset_id = watermark.get('assetId') or watermark.get('asset_id')
        if not asset_id:
            return image
        asset = Asset.objects.filter(category='watermark', pk=asset_id).first()
        if not asset:
            return image
        wm = asset.get_image()  # RGBA

        wm_w = max(1, int(wm.width * scale_pct))
        wm_h = max(1, int(wm.height * scale_pct))
        wm = wm.resize((wm_w, wm_h), resample=Image.Resampling.LANCZOS)

        # Apply opacity
        if opacity < 1.0:
            alpha = wm.getchannel('A')
            alpha = alpha.point(lambda a: int(a * opacity))
            wm.putalpha(alpha)

        x, y = _watermark_position_to_xy(
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
        # Estimate text bbox
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x, y = _watermark_position_to_xy(
            position=position, base_size=base.size, wm_size=(text_w, text_h),
            offset_x=offset_x, offset_y=offset_y
        )

        # Convert hex color + opacity
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


def _render_image(document_file: DocumentFile, state: Dict[str, Any]) -> Image.Image:
    image = _load_document_file_image(document_file=document_file)
    image = _apply_transformations(image=image, state=state)
    image = _apply_crop(image=image, state=state)
    image = _apply_resize(image=image, state=state)
    image = _apply_filters(image=image, state=state)
    image = _apply_watermark(image=image, state=state)
    return image


def _encode_image(
    image: Image.Image,
    fmt: str,
    quality: int,
    dpi: Optional[int] = None
) -> Tuple[bytes, str, str]:
    pillow_fmt, content_type = _map_format_to_pillow(fmt=fmt)
    buffer = io.BytesIO()

    save_kwargs: Dict[str, Any] = {}
    if dpi:
        save_kwargs['dpi'] = (dpi, dpi)
    if pillow_fmt in ('JPEG', 'WEBP'):
        save_kwargs['quality'] = max(10, min(int(quality or 85), 100))
        if pillow_fmt == 'JPEG':
            save_kwargs['optimize'] = True

    if pillow_fmt in ('JPEG',):
        if image.mode == 'RGBA':
            image = image.convert('RGB')

    image.save(buffer, format=pillow_fmt, **save_kwargs)
    buffer.seek(0)
    extension = pillow_fmt.lower()
    if extension == 'jpeg':
        extension = 'jpg'
    return buffer.getvalue(), content_type, extension


def _get_session_for_request(request, session_id: int) -> ImageEditSession:
    """
    Fetch an edit session and enforce access via the underlying DocumentFile ACL.

    Do NOT filter sessions by session.user. Auth can vary (Token vs Session) and
    we want consistent behavior: if user can edit the source document file, user
    can use the session.
    """
    session = get_object_or_404(
        ImageEditSession.objects.select_related('document_file', 'document_file__document'),
        pk=session_id
    )
    AccessControlList.objects.check_access(
        obj=session.document_file,
        permissions=(permission_image_edit,),
        user=request.user
    )
    return session


class HeadlessImageEditorSessionCreateView(APIView):
    # Use token auth only to avoid mixing Django session user with SPA token user.
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = HeadlessImageEditorSessionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document_file_id = serializer.validated_data['document_file_id']

        document_file = get_object_or_404(DocumentFile.objects.all(), pk=document_file_id)
        # Ensure permission failure returns 403 (not 404), so SPA can show proper error.
        AccessControlList.objects.check_access(
            obj=document_file,
            permissions=(permission_image_edit,),
            user=request.user
        )

        image = _load_document_file_image(document_file=document_file)

        initial_state = {
            'crop': {
                'x': 0, 'y': 0, 'width': image.width, 'height': image.height,
                'aspectRatio': 'free'
            },
            'resize': {
                'width': image.width,
                'height': image.height,
                'maintainAspect': True,
                'dpi': 72
            },
            'format': 'jpg',
            'quality': 85,
            'transform': {
                'rotation': 0,
                'flipHorizontal': False,
                'flipVertical': False
            },
            'filters': {
                'brightness': 0,
                'contrast': 0,
                'saturation': 0,
                'blur': 0,
                'sharpen': 0
            },
            'watermark': {
                'enabled': False,
                'type': 'text',
                'text': '',
                'fontFamily': 'Arial',
                'fontSize': 24,
                'color': '#ffffff',
                'position': 'bottom-right',
                'opacity': 50,
                'scale': 100,
                'offsetX': 20,
                'offsetY': 20
            }
        }

        session = ImageEditSession.objects.create(
            document_file=document_file,
            user=request.user,
            original_checksum=document_file.checksum,
            status='editing',
            state=initial_state
        )

        return Response(
            {
                'session_id': session.pk,
                'document_id': document_file.document_id,
                'document_file_id': document_file.pk,
                'original': {
                    'width': image.width,
                    'height': image.height,
                    'file_size': document_file.size,
                    'mimetype': document_file.mimetype,
                    'filename': document_file.filename
                },
                'state': session.state
            },
            status=status.HTTP_201_CREATED
        )


class HeadlessImageEditorSessionDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id: int):
        session = _get_session_for_request(request=request, session_id=session_id)

        return Response(
            {
                'session_id': session.pk,
                'document_id': session.document_file.document_id,
                'document_file_id': session.document_file_id,
                'status': session.status,
                'created': session.created.isoformat() if session.created else None,
                'modified': session.modified.isoformat() if session.modified else None,
                'state': session.state
            }
        )

    def patch(self, request, session_id: int):
        session = _get_session_for_request(request=request, session_id=session_id)
        serializer = HeadlessImageEditorSessionStateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        state = serializer.validated_data['state']
        if not isinstance(state, dict):
            return Response({'error': 'invalid_state'}, status=status.HTTP_400_BAD_REQUEST)

        session.state = state
        session.save(update_fields=('state', 'modified'))

        return Response({'success': True, 'session_id': session.pk, 'state': session.state})


class HeadlessImageEditorPreviewView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id: int):
        try:
            session = _get_session_for_request(request=request, session_id=session_id)

            max_w = _coerce_int(request.query_params.get('max_w'), 0)
            max_h = _coerce_int(request.query_params.get('max_h'), 0)
            preview_format = request.query_params.get('format') or 'jpeg'
            quality = _coerce_int(request.query_params.get('quality'), 85)

            image = _render_image(document_file=session.document_file, state=session.state or {})

            # Optional downscale for preview transport
            if max_w > 0 or max_h > 0:
                target = (
                    max(1, max_w) if max_w > 0 else image.width,
                    max(1, max_h) if max_h > 0 else image.height
                )
                image.thumbnail(target, resample=Image.Resampling.LANCZOS)

            dpi = _coerce_int(((session.state or {}).get('resize') or {}).get('dpi'), 0)
            data, content_type, _ext = _encode_image(
                image=image,
                fmt=preview_format,
                quality=quality,
                dpi=dpi or None
            )

            response = HttpResponse(content=data, content_type=content_type)
            response['Cache-Control'] = 'no-store'
            response['X-Preview-Width'] = str(image.width)
            response['X-Preview-Height'] = str(image.height)
            return response
        except Exception as exc:
            logger.exception(
                'Headless image-editor preview failed. session_id=%s user_id=%s error=%s',
                session_id,
                getattr(request.user, 'pk', None),
                exc
            )
            raise


class HeadlessImageEditorCommitView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id: int):
        session = _get_session_for_request(request=request, session_id=session_id)

        document = get_object_or_404(
            Document.valid.all(), pk=session.document_file.document_id
        )
        # Ensure permission failure returns 403 (not 404), so SPA can show proper error.
        AccessControlList.objects.check_access(
            obj=document,
            permissions=(permission_document_version_create,),
            user=request.user
        )

        comment = request.data.get('comment') or _('Edited via Image Editor')
        action_id = request.data.get('action_id') or DocumentFileActionUseNewPages.backend_id

        # Allow frontend to send the latest state explicitly to avoid any race
        # conditions with async PATCH calls. If provided and valid, persist it
        # and use it for rendering; otherwise fall back to the stored session state.
        request_state = request.data.get('state')
        if isinstance(request_state, dict):
            state = request_state
            session.state = state
            session.save(update_fields=('state', 'modified'))
        else:
            state = session.state or {}

        fmt = state.get('format') or 'jpg'
        quality = _coerce_int(state.get('quality'), 85)
        dpi = _coerce_int(((state.get('resize') or {}).get('dpi')), 0) or None

        image = _render_image(document_file=session.document_file, state=state)
        data, _content_type, ext = _encode_image(
            image=image,
            fmt=fmt,
            quality=quality,
            dpi=dpi
        )

        base_name = session.document_file.filename.rsplit('.', 1)[0]
        filename = f'{base_name}.{ext}'

        previous_active = document.version_active

        new_file = document.file_new(
            file_object=ContentFile(data, name=filename),
            filename=filename,
            action=action_id,
            comment=comment,
            _user=request.user
        )

        version = document.versions.order_by('-timestamp').first()
        if version:
            if version.active:
                version.active = False
                version.save(update_fields=('active',))
            if previous_active and previous_active.pk != version.pk:
                previous_active.active_set(save=True)

        serializer = HeadlessDocumentVersionSerializer(
            version, context={'request': request}
        )

        session.status = 'saved'
        session.edited_checksum = new_file.checksum
        session.save(update_fields=('status', 'edited_checksum', 'modified'))

        return Response(
            {
                'success': True,
                'document_id': document.pk,
                'file_id': new_file.pk,
                'version_id': version.pk if version else None,
                'version': serializer.data,
                'state': state,
            },
            status=status.HTTP_201_CREATED
        )


class HeadlessImageEditorWatermarkListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # NOTE: Base Mayan Asset model doesn't have a 'category' field.
        # We return all viewable assets; frontend can filter by naming convention
        # (e.g. internal_name prefix "watermark_") if desired.
        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_asset_view,
            queryset=Asset.objects.all(),
            user=request.user
        ).only('id', 'label', 'internal_name').order_by('label')

        results = [
            {
                'id': asset.pk,
                'label': asset.label,
                'internal_name': getattr(asset, 'internal_name', '')
            }
            for asset in queryset
        ]
        return Response({'results': results})


