import abc
import os
from typing import Dict, List, Optional, Any
import logging

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


class AIProviderError(Exception):
    """Base exception for AI provider errors"""
    pass


class AIProviderRateLimitError(AIProviderError):
    """Rate limit exceeded"""
    pass


class AIProviderAuthError(AIProviderError):
    """Authentication error"""
    pass


class BaseAIProvider(metaclass=abc.ABCMeta):
    """
    Base class for AI providers.

    Defines the interface that all AI providers must implement.
    """

    # Provider metadata
    name = None
    display_name = None
    description = None

    # Capabilities
    supports_vision = False
    supports_text = True
    supports_image_description = False
    supports_tag_extraction = False
    supports_color_analysis = False

    def __init__(self, api_key: str, **kwargs):
        """
        Initialize AI provider.

        Args:
            api_key: API key for the provider
            **kwargs: Additional configuration options
        """
        self._settings_cache = {}

    def get_setting(self, setting_name: str, default=None):
        """Get setting value from Django smart_settings or environment variables."""
        cache_key = f"{self.name}_{setting_name}"

        if cache_key in self._settings_cache:
            return self._settings_cache[cache_key]

        # Try Django smart_setting first
        django_setting_name = f'DAM_{self.name.upper()}_{setting_name}'
        django_setting = getattr(settings, django_setting_name, None)
        if django_setting is not None and django_setting != '':
            self._settings_cache[cache_key] = django_setting
            return django_setting

        # Fallback to environment variable
        env_var = f'DAM_{self.name.upper()}_{setting_name}'
        env_value = os.getenv(env_var, default)
        self._settings_cache[cache_key] = env_value
        return env_value

    @abc.abstractmethod
    def analyze_image(self, image_data: bytes, mime_type: str) -> Dict[str, Any]:
        """
        Analyze image and extract metadata.

        Args:
            image_data: Raw image bytes
            mime_type: MIME type of the image

        Returns:
            Dict with analysis results
        """
        pass

    @abc.abstractmethod
    def describe_image(self, image_data: bytes, mime_type: str) -> str:
        """
        Generate textual description of an image.

        Args:
            image_data: Raw image bytes
            mime_type: MIME type of the image

        Returns:
            Textual description
        """
        pass

    @abc.abstractmethod
    def extract_tags(self, image_data: bytes, mime_type: str) -> List[str]:
        """
        Extract tags/keywords from an image.

        Args:
            image_data: Raw image bytes
            mime_type: MIME type of the image

        Returns:
            List of tags
        """
        pass

    @abc.abstractmethod
    def extract_colors(self, image_data: bytes, mime_type: str) -> List[Dict[str, Any]]:
        """
        Extract dominant colors from an image.

        Args:
            image_data: Raw image bytes
            mime_type: MIME type of the image

        Returns:
            List of color dictionaries with RGB/hex values
        """
        pass

    @abc.abstractmethod
    def generate_alt_text(self, image_data: bytes, mime_type: str) -> str:
        """
        Generate alt text for accessibility.

        Args:
            image_data: Raw image bytes
            mime_type: MIME type of the image

        Returns:
            Alt text string
        """
        pass

    def is_available(self) -> bool:
        """
        Check if the provider is available and properly configured.

        Returns:
            True if available, False otherwise
        """
        try:
            # Basic connectivity check
            return bool(self.api_key)
        except Exception as e:
            logger.error(f"Provider {self.name} availability check failed: {e}")
            return False

    def get_capabilities(self) -> Dict[str, bool]:
        """
        Get provider capabilities.

        Returns:
            Dict of capability flags
        """
        return {
            'vision': self.supports_vision,
            'text': self.supports_text,
            'image_description': self.supports_image_description,
            'tag_extraction': self.supports_tag_extraction,
            'color_analysis': self.supports_color_analysis,
        }


# Global registry instance
_providers_registry = {}

class AIProviderRegistry:
    """
    Registry for AI providers.

    Manages registration and instantiation of AI providers.
    """

    @classmethod
    def register(cls, provider_id: str, provider_class_path: str):
        """
        Register an AI provider.

        Args:
            provider_id: Unique identifier for the provider
            provider_class_path: Import path to the provider class
        """
        global _providers_registry
        _providers_registry[provider_id] = provider_class_path
        logger.info(f"Registered AI provider: {provider_id}")

    @classmethod
    def get_provider_class(cls, provider_id: str):
        """
        Get provider class by ID.

        Args:
            provider_id: Provider identifier

        Returns:
            Provider class
        """
        global _providers_registry
        if provider_id not in _providers_registry:
            raise ValueError(f"Unknown AI provider: {provider_id}")

        from django.utils.module_loading import import_string
        return import_string(_providers_registry[provider_id])

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """
        Get list of available provider IDs.

        Returns:
            List of provider identifiers
        """
        global _providers_registry
        return list(_providers_registry.keys())

    @classmethod
    def create_provider(cls, provider_id: str, **kwargs) -> BaseAIProvider:
        """
        Create and configure a provider instance.

        Args:
            provider_id: Provider identifier
            **kwargs: Provider configuration

        Returns:
            Configured provider instance
        """
        provider_class = cls.get_provider_class(provider_id)
        return provider_class(**kwargs)
