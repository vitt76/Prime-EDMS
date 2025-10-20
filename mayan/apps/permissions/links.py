from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation.classes import Link
from mayan.apps.user_management.permissions import permission_group_edit

from .icons import (
    icon_group_role_list, icon_role_create, icon_role_edit,
    icon_role_group_list, icon_role_list, icon_role_multiple_delete,
    icon_role_permission_list, icon_role_single_delete
)
from .permissions import (
    permission_role_create, permission_role_delete, permission_role_edit,
    permission_role_view
)

# Group

link_group_role_list = Link(
    args='object.id', icon=icon_group_role_list,
    permissions=(permission_group_edit,), text=_('Roles'),
    view='permissions:group_role_list'
)

# Role

link_role_create = Link(
    icon=icon_role_create, permissions=(permission_role_create,),
    text=_('Create new role'), view='permissions:role_create'
)
link_role_single_delete = Link(
    args='object.id', icon=icon_role_single_delete,
    permissions=(permission_role_delete,), tags='dangerous',
    text=_('Delete'), view='permissions:role_single_delete'
)
link_role_multiple_delete = Link(
    icon=icon_role_multiple_delete, tags='dangerous', text=_('Delete'),
    view='permissions:role_multiple_delete'
)
link_role_edit = Link(
    args='object.id', icon=icon_role_edit,
    permissions=(permission_role_edit,), text=_('Edit'),
    view='permissions:role_edit'
)
link_role_list = Link(
    icon=icon_role_list, permissions=(permission_role_view,),
    text=_('Roles'), view='permissions:role_list'
)
link_role_group_list = Link(
    args='object.id', icon=icon_role_group_list,
    permissions=(permission_role_edit,), text=_('Groups'),
    view='permissions:role_group_list'
)
link_role_permission_list = Link(
    args='object.id', icon=icon_role_permission_list,
    permissions=(permission_role_edit,),
    text=_('Role permissions'), view='permissions:role_permission_list'
)
