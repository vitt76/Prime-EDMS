"""
URL configuration for headless_api app.

This module defines the URL patterns for the Headless API endpoints that provide
SPA-friendly REST interfaces for functionality not exposed by Mayan EDMS core API.
"""

from django.conf.urls import url

from .views.password_views import HeadlessPasswordChangeView
from .views.config_views import HeadlessDocumentTypeConfigView
from .views.activity_views import HeadlessActivityFeedView

app_name = 'headless_api'

# API URLs for Mayan REST API integration
api_urls = [
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
]
