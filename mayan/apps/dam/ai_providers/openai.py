import base64
import json
import logging
from typing import Dict, List, Any, Optional

import requests
from django.conf import settings

from .base import BaseAIProvider, AIProviderError, AIProviderRateLimitError, AIProviderAuthError

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI Vision API provider for image analysis.
    """

    name = 'openai'
    display_name = 'OpenAI Vision'
    description = 'Advanced image analysis using GPT-4 Vision'

    supports_vision = True
    supports_text = True
    supports_image_description = True
    supports_tag_extraction = True
    supports_color_analysis = True

    def __init__(self, api_key: str, model: str = 'gpt-4-vision-preview', **kwargs):
        super().__init__(api_key, **kwargs)
        self.model = model
        self.base_url = 'https://api.openai.com/v1'
        self.timeout = kwargs.get('timeout', 30)

    def _make_request(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """
        Make request to OpenAI API.

        Args:
            messages: Chat messages
            **kwargs: Additional parameters

        Returns:
            API response
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': self.model,
            'messages': messages,
            'max_tokens': kwargs.get('max_tokens', 500),
            'temperature': kwargs.get('temperature', 0.7)
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )

            if response.status_code == 429:
                raise AIProviderRateLimitError("OpenAI rate limit exceeded")
            elif response.status_code == 401:
                raise AIProviderAuthError("Invalid OpenAI API key")
            elif not response.ok:
                raise AIProviderError(f"OpenAI API error: {response.status_code} - {response.text}")

            return response.json()

        except requests.exceptions.Timeout:
            raise AIProviderError("OpenAI API timeout")
        except requests.exceptions.RequestException as e:
            raise AIProviderError(f"OpenAI API request failed: {e}")

    def _encode_image(self, image_data: bytes) -> str:
        """Encode image data to base64."""
        return base64.b64encode(image_data).decode('utf-8')

    def analyze_image(self, image_data: bytes, mime_type: str) -> Dict[str, Any]:
        """Analyze image and return comprehensive results."""
        base64_image = self._encode_image(image_data)

        messages = [{
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': """Analyze this image and provide detailed information in JSON format with the following structure:
{
    "description": "Detailed description of the image content",
    "tags": ["tag1", "tag2", "tag3"],
    "colors": [
        {"name": "color_name", "hex": "#RRGGBB", "rgb": [R, G, B]},
        ...
    ],
    "alt_text": "Accessibility alt text",
    "objects": ["object1", "object2"],
    "mood": "atmosphere/feeling",
    "style": "artistic style if applicable"
}
Be specific and detailed in your analysis."""
                },
                {
                    'type': 'image_url',
                    'image_url': {
                        'url': f"data:{mime_type};base64,{base64_image}"
                    }
                }
            ]
        }]

        response = self._make_request(messages, max_tokens=1000)
        content = response['choices'][0]['message']['content']

        # Try to parse JSON response
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback: extract information from text
            return self._parse_text_response(content)

    def _parse_text_response(self, content: str) -> Dict[str, Any]:
        """Parse non-JSON response into structured data."""
        # Basic fallback parsing
        return {
            'description': content[:500],
            'tags': [],
            'colors': [],
            'alt_text': content[:200],
            'objects': [],
            'mood': '',
            'style': ''
        }

    def describe_image(self, image_data: bytes, mime_type: str) -> str:
        """Generate detailed description of the image."""
        base64_image = self._encode_image(image_data)

        messages = [{
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': 'Provide a detailed, vivid description of this image. Be specific about colors, composition, subjects, and atmosphere.'
                },
                {
                    'type': 'image_url',
                    'image_url': {
                        'url': f"data:{mime_type};base64,{base64_image}"
                    }
                }
            ]
        }]

        response = self._make_request(messages, max_tokens=300)
        return response['choices'][0]['message']['content'].strip()

    def extract_tags(self, image_data: bytes, mime_type: str) -> List[str]:
        """Extract relevant tags from the image."""
        base64_image = self._encode_image(image_data)

        messages = [{
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': 'List relevant tags/keywords for this image. Provide them as a comma-separated list. Focus on visual elements, objects, colors, mood, and style.'
                },
                {
                    'type': 'image_url',
                    'image_url': {
                        'url': f"data:{mime_type};base64,{base64_image}"
                    }
                }
            ]
        }]

        response = self._make_request(messages, max_tokens=200)
        content = response['choices'][0]['message']['content']

        # Parse comma-separated tags
        tags = [tag.strip() for tag in content.split(',') if tag.strip()]
        return tags[:20]  # Limit to 20 tags

    def extract_colors(self, image_data: bytes, mime_type: str) -> List[Dict[str, Any]]:
        """Extract dominant colors from the image."""
        # For OpenAI, we'll use a simpler approach since it doesn't have built-in color analysis
        # In a real implementation, you might want to use a separate color analysis library
        # or ask GPT to describe colors

        base64_image = self._encode_image(image_data)

        messages = [{
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': 'Describe the dominant colors in this image. List them with their names and approximate hex codes. Format: Color Name: #HEXCODE'
                },
                {
                    'type': 'image_url',
                    'image_url': {
                        'url': f"data:{mime_type};base64,{base64_image}"
                    }
                }
            ]
        }]

        response = self._make_request(messages, max_tokens=200)
        content = response['choices'][0]['message']['content']

        # Parse color descriptions
        colors = []
        for line in content.split('\n'):
            if ':' in line and '#' in line:
                try:
                    name, hex_code = line.split(':', 1)
                    colors.append({
                        'name': name.strip(),
                        'hex': hex_code.strip(),
                        'rgb': self._hex_to_rgb(hex_code.strip())
                    })
                except:
                    continue

        return colors[:10]  # Limit to 10 colors

    def _hex_to_rgb(self, hex_code: str) -> List[int]:
        """Convert hex color to RGB list."""
        hex_code = hex_code.lstrip('#')
        return [int(hex_code[i:i+2], 16) for i in (0, 2, 4)]

    def generate_alt_text(self, image_data: bytes, mime_type: str) -> str:
        """Generate accessibility alt text."""
        base64_image = self._encode_image(image_data)

        messages = [{
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': 'Generate concise alt text for this image suitable for accessibility purposes. Focus on the main subject and key visual elements.'
                },
                {
                    'type': 'image_url',
                    'image_url': {
                        'url': f"data:{mime_type};base64,{base64_image}"
                    }
                }
            ]
        }]

        response = self._make_request(messages, max_tokens=100)
        return response['choices'][0]['message']['content'].strip()
