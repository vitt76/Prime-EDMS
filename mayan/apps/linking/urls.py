from django.conf.urls import url

from .api_views import (
    APIDocumentResolvedSmartLinkDetailView,
    APIDocumentResolvedSmartLinkDocumentListView,
    APIDocumentResolvedSmartLinkListView, APISmartLinkListView, APISmartLinkDetailView,
    APISmartLinkConditionListView, APISmartLinkConditionView,
    APISmartLinkDocumentTypeAddView, APISmartLinkDocumentTypeListView,
    APISmartLinkDocumentTypeRemoveView
)
from .views.smart_link_condition_views import (
    SmartLinkConditionCreateView, SmartLinkConditionDeleteView,
    SmartLinkConditionEditView, SmartLinkConditionListView
)
from .views.smart_link_views import (
    DocumentResolvedSmartLinkListView, DocumentTypeSmartLinkAddRemoveView,
    DocumentResolvedSmartLinkDocumentListView, SmartLinkCreateView,
    SmartLinkDeleteView, SmartLinkDocumentTypeAddRemoveView,
    SmartLinkEditView, SmartLinkListView
)

urlpatterns = [
    url(
        regex=r'^documents/(?P<document_id>\d+)/smart_links/$',
        name='document_smart_link_instance_list',
        view=DocumentResolvedSmartLinkListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/smart_links/(?P<smart_link_id>\d+)/$',
        name='smart_link_instance_view',
        view=DocumentResolvedSmartLinkDocumentListView.as_view()
    ),
    url(
        regex=r'^document_types/(?P<document_type_id>\d+)/smart_links/$',
        name='document_type_smart_links',
        view=DocumentTypeSmartLinkAddRemoveView.as_view()
    ),
    url(
        regex=r'^smart_links/$', name='smart_link_list',
        view=SmartLinkListView.as_view()
    ),
    url(
        regex=r'^smart_links/create/$', name='smart_link_create',
        view=SmartLinkCreateView.as_view()
    ),
    url(
        regex=r'^smart_links/(?P<smart_link_id>\d+)/delete/$',
        name='smart_link_delete', view=SmartLinkDeleteView.as_view()
    ),
    url(
        regex=r'^smart_links/(?P<smart_link_id>\d+)/document_types/$',
        name='smart_link_document_types',
        view=SmartLinkDocumentTypeAddRemoveView.as_view()
    ),
    url(
        regex=r'^smart_links/(?P<smart_link_id>\d+)/edit/$',
        name='smart_link_edit', view=SmartLinkEditView.as_view()
    ),
    url(
        regex=r'^smart_links/(?P<smart_link_id>\d+)/conditions/$',
        name='smart_link_condition_list',
        view=SmartLinkConditionListView.as_view()
    ),
    url(
        regex=r'^smart_links/(?P<smart_link_id>\d+)/conditions/create/$',
        name='smart_link_condition_create',
        view=SmartLinkConditionCreateView.as_view()
    ),
    url(
        regex=r'^smart_links/conditions/(?P<smart_link_condition_id>\d+)/delete/$',
        name='smart_link_condition_delete',
        view=SmartLinkConditionDeleteView.as_view()
    ),
    url(
        regex=r'^smart_links/conditions/(?P<smart_link_condition_id>\d+)/edit/$',
        name='smart_link_condition_edit',
        view=SmartLinkConditionEditView.as_view()
    )
]

api_urls = [
    url(
        regex=r'^smart_links/$', name='smartlink-list',
        view=APISmartLinkListView.as_view()
    ),
    url(
        regex=r'^smart_links/(?P<smart_link_id>[0-9]+)/$', name='smartlink-detail',
        view=APISmartLinkDetailView.as_view()
    ),
    url(
        regex=r'^smart_links/(?P<smart_link_id>[0-9]+)/conditions/$',
        name='smartlinkcondition-list',
        view=APISmartLinkConditionListView.as_view()
    ),
    url(
        regex=r'^smart_links/(?P<smart_link_id>[0-9]+)/conditions/(?P<smart_link_condition_id>[0-9]+)/$',
        name='smartlinkcondition-detail',
        view=APISmartLinkConditionView.as_view()
    ),
    url(
        regex=r'^smart_links/(?P<smart_link_id>[0-9]+)/document_types/$',
        name='smartlink-document_type-list',
        view=APISmartLinkDocumentTypeListView.as_view()
    ),
    url(
        regex=r'^smart_links/(?P<smart_link_id>[0-9]+)/document_types/add/$',
        name='smartlink-document_type-add',
        view=APISmartLinkDocumentTypeAddView.as_view()
    ),
    url(
        regex=r'^smart_links/(?P<smart_link_id>[0-9]+)/document_types/remove/$',
        name='smartlink-document_type-remove',
        view=APISmartLinkDocumentTypeRemoveView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>[0-9]+)/resolved_smart_links/$',
        name='resolvedsmartlink-list',
        view=APIDocumentResolvedSmartLinkListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>[0-9]+)/resolved_smart_links/(?P<resolved_smart_link_id>[0-9]+)/$',
        name='resolvedsmartlink-detail',
        view=APIDocumentResolvedSmartLinkDetailView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>[0-9]+)/resolved_smart_links/(?P<resolved_smart_link_id>[0-9]+)/documents/$',
        name='resolvedsmartlinkdocument-list',
        view=APIDocumentResolvedSmartLinkDocumentListView.as_view()
    )
]
