import json
import logging
import time
from typing import Dict, List, Any

import requests
from django.conf import settings

from .base import BaseAIProvider, AIProviderError, AIProviderRateLimitError, AIProviderAuthError

logger = logging.getLogger(__name__)


class GigaChatProvider(BaseAIProvider):
    """
    GigaChat provider for AI analysis.

    Sber's GigaChat model with some vision capabilities.
    """

    name = 'gigachat'
    display_name = 'GigaChat'
    description = 'Russian AI model by Sber'

    supports_vision = False  # Limited vision support
    supports_text = True
    supports_image_description = False
    supports_tag_extraction = True
    supports_color_analysis = False
    supports_alt_text_generation = True

    def __init__(self, client_id: str, client_secret: str, model: str = 'GigaChat', **kwargs):
        super().__init__('', **kwargs)  # API key not used directly
        self.client_id = client_id
        self.client_secret = client_secret
        self.model = model
        self.base_url = 'https://gigachat.devices.sberbank.ru/api/v1'
        self.timeout = kwargs.get('timeout', 30)
        self._access_token = None
        self._token_expires = 0

    def _get_access_token(self) -> str:
        """
        Get or refresh access token for GigaChat API.

        Returns:
            Access token
        """
        current_time = time.time()

        # Check if token is still valid (with 5 minute buffer)
        if self._access_token and current_time < (self._token_expires - 300):
            return self._access_token

        # Get new token
        auth_url = 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth'

        data = {
            'scope': 'GIGACHAT_API_PERS'
        }

        try:
            response = requests.post(
                auth_url,
                auth=(self.client_id, self.client_secret),
                data=data,
                timeout=self.timeout
            )

            if not response.ok:
                if response.status_code == 429:
                    raise AIProviderRateLimitError("GigaChat rate limit exceeded")
                elif response.status_code == 401:
                    raise AIProviderAuthError("Invalid GigaChat credentials")
                else:
                    raise AIProviderError(f"GigaChat auth error: {response.status_code} - {response.text}")

            result = response.json()
            self._access_token = result['access_token']

            # Token expires in 30 minutes (1800 seconds)
            self._token_expires = current_time + 1800

            return self._access_token

        except requests.exceptions.Timeout:
            raise AIProviderError("GigaChat auth timeout")
        except requests.exceptions.RequestException as e:
            raise AIProviderError(f"GigaChat auth request failed: {e}")

    def _make_request(self, messages: List[Dict], **kwargs) -> str:
        """
        Make request to GigaChat API.

        Args:
            messages: Chat messages
            **kwargs: Additional parameters

        Returns:
            Generated text response
        """
        access_token = self._get_access_token()

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': self.model,
            'messages': messages,
            'max_tokens': kwargs.get('max_tokens', 1000),
            'temperature': kwargs.get('temperature', 0.7),
            'stream': False
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=self.timeout
            )

            if response.status_code == 429:
                raise AIProviderRateLimitError("GigaChat rate limit exceeded")
            elif response.status_code == 401:
                # Token might be expired, reset it
                self._access_token = None
                self._token_expires = 0
                raise AIProviderAuthError("GigaChat token expired")
            elif not response.ok:
                raise AIProviderError(f"GigaChat API error: {response.status_code} - {response.text}")

            result = response.json()
            return result['choices'][0]['message']['content']

        except requests.exceptions.Timeout:
            raise AIProviderError("GigaChat API timeout")
        except requests.exceptions.RequestException as e:
            raise AIProviderError(f"GigaChat API request failed: {e}")

    def analyze_image(self, image_data: bytes, mime_type: str) -> Dict[str, Any]:
        """Limited image analysis through text descriptions."""
        return {
            'description': 'Изображение не может быть проанализировано - GigaChat имеет ограниченную поддержку изображений',
            'tags': self.extract_tags(image_data, mime_type),
            'colors': [],
            'alt_text': self.generate_alt_text(image_data, mime_type),
            'objects': [],
            'mood': '',
            'style': ''
        }

    def describe_image(self, image_data: bytes, mime_type: str) -> str:
        """Cannot describe images directly."""
        return "GigaChat имеет ограниченную поддержку анализа изображений"

    def extract_tags(self, image_data: bytes, mime_type: str) -> List[str]:
        """Generate tags using GigaChat."""
        prompt = f"""Проанализируйте файл типа {mime_type} и предложите релевантные теги/ключевые слова.
        Учитывайте тип файла и возможное содержание. Предоставьте теги через запятую."""

        try:
            response = self._make_request([{'role': 'user', 'content': prompt}])
            tags = [tag.strip() for tag in response.split(',') if tag.strip()]
            return tags[:15]  # Limit to 15 tags
        except AIProviderError:
            # Fallback tags based on mime type
            return self._get_fallback_tags(mime_type)

    def _get_fallback_tags(self, mime_type: str) -> List[str]:
        """Get fallback tags based on mime type."""
        base_tags = ['файл']

        if 'image' in mime_type:
            base_tags.append('изображение')
            if 'jpeg' in mime_type:
                base_tags.extend(['фото', 'JPEG'])
            elif 'png' in mime_type:
                base_tags.extend(['графика', 'PNG'])
        elif 'video' in mime_type:
            base_tags.extend(['видео', 'мультимедиа'])
        elif 'audio' in mime_type:
            base_tags.extend(['аудио', 'звук'])

        return base_tags

    def extract_colors(self, image_data: bytes, mime_type: str) -> List[Dict[str, Any]]:
        """Cannot extract colors without vision capabilities."""
        return []

    def generate_alt_text(self, image_data: bytes, mime_type: str) -> str:
        """Generate alt text using GigaChat."""
        prompt = f"""Создайте краткое и информативное описание для файла типа {mime_type}.
        Это описание будет использоваться для людей с нарушениями зрения.
        Сосредоточьтесь на возможном содержании файла."""

        try:
            return self._make_request([{'role': 'user', 'content': prompt}], max_tokens=100)
        except AIProviderError:
            return f"Файл типа {mime_type}"

    def is_available(self) -> bool:
        """Check if GigaChat is available."""
        try:
            return bool(self.client_id and self.client_secret)
        except Exception as e:
            logger.error(f"GigaChat availability check failed: {e}")
            return False
