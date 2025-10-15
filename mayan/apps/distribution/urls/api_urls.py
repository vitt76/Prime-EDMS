from django.http import JsonResponse
from django.urls import path

from ..views import (
    APIAccessLogListView, APIGeneratedRenditionDetailView,
    APIGeneratedRenditionListView, APIPublicationDetailView,
    APIPublicationItemDetailView, APIPublicationItemListView,
    APIPublicationListView, APIRecipientDetailView, APIRecipientListDetailView,
    APIRecipientListListView, APIRecipientListView, APIRenditionPresetDetailView,
    APIRenditionPresetListView, APIShareLinkDetailView, APIShareLinkListView
)

# API URLs для distribution
print("DEBUG: api_urls.py loaded, creating urlpatterns")
urlpatterns = [
    # Recipients
    path(
        route='recipients/',
        view=APIRecipientListView.as_view(),
        name='recipient-list'
    ),
    path(
        route='recipients/<int:recipient_id>/',
        view=APIRecipientDetailView.as_view(),
        name='recipient-detail'
    ),

    # Recipient Lists
    path(
        route='recipient_lists/',
        view=APIRecipientListListView.as_view(),
        name='recipientlist-list'
    ),
    path(
        route='recipient_lists/<int:recipient_list_id>/',
        view=APIRecipientListDetailView.as_view(),
        name='recipientlist-detail'
    ),

    # Rendition Presets
    path(
        route='rendition_presets/',
        view=APIRenditionPresetListView.as_view(),
        name='renditionpreset-list'
    ),
    path(
        route='rendition_presets/<int:preset_id>/',
        view=APIRenditionPresetDetailView.as_view(),
        name='renditionpreset-detail'
    ),

    # Publications
    path(
        route='publications/',
        view=APIPublicationListView.as_view(),
        name='publication-list'
    ),
    path(
        route='publications/<int:publication_id>/',
        view=APIPublicationDetailView.as_view(),
        name='publication-detail'
    ),

    # Publication Items
    path(
        route='publication_items/',
        view=APIPublicationItemListView.as_view(),
        name='publicationitem-list'
    ),
    path(
        route='publication_items/<int:publication_item_id>/',
        view=APIPublicationItemDetailView.as_view(),
        name='publicationitem-detail'
    ),

    # Share Links
    path(
        route='share_links/',
        view=APIShareLinkListView.as_view(),
        name='sharelink-list'
    ),
    path(
        route='share_links/<int:share_link_id>/',
        view=APIShareLinkDetailView.as_view(),
        name='sharelink-detail'
    ),

    # Generated Renditions
    path(
        route='generated_renditions/',
        view=APIGeneratedRenditionListView.as_view(),
        name='generatedrendition-list'
    ),
    path(
        route='generated_renditions/<int:rendition_id>/',
        view=APIGeneratedRenditionDetailView.as_view(),
        name='generatedrendition-detail'
    ),

    # Access Logs
    path(
        route='access_logs/',
        view=APIAccessLogListView.as_view(),
        name='accesslog-list'
    ),

    # Test endpoint
    path(
        route='test/',
        view=lambda request: JsonResponse({'status': 'ok', 'app': 'distribution'}),
        name='distribution-test'
    ),
]
