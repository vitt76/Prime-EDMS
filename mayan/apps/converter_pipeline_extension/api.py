"""
REST API for Converter Pipeline Extension
"""

from mayan.apps.rest_api import routers
from .views import DocumentFileConversionAPIView

router = routers.DefaultRouter()

# API endpoints will be auto-discovered by Mayan EDMS
# when has_rest_api = True in apps.py

api_router_entries = []

