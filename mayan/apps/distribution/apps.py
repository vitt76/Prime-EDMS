from mayan.apps.common.apps import MayanAppConfig
from django.utils.translation import ugettext_lazy as _


class DistributionApp(MayanAppConfig):
    """
    Distribution - модуль публикации материалов для Mayan EDMS.
    Управление получателями, пресетами рендишенов, токен-порталом.
    """
    app_namespace = 'distribution'
    app_url = ''
    has_rest_api = True
    has_static_media = False
    has_tests = True
    name = 'mayan.apps.distribution'
    verbose_name = _('Distribution Module')
    label = 'distribution'

    def ready(self):
        super().ready()

        # Ensure settings and storages are registered
        from . import settings as distribution_settings  # noqa: F401
        from . import storages as distribution_storages  # noqa: F401
        # Register permissions
        from . import permissions as distribution_permissions  # noqa: F401
        # Register signals
        from . import signals  # noqa: F401

        # Force add ourselves to INSTALLED_APPS if not already there
        from django.conf import settings
        app_name = 'mayan.apps.distribution'
        if app_name not in settings.INSTALLED_APPS:
            settings.INSTALLED_APPS.append(app_name)

        # Регистрация меню и ссылок
        try:
            from . import queues  # noqa: F401
            self._register_menu_links()
        except Exception:
            pass

        # URLs will be automatically discovered by REST API app via api_urls variable

    def _register_menu_links(self):
        """Регистрация всех меню и ссылок для distribution модуля"""
        from mayan.apps.documents.models import Document, DocumentFile
        from mayan.apps.common.menus import menu_main, menu_object

        # Импорт наших меню и ссылок
        from .menus import menu_distribution
        from .links.distribution_links import (
            link_distribution_publications, link_distribution_presets, link_distribution_recipients,
            link_document_publish, link_document_publications,
            link_document_file_add_to_publication
        )

        # ===== РЕГИСТРАЦИЯ В ГЛАВНОМ МЕНЮ =====

        menu_distribution.bind_links(
            links=(
                link_distribution_publications,
                link_distribution_presets,
                link_distribution_recipients
            )
        )

        menu_main.bind_links(
            links=(menu_distribution,),
            position=20  # После основных разделов
        )

        # ===== РЕГИСТРАЦИЯ В МЕНЮ ДОКУМЕНТОВ =====

        menu_object.bind_links(
            links=(link_document_publish, link_document_publications),
            sources=(Document,),
            position=12
        )

        menu_object.bind_links(
            links=(link_document_file_add_to_publication,),
            sources=(DocumentFile,),
            position=10
        )

