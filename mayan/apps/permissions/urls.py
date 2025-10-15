from django.conf.urls import url

from .api_views import (
    APIPermissionList, APIRoleDetailView, APIRoleGroupAddView,
    APIRoleGroupListView, APIRoleGroupRemoveView, APIRoleListView,
    APIRolePermissionAddView, APIRolePermissionListView,
    APIRolePermissionRemoveView
)

from .views import (
    GroupRoleAddRemoveView, RoleCreateView, RoleDeleteView, RoleEditView,
    RoleListView, RoleGroupAddRemoveView, RolePermissionAddRemoveView,
    StoredPermissionDetailView
)

urlpatterns = [
    url(
        regex=r'^groups/(?P<group_id>\d+)/roles/$', name='group_role_list',
        view=GroupRoleAddRemoveView.as_view()
    ),
    url(regex=r'^roles/$', name='role_list', view=RoleListView.as_view()),
    url(
        regex=r'^roles/create/$', name='role_create',
        view=RoleCreateView.as_view()
    ),
    url(
        regex=r'^roles/(?P<role_id>\d+)/delete/$', name='role_single_delete',
        view=RoleDeleteView.as_view()
    ),
    url(
        regex=r'^roles/(?P<role_id>\d+)/edit/$', name='role_edit',
        view=RoleEditView.as_view()
    ),
    url(
        regex=r'^roles/(?P<role_id>\d+)/groups/$', name='role_group_list',
        view=RoleGroupAddRemoveView.as_view()
    ),
    url(
        regex=r'^roles/(?P<role_id>\d+)/permissions/$',
        name='role_permission_list',
        view=RolePermissionAddRemoveView.as_view()
    ),
    url(
        regex=r'^roles/multiple/delete/$', name='role_multiple_delete',
        view=RoleDeleteView.as_view()
    ),
    url(
        regex=r'^stored_permissions/(?P<stored_permission_id>\d+)/$',
        name='stored_permission_detail',
        view=StoredPermissionDetailView.as_view()
    )
]

api_urls = [
    url(
        regex=r'^permissions/$', name='permission-list',
        view=APIPermissionList.as_view()
    ),
    url(regex=r'^roles/$', name='role-list', view=APIRoleListView.as_view()),
    url(
        regex=r'^roles/(?P<role_id>[0-9]+)/$', name='role-detail',
        view=APIRoleDetailView.as_view()
    ),
    url(
        regex=r'^roles/(?P<role_id>[0-9]+)/groups/$', name='role-group-list',
        view=APIRoleGroupListView.as_view()
    ),
    url(
        regex=r'^roles/(?P<role_id>[0-9]+)/groups/add/$',
        name='role-group-add', view=APIRoleGroupAddView.as_view()
    ),
    url(
        regex=r'^roles/(?P<role_id>[0-9]+)/groups/remove/$',
        name='role-group-remove', view=APIRoleGroupRemoveView.as_view()
    ),
    url(
        regex=r'^roles/(?P<role_id>[0-9]+)/permissions/$',
        name='role-permission-list', view=APIRolePermissionListView.as_view()
    ),
    url(
        regex=r'^roles/(?P<role_id>[0-9]+)/permissions/add/$',
        name='role-permission-add', view=APIRolePermissionAddView.as_view()
    ),
    url(
        regex=r'^roles/(?P<role_id>[0-9]+)/permissions/remove/$',
        name='role-permission-remove',
        view=APIRolePermissionRemoveView.as_view()
    )
]
