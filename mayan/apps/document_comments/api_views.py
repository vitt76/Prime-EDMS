from rest_framework.exceptions import PermissionDenied

from mayan.apps.documents.models import Document
from mayan.apps.rest_api import generics
from mayan.apps.rest_api.api_view_mixins import ExternalObjectAPIViewMixin

from .permissions import (
    permission_document_comment_create, permission_document_comment_delete,
    permission_document_comment_edit, permission_document_comment_view
)
from .serializers import CommentSerializer


def _filter_documents_by_organization(queryset, request):
    """Restrict document queryset to current organization (tenant isolation)."""
    organization = getattr(request, 'organization', None)
    if organization is None:
        return queryset
    if not hasattr(queryset.model, 'organization'):
        return queryset
    return queryset.filter(organization=organization)


class APICommentListView(
    ExternalObjectAPIViewMixin, generics.ListCreateAPIView
):
    """
    get: Returns a list of all the document comments.
    post: Create a new document comment.
    Tenant-scoped: only documents in the current organization.
    """
    external_object_queryset = Document.valid.all()
    external_object_pk_url_kwarg = 'document_id'
    mayan_external_object_permissions = {
        'GET': (permission_document_comment_view,),
        'POST': (permission_document_comment_create,)
    }
    ordering_fields = ('id', 'submit_date')
    serializer_class = CommentSerializer

    def get_external_object_queryset(self):
        qs = super().get_external_object_queryset()
        return _filter_documents_by_organization(qs, self.request)

    def get_queryset(self):
        return self.external_object.comments.all()

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
            'user': self.request.user,
            'document': self.external_object
        }


class APICommentView(
    ExternalObjectAPIViewMixin, generics.RetrieveUpdateDestroyAPIView
):
    """
    get: Returns the details of the selected document comment.
    patch/put: Edit the comment (only the author).
    delete: Delete the comment (only the author).
    Tenant-scoped: only documents in the current organization.
    """
    external_object_queryset = Document.valid.all()
    external_object_pk_url_kwarg = 'document_id'
    mayan_external_object_permissions = {
        'DELETE': (permission_document_comment_delete,),
        'GET': (permission_document_comment_view,),
        'PATCH': (permission_document_comment_edit,),
        'PUT': (permission_document_comment_edit,),
    }
    lookup_url_kwarg = 'comment_id'
    serializer_class = CommentSerializer

    def get_external_object_queryset(self):
        qs = super().get_external_object_queryset()
        return _filter_documents_by_organization(qs, self.request)

    def get_queryset(self):
        return self.external_object.comments.all()

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
            'document': self.external_object
        }

    def check_comment_owner(self, comment):
        """Only the comment author may update or delete."""
        if comment.user_id != self.request.user.pk:
            raise PermissionDenied(
                'Only the author of the comment can edit or delete it.'
            )

    def perform_update(self, serializer):
        self.check_comment_owner(serializer.instance)
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        self.check_comment_owner(instance)
        super().perform_destroy(instance)
