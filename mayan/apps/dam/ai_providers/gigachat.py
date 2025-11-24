import io
import logging
import mimetypes
import os
from typing import Dict, List, Any

from gigachat.exceptions import ResponseError
from gigachat.models import Chat, Messages
from PIL import Image

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

    supports_vision = True
    supports_text = True
    supports_image_description = True
    supports_tag_extraction = True
    supports_color_analysis = False
    supports_alt_text_generation = True

    def __init__(self, credentials: str = None, scope: str = 'GIGACHAT_API_PERS',
                 verify_ssl_certs: bool = False, model: str = 'GigaChat', **kwargs):
        super().__init__('', **kwargs)

        # Use settings with environment variable fallback
        self.credentials = credentials or self.get_setting('CREDENTIALS', os.getenv('DAM_GIGACHAT_CREDENTIALS', ''))
        self.scope = scope or self.get_setting('SCOPE', os.getenv('DAM_GIGACHAT_SCOPE', 'GIGACHAT_API_PERS'))
        self.verify_ssl_certs = verify_ssl_certs if verify_ssl_certs is not None else self.get_setting('VERIFY_SSL_CERTS', False)
        self.model = model or self.get_setting('MODEL', os.getenv('DAM_GIGACHAT_MODEL', 'GigaChat'))

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
        """Analyze image using GigaChat Vision workflow (upload + attachments)."""
        upload = None
        client = self._get_client()

        prompt = """Проанализируй прикреплённое изображение и верни JSON со следующими полями:

- description: подробное описание содержимого (2-3 предложения)
- tags: массив ключевых слов/тегов на русском языке (5-10 элементов)
- categories: массив категорий/тем (2-4 элемента)
- language: основной язык содержимого (если применимо)
- people: массив имён людей/персонажей (если есть)
- locations: массив географических мест (если есть)
- copyright: сведения об авторских правах (если есть)
- usage_rights: условия использования (если есть)

Ответ должен быть строго в формате JSON без дополнительного текста."""

        try:
            extension = mimetypes.guess_extension(mime_type) or '.bin'
            filename = f'dam-vision-input{extension}'

            try:
                upload = self._upload_image(
                    client=client,
                    filename=filename,
                    data=image_data,
                    mime_type=mime_type
                )
            except ResponseError as upload_error:
                if 'File format' in str(upload_error).lower():
                    logger.warning('GigaChat rejected %s, converting to JPEG.', mime_type)
                    converted_bytes, converted_mime, converted_ext = self._convert_to_jpeg(image_data)
                    upload = self._upload_image(
                        client=client,
                        filename=f'dam-vision-input{converted_ext}',
                        data=converted_bytes,
                        mime_type=converted_mime
                    )
                else:
                    raise

            chat = Chat(
                model=self.model or "GigaChat",
                messages=[
                    Messages(
                        role='user',
                        content=prompt,
                        attachments=[upload.id_]
                    )
                ]
            )

            response = client.chat(chat)

            if hasattr(response, 'choices') and response.choices:
                content = response.choices[0].message.content
            elif isinstance(response, str):
                content = response
            else:
                content = str(response)

            logger.info(f"GigaChat vision response: {content[:300]}...")

            try:
                import json
                parsed = json.loads(content.strip())
            except json.JSONDecodeError as json_error:
                logger.warning(f"JSON parsing failed: {json_error}, content: {content[:500]}")
                return self._parse_vision_response(content)
            else:
                parsed.setdefault('language', '')
                parsed.setdefault('people', [])
                parsed.setdefault('locations', [])
                parsed.setdefault('copyright', '')
                parsed.setdefault('usage_rights', '')
                parsed.setdefault('colors', [])
                parsed.setdefault(
                    'alt_text',
                    parsed.get('description', f'Изображение в формате {mime_type.split("/")[1].upper()}')
                )
                parsed['provider'] = 'gigachat'
                return parsed

        except Exception as e:
            logger.error(f"GigaChat image analysis failed: {e}")
            return self._fallback_image_analysis(mime_type, image_data)
        finally:
            if upload:
                try:
                    client.delete_file(upload.id_)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to delete temporary GigaChat file {upload.id_}: {cleanup_error}")

    def _upload_image(self, client, filename: str, data: bytes, mime_type: str):
        return client.upload_file(
            file=(filename, data, mime_type),
            purpose='general'
        )

    def _convert_to_jpeg(self, image_data: bytes):
        image = Image.open(io.BytesIO(image_data))
        buffer = io.BytesIO()
        image.convert('RGB').save(buffer, format='JPEG', quality=90)
        buffer.seek(0)
        return buffer.read(), 'image/jpeg', '.jpg'

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
