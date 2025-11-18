import logging
from typing import Dict, List, Any

from .base import BaseAIProvider, AIProviderError, AIProviderRateLimitError, AIProviderAuthError

logger = logging.getLogger(__name__)


class YandexGPTProvider(BaseAIProvider):
    """
    YandexGPT provider using yandexgptlite library.

    Lightweight integration with YandexGPT for text analysis.
    """

    name = 'yandexgpt'
    display_name = 'YandexGPT (yandexgptlite)'
    description = 'Russian AI model by Yandex (lightweight integration)'

    supports_vision = False  # YandexGPT doesn't support vision
    supports_text = True
    supports_image_description = False  # Can't analyze images directly
    supports_tag_extraction = True
    supports_color_analysis = False
    supports_alt_text_generation = True

    def __init__(self, api_key: str = None, folder_id: str = None, iam_token: str = None,
                 model: str = 'yandexgpt-lite', **kwargs):
        super().__init__(api_key or '', **kwargs)
        self.folder_id = folder_id
        self.iam_token = iam_token
        self.model = model
        self._client = None
        self.timeout = kwargs.get('timeout', 30)

    def _get_client(self):
        """Get or create yandexgptlite client."""
        if self._client is None:
            try:
                from yandexgptlite import YandexGPTLite
                # yandexgptlite requires folder and token as positional arguments
                token = self.api_key or self.iam_token
                if not token:
                    raise AIProviderError("No authentication token provided for YandexGPT")
                if not self.folder_id:
                    raise AIProviderError("Folder ID is required for YandexGPT")

                self._client = YandexGPTLite(self.folder_id, token)
            except ImportError:
                raise AIProviderError("yandexgptlite library not installed")
            except Exception as e:
                raise AIProviderError(f"Failed to initialize YandexGPT client: {e}")
        return self._client

    def _make_request(self, prompt: str, **kwargs) -> str:
        """
        Make request using yandexgptlite.
        """
        try:
            client = self._get_client()

            # yandexgptlite uses create_completion method
            response = client.create_completion(
                prompt=prompt,
                model=self.model,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 1000)
            )

            # Handle response format from yandexgptlite
            if isinstance(response, dict):
                # Try common response field names
                if 'text' in response:
                    return response['text']
                elif 'result' in response:
                    return response['result']
                elif 'completion' in response:
                    return response['completion']
                elif 'response' in response:
                    return response['response']
                else:
                    # Return the first string value found
                    for value in response.values():
                        if isinstance(value, str):
                            return value
                    return str(response)
            elif isinstance(response, str):
                return response
            else:
                return str(response)

        except Exception as e:
            if "rate limit" in str(e).lower() or "quota" in str(e).lower():
                raise AIProviderRateLimitError("YandexGPT rate limit exceeded")
            elif "auth" in str(e).lower() or "token" in str(e).lower() or "unauthorized" in str(e).lower():
                raise AIProviderAuthError(f"YandexGPT authentication failed: {e}")
            else:
                raise AIProviderError(f"YandexGPT request failed: {e}")

    def analyze_image(self, image_data: bytes, mime_type: str) -> Dict[str, Any]:
        """Limited image analysis (no direct vision support)."""
        return {
            'description': 'YandexGPT не поддерживает прямой анализ изображений',
            'tags': self.extract_tags(image_data, mime_type),
            'colors': [],
            'alt_text': self.generate_alt_text(image_data, mime_type),
            'objects': [],
            'mood': '',
            'style': ''
        }

    def describe_image(self, image_data: bytes, mime_type: str) -> str:
        """Cannot describe images directly."""
        return "YandexGPT имеет ограниченную поддержку анализа изображений"

    def extract_tags(self, image_data: bytes, mime_type: str) -> List[str]:
        """Generate tags using YandexGPT."""
        prompt = f"""На основе типа файла {mime_type} предложите релевантные теги/ключевые слова.
        Учитывайте тип файла и возможное содержание. Предоставьте теги через запятую на русском языке."""

        try:
            response = self._make_request(prompt, max_tokens=200)
            tags = [tag.strip() for tag in response.split(',') if tag.strip()]
            return tags[:15]
        except AIProviderError:
            return self._get_fallback_tags(mime_type)

    def _get_fallback_tags(self, mime_type: str) -> List[str]:
        """Get fallback tags based on mime type."""
        tags = ['файл']

        if 'image' in mime_type:
            tags.extend(['изображение', 'графика'])
            if 'jpeg' in mime_type:
                tags.extend(['фото', 'JPEG'])
            elif 'png' in mime_type:
                tags.extend(['прозрачный', 'PNG'])
        elif 'video' in mime_type:
            tags.extend(['видео', 'мультимедиа'])
        elif 'audio' in mime_type:
            tags.extend(['аудио', 'звук'])

        return tags

    def extract_colors(self, image_data: bytes, mime_type: str) -> List[Dict[str, Any]]:
        """Cannot extract colors without vision capabilities."""
        return []

    def generate_alt_text(self, image_data: bytes, mime_type: str) -> str:
        """Generate alt text using YandexGPT."""
        prompt = f"""Создайте краткое и информативное описание для файла типа {mime_type}.
        Это описание будет использоваться для людей с нарушениями зрения.
        Сосредоточьтесь на возможном содержании файла."""

        try:
            return self._make_request(prompt, max_tokens=150)
        except AIProviderError:
            return f"Файл типа {mime_type}"

    def is_available(self) -> bool:
        """Check if YandexGPT is available."""
        try:
            # Try to initialize client to validate configuration
            self._get_client()
            return bool(self.api_key or self.iam_token)
        except Exception as e:
            logger.error(f"YandexGPT availability check failed: {e}")
            return False