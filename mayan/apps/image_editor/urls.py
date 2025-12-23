from django.urls import path

from .views import ImageEditorView, WatermarkListView, WatermarkAssetView

app_name = 'image_editor'

# UI URL patterns - основной интерфейс
ui_urlpatterns = [
    path(
        'edit/<int:document_file_id>/',
        ImageEditorView.as_view(),
        name='edit_image'
    ),
    # [DEPRECATED] ImageEditorSaveView URL removed 2025-12-23
    # Replaced by HeadlessEditView: POST /api/v4/headless/documents/{id}/versions/new_from_edit/
]

# API URL patterns
api_urls = [
    path(
        'watermarks/',
        WatermarkListView.as_view(),
        name='list_watermarks'
    ),
    path(
        'watermark/<int:asset_id>/',
        WatermarkAssetView.as_view(),
        name='get_watermark'
    ),
]

# Основные URL patterns
urlpatterns = ui_urlpatterns + api_urls

# ДОПОЛНИТЕЛЬНЫЙ URL ДЛЯ ТЕСТИРОВАНИЯ (ОБЫЧНАЯ НАВИГАЦИЯ)
urlpatterns += [
    path('test/<int:document_file_id>/', ImageEditorView.as_view(), name='test_editor'),
]
