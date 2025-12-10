from django.conf.urls import url

from .api_views import AutoAdminCredentialsAPIView

api_urls = [
    url(
        regex=r'^credentials/$',
        view=AutoAdminCredentialsAPIView.as_view(),
        name='autoadmin-credentials'
    )
]

