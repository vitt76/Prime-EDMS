from django.urls import path, include

app_name = 'distribution'

# Import API URLs from api_urls.py
from .urls.api_urls import urlpatterns as api_urls

# Make api_urls available as module attribute for REST API
api_urls = api_urls

urlpatterns = [
    # Админ URLs будут добавлены позже
]
