from django.urls import path

from ..views import PublicationPortalView, download_rendition
from ..views.portal_views import share_link_view, check_share_link_password

# Public URLs (no authentication required)
urlpatterns = [
    # Publication portal - public access via token
    path(
        route='publish/<str:token>/',
        view=PublicationPortalView.as_view(),
        name='portal'
    ),

    # Download specific rendition
    path(
        route='publish/<str:token>/download/<int:rendition_id>/',
        view=download_rendition,
        name='download_rendition'
    ),

    # Direct access to rendition by share link token
    path(
        route='<str:token>/',
        view=share_link_view,
        name='share_link_direct'
    ),

    # Check password for share link (API endpoint)
    path(
        route='<str:token>/check-password/',
        view=check_share_link_password,
        name='check_share_link_password'
    ),
]
