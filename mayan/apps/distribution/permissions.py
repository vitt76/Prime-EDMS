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

# API permissions
permission_publication_api_create = namespace.add_permission(
    label=_('Create publications via API'), name='publication_api_create'
)
permission_publication_api_view = namespace.add_permission(
    label=_('View publications via API'), name='publication_api_view'
)
permission_publication_api_edit = namespace.add_permission(
    label=_('Edit publications via API'), name='publication_api_edit'
)
permission_publication_api_delete = namespace.add_permission(
    label=_('Delete publications via API'), name='publication_api_delete'
)
permission_recipient_api_manage = namespace.add_permission(
    label=_('Manage recipients via API'), name='recipient_api_manage'
)
permission_preset_api_manage = namespace.add_permission(
    label=_('Manage presets via API'), name='preset_api_manage'
)
