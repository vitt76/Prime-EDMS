import base64
import json
import logging
from typing import Any, Dict, List

import requests
from django.utils.translation import ugettext_lazy as _

from .base import BaseAIProvider, AIProviderError

logger = logging.getLogger(__name__)


DEFAULT_PROMPT = (
    'Ты выступаешь как модуль DAM. Проанализируй изображение и ответь строго '
    'в формате JSON без пояснений и дополнительного текста. Структура:\n'
    '{\n'
    '  "description": "короткое связное описание на русском языке, до 3 предложений",\n'
    '  "tags": ["ключевое_слово1", "ключевое_слово2", ...],\n'
    '  "categories": ["категория1", "категория2", ...]\n'
    '}\n'
    '• description: что изображено, контекст и важные детали.\n'
    '• tags: 5–10 лаконичных тегов одним словом или коротким словосочетанием.\n'
    '• categories: 3–5 более широких тематических групп.\n'
    'Никаких комментариев вне JSON.'
)


class LocalQwenVisionProvider(BaseAIProvider):
    """
    Провайдер для локально развёрнутой qwen3-vl через Ollama/LM Studio совместимый API.
    """

    name = 'qwenlocal'
    display_name = _('Local Qwen Vision')
    description = _(
        'Использует локальный сервис qwen3-vl для получения описаний, тегов и категорий.'
    )

    supports_vision = True
    supports_text = True
    supports_image_description = True
    supports_tag_extraction = True

    def __init__(
        self, api_url: str, model: str, prompt: str = None,
        timeout: int = 120, verify_ssl: bool = False, **kwargs
    ):
        """
        Args:
            api_url: URL эндпоинта /api/generate локального сервиса.
            model: Имя модели (например, qwen3-vl:8b-instruct).
            prompt: Пользовательский системный промпт (опционально).
            timeout: Таймаут HTTP-запроса в секундах.
            verify_ssl: Проверять SSL-сертификат (актуально для https).
        """
        super().__init__(api_key=api_url, **kwargs)
        if not api_url:
            raise AIProviderError('QwenLocal: API URL is required')
        if not model:
            raise AIProviderError('QwenLocal: model name is required')

        self.api_url = api_url.rstrip('/')
        self.model = model
        self.prompt = prompt or DEFAULT_PROMPT
        self.timeout = timeout
        self.verify_ssl = verify_ssl

    # ------------------------------------------------------------------ public API
    def analyze_image(self, image_data: bytes, mime_type: str) -> Dict[str, Any]:
        payload = {
            'model': self.model,
            'prompt': self.prompt,
            'images': [self._encode_image(image_data)]
        }

        response_text = self._invoke(payload=payload)
        parsed = self._parse_model_response(response_text=response_text)

        description = parsed.get('description', '').strip()
        tags = self._coerce_list(parsed.get('tags', []))
        categories = self._coerce_list(parsed.get('categories', []))

        logger.debug(
            'QwenLocal analysis completed: description=%s, tags=%s, categories=%s',
            description[:80], tags, categories
        )

        return {
            'description': description,
            'tags': tags,
            'categories': categories,
            'language': 'ru',
            'alt_text': description
        }

    def describe_image(self, image_data: bytes, mime_type: str) -> str:
        return self.analyze_image(image_data=image_data, mime_type=mime_type).get('description', '')

    def extract_tags(self, image_data: bytes, mime_type: str) -> List[str]:
        return self.analyze_image(image_data=image_data, mime_type=mime_type).get('tags', [])

    def extract_colors(self, image_data: bytes, mime_type: str) -> List[Dict[str, Any]]:
        return []

    def generate_alt_text(self, image_data: bytes, mime_type: str) -> str:
        return self.describe_image(image_data=image_data, mime_type=mime_type)

    def is_available(self) -> bool:
        """Local сервис считается доступным, если есть URL и имя модели."""
        return bool(self.api_url and self.model)

    # ------------------------------------------------------------------ internals
    def _encode_image(self, image_data: bytes) -> str:
        try:
            return base64.b64encode(image_data).decode('ascii')
        except Exception as exc:
            raise AIProviderError(f'QwenLocal: failed to base64-encode image: {exc}') from exc

    def _invoke(self, payload: Dict[str, Any]) -> str:
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                stream=True,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise AIProviderError(f'QwenLocal request failed: {exc}') from exc

        chunks = []
        for line in response.iter_lines():
            if not line:
                continue
            try:
                data = json.loads(line.decode('utf-8'))
            except json.JSONDecodeError:
                logger.debug('QwenLocal: skipping non-JSON chunk: %s', line[:200])
                continue

            if data.get('response'):
                chunks.append(data['response'])

        if not chunks:
            raise AIProviderError('QwenLocal: empty response from model')

        return ''.join(chunks).strip()

    def _parse_model_response(self, response_text: str) -> Dict[str, Any]:
        try:
            parsed = json.loads(response_text)
            if not isinstance(parsed, dict):
                raise ValueError('Payload is not a JSON object')
            return parsed
        except Exception as exc:
            logger.error('QwenLocal: unable to parse JSON response: %s', response_text)
            raise AIProviderError(f'QwenLocal: invalid JSON payload: {exc}') from exc

    def _coerce_list(self, value: Any) -> List[str]:
        if not value:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            return [item.strip() for item in value.split(',') if item.strip()]
        return [str(value).strip()]

