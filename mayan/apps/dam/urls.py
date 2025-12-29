from django.urls import include, path
from django.views.generic import RedirectView
from rest_framework import routers

app_name = 'dam'

from .api_views import (  # noqa: E402
    APIYandexDiskCopyFromDAMView,
    APIYandexDiskCopyToDAMView,
    APIYandexDiskFileDownloadView,
    APIYandexDiskFilePreviewView,
    APIYandexDiskFolderDetailView,
    AIAnalysisStatusView,
    DAMDashboardStatsView,
    DAMDocumentDetailView,
    DAMDocumentListView,
    DAMMetadataPresetViewSet,
    DocumentAIAnalysisViewSet,
    DocumentOCRExtractView,
    DocumentProcessingStatusView
)
from .views import (  # noqa: E402
    DAMDashboardView,
    DAMTestView,
    DocumentAIAnalysisDetailView,
    DocumentAIAnalysisEditView,
    DocumentAIAnalysisListView,
    DocumentAIAnalysisReanalyzeView,
    DocumentDAMMetadataView,
    YandexDiskSettingsView
)

# API router
router = routers.DefaultRouter()
router.register(r'ai-analysis', DocumentAIAnalysisViewSet, basename='ai-analysis')
router.register(r'metadata-presets', DAMMetadataPresetViewSet, basename='metadata-presets')

# Inner API URL patterns (mounted under /api/v4/dam/)
api_urlpatterns = [
    path('', include(router.urls)),
    path('analysis-status/', AIAnalysisStatusView.as_view(), name='analysis-status'),
    path('document-detail/<int:document_id>/', DAMDocumentDetailView.as_view(), name='document-detail'),
    path('documents/', DAMDocumentListView.as_view(), name='document-list'),
    path('dashboard-stats/', DAMDashboardStatsView.as_view(), name='dashboard-stats'),
    # Phase B4: Processing Status API
    path('documents/<int:pk>/processing_status/', DocumentProcessingStatusView.as_view(), name='processing-status'),
    # OCR extraction endpoint
    path('documents/<int:document_id>/ocr/extract/', DocumentOCRExtractView.as_view(), name='document-ocr-extract'),
    # Yandex Disk integration
    path(
        'yandex-disk/folders/<str:encoded_path>/',
        APIYandexDiskFolderDetailView.as_view(),
        name='yandex-disk-folder-detail'
    ),
    path(
        'yandex-disk/files/<str:encoded_path>/download/',
        APIYandexDiskFileDownloadView.as_view(),
        name='yandex-disk-file-download'
    ),
    path(
        'yandex-disk/files/<str:encoded_path>/preview/',
        APIYandexDiskFilePreviewView.as_view(),
        name='yandex-disk-file-preview'
    ),
    path(
        'yandex-disk/copy-to-dam/',
        APIYandexDiskCopyToDAMView.as_view(),
        name='yandex-disk-copy-to-dam'
    ),
    path(
        'yandex-disk/copy-from-dam/',
        APIYandexDiskCopyFromDAMView.as_view(),
        name='yandex-disk-copy-from-dam'
    ),
]

# Alias for REST API auto-discovery.
# These URLs will be included under `/api/v4/` by `rest_api.urls`,
# resulting in final paths like `/api/v4/dam/...`.
api_urls = [
    path(
        route='dam/',
        view=include((api_urlpatterns, 'dam'), namespace='dam')
    )
]

# UI URL patterns
ui_urlpatterns = [
    path(
        'settings/',
        RedirectView.as_view(url='/settings/namespaces/dam/', permanent=False),
        name='settings'
    ),
    path(
        'setup/yandex-disk/',
        YandexDiskSettingsView.as_view(),
        name='yandex_settings'
    ),
    path(
        'digital-assets/',
        DAMDashboardView.as_view(),
        name='dashboard'
    ),
    path(
        'test/',
        DAMTestView.as_view(),
        name='test'
    ),
    path(
        'analyses/',
        DocumentAIAnalysisListView.as_view(),
        name='ai_analysis_list'
    ),
    path(
        'document/<int:document_id>/',
        DocumentDAMMetadataView.as_view(),
        name='document_dam_metadata'
    ),
    path(
        'analysis/<int:ai_analysis_id>/',
        DocumentAIAnalysisDetailView.as_view(),
        name='asset_detail'
    ),
    path(
        'analysis/<int:ai_analysis_id>/edit/',
        DocumentAIAnalysisEditView.as_view(),
        name='asset_edit'
    ),
    path(
        'analysis/<int:ai_analysis_id>/reanalyze/',
        DocumentAIAnalysisReanalyzeView.as_view(),
        name='asset_reanalyze'
    ),
]

# Main URL patterns
urlpatterns = [
    path('api/', include(api_urlpatterns)),
    path('', include(ui_urlpatterns)),
]
