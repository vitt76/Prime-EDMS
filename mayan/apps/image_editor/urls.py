from django.urls import path

from .views import ImageEditorView, ImageEditorSaveView

app_name = 'image_editor'

# UI URL patterns - основной интерфейс
ui_urlpatterns = [
    path(
        'edit/<int:document_file_id>/',
        ImageEditorView.as_view(),
        name='edit_image'
    ),
    path(
        'save/<int:document_file_id>/',
        ImageEditorSaveView.as_view(),
        name='save_image'
    )
]

# API URL patterns (пока пустые)
api_urls = []

# Основные URL patterns
urlpatterns = ui_urlpatterns + api_urls

# ДОПОЛНИТЕЛЬНЫЙ URL ДЛЯ ТЕСТИРОВАНИЯ (ОБЫЧНАЯ НАВИГАЦИЯ)
from .views import ImageEditorView
urlpatterns += [
    path('test/<int:document_file_id>/', ImageEditorView.as_view(), name='test_editor'),
]
