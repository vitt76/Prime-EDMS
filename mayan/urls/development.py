from django.conf import settings
from django.conf.urls import include, url

from .base import *  # NOQA

if 'rosetta' in settings.INSTALLED_APPS:
    try:
        import rosetta  # NOQA
    except ImportError:
        pass
    else:
        urlpatterns += [  # NOQA
            url(regex=r'^rosetta/', view=include('rosetta.urls'), name='rosetta')
        ]

if 'debug_toolbar' in settings.INSTALLED_APPS:
    try:
        import debug_toolbar
    except ImportError:
        pass
    else:
        urlpatterns += [  # NOQA
            url(regex=r'^__debug__/', view=include(debug_toolbar.urls))
        ]

if 'silk' in settings.INSTALLED_APPS:
    try:
        import silk
    except ImportError:
        pass
    else:
        urlpatterns += [  # NOQA
            url(regex=r'^silk/', view=include('silk.urls', namespace='silk'))
        ]

# Add distribution URLs
# Temporarily disabled for debugging
# if 'mayan.apps.distribution' in settings.INSTALLED_APPS:
#     try:
#         from mayan.apps.distribution.urls.api_urls import urlpatterns as distribution_urls
#         urlpatterns += [  # NOQA
#             url(regex=r'^api/v4/', view=include(distribution_urls))
#         ]
#         print("DEBUG: Added distribution URLs to main urlpatterns")
#     except ImportError as e:
#         print(f"WARNING: Could not import distribution URLs: {e}")