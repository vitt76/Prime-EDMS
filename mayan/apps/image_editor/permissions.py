from django.utils.translation import ugettext_lazy as _

from mayan.apps.permissions.classes import PermissionNamespace

namespace = PermissionNamespace(label=_('Image editor'), name='image_editor')

permission_image_edit = namespace.add_permission(
    label=_('Редактирование изображений документов'),
    name='image_edit'
)
