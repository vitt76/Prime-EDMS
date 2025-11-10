import json
import logging
from typing import Dict, List, Any

import requests
from django.conf import settings

from .base import BaseAIProvider, AIProviderError, AIProviderRateLimitError, AIProviderAuthError

logger = logging.getLogger(__name__)


class YandexGPTProvider(BaseAIProvider):
    """
    YandexGPT provider for text-based AI analysis.

    Note: YandexGPT doesn't have built-in vision capabilities,
    so image analysis is done through text descriptions.
    """

    name = 'yandexgpt'
    display_name = 'YandexGPT'
    description = 'Russian AI model by Yandex'

    supports_vision = False  # YandexGPT doesn't support vision
    supports_text = True
    supports_image_description = False  # Can't analyze images directly
    supports_tag_extraction = True
    supports_color_analysis = False
    supports_alt_text_generation = True

    def __init__(self, api_key: str, folder_id: str, model: str = 'general', **kwargs):
        super().__init__(api_key, **kwargs)
        self.folder_id = folder_id
        self.model = model
        self.base_url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
        self.timeout = kwargs.get('timeout', 30)

    def _make_request(self, prompt: str, **kwargs) -> str:
        """
        Make request to YandexGPT API.

        Args:
            prompt: Text prompt
            **kwargs: Additional parameters

        Returns:
            Generated text response
        """
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'modelUri': f'gpt://{self.folder_id}/{self.model}',
            'completionOptions': {
                'stream': False,
                'temperature': kwargs.get('temperature', 0.7),
                'maxTokens': kwargs.get('max_tokens', 1000)
            },
            'messages': [
                {
                    'role': 'user',
                    'text': prompt
                }
            ]
        }

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )

            if response.status_code == 429:
                raise AIProviderRateLimitError("YandexGPT rate limit exceeded")
            elif response.status_code == 401:
                raise AIProviderAuthError("Invalid YandexGPT API key")
            elif not response.ok:
                raise AIProviderError(f"YandexGPT API error: {response.status_code} - {response.text}")

            result = response.json()
            return result['result']['alternatives'][0]['message']['text']

        except requests.exceptions.Timeout:
            raise AIProviderError("YandexGPT API timeout")
        except requests.exceptions.RequestException as e:
            raise AIProviderError(f"YandexGPT API request failed: {e}")

    def analyze_image(self, image_data: bytes, mime_type: str) -> Dict[str, Any]:
        """
        YandexGPT doesn't support vision, so we return limited analysis.
        In practice, you might want to combine this with OCR or other services.
        """
        return {
            'description': 'Изображение не может быть проанализировано - YandexGPT не поддерживает анализ изображений',
            'tags': [],
            'colors': [],
            'alt_text': 'Изображение',
            'objects': [],
            'mood': '',
            'style': ''
        }

    def describe_image(self, image_data: bytes, mime_type: str) -> str:
        """Cannot describe images directly."""
        return "YandexGPT не поддерживает анализ изображений напрямую"

    def extract_tags(self, image_data: bytes, mime_type: str) -> List[str]:
        """
        Generate generic tags based on file type.
        In practice, combine with OCR or other analysis.
        """
        base_tags = ['файл', 'изображение']

        if 'jpeg' in mime_type or 'jpg' in mime_type:
            base_tags.extend(['фото', 'JPEG'])
        elif 'png' in mime_type:
            base_tags.extend(['изображение', 'PNG'])
        elif 'gif' in mime_type:
            base_tags.extend(['анимация', 'GIF'])

        return base_tags

    def extract_colors(self, image_data: bytes, mime_type: str) -> List[Dict[str, Any]]:
        """Cannot extract colors without vision capabilities."""
        return []

    def generate_alt_text(self, image_data: bytes, mime_type: str) -> str:
        """Generate basic alt text using YandexGPT."""
        prompt = f"""Создайте краткое описание для изображения в формате {mime_type}.
        Это должно быть подходящее описание для атрибута alt в HTML, описывающее
        основное содержание изображения для людей с нарушениями зрения."""

        try:
            return self._make_request(prompt, max_tokens=100)
        except AIProviderError:
            return f"Изображение в формате {mime_type}"

    def is_available(self) -> bool:
        """Check if YandexGPT is available."""
        try:
            return bool(self.api_key and self.folder_id)
        except Exception as e:
            logger.error(f"YandexGPT availability check failed: {e}")
            return False
