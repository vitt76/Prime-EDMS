from django.urls import path, include
from django.views.generic import TemplateView, RedirectView
from rest_framework import routers

app_name = 'dam'

from .api_views import (
    DocumentAIAnalysisViewSet,
    DAMMetadataPresetViewSet,
    AIAnalysisStatusView,
    DAMDocumentDetailView,
    DAMDocumentListView,
    DAMDashboardStatsView,
    DocumentProcessingStatusView,
    DocumentOCRExtractView
)
from .views import (
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

# API URL patterns
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
]

# Alias for REST API auto-discovery
api_urls = api_urlpatterns

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
