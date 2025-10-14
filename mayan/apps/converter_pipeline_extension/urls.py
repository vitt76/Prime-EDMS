"""
URL patterns for Converter Pipeline Extension
"""

from django.urls import path, include
from django.http import HttpResponse

from .views import (
    DocumentFileConversionAPIView, DocumentFileConvertRedirectView,
    MediaConversionView
)
from django.views.generic import TemplateView

app_name = 'converter_pipeline_extension'

# Удаляем простую функцию, используем MediaConversionView

urlpatterns = [
    # Тестовый URL для проверки
    path(
        'test/',
        TemplateView.as_view(template_name='converter_pipeline_extension/setup_instructions.html'),
        name='test_page'
    ),
    # Основные страницы конвертации
    path(
        'media-conversion/<int:document_file_id>/',
        MediaConversionView.as_view(),
        name='convert_media'
    ),
    # REST API endpoints
    path(
        'api/document-files/<int:document_file_id>/convert/',
        DocumentFileConversionAPIView.as_view(),
        name='document_file_convert_api'
    ),
    # Setup instructions
    path(
        'setup/',
        TemplateView.as_view(template_name='converter_pipeline_extension/setup_instructions.html'),
        name='setup_instructions'
    ),
]
