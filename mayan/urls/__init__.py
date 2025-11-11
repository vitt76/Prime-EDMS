from django.conf.urls import include, url

from .base import *  # NOQA

try:
    urlpatterns += [  # NOQA
        url(
            regex=r'^dam/',
            view=include(('mayan.apps.dam.urls', 'dam'), namespace='dam')
        )
    ]
    print('✅ mayan.urls: DAM URLs included at import time.')
except ImportError as exc:
    print(f'⚠️ mayan.urls: DAM URLs import skipped: {exc}')
