from django.utils.translation import ugettext_lazy as _

from rest_framework.reverse import reverse

from mayan.apps.documents.models import DocumentType
from mayan.apps.documents.permissions import permission_document_type_edit
from mayan.apps.documents.serializers.document_serializers import (
    DocumentSerializer
)
from mayan.apps.rest_api import serializers
from mayan.apps.rest_api.relations import (
    FilteredPrimaryKeyRelatedField, MultiKwargHyperlinkedIdentityField
)

from .models import ResolvedSmartLink, SmartLink, SmartLinkCondition


class SmartLinkConditionSerializer(serializers.HyperlinkedModelSerializer):
    smart_link_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='smart_link_id',
        view_name='rest_api:smartlink-detail'
    )
    url = MultiKwargHyperlinkedIdentityField(
        view_kwargs=(
            {
                'lookup_field': 'smart_link_id',
                'lookup_url_kwarg': 'smart_link_id',
            },
            {
                'lookup_field': 'pk',
                'lookup_url_kwarg': 'smart_link_condition_id',
            }
        ),
        view_name='rest_api:smartlinkcondition-detail'
    )

    class Meta:
        fields = (
            'enabled', 'expression', 'foreign_document_data', 'inclusion',
            'id', 'negated', 'operator', 'smart_link_id', 'smart_link_url',
            'url'
        )
        model = SmartLinkCondition
        read_only_fields = ('id', 'smart_link_id', 'smart_link_url', 'url')


class SmartLinkDocumentTypeAddSerializer(serializers.Serializer):
    document_type = FilteredPrimaryKeyRelatedField(
        help_text=_(
            'Primary key of the document type to add to the smart link.'
        ), source_model=DocumentType,
        source_permission=permission_document_type_edit
    )


class SmartLinkDocumentTypeRemoveSerializer(serializers.Serializer):
    document_type = FilteredPrimaryKeyRelatedField(
        help_text=_(
            'Primary key of the document type to remove from the smart link.'
        ), source_model=DocumentType,
        source_permission=permission_document_type_edit
    )


class SmartLinkSerializer(serializers.HyperlinkedModelSerializer):
    conditions_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='smart_link_id',
        view_name='rest_api:smartlinkcondition-list'
    )
    document_types_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='smart_link_id',
        view_name='rest_api:smartlink-document_type-list'
    )
    document_types_add_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='smart_link_id',
        view_name='rest_api:smartlink-document_type-add'
    )
    document_types_remove_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='smart_link_id',
        view_name='rest_api:smartlink-document_type-remove'
    )

    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_url_kwarg': 'smart_link_id',
                'view_name': 'rest_api:smartlink-detail'
            }
        }
        fields = (
            'conditions_url', 'document_types_url', 'document_types_add_url',
            'document_types_remove_url', 'dynamic_label', 'enabled',
            'label', 'id', 'url'
        )
        model = SmartLink
        read_only_fields = (
            'conditions_url', 'document_types_url', 'document_types_add_url',
            'document_types_remove_url', 'id', 'url'
        )


class ResolvedSmartLinkDocumentSerializer(DocumentSerializer):
    resolved_smart_link_url = serializers.SerializerMethodField()

    class Meta(DocumentSerializer.Meta):
        fields = DocumentSerializer.Meta.fields + (
            'resolved_smart_link_url',
        )
        read_only_fields = DocumentSerializer.Meta.fields

    def get_resolved_smart_link_url(self, instance):
        return reverse(
            viewname='rest_api:resolvedsmartlink-detail', kwargs={
                'document_id': self.context['document'].pk,
                'resolved_smart_link_id': self.context['resolved_smart_link'].pk
            }, request=self.context['request'],
            format=self.context['format']
        )


class ResolvedSmartLinkSerializer(serializers.HyperlinkedModelSerializer):
    documents_url = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    smart_link_url = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'documents_url', 'label', 'smart_link_url', 'url'
        )
        model = ResolvedSmartLink
        read_only_fields = fields

    def get_documents_url(self, instance):
        return reverse(
            viewname='rest_api:resolvedsmartlinkdocument-list',
            kwargs={
                'document_id': self.context['document'].pk,
                'resolved_smart_link_id': instance.pk
            },
            request=self.context['request'], format=self.context['format']
        )

    def get_label(self, instance):
        return instance.get_label_for(document=self.context['document'])

    def get_smart_link_url(self, instance):
        return reverse(
            viewname='rest_api:smartlink-detail',
            kwargs={
                'smart_link_id': instance.pk
            }, request=self.context['request'], format=self.context['format']
        )

    def get_url(self, instance):
        return reverse(
            viewname='rest_api:resolvedsmartlink-detail',
            kwargs={
                'document_id': self.context['document'].pk,
                'resolved_smart_link_id': instance.pk
            },
            request=self.context['request'], format=self.context['format']
        )
