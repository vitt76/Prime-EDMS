"""
Claude AI provider placeholder.

TODO: Implement Claude Vision API integration.
"""

from .base import BaseAIProvider


class ClaudeProvider(BaseAIProvider):
    """
    Anthropic Claude provider for image analysis.

    TODO: Implement full Claude Vision API integration.
    """

    name = 'claude'
    display_name = 'Claude Vision'
    description = 'Advanced image analysis using Claude Vision'

    supports_vision = True
    supports_text = True
    supports_image_description = True
    supports_tag_extraction = True
    supports_color_analysis = True

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        # Stub; see docs/TODO.md

    def analyze_image(self, image_data: bytes, mime_type: str):
        # Stub
        return {}

    def describe_image(self, image_data: bytes, mime_type: str) -> str:
        # Stub
        return "Claude analysis not yet implemented"

    def extract_tags(self, image_data: bytes, mime_type: str) -> list:
        # Stub
        return []

    def extract_colors(self, image_data: bytes, mime_type: str) -> list:
        # Stub
        return []

    def generate_alt_text(self, image_data: bytes, mime_type: str) -> str:
        # Stub
        return "Alt text generation not yet implemented"
