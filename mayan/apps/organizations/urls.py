"""
URL configuration for Organizations app.

These URLs are registered under the headless API namespace via
``headless_api/urls.py`` concatenation and ``rest_api/apps.py``
auto-discovery.  All patterns carry the ``headless/`` prefix so
they resolve to ``/api/v4/headless/organizations/...`` and
``/api/v4/headless/plans/``.
"""

from django.urls import path, re_path

from .api_views import (
    CurrentOrganizationView,
    OrganizationDetailView,
    OrganizationListCreateView,
    OrganizationMembersView,
    PlanListView,
)

app_name = 'organizations'

# Strict UUID pattern for organization_id
_UUID = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'

api_urls = [
    # Organization CRUD
    path(
        'headless/organizations/',
        OrganizationListCreateView.as_view(),
        name='api-organization-list-create'
    ),
    path(
        'headless/organizations/current/',
        CurrentOrganizationView.as_view(),
        name='api-organization-current'
    ),
    re_path(
        r'^headless/organizations/(?P<organization_id>{uuid})/$'.format(
            uuid=_UUID
        ),
        OrganizationDetailView.as_view(),
        name='api-organization-detail'
    ),

    # Members management
    re_path(
        r'^headless/organizations/(?P<organization_id>{uuid})/members/$'.format(
            uuid=_UUID
        ),
        OrganizationMembersView.as_view(),
        name='api-organization-members'
    ),

    # Plans
    path(
        'headless/plans/',
        PlanListView.as_view(),
        name='api-plan-list'
    ),
]
