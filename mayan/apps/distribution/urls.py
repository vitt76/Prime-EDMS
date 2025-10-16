from django.urls import path, include

from .urls.api_urls import urlpatterns as api_urlpatterns
from .urls.public_urls import urlpatterns as public_urlpatterns

app_name = 'distribution'

# API URLs for REST framework (this is what REST API app discovers)
api_urls = api_urlpatterns

urlpatterns = [
    # Public portal URLs (no auth required)
    *public_urlpatterns,

    # Админ URLs будут добавлены позже
]
