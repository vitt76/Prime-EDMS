# URLs package

# Import and expose api_urls for REST API
from .api_urls import urlpatterns as api_urls

# Main urlpatterns for the app - import from urls.py
from .urls import urlpatterns
