from django.urls import path, include
from django.http import HttpResponse

from .api_urls import urlpatterns as api_urlpatterns
from .public_urls import urlpatterns as public_urlpatterns
from ..ui_views import (
    AddToPublicationView, DocumentPublicationsView, GenerateFileRenditionsView,
    PresetsListView, PresetsView, PublicationCreateFromDocumentView,
    PublicationCreateMultipleView, PublicationCreateView, PublicationDeleteView,
    PublicationDetailView, PublicationListView, RecipientsListView,
    RecipientsView, ShareLinkManagementView, ShareLinksListView, ShareLinksView,
    SimpleTestView, TestView
)

app_name = 'distribution'

# API URLs for REST framework (this is what REST API app discovers)
api_urls = api_urlpatterns

# UI URL patterns with namespace
ui_urlpatterns = [
    # Test URL
    path('test/', lambda request: HttpResponse('Distribution UI works!'), name='test'),

    # Simple publication list test
    path('publications-test/', lambda request: HttpResponse('<h1>Publications Test</h1><p>Distribution UI is working!</p>'), name='publication_list_test'),

    # Test URL without namespace
    path('test-no-namespace/', lambda request: HttpResponse('<h1>Test No Namespace</h1><p>This works!</p>'), name='test_no_namespace'),

    # Test TemplateView
    path('test-template/', TestView.as_view(), name='test_template'),

    # Simple HTML test page
    path('test-simple/', SimpleTestView.as_view(), name='test_simple'),

    # Public portal URLs (no auth required)
    *public_urlpatterns,

    # UI URLs для управления публикациями
    path(
        'documents/<int:document_id>/publish/',
        PublicationCreateFromDocumentView.as_view(),
        name='publication_create_from_document'
    ),
    path(
        'documents/<int:document_id>/publications/',
        DocumentPublicationsView.as_view(),
        name='document_publications'
    ),
    path(
        'publications/create-multiple/',
        PublicationCreateMultipleView.as_view(),
        name='publication_create_multiple'
    ),

    # UI URLs для файлов документов
    path(
        'files/<int:document_file_id>/add-to-publication/',
        AddToPublicationView.as_view(),
        name='add_to_publication'
    ),
    path(
        'files/<int:document_file_id>/generate-renditions/',
        GenerateFileRenditionsView.as_view(),
        name='generate_file_renditions'
    ),

    # UI URLs для публикаций (SPA-compatible)
    path(
        'publications/',
        PublicationListView.as_view(),
        name='publication_list'
    ),
    path(
        'publications/create/',
        PublicationCreateView.as_view(),
        name='publication_create'
    ),
    path(
        'publications/<int:pk>/',
        PublicationDetailView.as_view(),
        name='publication_detail'
    ),
    path(
        'publications/<int:pk>/delete/',
        PublicationDeleteView.as_view(),
        name='publication_delete'
    ),

    # UI URLs для управления (SPA-compatible)
    path(
        'recipients/',
        RecipientsView.as_view(),
        name='recipient_list'
    ),
    path(
        'presets/',
        PresetsView.as_view(),
        name='preset_list'
    ),
    path(
        'share-links/',
        ShareLinksView.as_view(),
        name='share_link_list'
    ),
    path(
        'share-links/manage/',
        ShareLinkManagementView.as_view(),
        name='share_link_manage'
    ),

    # Test views
    path('test-template/', TestView.as_view(), name='test_template'),
    path('test-simple/', SimpleTestView.as_view(), name='test_simple'),
]

urlpatterns = ui_urlpatterns
