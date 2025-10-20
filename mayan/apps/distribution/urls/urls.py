from django.urls import path
from .api_urls import urlpatterns as api_urlpatterns
from .public_urls import urlpatterns as public_urlpatterns
from ..ui_views import (
    AddDocumentsToPublicationView, AddToPublicationView, DocumentPublicationsView, GenerateFileRenditionsView,
    PresetCreateTemplateView, PresetDeleteView, PresetEditTemplateView, PresetsTemplateView,
    PublicationCreateFromDocumentView, PublicationCreateMultipleView, PublicationCreateTemplateView,
    PublicationDeleteView, PublicationDetailView, PublicationEditView, PublicationListTemplateView,
    RecipientsTemplateView, ShareLinkManagementView, ShareLinksTemplateView,
    RenditionDownloadView
)
from ..views.share_link_views import ShareLinkCreateView

app_name = 'distribution'

# API URLs for REST framework (this is what REST API app discovers)
api_urls = api_urlpatterns

# UI URL patterns with namespace
ui_urlpatterns = [
    # Test URL

    # Public portal URLs (no auth required)
    *public_urlpatterns,

    # UI URLs для управления публикациями
    path(
        'distribution/documents/<int:document_id>/publish/',
        PublicationCreateFromDocumentView.as_view(),
        name='publication_create_from_document'
    ),
    path(
        'distribution/documents/<int:document_id>/publications/',
        DocumentPublicationsView.as_view(),
        name='document_publications'
    ),
    path(
        'distribution/publications/create-multiple/',
        PublicationCreateMultipleView.as_view(),
        name='publication_create_multiple'
    ),

    # UI URLs для файлов документов
    path(
        'distribution/files/<int:document_file_id>/add-to-publication/',
        AddToPublicationView.as_view(),
        name='add_to_publication'
    ),
    path(
        'distribution/files/<int:document_file_id>/generate-renditions/',
        GenerateFileRenditionsView.as_view(),
        name='generate_file_renditions'
    ),

    # UI URLs для публикаций (SPA-compatible)
    path(
        'distribution/publications/',
        PublicationListTemplateView.as_view(),
        name='publication_list'
    ),
    path(
        'distribution/publications/create/',
        PublicationCreateTemplateView.as_view(),
        name='publication_create'
    ),
    path(
        'distribution/publications/<int:pk>/',
        PublicationDetailView.as_view(),
        name='publication_detail'
    ),
    path(
        'distribution/publications/<int:pk>/edit/',
        PublicationEditView.as_view(),
        name='publication_edit'
    ),
    path(
        'distribution/publications/<int:pk>/delete/',
        PublicationDeleteView.as_view(),
        name='publication_delete'
    ),
    path(
        'distribution/publications/<int:publication_id>/add-documents/',
        AddDocumentsToPublicationView.as_view(),
        name='add_documents_to_publication'
    ),
    path(
        'distribution/renditions/<int:rendition_id>/download/',
        RenditionDownloadView.as_view(),
        name='rendition_download'
    ),

    # UI URLs для управления (SPA-compatible)
    path(
        'distribution/recipients/',
        RecipientsTemplateView.as_view(),
        name='recipient_list'
    ),
    path(
        'distribution/presets/',
        PresetsTemplateView.as_view(),
        name='preset_list'
    ),
    path(
        'distribution/presets/create/',
        PresetCreateTemplateView.as_view(),
        name='preset_create'
    ),
    path(
        'distribution/presets/<int:preset_id>/edit/',
        PresetEditTemplateView.as_view(),
        name='preset_edit'
    ),
    path(
        'distribution/presets/<int:preset_id>/delete/',
        PresetDeleteView.as_view(),
        name='preset_delete'
    ),
    path(
        'distribution/share-links/',
        ShareLinksTemplateView.as_view(),
        name='share_link_list'
    ),
    path(
        'distribution/share-links/manage/',
        ShareLinkManagementView.as_view(),
        name='share_link_manage'
    ),
    path(
        'distribution/share-links/create/<int:rendition_id>/',
        ShareLinkCreateView.as_view(),
        name='share_link_create'
    ),
]

urlpatterns = ui_urlpatterns
