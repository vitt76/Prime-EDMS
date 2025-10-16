from mayan.apps.common.apps import MayanAppConfig
from django.utils.translation import ugettext_lazy as _


class DistributionApp(MayanAppConfig):
    """
    Distribution - модуль публикации материалов для Mayan EDMS.
    Управление получателями, пресетами рендишенов, токен-порталом.
    """
    app_namespace = 'distribution'
    app_url = 'distribution'
    has_rest_api = True
    has_static_media = False
    has_tests = True
    name = 'mayan.apps.distribution'
    verbose_name = _('Distribution Module')
    label = 'distribution'

    def ready(self):
        super().ready()
        print('📦 Distribution module loaded successfully!')

        # Force add ourselves to INSTALLED_APPS if not already there
        from django.conf import settings
        app_name = 'mayan.apps.distribution'
        if app_name not in settings.INSTALLED_APPS:
            settings.INSTALLED_APPS.append(app_name)
            print(f'✅ Added {app_name} to INSTALLED_APPS via ready()')

        # Регистрация меню и ссылок
        print('🔗 Starting distribution menu registration...')
        try:
            self._register_menu_links()
            print('✅ Distribution menu links registered successfully!')
        except Exception as e:
            print(f'❌ CRITICAL: Failed to register menu links: {e}')
            import traceback
            traceback.print_exc()

        # URLs will be automatically discovered by REST API app via api_urls variable

    def _register_menu_links(self):
        """Регистрация всех меню и ссылок для distribution модуля"""
        from mayan.apps.documents.models import Document, DocumentFile
        from mayan.apps.common.menus import menu_main, menu_object

        # Импорт наших меню и ссылок
        from .menus import menu_distribution
        from .links.distribution_links import (
            link_document_test, link_document_publish, link_document_publications,
            link_document_file_add_to_publication
        )

        # ===== РЕГИСТРАЦИЯ В ГЛАВНОМ МЕНЮ =====

        # Добавляем наше меню в главное меню навигации
        menu_main.bind_links(
            links=(menu_distribution,),
            position=20  # После основных разделов
        )

        # ===== РЕГИСТРАЦИЯ В МЕНЮ ДОКУМЕНТОВ =====

        # Регистрация в меню документов
        menu_object.bind_links(
            links=(link_document_test, link_document_publish, link_document_publications),
            sources=(Document,),
            position=12
        )

        # Регистрация в меню файлов документов
        menu_object.bind_links(
            links=(link_document_file_add_to_publication,),
            sources=(DocumentFile,),
            position=10
        )

        print('✅ Distribution menu links registered successfully!')

