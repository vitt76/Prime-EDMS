"""
API URL patterns for Storage app.
Phase B3.2 - Chunked Upload API Support.
"""
from django.conf.urls import url

from .api_views_chunked_upload import (
    ChunkedUploadInitView,
    ChunkedUploadAppendView,
    ChunkedUploadCompleteView,
    ChunkedUploadStatusView,
    ChunkedUploadAbortView
)

api_urls = [
    # Chunked Upload API
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


