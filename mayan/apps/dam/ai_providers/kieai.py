import re
from typing import Any, Dict, List, Optional

from .base import BaseAIProvider, AIProviderError
from ..services import KieAIClient, KieAIClientError


class KieAIProvider(BaseAIProvider):
    """
    Adapter for Kie.ai vision/OCR API.
    """

    name = 'kieai'
    display_name = 'Kie.ai Vision'
    description = 'OCR и извлечение текста через Kie.ai объединённый API'

    supports_vision = True
    supports_text = True
    supports_image_description = True
    supports_tag_extraction = True

    def __init__(
        self,
        api_key: str,
        base_url: str,
        upload_url: Optional[str] = None,
        ocr_endpoint: str = 'generate',
        status_endpoint: str = 'record-info',
        default_language: str = 'en',
        timeout: int = 30,
        upload_path: str = 'prime-edms/dam',
        model: str = 'flux-kontext-pro',
        default_prompt: str = 'Опиши содержимое изображения максимально подробно.',
        aspect_ratio: str = '1:1',
        **kwargs
    ):
        super().__init__(api_key, **kwargs)
        self.api_key = api_key
        self.upload_path = upload_path
        self.client = KieAIClient(
            api_key=api_key,
            base_url=base_url,
            upload_url=upload_url,
            ocr_endpoint=ocr_endpoint,
            status_endpoint=status_endpoint,
            default_language=default_language,
            timeout=timeout,
            upload_path=upload_path,
            model=model,
            default_prompt=default_prompt,
            aspect_ratio=aspect_ratio
        )

    # ------------------------------------------------------------------ helpers
    def _upload_and_recognize(self, image_data: bytes, mime_type: str) -> Dict[str, Any]:
        extension = 'bin'
        if mime_type and '/' in mime_type:
            extension = mime_type.split('/')[-1]
        file_name = f'prime-edms.{extension}'

        try:
            return self.client.extract_text(
                file_name=file_name,
                file_bytes=image_data,
                upload_path=self.upload_path
            )
        except KieAIClientError as exc:
            raise AIProviderError(f'Kie.ai request failed: {exc}') from exc

    def _keyword_tags(self, text: str) -> List[str]:
        if not text:
            return []

        words = re.findall(r'[A-Za-zА-Яа-я0-9]{4,}', text.lower())
        unique = []
        for word in words:
            if word not in unique:
                unique.append(word)
            if len(unique) >= 15:
                break
        return unique

    # ------------------------------------------------------------------ Base overrides
    def analyze_image(self, image_data: bytes, mime_type: str) -> Dict[str, Any]:
        payload = self._upload_and_recognize(image_data=image_data, mime_type=mime_type)
        text = payload.get('text') or ''
        language = payload.get('language') or ''

        return {
            'description': text,
            'alt_text': text[:250],
            'tags': self._keyword_tags(text),
            'colors': [],
            'categories': ['ocr', 'text_extraction'],
            'language': language,
            'provider': self.name,
            'extra': {
                'downloadUrl': payload.get('downloadUrl'),
                'confidence': payload.get('confidence')
            }
        }

    def describe_image(self, image_data: bytes, mime_type: str) -> str:
        payload = self._upload_and_recognize(image_data=image_data, mime_type=mime_type)
        return payload.get('text', '')

    def extract_tags(self, image_data: bytes, mime_type: str) -> List[str]:
        text = self.describe_image(image_data=image_data, mime_type=mime_type)
        return self._keyword_tags(text)

    def extract_colors(self, image_data: bytes, mime_type: str) -> List[Dict[str, Any]]:
        # OCR провайдер не предоставляет цветовую информацию
        return []

    def generate_alt_text(self, image_data: bytes, mime_type: str) -> str:
        text = self.describe_image(image_data=image_data, mime_type=mime_type)
        return text[:250]

    def is_available(self) -> bool:
        try:
            return bool(self.api_key)
        except Exception:
            return False

