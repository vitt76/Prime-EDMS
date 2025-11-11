import logging
from typing import Dict, List, Any

from .base import BaseAIProvider, AIProviderError, AIProviderRateLimitError, AIProviderAuthError

logger = logging.getLogger(__name__)


class GigaChatProvider(BaseAIProvider):
    """
    GigaChat provider using official gigachat library.

    Sber's GigaChat model with Russian language support.
    """

    name = 'gigachat'
    display_name = 'GigaChat (Official)'
    description = 'Russian AI model by Sber (official library)'

    supports_vision = False  # Limited vision support
    supports_text = True
    supports_image_description = False
    supports_tag_extraction = True
    supports_color_analysis = False
    supports_alt_text_generation = True

    def __init__(self, credentials: str = None, scope: str = 'GIGACHAT_API_PERS',
                 verify_ssl_certs: bool = False, model: str = 'GigaChat', **kwargs):
        super().__init__('', **kwargs)
        self.credentials = credentials
        self.scope = scope
        self.verify_ssl_certs = verify_ssl_certs
        self.model = model
        self._client = None

    def _get_client(self):
        """Get or create GigaChat client."""
        if self._client is None:
            try:
                from gigachat import GigaChat
                self._client = GigaChat(
                    credentials=self.credentials,
                    scope=self.scope,
                    verify_ssl_certs=self.verify_ssl_certs,
                    model=self.model
                )
            except ImportError:
                raise AIProviderError("gigachat library not installed")
            except Exception as e:
                raise AIProviderError(f"Failed to initialize GigaChat client: {e}")
        return self._client

    def _make_request(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Make request using official GigaChat library.
        Returns structured response with metadata fields.
        """
        try:
            client = self._get_client()

            # Enhanced prompt for structured metadata extraction
            structured_prompt = f"""{prompt}

Пожалуйста, проанализируй этот файл и предоставь структурированную информацию в формате JSON со следующими полями:

- description: подробное описание содержимого (2-3 предложения)
- tags: массив ключевых слов/тегов на русском языке (5-10 элементов)
- categories: массив категорий/тем (2-4 элемента)
- language: основной язык содержимого (если применимо)
- people: массив имен людей/персонажей (если есть)
- locations: массив географических мест (если есть)
- copyright: информация об авторских правах (если есть)
- usage_rights: условия использования (если есть)

Ответ должен быть только в формате JSON без дополнительного текста."""

            # Use the chat method
            response = client.chat(structured_prompt)

            # Handle response format
            if hasattr(response, 'choices') and response.choices:
                content = response.choices[0].message.content
            elif isinstance(response, str):
                content = response
            else:
                content = str(response)

            # Try to parse as JSON - handle markdown code blocks
            try:
                import json
                import re

                # Remove markdown code block formatting if present
                json_content = content.strip()
                json_match = re.search(r'```json\s*(.*?)\s*```', json_content, re.DOTALL)
                if json_match:
                    json_content = json_match.group(1)

                parsed = json.loads(json_content)

                # Validate and normalize structure
                return {
                    'description': parsed.get('description', ''),
                    'tags': parsed.get('tags', []) if isinstance(parsed.get('tags'), list) else [],
                    'categories': parsed.get('categories', []) if isinstance(parsed.get('categories'), list) else [],
                    'language': parsed.get('language', ''),
                    'people': parsed.get('people', []) if isinstance(parsed.get('people'), list) else [],
                    'locations': parsed.get('locations', []) if isinstance(parsed.get('locations'), list) else [],
                    'copyright': parsed.get('copyright', ''),
                    'usage_rights': parsed.get('usage_rights', ''),
                    'provider': 'gigachat'
                }
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"JSON parsing failed: {e}, content: {content[:200]}...")
                # Fallback: extract basic description
                return {
                    'description': content.strip(),
                    'tags': [],
                    'categories': [],
                    'language': '',
                    'people': [],
                    'locations': [],
                    'copyright': '',
                    'usage_rights': '',
                    'provider': 'gigachat'
                }

        except Exception as e:
            if "rate limit" in str(e).lower() or "429" in str(e):
                raise AIProviderRateLimitError("GigaChat rate limit exceeded")
            elif "auth" in str(e).lower() or "token" in str(e).lower() or "401" in str(e):
                raise AIProviderAuthError(f"GigaChat authentication failed: {e}")
            else:
                raise AIProviderError(f"GigaChat request failed: {e}")

    def analyze_image(self, image_data: bytes, mime_type: str) -> Dict[str, Any]:
        """Analyze image using GigaChat with structured metadata extraction."""
        # Create prompt for image analysis
        prompt = f"Проанализируй файл типа {mime_type}."

        # Get structured response from GigaChat
        try:
            structured_response = self._make_request(prompt)
            return structured_response
        except Exception as e:
            logger.warning(f"GigaChat structured analysis failed: {e}")
            # Fallback to basic analysis
            return {
                'description': f'Файл типа {mime_type} - анализ не удался',
                'tags': self.extract_tags(image_data, mime_type),
                'categories': [],
                'language': '',
                'people': [],
                'locations': [],
                'copyright': '',
                'usage_rights': '',
                'colors': [],
                'alt_text': self.generate_alt_text(image_data, mime_type),
                'provider': 'gigachat'
            }

    def describe_image(self, image_data: bytes, mime_type: str) -> str:
        """Cannot describe images directly."""
        return "GigaChat имеет ограниченную поддержку анализа изображений"

    def extract_tags(self, image_data: bytes, mime_type: str) -> List[str]:
        """Generate tags using GigaChat."""
        prompt = f"""Проанализируйте файл типа {mime_type} и предложите релевантные теги/ключевые слова.
        Учитывайте тип файла и возможное содержание. Предоставьте теги через запятую на русском языке."""

        try:
            response = self._make_request(prompt, max_tokens=200)
            tags = [tag.strip() for tag in response.split(',') if tag.strip()]
            return tags[:15]  # Limit to 15 tags
        except AIProviderError:
            return self._get_fallback_tags(mime_type)

    def _get_fallback_tags(self, mime_type: str) -> List[str]:
        """Get fallback tags based on mime type."""
        base_tags = ['файл']

        if 'image' in mime_type:
            base_tags.extend(['изображение', 'графика'])
            if 'jpeg' in mime_type:
                base_tags.extend(['фото', 'JPEG'])
            elif 'png' in mime_type:
                base_tags.extend(['прозрачный', 'PNG'])
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
            return self._make_request(prompt, max_tokens=150)
        except AIProviderError:
            return f"Файл типа {mime_type}"

    def is_available(self) -> bool:
        """Check if GigaChat is available."""
        try:
            return bool(self.credentials)
        except Exception as e:
            logger.error(f"GigaChat availability check failed: {e}")
            return False
