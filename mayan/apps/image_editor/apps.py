from mayan.apps.common.apps import MayanAppConfig
from django.utils.translation import ugettext_lazy as _


class ImageEditorApp(MayanAppConfig):
    """Настройка приложения графического редактора изображений."""

    app_namespace = 'image_editor'
    app_url = 'image-editor'
    has_rest_api = False
    has_static_media = True
    has_tests = True
    name = 'mayan.apps.image_editor'
    verbose_name = _('Image editor')

    def ready(self):
        super().ready()
        try:
            from . import permissions as image_editor_permissions  # noqa: F401
        except Exception:
            pass
        try:
            from .urls import ui_urlpatterns  # noqa: F401
        except Exception:
            pass

        # Регистрация ссылок меню и очередей выполняется здесь
        self._register_links()

    def _register_links(self):
        """Привязка ссылок графического редактора к меню Mayan."""
        try:
            from mayan.apps.documents.models import DocumentFile
            from mayan.apps.common.menus import menu_list_facet

            from .links import link_document_file_edit_image

            menu_list_facet.bind_links(
                links=(link_document_file_edit_image,),
                sources=(DocumentFile,),
                position=5
            )
        except Exception:
            # Не блокируем запуск, если зависимых модулей пока нет
            pass
