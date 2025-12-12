from django.conf.urls import include, url
from django.http import JsonResponse

from .api_views import (
    APIRoot, APIVersionRoot, BatchRequestAPIView, BrowseableObtainAuthToken,
    ProjectInformationAPIView, schema_view
)
from mayan.apps.permissions.urls import api_urls as permissions_api_urls
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
from mayan.apps.headless_api.views.version_views import HeadlessEditView
from mayan.apps.headless_api.views.conversion_views import HeadlessDocumentConvertView
from mayan.apps.headless_api.views.dashboard_stats_views import HeadlessDashboardStatsView
from mayan.apps.headless_api.views.auth_views import HeadlessAuthMeView
from .literals import API_VERSION

# #region agent log
try:
    import json as _json, time as _time
    with open(r"c:\DAM\Prime-EDMS\.cursor\debug.log", "a", encoding="utf-8") as _f:
        _f.write(_json.dumps({
            "id": "log_rest_api_urls_enter",
            "timestamp": _time.time() * 1000,
            "sessionId": "debug-session",
            "runId": "pre-fix",
            "hypothesisId": "H3",
            "location": "rest_api/urls.py:api_version_urls",
            "message": "Building rest_api api_version_urls",
            "data": {}
        }) + "\n")
except Exception:
    pass
# #endregion agent log

# #region agent log http
try:
    import json as _json, time as _time
    import urllib.request as _r
    _r.urlopen(
        _r.Request(
            "http://host.docker.internal:7242/ingest/e2a91df7-36f3-4ec3-8d36-7745f17b1cac",
            data=_json.dumps({
                "id": "log_rest_api_urls_enter_http",
                "timestamp": _time.time() * 1000,
                "sessionId": "debug-session",
                "runId": "pre-fix",
                "hypothesisId": "H3",
                "location": "rest_api/urls.py:api_version_urls",
                "message": "Building rest_api api_version_urls",
                "data": {}
            }).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        ),
        timeout=2
    )
except Exception:
    pass
# #endregion agent log

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
        regex=r'^headless/auth/me/$',
        view=HeadlessAuthMeView.as_view(),
        name='headless-auth-me'
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
        regex=r'^headless/dashboard/stats/$',
        view=HeadlessDashboardStatsView.as_view(),
        name='headless-dashboard-stats'
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
        regex=r'^headless/ping/$',
        view=lambda request: JsonResponse({'status': 'pong'}),
        name='headless-ping'
    ),
    url(
        regex=r'^headless/profile/$',
        view=HeadlessProfileView.as_view(),
        name='headless-profile'
    ),
    url(
        regex=r'^headless/documents/(?P<document_id>\d+)/versions/new_from_edit/$',
        view=HeadlessEditView.as_view(),
        name='headless-document-version-new-from-edit'
    ),
    url(
        regex=r'^headless/documents/(?P<document_id>\d+)/convert/$',
        view=HeadlessDocumentConvertView.as_view(),
        name='headless-document-convert'
    )
]

# Expose permissions (roles) API for SPA role/permission matrix.
api_version_urls.extend(permissions_api_urls)

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
