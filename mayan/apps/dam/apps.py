from mayan.apps.common.apps import MayanAppConfig
from mayan.apps.common.menus import menu_main
from mayan.apps.templating.classes import AJAXTemplate
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
    label = 'dam'

    def ready(self):
        print(f'🔍 DAM ready() called for {self.name}')
        super().ready()
        print('🎨 DAM module ready() called!')

        # Force add ourselves to INSTALLED_APPS if not already there
        from django.conf import settings
        app_name = 'mayan.apps.dam'
        if app_name not in settings.INSTALLED_APPS:
            settings.INSTALLED_APPS.append(app_name)
            print(f'✅ Added {app_name} to INSTALLED_APPS via ready()')

        # Ensure URLs are registered even if automatic wiring fails
        try:
            from django.conf.urls import include, url
            from mayan.urls import urlpatterns as mayan_urlpatterns

            if not any(getattr(pattern, 'namespace', None) == self.app_namespace for pattern in mayan_urlpatterns):
                mayan_urlpatterns += (
                    url(
                        regex=r'^dam/',
                        view=include(
                            ('mayan.apps.dam.urls', self.app_namespace),
                            namespace=self.app_namespace
                        )
                    ),
                )
                print('✅ DAM URLs registered manually via ready().')
        except Exception as exc:
            print(f'⚠️ DAM URL registration failed: {exc}')

        print('🎨 DAM module loaded successfully!')

    def _register_ai_providers(self):
        """Регистрация доступных AI провайдеров"""
        from .ai_providers import AIProviderRegistry

        print(f'🤖 Registering AI providers...')

        # Регистрация провайдеров
        AIProviderRegistry.register('openai', 'mayan.apps.dam.ai_providers.openai.OpenAIProvider')
        AIProviderRegistry.register('claude', 'mayan.apps.dam.ai_providers.claude.ClaudeProvider')
        AIProviderRegistry.register('gemini', 'mayan.apps.dam.ai_providers.gemini.GeminiProvider')
        AIProviderRegistry.register('yandexgpt', 'mayan.apps.dam.ai_providers.yandex.YandexGPTProvider')
        AIProviderRegistry.register('gigachat', 'mayan.apps.dam.ai_providers.gigachat.GigaChatProvider')

        print(f'🤖 AI providers registered: {list(AIProviderRegistry._providers.keys())}')
        print('🤖 AI providers registered successfully!')

    def _register_signals(self):
        """Регистрация сигналов для автоматического анализа"""
        from . import signals
        print('📡 DAM signals registered!')

    def _extend_search(self):
        """Extend document search with AI metadata fields."""
        try:
            from .search import extend_document_search
            extend_document_search()
            print('🔍 DAM search fields extended!')
        except Exception as e:
            print(f'⚠️  DAM search extension failed: {e}')

    def _register_ajax_templates(self):
        """Register AJAX templates for dynamic content loading."""
        try:
            AJAXTemplate(
                name='dam_document_detail',
                template_name='dam/ajax_document_dam.html'
            )
            print('🔄 DAM AJAX templates registered!')
        except Exception as e:
            print(f'⚠️  DAM AJAX templates registration failed: {e}')

    def _register_menus(self):
        """Register DAM links in document menus."""
        try:
            from .links import link_dam_dashboard, link_ai_analysis_list, link_dam_test

            # Add DAM links to document menu
            from mayan.apps.documents.apps import DocumentsApp
            from mayan.apps.documents.menus import menu_documents

            menu_documents.bind_links(
                links=(link_dam_dashboard, link_ai_analysis_list, link_dam_test),
                position=10
            )
            print('📋 DAM links added to Documents menu!')
        except Exception as e:
            print(f'⚠️  DAM menu registration failed: {e}')
