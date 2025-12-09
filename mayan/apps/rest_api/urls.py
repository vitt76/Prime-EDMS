from django.conf.urls import include, url

from .api_views import (
    APIRoot, APIVersionRoot, BatchRequestAPIView, BrowseableObtainAuthToken,
    ProjectInformationAPIView, schema_view
)
from mayan.apps.headless_api.views.config_views import HeadlessDocumentTypeConfigView
from mayan.apps.headless_api.views.activity_views import (
    DashboardActivityView, HeadlessActivityFeedView
)
from mayan.apps.headless_api.views.favorites_views import (
    HeadlessFavoriteListView, HeadlessFavoriteToggleView
)
from mayan.apps.headless_api.views.password_views import HeadlessPasswordChangeView
from mayan.apps.headless_api.views.my_uploads_views import HeadlessMyUploadsView
from mayan.apps.headless_api.views.profile_views import HeadlessProfileView
from .literals import API_VERSION

api_version_urls = [
    url(regex=r'^$', name='api_version_root', view=APIVersionRoot.as_view()),
    url(
        regex=r'^auth/token/obtain/$', name='auth_token_obtain',
        view=BrowseableObtainAuthToken.as_view()
    ),
    url(
        regex=r'^project/$', name='project_information',
        view=ProjectInformationAPIView.as_view()
    ),
    url(
        regex=r'^batch_requests/$', name='batchrequest-create',
        view=BatchRequestAPIView.as_view()
    ),
    # Headless API endpoints
    url(
        regex=r'^headless/config/document_types/$',
        view=HeadlessDocumentTypeConfigView.as_view(),
        name='headless-config-document-types-list'
    ),
    url(
        regex=r'^headless/config/document_types/(?P<document_type_id>\d+)/$',
        view=HeadlessDocumentTypeConfigView.as_view(),
        name='headless-config-document-type-detail'
    ),
    url(
        regex=r'^headless/activity/feed/$',
        view=HeadlessActivityFeedView.as_view(),
        name='headless-activity-feed'
    ),
    url(
        regex=r'^headless/dashboard/activity/$',
        view=DashboardActivityView.as_view(),
        name='headless-dashboard-activity'
    ),
    url(
        regex=r'^headless/favorites/$',
        view=HeadlessFavoriteListView.as_view(),
        name='headless-favorites-list'
    ),
    url(
        regex=r'^headless/favorites/(?P<document_id>\d+)/$',
        view=HeadlessFavoriteToggleView.as_view(),
        name='headless-favorites-toggle'
    ),
    url(
        regex=r'^headless/password/change/$',
        view=HeadlessPasswordChangeView.as_view(),
        name='headless-password-change'
    ),
    url(
        regex=r'^headless/documents/my_uploads/$',
        view=HeadlessMyUploadsView.as_view(),
        name='headless-my-uploads'
    ),
    url(
        regex=r'^headless/profile/$',
        view=HeadlessProfileView.as_view(),
        name='headless-profile'
    )
]

api_urls = [
    url(
        regex=r'^swagger(?P<format>.json|.yaml)$', name='schema-json',
        view=schema_view.without_ui(cache_timeout=None),
    ),
    url(regex=r'^v{}/'.format(API_VERSION), view=include(api_version_urls)),
    url(regex=r'^$', name='api_root', view=APIRoot.as_view())
]

urlpatterns = [
    url(
        regex=r'^swagger/ui/$', name='schema-swagger-ui',
        view=schema_view.with_ui('swagger', cache_timeout=None)
    ),
    url(
        regex=r'^redoc/ui/$', name='schema-redoc',
        view=schema_view.with_ui('redoc', cache_timeout=None)
    ),
    url(regex=r'^', view=include(api_urls))
]
