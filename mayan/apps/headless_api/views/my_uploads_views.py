from django.contrib.contenttypes.models import ContentType

from django.db.models import IntegerField
from django.db.models.functions import Cast
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models import Document
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.serializers.optimized_document_serializers import (
    OptimizedDocumentListSerializer
)
from mayan.apps.events.models import Action
from mayan.apps.rest_api import generics
from mayan.apps.rest_api.pagination import MayanPageNumberPagination


class HeadlessMyUploadsView(generics.ListAPIView):
    """
    Return documents uploaded by the current user.

    Data source: Event stream (Action) with verb 'documents.document_create'
    and actor == current user. Results are ACL-filtered.
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = OptimizedDocumentListSerializer
    pagination_class = MayanPageNumberPagination
    ordering_fields = ('datetime_created', 'label', 'id', 'document_type__label')

    def get_queryset(self):
        document_ct = ContentType.objects.get_for_model(Document)

        verbs = [
            'documents.document_create',
            'documents.document_file_created'
        ]

        doc_ids = Action.objects.filter(
            verb__in=verbs,
            actor_object_id=str(self.request.user.pk),
            target_content_type=document_ct,
            target_object_id__regex=r'^\d+$'
        ).annotate(
            target_id_int=Cast('target_object_id', IntegerField())
        ).values_list('target_id_int', flat=True).distinct()

        queryset = Document.valid.filter(pk__in=doc_ids)

        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_document_view,
            queryset=queryset,
            user=self.request.user
        )

        ordering = self.request.query_params.get('ordering', '-datetime_created')
        if ordering and ordering.lstrip('-') in [field.lstrip('-') for field in self.ordering_fields]:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-datetime_created')

        return queryset
