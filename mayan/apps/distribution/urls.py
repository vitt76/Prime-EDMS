from django.urls import path, include

from .urls.api_urls import urlpatterns as api_urlpatterns

app_name = 'distribution'

# API URLs for REST framework
api_urls = api_urlpatterns

urlpatterns = [
    # Админ URLs будут добавлены позже
]
