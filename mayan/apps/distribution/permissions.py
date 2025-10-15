from django.utils.translation import ugettext_lazy as _

from mayan.apps.permissions import PermissionNamespace

namespace = PermissionNamespace(label=_('Distribution'), name='distribution')

# Publication permissions
permission_publication_create = namespace.add_permission(
    label=_('Create publications'), name='publication_create'
)
permission_publication_edit = namespace.add_permission(
    label=_('Edit publications'), name='publication_edit'
)
permission_publication_delete = namespace.add_permission(
    label=_('Delete publications'), name='publication_delete'
)
permission_publication_view = namespace.add_permission(
    label=_('View publications'), name='publication_view'
)

# Distribution permissions
permission_publication_download = namespace.add_permission(
    label=_('Download from publications'), name='publication_download'
)
permission_recipient_manage = namespace.add_permission(
    label=_('Manage recipients and lists'), name='recipient_manage'
)
permission_rendition_preset_manage = namespace.add_permission(
    label=_('Manage rendition presets'), name='rendition_preset_manage'
)
