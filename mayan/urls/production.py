from django.conf import settings
from django.conf.urls import include, url

from .base import *  # NOQA

# DAM app URLs (for production)
if 'mayan.apps.dam' in getattr(settings, 'INSTALLED_APPS', []):
    urlpatterns += [  # NOQA
        url(regex=r'^dam/', view=include('mayan.apps.dam.urls'))
    ]
