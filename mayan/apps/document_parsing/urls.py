from django.conf.urls import url

from .api_views import (
    APIDocumentFilePageContentView, APIDocumentTypeParsingSettingsView
)
from .views import (
    DocumentFileContentView, DocumentFileContentDeleteView,
    DocumentFileContentDownloadView, DocumentFilePageContentView,
    DocumentFileSubmitView, DocumentTypeSettingsEditView,
    DocumentTypeSubmitView
)

urlpatterns_document_files = [
    url(
        regex=r'^documents/files/(?P<document_file_id>\d+)/content/$',
        name='document_file_content_view',
        view=DocumentFileContentView.as_view()
    ),
    url(
        regex=r'^documents/files/(?P<document_file_id>\d+)/content/delete/$',
        name='document_file_content_single_delete',
        view=DocumentFileContentDeleteView.as_view()
    ),
    url(
        regex=r'^documents/files/multiple/content/delete/$',
        name='document_file_content_multiple_delete',
        view=DocumentFileContentDeleteView.as_view()
    ),
    url(
        regex=r'^documents/files/(?P<document_file_id>\d+)/content/download/$',
        name='document_file_content_download',
        view=DocumentFileContentDownloadView.as_view()
    ),
    url(
        regex=r'^documents/files/(?P<document_file_id>\d+)/submit/$',
        name='document_file_parsing_single_submit',
        view=DocumentFileSubmitView.as_view()
    ),
    url(
        regex=r'^documents/files/multiple/submit/$',
        name='document_file_parsing_multiple_submit',
        view=DocumentFileSubmitView.as_view()
    ),
    url(
        regex=r'^documents/files/pages/(?P<document_file_page_id>\d+)/content/$',
        name='document_file_page_content_view',
        view=DocumentFilePageContentView.as_view()
    )
]

urlpatterns_document_types = [
    url(
        regex=r'^document_types/submit/$', name='document_type_submit',
        view=DocumentTypeSubmitView.as_view()
    ),
    url(
        regex=r'^document_types/(?P<document_type_id>\d+)/parsing/settings/$',
        name='document_type_parsing_settings',
        view=DocumentTypeSettingsEditView.as_view()
    )
]

urlpatterns = []
urlpatterns.extend(urlpatterns_document_files)
urlpatterns.extend(urlpatterns_document_types)

api_urls = [
    url(
        regex=r'^document_types/(?P<document_type_id>\d+)/parsing/settings/$',
        name='document-type-parsing-settings-view',
        view=APIDocumentTypeParsingSettingsView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/files/(?P<document_file_id>\d+)/pages/(?P<document_file_page_id>\d+)/content/$',
        name='document-file-page-content-view',
        view=APIDocumentFilePageContentView.as_view()
    )
]
