from django.utils.translation import ugettext_lazy as _

from mayan.apps.authentication.link_conditions import condition_user_is_authenticated
from mayan.apps.navigation.classes import Link, Separator, Text
from mayan.apps.navigation.utils import factory_condition_queryset_access

from .icons import (
    icon_current_user_detail, icon_group_create, icon_group_single_delete,
    icon_group_multiple_delete, icon_group_edit, icon_group_list,
    icon_group_setup, icon_group_user_list, icon_user_create,
    icon_user_edit, icon_user_group_list, icon_user_list,
    icon_user_single_delete, icon_user_multiple_delete,
    icon_user_set_options, icon_user_setup
)
from .link_conditions import condition_user_is_not_superuser
from .permissions import (
    permission_group_create, permission_group_delete, permission_group_edit,
    permission_group_view, permission_user_create, permission_user_delete,
    permission_user_edit, permission_user_view
)
from .utils import get_user_label_text

# Current user

link_current_user_details = Link(
    args='request.user.id',
    condition=condition_user_is_authenticated,
    icon=icon_current_user_detail, text=_('User details'),
    view='user_management:user_details'
)

# Group

link_group_create = Link(
    icon=icon_group_create, permissions=(permission_group_create,),
    text=_('Create new group'), view='user_management:group_create'
)
link_group_single_delete = Link(
    args='object.id', icon=icon_group_single_delete,
    permissions=(permission_group_delete,), tags='dangerous',
    text=_('Delete'), view='user_management:group_single_delete'
)
link_group_multiple_delete = Link(
    icon=icon_group_multiple_delete, tags='dangerous', text=_('Delete'),
    view='user_management:group_multiple_delete'
)
link_group_edit = Link(
    args='object.id', icon=icon_group_edit,
    permissions=(permission_group_edit,), text=_('Edit'),
    view='user_management:group_edit'
)
link_group_list = Link(
    condition=factory_condition_queryset_access(
        app_label='auth', model_name='Group',
        object_permission=permission_group_view,
    ), icon=icon_group_list, text=_('Groups'),
    view='user_management:group_list'
)
link_group_user_list = Link(
    args='object.id', icon=icon_group_user_list,
    permissions=(permission_group_edit,), text=_('Users'),
    view='user_management:group_members'
)
link_group_setup = Link(
    condition=factory_condition_queryset_access(
        app_label='auth', model_name='Group',
        callback=condition_user_is_not_superuser,
        object_permission=permission_group_view,
        view_permission=permission_group_create
    ), icon=icon_group_setup, text=_('Groups'),
    view='user_management:group_list'
)

# User

link_user_create = Link(
    condition=condition_user_is_authenticated, icon=icon_user_create,
    permissions=(permission_user_create,), text=_('Create new user'),
    view='user_management:user_create'
)
link_user_single_delete = Link(
    args='object.id', condition=condition_user_is_authenticated,
    icon=icon_user_single_delete, permissions=(permission_user_delete,),
    tags='dangerous', text=_('Delete'),
    view='user_management:user_single_delete'
)
link_user_multiple_delete = Link(
    icon=icon_user_multiple_delete, tags='dangerous', text=_('Delete'),
    view='user_management:user_multiple_delete'
)
link_user_edit = Link(
    args='object.id', condition=condition_user_is_authenticated,
    icon=icon_user_edit, permissions=(permission_user_edit,), text=_('Edit'),
    view='user_management:user_edit'
)
link_user_group_list = Link(
    args='object.id', condition=condition_user_is_authenticated,
    icon=icon_user_group_list, permissions=(permission_user_edit,),
    text=_('Groups'), view='user_management:user_groups'
)
link_user_list = Link(
    icon=icon_user_list, text=_('Users'),
    condition=factory_condition_queryset_access(
        app_label='auth', model_name='User',
        callback=condition_user_is_authenticated,
        object_permission=permission_user_view,
        view_permission=permission_user_create
    ), view='user_management:user_list'
)
link_user_set_options = Link(
    args='object.id', condition=condition_user_is_authenticated,
    icon=icon_user_set_options, permissions=(permission_user_edit,),
    text=_('User options'), view='user_management:user_options'
)
link_user_setup = Link(
    condition=factory_condition_queryset_access(
        app_label='auth', model_name='User',
        object_permission=permission_user_view,
        view_permission=permission_user_create,
    ), icon=icon_user_setup, text=_('Users'),
    view='user_management:user_list'
)

separator_user_label = Separator()

text_user_label = Text(
    html_extra_classes='menu-user-name', text=get_user_label_text
)
