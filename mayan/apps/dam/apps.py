from mayan.apps.common.apps import MayanAppConfig
from django.utils.translation import ugettext_lazy as _


class DAMApp(MayanAppConfig):
    """
    Digital Asset Management extension for Mayan EDMS.

    Provides AI-powered metadata enrichment and advanced asset management
    capabilities using multiple AI providers including OpenAI, Claude, Gemini,
    YandexGPT, and GigaChat.
    """
    app_namespace = 'dam'
    app_url = 'dam'
    has_rest_api = True
    has_static_media = True
    has_tests = True
    name = 'mayan.apps.dam'
    verbose_name = _('Digital Asset Management')

    def ready(self):
        super().ready()
        print('🎨 DAM module loaded successfully!')

        # Регистрация AI провайдеров
        self._register_ai_providers()

        # Регистрация сигналов
        self._register_signals()

    def _register_ai_providers(self):
        """Регистрация доступных AI провайдеров"""
        from .ai_providers import AIProviderRegistry

        # Регистрация провайдеров
        AIProviderRegistry.register('openai', 'mayan.apps.dam.ai_providers.openai.OpenAIProvider')
        AIProviderRegistry.register('claude', 'mayan.apps.dam.ai_providers.claude.ClaudeProvider')
        AIProviderRegistry.register('gemini', 'mayan.apps.dam.ai_providers.gemini.GeminiProvider')
        AIProviderRegistry.register('yandexgpt', 'mayan.apps.dam.ai_providers.yandex.YandexGPTProvider')
        AIProviderRegistry.register('gigachat', 'mayan.apps.dam.ai_providers.gigachat.GigaChatProvider')

        print('🤖 AI providers registered successfully!')

    def _register_signals(self):
        """Регистрация сигналов для автоматического анализа"""
        from . import signals
        print('📡 DAM signals registered!')
