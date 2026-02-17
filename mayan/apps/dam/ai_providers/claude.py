"""
Claude AI provider — integration with Anthropic Claude Vision API.
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


class ClaudeProvider(BaseAIProvider):
    """
    Anthropic Claude provider for image analysis via Messages API (vision).
    """

    name = 'claude'
    display_name = 'Claude Vision'
    description = 'Advanced image analysis using Claude Vision'

    supports_vision = True
    supports_text = True
    supports_image_description = True
    supports_tag_extraction = True
    supports_color_analysis = True

    def __init__(self, api_key: str, model: str = 'claude-3-5-sonnet-20241022', **kwargs):
        super().__init__(api_key, **kwargs)
        self.api_key = api_key
        self.model = model
        self.base_url = 'https://api.anthropic.com/v1'
        self.timeout = int(kwargs.get('timeout', 60))

    def _make_request(self, content: List[Dict[str, Any]], max_tokens: int = 1024) -> str:
        """
        Call Claude Messages API.

        Args:
            content: List of content blocks (image + text).
            max_tokens: Max tokens in response.

        Returns:
            Response text from the first content block.
        """
        url = f'{self.base_url}/messages'
        headers = {
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01',
            'Content-Type': 'application/json',
        }
        data = {
            'model': self.model,
            'max_tokens': max_tokens,
            'messages': [{'role': 'user', 'content': content}],
        }
        try:
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=self.timeout,
            )
            if response.status_code == 429:
                raise AIProviderRateLimitError('Claude API rate limit exceeded')
            if response.status_code == 401:
                raise AIProviderAuthError('Invalid Claude API key')
            if not response.ok:
                raise AIProviderError(
                    f'Claude API error: {response.status_code} - {response.text[:500]}'
                )
            body = response.json()
            for block in body.get('content', []):
                if block.get('type') == 'text':
                    return block.get('text', '')
            return ''
        except requests.exceptions.Timeout:
            raise AIProviderError('Claude API timeout')
        except requests.exceptions.RequestException as e:
            raise AIProviderError(f'Claude API request failed: {e}')

    def _encode_image(self, image_data: bytes) -> str:
        return base64.b64encode(image_data).decode('utf-8')

    def _content_with_image(self, image_data: bytes, mime_type: str, text_prompt: str) -> List[Dict]:
        media_type = mime_type if mime_type in ('image/jpeg', 'image/png', 'image/gif', 'image/webp') else 'image/jpeg'
        b64 = self._encode_image(image_data)
        return [
            {
                'type': 'image',
                'source': {'type': 'base64', 'media_type': media_type, 'data': b64},
            },
            {'type': 'text', 'text': text_prompt},
        ]

    def analyze_image(self, image_data: bytes, mime_type: str) -> Dict[str, Any]:
        """Analyze image and return structured metadata (description, tags, colors, alt_text)."""
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
        content = self._content_with_image(image_data, mime_type, prompt)
        text = self._make_request(content, max_tokens=1000)
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
        content = self._content_with_image(image_data, mime_type, prompt)
        return self._make_request(content, max_tokens=300).strip()

    def extract_tags(self, image_data: bytes, mime_type: str) -> List[str]:
        """Extract relevant tags/keywords from the image."""
        prompt = 'List relevant tags/keywords for this image as a comma-separated list. Focus on visual elements, objects, colors, mood, and style.'
        content = self._content_with_image(image_data, mime_type, prompt)
        text = self._make_request(content, max_tokens=200).strip()
        tags = [t.strip() for t in text.split(',') if t.strip()]
        return tags[:20]

    def extract_colors(self, image_data: bytes, mime_type: str) -> List[Dict[str, Any]]:
        """Extract dominant colors from the image."""
        prompt = 'Describe the dominant colors in this image. List them as: Color Name: #HEXCODE (one per line).'
        content = self._content_with_image(image_data, mime_type, prompt)
        text = self._make_request(content, max_tokens=200).strip()
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
        content = self._content_with_image(image_data, mime_type, prompt)
        return self._make_request(content, max_tokens=100).strip()
