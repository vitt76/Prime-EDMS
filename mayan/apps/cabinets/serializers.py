from django.utils.translation import ugettext_lazy as _

from rest_framework.reverse import reverse
from rest_framework_recursive.fields import RecursiveField

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models import Document
from mayan.apps.rest_api import serializers
from mayan.apps.rest_api.relations import FilteredPrimaryKeyRelatedField

from .models import Cabinet
from .permissions import (
    permission_cabinet_add_document, permission_cabinet_create,
    permission_cabinet_delete, permission_cabinet_edit,
    permission_cabinet_remove_document
)


class CabinetSerializer(serializers.ModelSerializer):
    children = RecursiveField(
        help_text=_('List of children cabinets.'), many=True, read_only=True
    )
    document_count = serializers.SerializerMethodField(
        help_text=_('Number of documents in this cabinet for the current user.'),
        read_only=True
    )
    documents_url = serializers.HyperlinkedIdentityField(
        help_text=_(
            'URL of the API endpoint showing the list documents inside this '
            'cabinet.'
        ), lookup_url_kwarg='cabinet_id',
        view_name='rest_api:cabinet-document-list'
    )
    can_add_children = serializers.SerializerMethodField(
        help_text=_('Whether the user can add child cabinets.'),
        read_only=True
    )
    can_delete = serializers.SerializerMethodField(
        help_text=_('Whether the user can delete this cabinet.'),
        read_only=True
    )
    can_edit = serializers.SerializerMethodField(
        help_text=_('Whether the user can edit this cabinet.'),
        read_only=True
    )
    created_at = serializers.SerializerMethodField(read_only=True)
    updated_at = serializers.SerializerMethodField(read_only=True)
    full_path = serializers.SerializerMethodField(
        help_text=_(
            'The name of this cabinet level appended to the names of its '
            'ancestors.'
        ), read_only=True
    )
    parent_url = serializers.SerializerMethodField(read_only=True)

    # This is here because parent is optional in the model but the serializer
    # sets it as required.
    parent = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=Cabinet.objects.all(), required=False
    )

    # DEPRECATION: Version 5.0, remove 'parent' fields from GET request as
    # it is replaced by 'parent_id'.

    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_url_kwarg': 'cabinet_id',
                'view_name': 'rest_api:cabinet-detail'
            },
        }
        fields = (
            'children', 'documents_url', 'document_count', 'full_path', 'id',
            'label', 'parent_id', 'parent', 'parent_url', 'url',
            'can_add_children', 'can_delete', 'can_edit', 'created_at',
            'updated_at'
        )
        model = Cabinet
        read_only_fields = (
            'can_add_children', 'can_delete', 'can_edit', 'children',
            'created_at', 'document_count', 'documents_url', 'full_path', 'id',
            'parent_id', 'parent_url', 'updated_at', 'url'
        )

    def get_full_path(self, obj):
        return obj.get_full_path()

    def get_parent_url(self, obj):
        if obj.parent:
            return reverse(
                viewname='rest_api:cabinet-detail',
                kwargs={'cabinet_id': obj.parent.pk},
                format=self.context['format'],
                request=self.context.get('request')
            )
        else:
            return ''

    def get_document_count(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if not user:
            return 0

        return obj.get_document_count(user=user)

    def _check_permission(self, obj, permission):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if not user:
            return False

        try:
            AccessControlList.objects.check_access(
                obj=obj, permissions=(permission,), user=user
            )
            return True
        except Exception:
            return False

    def get_can_add_children(self, obj):
        return self._check_permission(
            obj=obj, permission=permission_cabinet_create
        )

    def get_can_delete(self, obj):
        return self._check_permission(
            obj=obj, permission=permission_cabinet_delete
        )

    def get_can_edit(self, obj):
        return self._check_permission(
            obj=obj, permission=permission_cabinet_edit
        )

    def get_created_at(self, obj):
        value = getattr(obj, 'datetime_created', None)
        if value:
            return value.isoformat()
        return None

    def get_updated_at(self, obj):
        value = getattr(obj, 'datetime_modified', None)
        if value:
            return value.isoformat()
        return None


class CabinetDocumentAddSerializer(serializers.Serializer):
    document = FilteredPrimaryKeyRelatedField(
        source_queryset=Document.valid.all(),
        source_permission=permission_cabinet_add_document
    )


class CabinetDocumentRemoveSerializer(serializers.Serializer):
    document = FilteredPrimaryKeyRelatedField(
        source_queryset=Document.valid.all(),
        source_permission=permission_cabinet_remove_document
    )


class CabinetDocumentBulkSerializer(serializers.Serializer):
    documents = FilteredPrimaryKeyRelatedField(
        many=True, source_queryset=Document.valid.all(),
        source_permission=permission_cabinet_add_document
    )

    def validate_documents(self, value):
        if not value:
            raise serializers.ValidationError(_('Document list cannot be empty.'))
        return value


class CabinetDocumentBulkRemoveSerializer(serializers.Serializer):
    documents = FilteredPrimaryKeyRelatedField(
        many=True, source_queryset=Document.valid.all(),
        source_permission=permission_cabinet_remove_document
    )

    def validate_documents(self, value):
        if not value:
            raise serializers.ValidationError(_('Document list cannot be empty.'))
        return value
