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

    supports_vision = False  # GigaChat doesn't support vision API (only image generation)
    supports_text = True
    supports_image_description = False  # GigaChat cannot analyze images, only generate them
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
        """Analyze image using GigaChat Vision API."""
        try:
            import base64

            # Convert image to base64
            image_b64 = base64.b64encode(image_data).decode('utf-8')

            # Create vision prompt for image analysis
            prompt = """Проанализируй это изображение и предоставь структурированную информацию в формате JSON со следующими полями:

- description: подробное описание содержимого изображения (2-3 предложения)
- tags: массив ключевых слов/тегов на русском языке (5-10 элементов)
- categories: массив категорий/тем (2-4 элемента)
- language: основной язык содержимого (если применимо)
- people: массив имен людей/персонажей (если есть)
- locations: массив географических мест (если есть)

Ответ должен быть только в формате JSON без дополнительного текста."""

            client = self._get_client()

            # Try to use GigaChat Vision API
            try:
                # Create message with image using the correct format for GigaChat
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_b64}"
                                }
                            }
                        ]
                    }
                ]

                response = client.chat(messages=messages, model="GigaChat-2-Plus")

                # Parse response
                if hasattr(response, 'choices') and response.choices:
                    content = response.choices[0].message.content
                elif isinstance(response, str):
                    content = response
                else:
                    content = str(response)

                logger.info(f"GigaChat vision response: {content[:300]}...")

                # Try to parse JSON response
                try:
                    import json
                    result = json.loads(content.strip())
                    result['provider'] = 'gigachat'
                    # Ensure all required fields are present
                    result.setdefault('language', '')
                    result.setdefault('people', [])
                    result.setdefault('locations', [])
                    result.setdefault('copyright', '')
                    result.setdefault('usage_rights', '')
                    result.setdefault('colors', [])
                    result.setdefault('alt_text', result.get('description', f'Изображение в формате {mime_type.split("/")[1].upper()}'))
                    return result
                except json.JSONDecodeError as json_error:
                    logger.warning(f"JSON parsing failed: {json_error}, content: {content[:500]}")
                    # If not JSON, create structured response from text
                    return self._parse_vision_response(content)

            except Exception as vision_error:
                logger.warning(f"GigaChat vision API failed: {vision_error}")
                # Fallback to text-only analysis
                return self._fallback_image_analysis(mime_type, image_data)

        except Exception as e:
            logger.error(f"GigaChat image analysis failed: {e}")
            return self._fallback_image_analysis(mime_type, image_data)

    def _parse_vision_response(self, content: str) -> Dict[str, Any]:
        """Parse vision API response into structured format."""
        # Simple parsing for vision responses that aren't in JSON format
        description = content.strip()
        if len(description) > 500:
            description = description[:500] + "..."

        # Extract basic tags from description
        tags = ['изображение', 'фото']
        if 'город' in description.lower() or 'улица' in description.lower():
            tags.extend(['город', 'улица'])
        if 'люди' in description.lower() or 'человек' in description.lower():
            tags.extend(['люди', 'персонажи'])
        if 'вечер' in description.lower() or 'ночь' in description.lower():
            tags.extend(['вечер', 'освещение'])

        return {
            'description': description,
            'tags': tags[:10],  # Limit to 10 tags
            'categories': ['изображения', 'фотографии'],
            'language': 'ru',
            'people': [],
            'locations': [],
            'copyright': '',
            'usage_rights': '',
            'colors': [],
            'alt_text': description,
            'provider': 'gigachat'
        }

    def _parse_text_response(self, content: str) -> Dict[str, Any]:
        """Parse text response into structured format."""
        # Simple parsing - extract description and create basic tags
        description = content.strip()
        if len(description) > 200:
            description = description[:200] + "..."

        return {
            'description': description,
            'tags': ['изображение', 'фото', 'графика'],
            'categories': ['медиа'],
            'language': 'ru',
            'people': [],
            'locations': [],
            'copyright': '',
            'usage_rights': '',
            'colors': [],
            'alt_text': description,
            'provider': 'gigachat'
        }

    def _fallback_image_analysis(self, mime_type: str, image_data: bytes = None) -> Dict[str, Any]:
        """Fallback analysis when vision API fails."""
        from mayan.apps.dam.tasks import get_fallback_analysis
        return get_fallback_analysis(mime_type, image_data)

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
