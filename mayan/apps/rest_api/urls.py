from django.conf.urls import include, url
from django.http import JsonResponse

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .api_views import (
    APIRoot, APIVersionRoot, BatchRequestAPIView, BrowseableObtainAuthToken,
    ProjectInformationAPIView
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
from mayan.apps.headless_api.views.version_views import (
    HeadlessEditView, HeadlessVersionActivateView
)
from mayan.apps.headless_api.views.conversion_views import HeadlessDocumentConvertView
from mayan.apps.headless_api.views.dashboard_stats_views import HeadlessDashboardStatsView
from mayan.apps.headless_api.views.auth_views import HeadlessAuthMeView
from mayan.apps.headless_api.views.storage_views import HeadlessS3ConfigView, HeadlessS3StatsView
from mayan.apps.headless_api.views.users_views import HeadlessUsersDetailView, HeadlessUsersListCreateView
from mayan.apps.headless_api.views.admin_logs_views import HeadlessAdminLogsView
from mayan.apps.headless_api.views.analytics_views import (
    AssetBankViewSet, CampaignPerformanceViewSet, SearchAnalyticsViewSet,
    ApprovalAnalyticsViewSet, ROIDashboardViewSet, UserActivityViewSet,
    DistributionAnalyticsViewSet, ContentIntelligenceViewSet
)
from mayan.apps.analytics.api_views import EmailClickWebhookView
from mayan.apps.analytics.api_views import AnalyticsEventsExportView
from mayan.apps.analytics.api_views import AnalyticsHealthCheckView
from mayan.apps.headless_api.views.image_editor_views import (
    HeadlessImageEditorCommitView,
    HeadlessImageEditorPreviewView,
    HeadlessImageEditorSessionCreateView,
    HeadlessImageEditorSessionDetailView,
    HeadlessImageEditorWatermarkListView
)
from mayan.apps.headless_api.views.notification_views import (
    HeadlessNotificationDetailView,
    HeadlessNotificationListView,
    HeadlessNotificationPreferenceView,
    HeadlessNotificationReadAllView,
    HeadlessNotificationReadView,
    HeadlessNotificationUnreadCountView,
)
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
        regex=r'^headless/auth/me/$',
        view=HeadlessAuthMeView.as_view(),
        name='headless-auth-me'
    ),
    url(
        regex=r'^headless/storage/s3/config/$',
        view=HeadlessS3ConfigView.as_view(),
        name='headless-storage-s3-config'
    ),
    url(
        regex=r'^headless/storage/s3/stats/$',
        view=HeadlessS3StatsView.as_view(),
        name='headless-storage-s3-stats'
    ),
    url(
        regex=r'^headless/users/$',
        view=HeadlessUsersListCreateView.as_view(),
        name='headless-users-list'
    ),
    url(
        regex=r'^headless/users/(?P<user_id>\d+)/$',
        view=HeadlessUsersDetailView.as_view(),
        name='headless-users-detail'
    ),
    url(
        regex=r'^headless/activity/feed/$',
        view=HeadlessActivityFeedView.as_view(),
        name='headless-activity-feed'
    ),
    url(
        regex=r'^headless/admin/logs/$',
        view=HeadlessAdminLogsView.as_view(),
        name='headless-admin-logs'
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
    # Analytics (Asset Bank, Phase 1)
    url(
        regex=r'^headless/analytics/dashboard/assets/top-metrics/$',
        view=AssetBankViewSet.as_view({'get': 'top_metrics'}),
        name='headless-analytics-asset-bank-top-metrics'
    ),
    url(
        regex=r'^headless/analytics/dashboard/assets/distribution/$',
        view=AssetBankViewSet.as_view({'get': 'asset_distribution'}),
        name='headless-analytics-asset-bank-distribution'
    ),
    url(
        regex=r'^headless/analytics/dashboard/assets/most-downloaded/$',
        view=AssetBankViewSet.as_view({'get': 'most_downloaded'}),
        name='headless-analytics-asset-bank-most-downloaded'
    ),
    # Analytics (Phase 2 - Campaign Performance)
    url(
        regex=r'^headless/analytics/campaigns/$',
        view=CampaignPerformanceViewSet.as_view({'get': 'campaigns'}),
        name='headless-analytics-campaigns-list'
    ),
    url(
        regex=r'^headless/analytics/campaigns/create/$',
        view=CampaignPerformanceViewSet.as_view({'post': 'create_campaign'}),
        name='headless-analytics-campaigns-create'
    ),
    url(
        regex=r'^headless/analytics/campaigns/add-assets/$',
        view=CampaignPerformanceViewSet.as_view({'post': 'add_assets'}),
        name='headless-analytics-campaigns-add-assets'
    ),
    url(
        regex=r'^headless/analytics/campaigns/update-financials/$',
        view=CampaignPerformanceViewSet.as_view({'post': 'update_financials'}),
        name='headless-analytics-campaigns-update-financials'
    ),
    url(
        regex=r'^headless/analytics/dashboard/campaigns/$',
        view=CampaignPerformanceViewSet.as_view({'get': 'dashboard'}),
        name='headless-analytics-campaigns-dashboard'
    ),
    url(
        regex=r'^analytics/campaigns/(?P<campaign_id>[^/]+)/export/pdf/$',
        view=CampaignPerformanceViewSet.as_view({'post': 'export_pdf'}),
        name='analytics-campaign-export-pdf'
    ),
    # Analytics (Phase 2 - Search Analytics)
    url(
        regex=r'^headless/analytics/dashboard/search/top-queries/$',
        view=SearchAnalyticsViewSet.as_view({'get': 'top_queries'}),
        name='headless-analytics-search-top-queries'
    ),
    url(
        regex=r'^headless/analytics/dashboard/search/null-searches/$',
        view=SearchAnalyticsViewSet.as_view({'get': 'null_searches'}),
        name='headless-analytics-search-null-searches'
    ),
    url(
        regex=r'^headless/analytics/dashboard/search/daily/$',
        view=SearchAnalyticsViewSet.as_view({'get': 'daily'}),
        name='headless-analytics-search-daily'
    ),
    # Analytics (Phase 2 - User activity)
    url(
        regex=r'^headless/analytics/dashboard/users/adoption-heatmap/$',
        view=UserActivityViewSet.as_view({'get': 'adoption_by_department'}),
        name='headless-analytics-user-adoption-heatmap'
    ),
    # --- Analytics Expansion (Phase 2 & 3) ---
    # Asset Bank (additional)
    url(
        regex=r'^headless/analytics/dashboard/assets/distribution-trend/$',
        view=AssetBankViewSet.as_view({'get': 'distribution_trend'}),
        name='headless-analytics-asset-bank-distribution-trend'
    ),
    url(
        regex=r'^headless/analytics/dashboard/assets/detail/$',
        view=AssetBankViewSet.as_view({'get': 'asset_detail'}),
        name='headless-analytics-asset-bank-asset-detail'
    ),
    url(
        regex=r'^headless/analytics/dashboard/assets/reuse-metrics/$',
        view=AssetBankViewSet.as_view({'get': 'reuse_metrics'}),
        name='headless-analytics-asset-bank-reuse-metrics'
    ),
    url(
        regex=r'^headless/analytics/dashboard/assets/storage-trends/$',
        view=AssetBankViewSet.as_view({'get': 'storage_trends'}),
        name='headless-analytics-asset-bank-storage-trends'
    ),
    url(
        regex=r'^headless/analytics/dashboard/assets/alerts/$',
        view=AssetBankViewSet.as_view({'get': 'alerts'}),
        name='headless-analytics-asset-bank-alerts'
    ),
    # Campaigns (additional)
    url(
        regex=r'^headless/analytics/dashboard/campaigns/top-assets/$',
        view=CampaignPerformanceViewSet.as_view({'get': 'top_assets'}),
        name='headless-analytics-campaigns-top-assets'
    ),
    url(
        regex=r'^headless/analytics/dashboard/campaigns/timeline/$',
        view=CampaignPerformanceViewSet.as_view({'get': 'timeline'}),
        name='headless-analytics-campaigns-timeline'
    ),
    url(
        regex=r'^headless/analytics/dashboard/campaigns/geography/$',
        view=CampaignPerformanceViewSet.as_view({'get': 'geography'}),
        name='headless-analytics-campaigns-geography'
    ),
    # Search tracking
    url(
        regex=r'^headless/analytics/track/search/click/$',
        view=SearchAnalyticsViewSet.as_view({'post': 'click'}),
        name='headless-analytics-search-track-click'
    ),
    # User activity (additional)
    url(
        regex=r'^headless/analytics/dashboard/users/login-patterns/$',
        view=UserActivityViewSet.as_view({'get': 'login_patterns'}),
        name='headless-analytics-user-login-patterns'
    ),
    url(
        regex=r'^headless/analytics/dashboard/users/cohorts/$',
        view=UserActivityViewSet.as_view({'get': 'cohorts'}),
        name='headless-analytics-user-cohorts'
    ),
    url(
        regex=r'^headless/analytics/dashboard/users/feature-adoption/$',
        view=UserActivityViewSet.as_view({'get': 'feature_adoption'}),
        name='headless-analytics-user-feature-adoption'
    ),
    # Approvals
    url(
        regex=r'^headless/analytics/dashboard/approvals/summary/$',
        view=ApprovalAnalyticsViewSet.as_view({'get': 'summary'}),
        name='headless-analytics-approvals-summary'
    ),
    url(
        regex=r'^headless/analytics/dashboard/approvals/timeseries/$',
        view=ApprovalAnalyticsViewSet.as_view({'get': 'timeseries'}),
        name='headless-analytics-approvals-timeseries'
    ),
    url(
        regex=r'^headless/analytics/dashboard/approvals/recommendations/$',
        view=ApprovalAnalyticsViewSet.as_view({'get': 'recommendations'}),
        name='headless-analytics-approvals-recommendations'
    ),
    # ROI
    url(
        regex=r'^headless/analytics/dashboard/roi/summary/$',
        view=ROIDashboardViewSet.as_view({'get': 'summary'}),
        name='headless-analytics-roi-summary'
    ),
    url(
        regex=r'^headless/analytics/dashboard/roi/estimate/$',
        view=ROIDashboardViewSet.as_view({'get': 'estimate'}),
        name='headless-analytics-roi-estimate'
    ),
    # Distribution
    url(
        regex=r'^headless/analytics/dashboard/distribution/$',
        view=DistributionAnalyticsViewSet.as_view({'get': 'dashboard'}),
        name='headless-analytics-distribution-dashboard'
    ),
    url(
        regex=r'^headless/analytics/dashboard/distribution/conversion-rate/$',
        view=DistributionAnalyticsViewSet.as_view({'get': 'conversion_rate'}),
        name='headless-analytics-distribution-conversion-rate'
    ),
    url(
        regex=r'^headless/analytics/dashboard/distribution/velocity/$',
        view=DistributionAnalyticsViewSet.as_view({'get': 'velocity'}),
        name='headless-analytics-distribution-velocity'
    ),
    url(
        regex=r'^headless/analytics/ingest/distribution-events/$',
        view=DistributionAnalyticsViewSet.as_view({'post': 'ingest'}),
        name='headless-analytics-distribution-ingest'
    ),
    # Content Intelligence
    url(
        regex=r'^headless/analytics/dashboard/content-intel/content-gaps/$',
        view=ContentIntelligenceViewSet.as_view({'get': 'content_gaps'}),
        name='headless-analytics-content-gaps'
    ),
    url(
        regex=r'^headless/analytics/dashboard/content-intel/compliance/metadata/$',
        view=ContentIntelligenceViewSet.as_view({'get': 'metadata_compliance'}),
        name='headless-analytics-content-intel-metadata-compliance'
    ),
    # Analytics Webhooks (external providers)
    url(
        regex=r'^analytics/webhooks/email/click/$',
        view=EmailClickWebhookView.as_view(),
        name='analytics-webhook-email-click'
    ),
    url(
        regex=r'^analytics/export/events/$',
        view=AnalyticsEventsExportView.as_view(),
        name='analytics-export-events'
    ),
    url(
        regex=r'^analytics/health/$',
        view=AnalyticsHealthCheckView.as_view(),
        name='analytics-health'
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
        regex=r'^headless/documents/(?P<document_id>\d+)/versions/activate/$',
        view=HeadlessVersionActivateView.as_view(),
        name='headless-document-version-activate'
    ),
    url(
        regex=r'^headless/documents/(?P<document_id>\d+)/convert/$',
        view=HeadlessDocumentConvertView.as_view(),
        name='headless-document-convert'
    ),
    # Headless image editor endpoints (server-side render + version commit)
    url(
        regex=r'^headless/image-editor/sessions/$',
        view=HeadlessImageEditorSessionCreateView.as_view(),
        name='headless-image-editor-session-create'
    ),
    url(
        regex=r'^headless/image-editor/sessions/(?P<session_id>\d+)/$',
        view=HeadlessImageEditorSessionDetailView.as_view(),
        name='headless-image-editor-session-detail'
    ),
    url(
        regex=r'^headless/image-editor/sessions/(?P<session_id>\d+)/preview/$',
        view=HeadlessImageEditorPreviewView.as_view(),
        name='headless-image-editor-preview'
    ),
    url(
        regex=r'^headless/image-editor/sessions/(?P<session_id>\d+)/commit/$',
        view=HeadlessImageEditorCommitView.as_view(),
        name='headless-image-editor-commit'
    ),
    url(
        regex=r'^headless/image-editor/watermarks/$',
        view=HeadlessImageEditorWatermarkListView.as_view(),
        name='headless-image-editor-watermarks'
    ),
    # Headless notification endpoints
    url(
        regex=r'^headless/notifications/$',
        view=HeadlessNotificationListView.as_view(),
        name='headless-notifications-list'
    ),
    url(
        regex=r'^headless/notifications/(?P<notification_id>\d+)/$',
        view=HeadlessNotificationDetailView.as_view(),
        name='headless-notifications-detail'
    ),
    url(
        regex=r'^headless/notifications/(?P<notification_id>\d+)/read/$',
        view=HeadlessNotificationReadView.as_view(),
        name='headless-notifications-read'
    ),
    url(
        regex=r'^headless/notifications/read-all/$',
        view=HeadlessNotificationReadAllView.as_view(),
        name='headless-notifications-read-all'
    ),
    url(
        regex=r'^headless/notifications/unread-count/$',
        view=HeadlessNotificationUnreadCountView.as_view(),
        name='headless-notifications-unread-count'
    ),
    url(
        regex=r'^headless/notifications/preferences/$',
        view=HeadlessNotificationPreferenceView.as_view(),
        name='headless-notifications-preferences'
    )
]

# Expose permissions (roles) API for SPA role/permission matrix.
api_version_urls.extend(permissions_api_urls)

api_urls = [
    url(regex=r'^v{}/'.format(API_VERSION), view=include(api_version_urls)),
    url(regex=r'^$', name='api_root', view=APIRoot.as_view())
]

urlpatterns = [
    url(
        regex=r'^schema/$', name='schema-openapi',
        view=SpectacularAPIView.as_view()
    ),
    url(
        regex=r'^schema/ui/$', name='schema-openapi-ui',
        view=SpectacularSwaggerView.as_view(url_name='rest_api:schema-openapi')
    ),
    url(regex=r'^', view=include(api_urls))
]
