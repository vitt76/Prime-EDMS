from django.conf.urls import url

from .api_views import (
    APICabinetDocumentAddView, APICabinetDocumentBulkAddView,
    APICabinetDocumentBulkRemoveView, APICabinetDocumentListView,
    APICabinetDocumentRemoveView, APICabinetListView, APICabinetShareListView,
    APICabinetShareView, APICabinetTreeView, APICabinetView,
    APIDocumentCabinetListView, PublicCabinetShareDetailView
)
from .views import (
    DocumentCabinetAddView, DocumentCabinetListView,
    DocumentCabinetRemoveView, CabinetChildAddView, CabinetCreateView,
    CabinetDeleteView, CabinetDetailView, CabinetEditView, CabinetListView,
)

urlpatterns_cabinets = [
    url(
        regex=r'^cabinets/$', name='cabinet_list',
        view=CabinetListView.as_view()
    ),
    url(
        regex=r'^cabinets/create/$', name='cabinet_create',
        view=CabinetCreateView.as_view()
    ),
    url(
        regex=r'^cabinets/(?P<cabinet_id>\d+)/$', name='cabinet_view',
        view=CabinetDetailView.as_view()
    ),
    url(
        regex=r'^cabinets/(?P<cabinet_id>\d+)/children/add/$',
        name='cabinet_child_add', view=CabinetChildAddView.as_view()
    ),
    url(
        regex=r'^cabinets/(?P<cabinet_id>\d+)/delete/$',
        name='cabinet_delete', view=CabinetDeleteView.as_view()
    ),
    url(
        regex=r'^cabinets/(?P<cabinet_id>\d+)/edit/$', name='cabinet_edit',
        view=CabinetEditView.as_view()
    )
]

urlpatterns_documents_cabinets = [
    url(
        regex=r'^documents/(?P<document_id>\d+)/cabinets/$',
        name='document_cabinet_list', view=DocumentCabinetListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/cabinets/add/$',
        name='document_cabinet_add', view=DocumentCabinetAddView.as_view()
    ),
    url(
        regex=r'^documents/multiple/cabinets/add/$',
        name='document_multiple_cabinet_add',
        view=DocumentCabinetAddView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/cabinets/remove/$',
        name='document_cabinet_remove',
        view=DocumentCabinetRemoveView.as_view()
    ),
    url(
        regex=r'^documents/multiple/cabinets/remove/$',
        name='multiple_document_cabinet_remove',
        view=DocumentCabinetRemoveView.as_view()
    )
]

urlpatterns = []
urlpatterns.extend(urlpatterns_cabinets)
urlpatterns.extend(urlpatterns_documents_cabinets)

api_urls = [
    url(
        regex=r'^cabinets/tree/$', name='cabinet-tree',
        view=APICabinetTreeView.as_view()
    ),
    url(
        regex=r'^cabinets/(?P<cabinet_id>[0-9]+)/$', name='cabinet-detail',
        view=APICabinetView.as_view()
    ),
    url(
        regex=r'^cabinets/$', name='cabinet-list',
        view=APICabinetListView.as_view()
    ),
    url(
        regex=r'^cabinets/(?P<cabinet_id>[0-9]+)/documents/$',
        name='cabinet-document-list',
        view=APICabinetDocumentListView.as_view()
    ),
    url(
        regex=r'^cabinets/(?P<cabinet_id>[0-9]+)/documents/add/$',
        name='cabinet-document-add', view=APICabinetDocumentAddView.as_view()
    ),
    url(
        regex=r'^cabinets/(?P<cabinet_id>[0-9]+)/documents/remove/$',
        name='cabinet-document-remove', view=APICabinetDocumentRemoveView.as_view()
    ),
    url(
        regex=r'^cabinets/(?P<cabinet_id>[0-9]+)/documents/bulk-add/$',
        name='cabinet-document-bulk-add',
        view=APICabinetDocumentBulkAddView.as_view()
    ),
    url(
        regex=r'^cabinets/(?P<cabinet_id>[0-9]+)/documents/bulk-remove/$',
        name='cabinet-document-bulk-remove',
        view=APICabinetDocumentBulkRemoveView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>[0-9]+)/cabinets/$',
        name='document-cabinet-list',
        view=APIDocumentCabinetListView.as_view()
    ),
    url(
        regex=r'^cabinets/(?P<cabinet_id>[0-9]+)/shares/$',
        name='cabinet-share-list',
        view=APICabinetShareListView.as_view()
    ),
    url(
        regex=r'^cabinets/(?P<cabinet_id>[0-9]+)/shares/(?P<uuid>[0-9a-f-]+)/$',
        name='cabinet-share-detail',
        view=APICabinetShareView.as_view()
    ),
    url(
        regex=r'^public/shares/(?P<uuid>[0-9a-f-]+)/$',
        name='public-cabinet-share-detail',
        view=PublicCabinetShareDetailView.as_view()
    )
]
