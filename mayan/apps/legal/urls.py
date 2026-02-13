from django.conf.urls import url

from .api_views import ConsentLogAPIView

app_name = 'legal'

api_urls = [
    url(
        regex=r'^public/legal/consent/$',
        view=ConsentLogAPIView.as_view(),
        name='public-legal-consent'
    ),
]
