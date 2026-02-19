from rest_framework.permissions import AllowAny

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.serializers.document_serializers import DocumentSerializer
from mayan.apps.rest_api import generics
from mayan.apps.rest_api.api_view_mixins import ExternalObjectAPIViewMixin

from .models import Cabinet, CabinetShare
from .permissions import (
    permission_cabinet_add_document, permission_cabinet_create,
    permission_cabinet_delete, permission_cabinet_edit,
    permission_cabinet_remove_document, permission_cabinet_view
)
from .serializers import (
    CabinetDocumentAddSerializer, CabinetDocumentBulkRemoveSerializer,
    CabinetDocumentBulkSerializer, CabinetDocumentRemoveSerializer,
    CabinetSerializer, CabinetShareCreateSerializer, CabinetShareSerializer
)


def _filter_cabinets_by_organization(queryset, request):
    """Restrict cabinet queryset to current organization (tenant isolation)."""
    organization = getattr(request, 'organization', None)
    if organization is None:
        return queryset
    return queryset.filter(organization=organization)


class APIDocumentCabinetListView(
    ExternalObjectAPIViewMixin, generics.ListAPIView
):
    """
    Returns a list of all the cabinets to which a document belongs.
    Tenant-scoped: only cabinets of the document's organization are returned.
    """
    external_object_queryset = Document.valid.all()
    external_object_pk_url_kwarg = 'document_id'
    mayan_external_object_permissions = {'GET': (permission_cabinet_view,)}
    mayan_object_permissions = {'GET': (permission_cabinet_view,)}
    serializer_class = CabinetSerializer

    def get_queryset(self):
        qs = self.external_object.cabinets.all()
        return _filter_cabinets_by_organization(qs, self.request)


class APICabinetListView(generics.ListCreateAPIView):
    """
    get: Returns a list of all the cabinets (filtered by current organization).
    post: Create a new cabinet (organization set from request).
    """
    mayan_object_permissions = {'GET': (permission_cabinet_view,)}
    mayan_view_permissions = {'POST': (permission_cabinet_create,)}
    ordering_fields = ('id', 'label')
    queryset = Cabinet.objects.all()
    serializer_class = CabinetSerializer

    def get_queryset(self):
        return _filter_cabinets_by_organization(
            super().get_queryset(), self.request
        )

    def perform_create(self, serializer):
        organization = getattr(self.request, 'organization', None)
        if organization is not None:
            serializer.save(organization=organization)
        else:
            serializer.save()

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user
        }


class APICabinetTreeView(generics.ListAPIView):
    """
    get: Returns a hierarchical list of cabinets (root nodes with children).
    Tenant-scoped: only cabinets of the current organization.
    """
    mayan_object_permissions = {'GET': (permission_cabinet_view,)}
    pagination_class = None
    serializer_class = CabinetSerializer

    def get_queryset(self):
        qs = Cabinet.objects.filter(parent=None).prefetch_related(
            'children', 'documents'
        )
        return _filter_cabinets_by_organization(qs, self.request)


class APICabinetView(generics.RetrieveUpdateDestroyAPIView):
    """
    delete: Delete the selected cabinet.
    get: Returns the details of the selected cabinet.
    patch: Edit the selected cabinet.
    put: Edit the selected cabinet.
    Tenant-scoped: only cabinets of the current organization.
    """
    lookup_url_kwarg = 'cabinet_id'
    mayan_object_permissions = {
        'GET': (permission_cabinet_view,),
        'PUT': (permission_cabinet_edit,),
        'PATCH': (permission_cabinet_edit,),
        'DELETE': (permission_cabinet_delete,)
    }
    queryset = Cabinet.objects.all()
    serializer_class = CabinetSerializer

    def get_queryset(self):
        return _filter_cabinets_by_organization(
            super().get_queryset(), self.request
        )

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user
        }


class APICabinetDocumentAddView(generics.ObjectActionAPIView):
    """
    post: Add a document to a cabinet.
    Tenant-scoped: cabinet must belong to current organization.
    """
    lookup_url_kwarg = 'cabinet_id'
    mayan_object_permissions = {
        'POST': (permission_cabinet_add_document,)
    }
    serializer_class = CabinetDocumentAddSerializer
    queryset = Cabinet.objects.all()

    def get_queryset(self):
        return _filter_cabinets_by_organization(
            super().get_queryset(), self.request
        )

    def object_action(self, request, serializer):
        document = serializer.validated_data['document']
        self.object._event_actor = self.request.user
        self.object.document_add(document=document)


class APICabinetDocumentBulkAddView(generics.ObjectActionAPIView):
    """
    post: Add multiple documents to a cabinet.
    Tenant-scoped: cabinet must belong to current organization.
    """
    lookup_url_kwarg = 'cabinet_id'
    mayan_object_permissions = {
        'POST': (permission_cabinet_add_document,)
    }
    serializer_class = CabinetDocumentBulkSerializer
    queryset = Cabinet.objects.all()

    def get_queryset(self):
        return _filter_cabinets_by_organization(
            super().get_queryset(), self.request
        )

    def object_action(self, request, serializer):
        documents = serializer.validated_data['documents']
        self.object._event_actor = self.request.user
        for document in documents:
            self.object.document_add(document=document)


class APICabinetDocumentRemoveView(generics.ObjectActionAPIView):
    """
    post: Remove a document from a cabinet.
    Tenant-scoped: cabinet must belong to current organization.
    """
    lookup_url_kwarg = 'cabinet_id'
    mayan_object_permissions = {
        'POST': (permission_cabinet_remove_document,)
    }
    serializer_class = CabinetDocumentRemoveSerializer
    queryset = Cabinet.objects.all()

    def get_queryset(self):
        return _filter_cabinets_by_organization(
            super().get_queryset(), self.request
        )

    def object_action(self, request, serializer):
        document = serializer.validated_data['document']
        self.object._event_actor = self.request.user
        self.object.document_remove(document=document)


