from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation.classes import Link

from ..icons import (
    icon_distribution, icon_distribution_add, icon_distribution_download,
    icon_distribution_link, icon_distribution_list, icon_distribution_publish,
    icon_distribution_settings, icon_distribution_token, icon_distribution_user
)
from ..permissions import (
    permission_publication_api_create, permission_publication_api_view,
    permission_publication_api_edit, permission_recipient_manage,
    permission_rendition_preset_manage
)


# ===== ДОКУМЕНТЫ =====

# Публикация документа - UI страница
link_document_publish = Link(
    args='resolved_object.id',
    icon=icon_distribution_publish,
    permissions=(permission_publication_api_create,),
    text=_('Опубликовать/Поделиться'),
    view='distribution:publication_create_from_document'
)

# Просмотр публикаций документа - UI страница
link_document_publications = Link(
    icon=icon_distribution_list,
    permissions=(permission_publication_api_view,),
    text=_('Публикации'),
    view='distribution:publication_list'
)

# Публикация нескольких документов - пока отключена
# link_document_publish_multiple = Link(
#     icon=icon_distribution_publish,
#     permissions=(permission_publication_api_create,),
#     text=_('Опубликовать выбранные'),
#     view='distribution:publication_create_multiple'
# )


# ===== ФАЙЛЫ ДОКУМЕНТОВ =====

# Добавление файла в публикацию - UI страница
link_document_file_add_to_publication = Link(
    args='resolved_object.id',
    icon=icon_distribution_add,
    permissions=(permission_publication_api_edit,),
    text=_('Добавить в публикацию'),
    view='distribution:add_to_publication'
)

# Генерация rendition'ов для файла - пока отключена
# link_document_file_generate_renditions = Link(
#     args='resolved_object.id',
#     icon=icon_distribution_download,
#     permissions=(permission_publication_api_edit,),
#     text=_('Создать версии файлов'),
#     view='distribution:generate_file_renditions'
# )


# ===== ГЛАВНОЕ МЕНЮ =====

# Публикации
link_distribution_publications = Link(
    icon=icon_distribution_list,
    permissions=(permission_publication_api_view,),
    text=_('Публикации'),
    view='distribution:publication_list'
)

link_distribution_presets = Link(
    icon=icon_distribution_settings,
    permissions=(permission_publication_api_view,),
    text=_('Пресеты'),
    view='distribution:preset_list'
)

# Управление получателями - UI страница
link_recipient_management = Link(
    icon=icon_distribution_user,
    permissions=(permission_recipient_manage,),
    text=_('Получатели'),
    view='distribution:recipient_list'
)

# Управление пресетами - UI страница
link_preset_management = Link(
    icon=icon_distribution_settings,
    permissions=(permission_rendition_preset_manage,),
    text=_('Пресеты рендишенов'),
    view='distribution:preset_list'
)
# Управление ссылками - UI страница
link_share_link_management = Link(
    icon=icon_distribution_link,
    permissions=(permission_publication_api_view,),
    text=_('Ссылки для скачивания'),
    view='distribution:share_link_list'
)

