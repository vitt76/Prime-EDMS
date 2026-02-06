"""Provider registry for external analytics adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Type

from .base import BaseAnalyticsProvider


@dataclass(frozen=True)
class ProviderSpec:
    provider_id: str
    channel: str
    cls: Type[BaseAnalyticsProvider]


class AnalyticsProviderRegistry:
    """Simple in-process registry for analytics providers."""

    _providers: Dict[str, ProviderSpec] = {}
    _channels: Dict[str, ProviderSpec] = {}

    @classmethod
    def register(cls, provider_cls: Type[BaseAnalyticsProvider]) -> None:
        provider_id = (getattr(provider_cls, 'provider_id', '') or '').strip()
        channel = (getattr(provider_cls, 'channel', '') or '').strip()
        if not provider_id or not channel:
            return
        spec = ProviderSpec(provider_id=provider_id, channel=channel, cls=provider_cls)
        cls._providers[provider_id] = spec
        cls._channels[channel] = spec

    @classmethod
    def get_by_provider_id(cls, provider_id: str) -> Optional[BaseAnalyticsProvider]:
        spec = cls._providers.get((provider_id or '').strip())
        return spec.cls() if spec else None

    @classmethod
    def get_by_channel(cls, channel: str) -> Optional[BaseAnalyticsProvider]:
        spec = cls._channels.get((channel or '').strip())
        return spec.cls() if spec else None


def register_default_providers() -> None:
    """Register built-in stub providers."""
    from .email import EmailAnalyticsProvider
    from .wildberries import WildberriesAnalyticsProvider
    from .youtube import YouTubeAnalyticsProvider

    AnalyticsProviderRegistry.register(EmailAnalyticsProvider)
    AnalyticsProviderRegistry.register(WildberriesAnalyticsProvider)
    AnalyticsProviderRegistry.register(YouTubeAnalyticsProvider)


