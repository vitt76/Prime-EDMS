from django.conf.urls import include, url
from django.views.generic import RedirectView

from .views import (
    DownloadFileDeleteView, DownloadFileDownloadViewView,
    DownloadFileListView
)
from .api_views_chunked_upload import (
    ChunkedUploadInitView,
    ChunkedUploadAppendView,
    ChunkedUploadCompleteView,
    ChunkedUploadStatusView,
    ChunkedUploadAbortView
)

# UI URL patterns
urlpatterns = [
    url(
        regex=r'^downloads/(?P<download_file_id>\d+)/delete/$',
        name='download_file_delete',
        view=DownloadFileDeleteView.as_view()
    ),
    url(
        regex=r'^downloads/(?P<download_file_id>\d+)/download/$',
        name='download_file_download',
        view=DownloadFileDownloadViewView.as_view()
    ),
    url(
        regex=r'^downloads/$', name='download_file_list',
        view=DownloadFileListView.as_view()
    ),
    url(
        regex=r'^settings/$',
        view=RedirectView.as_view(url='/settings/namespaces/storage/', permanent=False),
        name='settings'
    )
]

# API URL patterns for chunked upload (Phase B3.2)
api_urls = [
    url(
        regex=r'^uploads/init/$',
        name='chunked_upload_init',
        view=ChunkedUploadInitView.as_view()
    ),
    url(
        regex=r'^uploads/append/$',
        name='chunked_upload_append',
        view=ChunkedUploadAppendView.as_view()
    ),
    url(
        regex=r'^uploads/complete/$',
        name='chunked_upload_complete',
        view=ChunkedUploadCompleteView.as_view()
    ),
    url(
        regex=r'^uploads/status/(?P<upload_id>[0-9a-f-]+)/$',
        name='chunked_upload_status',
        view=ChunkedUploadStatusView.as_view()
    ),
    url(
        regex=r'^uploads/abort/$',
        name='chunked_upload_abort',
        view=ChunkedUploadAbortView.as_view()
    ),
]
