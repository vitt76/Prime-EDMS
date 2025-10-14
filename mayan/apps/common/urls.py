from django.conf.urls import url
from django.contrib import admin

from django.views.i18n import JavaScriptCatalog

from .api_views import APIContentTypeList
from .views import (
    AboutView, FaviconRedirectView, HomeView, LicenseView, ObjectCopyView,
    RootView, SetupListView, ToolsListView
)

# Import converter redirect view for public access
try:
    from mayan.apps.converter_pipeline_extension.views import DocumentFileConvertRedirectView
except ImportError:
    DocumentFileConvertRedirectView = None

urlpatterns_misc = [
    url(
        regex=r'^favicon\.ico$', view=FaviconRedirectView.as_view()
    ),
    url(
        regex=r'^jsi18n/(?P<packages>\S+?)/$', name='javascript_catalog',
        view=JavaScriptCatalog.as_view()
    ),
    url(
        regex=r'^object/(?P<app_label>[-\w]+)/(?P<model_name>[-\w]+)/(?P<object_id>\d+)/copy/$',
        name='object_copy', view=ObjectCopyView.as_view()
    ),
]

# Converter redirect URL moved to main urlpatterns above

urlpatterns = [
    url(regex=r'^$', name='root', view=RootView.as_view()),
    url(regex=r'^home/$', name='home', view=HomeView.as_view()),
    url(regex=r'^about/$', name='about_view', view=AboutView.as_view()),
    url(regex=r'^license/$', name='license_view', view=LicenseView.as_view()),
    url(regex=r'^setup/$', name='setup_list', view=SetupListView.as_view()),
    url(regex=r'^tools/$', name='tools_list', view=ToolsListView.as_view())
]

# Add converter redirect URL if extension is available
if DocumentFileConvertRedirectView:
    urlpatterns.append(
        url(
            regex=r'^converter-pipeline/document-files/(?P<document_file_id>\d+)/convert/$',
            view=DocumentFileConvertRedirectView.as_view(),
            name='document_file_convert_redirect_public'
        )
    )

urlpatterns.extend(urlpatterns_misc)

passthru_urlpatterns = [
    url(regex=r'^admin/', view=admin.site.urls)
]

api_urls = [
    url(
        regex=r'^content_types/$', view=APIContentTypeList.as_view(),
        name='content-type-list'
    )
]
