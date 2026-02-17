"""
Gemini AI provider — integration with Google Gemini Vision API.
"""

import base64
import json
import logging
from typing import Any, Dict, List

import requests

from .base import (
    BaseAIProvider,
    AIProviderError,
    AIProviderRateLimitError,
    AIProviderAuthError,
)

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    """
    Google Gemini provider for image analysis via generateContent API (vision).
    """

    name = 'gemini'
    display_name = 'Gemini Vision'
    description = 'Advanced image analysis using Google Gemini'

    supports_vision = True
    supports_text = True
    supports_image_description = True
    supports_tag_extraction = True
    supports_color_analysis = True

    def __init__(self, api_key: str, model: str = 'gemini-2.0-flash', **kwargs):
        super().__init__(api_key, **kwargs)
        self.api_key = api_key
        self.model = model
        self.base_url = 'https://generativelanguage.googleapis.com/v1beta'
        self.timeout = int(kwargs.get('timeout', 60))

    def _make_request(self, contents: List[Dict[str, Any]], max_tokens: int = 1024) -> str:
        """
        Call Gemini generateContent API.

        Args:
            contents: Request contents (parts with inline_data and/or text).
            max_tokens: Max output tokens.

        Returns:
            Response text from the first candidate.
        """
        url = f'{self.base_url}/models/{self.model}:generateContent'
        params = {'key': self.api_key}
        data = {
            'contents': [{'parts': contents}],
            'generationConfig': {
                'maxOutputTokens': max_tokens,
                'temperature': 0.7,
            },
        }
        try:
            response = requests.post(
                url,
                params=params,
                json=data,
                timeout=self.timeout,
            )
            if response.status_code == 429:
                raise AIProviderRateLimitError('Gemini API rate limit exceeded')
            if response.status_code == 401 or response.status_code == 403:
                raise AIProviderAuthError('Invalid Gemini API key')
            if not response.ok:
                raise AIProviderError(
                    f'Gemini API error: {response.status_code} - {response.text[:500]}'
                )
            body = response.json()
            candidates = body.get('candidates', [])
            if not candidates:
                return ''
            parts = candidates[0].get('content', {}).get('parts', [])
            for part in parts:
                if 'text' in part:
                    return part['text'].strip()
            return ''
        except requests.exceptions.Timeout:
            raise AIProviderError('Gemini API timeout')
        except requests.exceptions.RequestException as e:
            raise AIProviderError(f'Gemini API request failed: {e}')

    def _encode_image(self, image_data: bytes) -> str:
        return base64.b64encode(image_data).decode('utf-8')

    def _parts_with_image(self, image_data: bytes, mime_type: str, text: str) -> List[Dict]:
        media_type = mime_type if mime_type in ('image/jpeg', 'image/png', 'image/gif', 'image/webp') else 'image/jpeg'
        return [
            {'inline_data': {'mime_type': media_type, 'data': self._encode_image(image_data)}},
            {'text': text},
        ]

    def analyze_image(self, image_data: bytes, mime_type: str) -> Dict[str, Any]:
        """Analyze image and return structured metadata."""
        prompt = """Analyze this image and provide detailed information in JSON format with the following structure only (no markdown, no code block):
{
    "description": "Detailed description of the image content",
    "tags": ["tag1", "tag2", "tag3"],
    "colors": [
        {"name": "color_name", "hex": "#RRGGBB", "rgb": [R, G, B]}
    ],
    "alt_text": "Accessibility alt text",
    "categories": ["category1"],
    "people": [],
    "locations": []
}
Be specific and detailed. Use empty arrays where not applicable."""
        parts = self._parts_with_image(image_data, mime_type, prompt)
        text = self._make_request(parts, max_tokens=1000)
        text = text.strip()
        if text.startswith('```'):
            text = text.split('\n', 1)[-1].rsplit('```', 1)[0].strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = self._parse_text_fallback(text)
        return {
            'description': data.get('description', ''),
            'tags': data.get('tags', [])[:30],
            'colors': data.get('colors', [])[:15],
            'alt_text': data.get('alt_text', data.get('description', '')[:200]),
            'categories': data.get('categories', []),
            'people': data.get('people', []),
            'locations': data.get('locations', []),
        }

    def _parse_text_fallback(self, content: str) -> Dict[str, Any]:
        return {
            'description': content[:1000],
            'tags': [],
            'colors': [],
            'alt_text': content[:200],
            'categories': [],
            'people': [],
            'locations': [],
        }

    def describe_image(self, image_data: bytes, mime_type: str) -> str:
        """Generate detailed description of the image."""
        prompt = 'Provide a detailed, vivid description of this image. Be specific about colors, composition, subjects, and atmosphere.'
        parts = self._parts_with_image(image_data, mime_type, prompt)
        return self._make_request(parts, max_tokens=300).strip()

    def extract_tags(self, image_data: bytes, mime_type: str) -> List[str]:
        """Extract relevant tags/keywords from the image."""
        prompt = 'List relevant tags/keywords for this image as a comma-separated list. Focus on visual elements, objects, colors, mood, and style.'
        parts = self._parts_with_image(image_data, mime_type, prompt)
        text = self._make_request(parts, max_tokens=200).strip()
        tags = [t.strip() for t in text.split(',') if t.strip()]
        return tags[:20]

    def extract_colors(self, image_data: bytes, mime_type: str) -> List[Dict[str, Any]]:
        """Extract dominant colors from the image."""
        prompt = 'Describe the dominant colors in this image. List them as: Color Name: #HEXCODE (one per line).'
        parts = self._parts_with_image(image_data, mime_type, prompt)
        text = self._make_request(parts, max_tokens=200).strip()
        colors = []
        for line in text.split('\n'):
            if ':' in line and '#' in line:
                try:
                    name, hex_part = line.split(':', 1)
                    hex_code = hex_part.strip().split()[0] if hex_part.strip() else ''
                    if hex_code.startswith('#'):
                        colors.append({
                            'name': name.strip(),
                            'hex': hex_code,
                            'rgb': self._hex_to_rgb(hex_code),
                        })
                except (ValueError, IndexError):
                    continue
        return colors[:10]

    def _hex_to_rgb(self, hex_code: str) -> List[int]:
        hex_code = hex_code.lstrip('#')
        if len(hex_code) != 6:
            return [0, 0, 0]
        return [int(hex_code[i:i + 2], 16) for i in (0, 2, 4)]

    def generate_alt_text(self, image_data: bytes, mime_type: str) -> str:
        """Generate accessibility alt text."""
        prompt = 'Generate concise alt text for this image suitable for accessibility. Focus on the main subject and key visual elements.'
        parts = self._parts_with_image(image_data, mime_type, prompt)
        return self._make_request(parts, max_tokens=100).strip()
