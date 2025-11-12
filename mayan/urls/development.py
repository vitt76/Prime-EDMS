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

# Note: converter_pipeline_extension is registered automatically
# via MayanAppConfig for extra_apps in config.yml

# Specific routes for DAM SPA pages (exclude API)
from django.views.generic import TemplateView
urlpatterns += [  # NOQA
    url(regex=r'^digital-assets/digital-assets/(?!api/).*', view=TemplateView.as_view(template_name='appearance/base.html'), name='dam-dashboard-spa-route'),
    url(regex=r'^digital-assets/(?!api/).*', view=TemplateView.as_view(template_name='appearance/base.html'), name='dam-spa-route')
]