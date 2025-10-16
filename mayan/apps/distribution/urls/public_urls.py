from django.urls import path

from ..views import PublicationPortalView, download_rendition

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
]