class APICabinetDocumentBulkRemoveView(generics.ObjectActionAPIView):
    """
    post: Remove multiple documents from a cabinet.
    Tenant-scoped: cabinet must belong to current organization.
    """
    lookup_url_kwarg = 'cabinet_id'
    mayan_object_permissions = {
        'POST': (permission_cabinet_remove_document,)
    }
    serializer_class = CabinetDocumentBulkRemoveSerializer
    queryset = Cabinet.objects.all()

    def get_queryset(self):
        return _filter_cabinets_by_organization(
            super().get_queryset(), self.request
        )

    def object_action(self, request, serializer):
        documents = serializer.validated_data['documents']
        self.object._event_actor = self.request.user
        for document in documents:
            self.object.document_remove(document=document)


class APICabinetDocumentListView(
    ExternalObjectAPIViewMixin, generics.ListAPIView
):
    """
    get: Returns a list of all the documents contained in a particular cabinet.
    Tenant-scoped: cabinet is resolved from current organization.
    """
    external_object_class = Cabinet
    external_object_pk_url_kwarg = 'cabinet_id'
    mayan_external_object_permissions = {'GET': (permission_cabinet_view,)}
    mayan_object_permissions = {
        'GET': (permission_document_view,),
    }
    serializer_class = DocumentSerializer

    def get_external_object_queryset(self):
        qs = super().get_external_object_queryset()
        return _filter_cabinets_by_organization(qs, self.request)

    def get_queryset(self):
        return Document.valid.filter(
            pk__in=self.external_object.documents.only('pk')
        )


class APICabinetShareListView(
    ExternalObjectAPIViewMixin, generics.ListCreateAPIView
):
    """
    get: List share links for a cabinet.
    post: Create a new share link for the cabinet.
    """
    external_object_class = Cabinet
    external_object_pk_url_kwarg = 'cabinet_id'
    mayan_external_object_permissions = {
        'GET': (permission_cabinet_view,),
        'POST': (permission_cabinet_view,),
    }
    serializer_class = CabinetShareSerializer

    def get_external_object_queryset(self):
        qs = super().get_external_object_queryset()
        return _filter_cabinets_by_organization(qs, self.request)

    def get_queryset(self):
        return CabinetShare.objects.filter(
            cabinet=self.external_object
        ).select_related('cabinet', 'organization', 'created_by')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CabinetShareCreateSerializer
        return CabinetShareSerializer

    def create(self, request, *args, **kwargs):
        self.external_object = self.get_external_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        organization = getattr(request, 'organization', None)
        if not organization:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'organization': 'Request organization is required.'})
        share = CabinetShare(
            cabinet=self.external_object,
            organization=organization,
            created_by=request.user,
            expires_at=serializer.validated_data.get('expires_at'),
        )
        password = serializer.validated_data.get('password') or ''
        if password:
            share.set_password(password)
        share.save()
        output_serializer = CabinetShareSerializer(
            share, context=self.get_serializer_context()
        )
        return generics.Response(
            output_serializer.data,
            status=generics.status.HTTP_201_CREATED
        )


class APICabinetShareView(generics.DestroyAPIView):
    """
    delete: Revoke a cabinet share link.
    """
    lookup_url_kwarg = 'uuid'
    lookup_field = 'uuid'
    queryset = CabinetShare.objects.all()
    serializer_class = CabinetShareSerializer

    def get_queryset(self):
        org = getattr(self.request, 'organization', None)
        qs = CabinetShare.objects.filter(
            cabinet_id=self.kwargs.get('cabinet_id')
        ).select_related('cabinet')
        if org is not None:
            qs = qs.filter(organization=org)
        return qs

    def perform_destroy(self, instance):
        AccessControlList.objects.check_access(
            obj=instance.cabinet,
            permissions=(permission_cabinet_view,),
            user=self.request.user
        )
        instance.delete()


class PublicCabinetShareDetailView(generics.RetrieveAPIView):
    """
    get: Public (unauthenticated) read-only access to a shared cabinet.
    Returns cabinet label and list of documents (id, label, thumbnail_url).
    Query param: password= for password-protected shares.
    Responses: 200 OK, 403 expired/requires_password, 404 not found.
    """
    permission_classes = (AllowAny,)
    lookup_url_kwarg = 'uuid'
    lookup_field = 'uuid'
    queryset = CabinetShare.objects.all().select_related('cabinet')

    def retrieve(self, request, *args, **kwargs):
        share = self.get_object()
        if share.is_expired():
            from rest_framework.exceptions import PermissionDenied
            from rest_framework.response import Response
            return Response(
                {'detail': 'Share link has expired.', 'expired': True},
                status=403
            )
        if share.password_hash and not share.check_password(
            request.query_params.get('password', '')
        ):
            from rest_framework.response import Response
            return Response(
                {
                    'detail': 'This share requires a password.',
                    'requires_password': True,
                },
                status=403
            )
        cabinet = share.cabinet
        documents_qs = Document.valid.filter(
            pk__in=cabinet.documents.only('pk')
        ).only('id', 'label')
        documents = [
            {
                'id': doc.id,
                'label': doc.label,
                'thumbnail_url': None,
            }
            for doc in documents_qs
        ]
        from rest_framework.response import Response
        return Response({
            'label': cabinet.label,
            'uuid': str(share.uuid),
            'documents': documents,
        })
