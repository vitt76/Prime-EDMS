"""
URL configuration for headless_api app.

This module defines the URL patterns for the Headless API endpoints that provide
SPA-friendly REST interfaces for functionality not exposed by Mayan EDMS core API.
"""

from django.conf.urls import url
from django.http import JsonResponse

from .views.password_views import HeadlessPasswordChangeView
from .views.config_views import HeadlessDocumentTypeConfigView
from .views.activity_views import DashboardActivityView, HeadlessActivityFeedView
from .views.favorites_views import HeadlessFavoriteListView, HeadlessFavoriteToggleView
from .views.my_uploads_views import HeadlessMyUploadsView
from .views.profile_views import HeadlessProfileView
from .views.version_views import HeadlessEditView, HeadlessVersionActivateView
from .views.conversion_views import HeadlessDocumentConvertView
from .views.auth_views import HeadlessAuthMeView
from .views.dashboard_stats_views import HeadlessDashboardStatsView
from .views.task_status_views import HeadlessTaskStatusView
from .views.admin_logs_views import HeadlessAdminLogsView
from .views.notification_views import (
    HeadlessNotificationDetailView,
    HeadlessNotificationListView,
    HeadlessNotificationPreferenceView,
    HeadlessNotificationReadAllView,
    HeadlessNotificationReadView,
    HeadlessNotificationUnreadCountView,
)
from .views.analytics_views import (
    AssetBankViewSet, CampaignPerformanceViewSet, SearchAnalyticsViewSet,
    ApprovalAnalyticsViewSet, ROIDashboardViewSet, UserActivityViewSet,
    DistributionAnalyticsViewSet, ContentIntelligenceViewSet
)

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
        regex=r'^admin/logs/$',
        view=HeadlessAdminLogsView.as_view(),
        name='api-admin-logs'
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
        regex=r'^documents/(?P<document_id>\d+)/versions/activate/$',
        view=HeadlessVersionActivateView.as_view(),
        name='api-document-version-activate'
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
    url(
        regex=r'^notifications/$',
        view=HeadlessNotificationListView.as_view(),
        name='api-notifications-list'
    ),
    url(
        regex=r'^notifications/(?P<notification_id>\d+)/$',
        view=HeadlessNotificationDetailView.as_view(),
        name='api-notifications-detail'
    ),
    url(
        regex=r'^notifications/(?P<notification_id>\d+)/read/$',
        view=HeadlessNotificationReadView.as_view(),
        name='api-notifications-read'
    ),
    url(
        regex=r'^notifications/read-all/$',
        view=HeadlessNotificationReadAllView.as_view(),
        name='api-notifications-read-all'
    ),
    url(
        regex=r'^notifications/unread-count/$',
        view=HeadlessNotificationUnreadCountView.as_view(),
        name='api-notifications-unread-count'
    ),
    url(
        regex=r'^notifications/preferences/$',
        view=HeadlessNotificationPreferenceView.as_view(),
        name='api-notifications-preferences'
    ),
    # Analytics (Asset Bank, Phase 1)
    url(
        regex=r'^analytics/dashboard/assets/top-metrics/$',
        view=AssetBankViewSet.as_view({'get': 'top_metrics'}),
        name='api-analytics-asset-bank-top-metrics'
    ),
    url(
        regex=r'^analytics/dashboard/assets/distribution/$',
        view=AssetBankViewSet.as_view({'get': 'asset_distribution'}),
        name='api-analytics-asset-bank-distribution'
    ),
    url(
        regex=r'^analytics/dashboard/assets/distribution-trend/$',
        view=AssetBankViewSet.as_view({'get': 'distribution_trend'}),
        name='api-analytics-asset-bank-distribution-trend'
    ),
    url(
        regex=r'^analytics/dashboard/assets/most-downloaded/$',
        view=AssetBankViewSet.as_view({'get': 'most_downloaded'}),
        name='api-analytics-asset-bank-most-downloaded'
    ),
    url(
        regex=r'^analytics/dashboard/assets/detail/$',
        view=AssetBankViewSet.as_view({'get': 'asset_detail'}),
        name='api-analytics-asset-bank-asset-detail'
    ),
    url(
        regex=r'^analytics/dashboard/assets/reuse-metrics/$',
        view=AssetBankViewSet.as_view({'get': 'reuse_metrics'}),
        name='api-analytics-asset-bank-reuse-metrics'
    ),
    url(
        regex=r'^analytics/dashboard/assets/storage-trends/$',
        view=AssetBankViewSet.as_view({'get': 'storage_trends'}),
        name='api-analytics-asset-bank-storage-trends'
    ),
    url(
        regex=r'^analytics/dashboard/assets/alerts/$',
        view=AssetBankViewSet.as_view({'get': 'alerts'}),
        name='api-analytics-asset-bank-alerts'
    ),
    # Analytics (Phase 2 - Campaign Performance)
    url(
        regex=r'^analytics/campaigns/$',
        view=CampaignPerformanceViewSet.as_view({'get': 'campaigns'}),
        name='api-analytics-campaigns-list'
    ),
    url(
        regex=r'^analytics/campaigns/create/$',
        view=CampaignPerformanceViewSet.as_view({'post': 'create_campaign'}),
        name='api-analytics-campaigns-create'
    ),
    url(
        regex=r'^analytics/campaigns/add-assets/$',
        view=CampaignPerformanceViewSet.as_view({'post': 'add_assets'}),
        name='api-analytics-campaigns-add-assets'
    ),
    url(
        regex=r'^analytics/campaigns/(?P<campaign_id>[\w-]+)/engagement/$',
        view=CampaignPerformanceViewSet.as_view({'post': 'engagement'}),
        name='api-analytics-campaigns-engagement'
    ),
    url(
        regex=r'^analytics/dashboard/campaigns/$',
        view=CampaignPerformanceViewSet.as_view({'get': 'dashboard'}),
        name='api-analytics-campaigns-dashboard'
    ),
    url(
        regex=r'^analytics/dashboard/campaigns/top-assets/$',
        view=CampaignPerformanceViewSet.as_view({'get': 'top_assets'}),
        name='api-analytics-campaigns-top-assets'
    ),
    url(
        regex=r'^analytics/dashboard/campaigns/timeline/$',
        view=CampaignPerformanceViewSet.as_view({'get': 'timeline'}),
        name='api-analytics-campaigns-timeline'
    ),
    url(
        regex=r'^analytics/dashboard/campaigns/geography/$',
        view=CampaignPerformanceViewSet.as_view({'get': 'geography'}),
        name='api-analytics-campaigns-geography'
    ),
    # Analytics (Phase 2 - Search Analytics)
    url(
        regex=r'^analytics/dashboard/search/top-queries/$',
        view=SearchAnalyticsViewSet.as_view({'get': 'top_queries'}),
        name='api-analytics-search-top-queries'
    ),
    url(
        regex=r'^analytics/dashboard/search/null-searches/$',
        view=SearchAnalyticsViewSet.as_view({'get': 'null_searches'}),
        name='api-analytics-search-null-searches'
    ),
    url(
        regex=r'^analytics/dashboard/search/daily/$',
        view=SearchAnalyticsViewSet.as_view({'get': 'daily'}),
        name='api-analytics-search-daily'
    ),
    url(
        regex=r'^analytics/track/search/click/$',
        view=SearchAnalyticsViewSet.as_view({'post': 'click'}),
        name='api-analytics-search-track-click'
    ),
    # Analytics (Phase 2 - User activity)
    url(
        regex=r'^analytics/dashboard/users/adoption-heatmap/$',
        view=UserActivityViewSet.as_view({'get': 'adoption_by_department'}),
        name='api-analytics-user-adoption-heatmap'
    ),
    url(
        regex=r'^analytics/dashboard/users/login-patterns/$',
        view=UserActivityViewSet.as_view({'get': 'login_patterns'}),
        name='api-analytics-user-login-patterns'
    ),
    url(
        regex=r'^analytics/dashboard/users/cohorts/$',
        view=UserActivityViewSet.as_view({'get': 'cohorts'}),
        name='api-analytics-user-cohorts'
    ),
    url(
        regex=r'^analytics/dashboard/users/feature-adoption/$',
        view=UserActivityViewSet.as_view({'get': 'feature_adoption'}),
        name='api-analytics-user-feature-adoption'
    ),
    # Analytics (Phase 2 - Approval workflow)
    url(
        regex=r'^analytics/dashboard/approvals/summary/$',
        view=ApprovalAnalyticsViewSet.as_view({'get': 'summary'}),
        name='api-analytics-approvals-summary'
    ),
    url(
        regex=r'^analytics/dashboard/approvals/timeseries/$',
        view=ApprovalAnalyticsViewSet.as_view({'get': 'timeseries'}),
        name='api-analytics-approvals-timeseries'
    ),
    url(
        regex=r'^analytics/dashboard/approvals/recommendations/$',
        view=ApprovalAnalyticsViewSet.as_view({'get': 'recommendations'}),
        name='api-analytics-approvals-recommendations'
    ),
    url(
        regex=r'^analytics/dashboard/roi/summary/$',
        view=ROIDashboardViewSet.as_view({'get': 'summary'}),
        name='api-analytics-roi-summary'
    ),
    # Analytics (Release 3 - Distribution)
    url(
        regex=r'^analytics/dashboard/distribution/$',
        view=DistributionAnalyticsViewSet.as_view({'get': 'dashboard'}),
        name='api-analytics-distribution-dashboard'
    ),
    url(
        regex=r'^analytics/ingest/distribution-events/$',
        view=DistributionAnalyticsViewSet.as_view({'post': 'ingest'}),
        name='api-analytics-distribution-ingest'
    ),
    # Analytics (Release 3 - Content Intelligence)
    url(
        regex=r'^analytics/dashboard/content-intel/content-gaps/$',
        view=ContentIntelligenceViewSet.as_view({'get': 'content_gaps'}),
        name='api-analytics-content-gaps'
    ),
    url(
        regex=r'^analytics/dashboard/content-intel/compliance/metadata/$',
        view=ContentIntelligenceViewSet.as_view({'get': 'metadata_compliance'}),
        name='api-analytics-content-intel-metadata-compliance'
    ),
]
