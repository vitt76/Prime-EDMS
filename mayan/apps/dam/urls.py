from django.urls import path, include
from rest_framework import routers

from .api_views import (
    DocumentAIAnalysisViewSet,
    DAMMetadataPresetViewSet,
    AIAnalysisStatusView
)

# API router
router = routers.DefaultRouter()
router.register(r'ai-analysis', DocumentAIAnalysisViewSet, basename='ai-analysis')
router.register(r'metadata-presets', DAMMetadataPresetViewSet, basename='metadata-presets')

# API URL patterns
api_urlpatterns = [
    path('', include(router.urls)),
    path('analysis-status/', AIAnalysisStatusView.as_view(), name='analysis-status'),
]

# Main URL patterns
urlpatterns = [
    path('api/', include(api_urlpatterns)),
]
