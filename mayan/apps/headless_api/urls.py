"""
URL configuration for headless_api app.

This module defines the URL patterns for the Headless API endpoints that provide
SPA-friendly REST interfaces for functionality not exposed by Mayan EDMS core API.
"""

print(">>> HEADLESS URLS LOADED <<<")  # Debug canary for runtime import

from django.conf.urls import url
from django.http import JsonResponse

from .views.password_views import HeadlessPasswordChangeView
from .views.config_views import HeadlessDocumentTypeConfigView
from .views.activity_views import DashboardActivityView, HeadlessActivityFeedView
from .views.favorites_views import HeadlessFavoriteListView, HeadlessFavoriteToggleView
from .views.my_uploads_views import HeadlessMyUploadsView
from .views.profile_views import HeadlessProfileView
from .views.version_views import HeadlessEditView
from .views.conversion_views import HeadlessDocumentConvertView
from .views.auth_views import HeadlessAuthMeView
from .views.dashboard_stats_views import HeadlessDashboardStatsView
from .views.task_status_views import HeadlessTaskStatusView

app_name = 'headless_api'

# API URLs for Mayan REST API integration
api_urls = [
    url(regex=r'^ping/$', view=lambda request: JsonResponse({'status': 'pong'}), name='api-ping'),
    url(
        regex=r'^auth/me/$',
        view=HeadlessAuthMeView.as_view(),
        name='api-auth-me'
    ),
    url(
        regex=r'^password/change/$',
        view=HeadlessPasswordChangeView.as_view(),
        name='api-password-change'
    ),
    url(
        regex=r'^config/document_types/$',
        view=HeadlessDocumentTypeConfigView.as_view(),
        name='api-config-document-types-list'
    ),
    url(
        regex=r'^config/document_types/(?P<document_type_id>\d+)/$',
        view=HeadlessDocumentTypeConfigView.as_view(),
        name='api-config-document-type-detail'
    ),
    url(
        regex=r'^activity/feed/$',
        view=HeadlessActivityFeedView.as_view(),
        name='api-activity-feed'
    ),
    url(
        regex=r'^dashboard/activity/$',
        view=DashboardActivityView.as_view(),
        name='api-dashboard-activity'
    ),
    url(
        regex=r'^dashboard/stats/$',
        view=HeadlessDashboardStatsView.as_view(),
        name='api-dashboard-stats'
    ),
    url(
        regex=r'^favorites/$',
        view=HeadlessFavoriteListView.as_view(),
        name='api-favorites-list'
    ),
    url(
        regex=r'^favorites/(?P<document_id>\d+)/$',
        view=HeadlessFavoriteToggleView.as_view(),
        name='api-favorites-toggle'
    ),
    url(
        regex=r'^documents/my_uploads/$',
        view=HeadlessMyUploadsView.as_view(),
        name='api-my-uploads'
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/versions/new_from_edit/$',
        view=HeadlessEditView.as_view(),
        name='api-document-version-new-from-edit'
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/convert/$',
        view=HeadlessDocumentConvertView.as_view(),
        name='api-document-convert'
    ),
    url(
        regex=r'^profile/$',
        view=HeadlessProfileView.as_view(),
        name='api-profile'
    ),
    url(
        regex=r'^tasks/(?P<task_id>[\w-]+)/status/$',
        view=HeadlessTaskStatusView.as_view(),
        name='api-task-status'
    ),
]
