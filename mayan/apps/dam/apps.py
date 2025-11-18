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
    app_url = 'digital-assets'
    has_rest_api = True
    has_static_media = True
    has_tests = True
    name = 'mayan.apps.dam'
    verbose_name = _('Digital Asset Management')
    label = 'dam'

    def ready(self):
        print(f'🔍 DAM ready() called for {self.name}')
        print(f'📍 app_url: {self.app_url}, app_namespace: {self.app_namespace}')
        super().ready()

        # Регистрация настроек в системе
        try:
            from .settings import namespace
            # Namespace registration happens automatically when imported
            print('✅ DAM settings registered!')
        except Exception as e:
            print(f'⚠️ DAM settings registration failed: {e}')

        # Add DAM property to Document model
        self._add_dam_property_to_document()

        print('🎨 DAM module ready() called!')
        print(f'✅ DAM URL should be available at: /{self.app_url}/')

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

        # Register supporting components
        try:
            self._register_ai_providers()
            self._register_signals()
            self._extend_search()
            self._register_ajax_templates()
            self._register_menus()
            self._register_settings_menu()
        except Exception as exc:
            print(f'⚠️ DAM component registration failed during ready(): {exc}')
            # Continue with other components even if one fails
            pass

        print('🎨 DAM module loaded successfully!')

    def _register_ai_providers(self):
        """Регистрация доступных AI провайдеров"""
        try:
            from .ai_providers import AIProviderRegistry

            print(f'🤖 Registering AI providers...')

            # Регистрация провайдеров (GigaChat первым как наиболее надежный)
            AIProviderRegistry.register('gigachat', 'mayan.apps.dam.ai_providers.gigachat.GigaChatProvider')
            AIProviderRegistry.register('openai', 'mayan.apps.dam.ai_providers.openai.OpenAIProvider')
            AIProviderRegistry.register('claude', 'mayan.apps.dam.ai_providers.claude.ClaudeProvider')
            AIProviderRegistry.register('gemini', 'mayan.apps.dam.ai_providers.gemini.GeminiProvider')
            AIProviderRegistry.register('yandexgpt', 'mayan.apps.dam.ai_providers.yandex.YandexGPTProvider')

            print(f'🤖 AI providers registered: {list(AIProviderRegistry.get_available_providers())}')
            print('🤖 AI providers registered successfully!')
        except Exception as e:
            print(f'❌ Failed to register AI providers: {e}')
            import traceback
            traceback.print_exc()

    def _register_signals(self):
        """Регистрация сигналов для автоматического анализа"""
        from . import signals
        print('📡 DAM signals registered!')

    def _extend_search(self):
        """Extend document search with AI metadata fields."""
        try:
            from .search import extend_document_search
            extend_document_search()
            print('🔍 DAM search fields extension enabled!')
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

    def _add_dam_property_to_document(self):
        """Add dam_analysis property to Document model dynamically."""
        try:
            from mayan.apps.documents.models import Document

            def dam_analysis_property(self):
                """
                Get AI analysis for this document.
                Returns None if no analysis exists (for form compatibility).
                """
                try:
                    return self.ai_analysis
                except:
                    return None

            # Add property to Document model
            Document.dam_analysis = property(dam_analysis_property)
            print('✅ Added dam_analysis property to Document model')
        except Exception as e:
            print(f'⚠️  Failed to add dam_analysis property: {e}')

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

    def _register_settings_menu(self):
        """Register DAM settings link in system menu."""
        try:
            from .links import link_dam_settings

            # Add DAM settings to setup menu
            from mayan.apps.common.menus import menu_setup
            menu_setup.bind_links(
                links=(link_dam_settings,),
                position=20
            )
            print('📋 DAM settings link added to System menu!')
        except Exception as e:
            print(f'⚠️  DAM settings menu registration failed: {e}')
