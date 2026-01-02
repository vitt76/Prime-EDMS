from django.conf import settings
from django.conf.urls import include, url

from .base import *  # NOQA

# Prometheus metrics endpoint (best-effort, optional dependency).
if 'django_prometheus' in settings.INSTALLED_APPS:
    try:
        import django_prometheus  # NOQA: F401
    except ImportError:
        pass
    else:
        urlpatterns += [  # NOQA
            url(regex=r'^metrics/', view=include('django_prometheus.urls'))
        ]

# DAM app URLs (for production)
if 'mayan.apps.dam' in getattr(settings, 'INSTALLED_APPS', []):
    urlpatterns += [  # NOQA
        url(regex=r'^dam/', view=include('mayan.apps.dam.urls'))
    ]
