import logging

from django.apps import apps
from django.db.models.signals import post_delete, post_save, pre_delete
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.classes import ModelPermission
from mayan.apps.acls.permissions import (
    permission_acl_edit, permission_acl_view
)
from mayan.apps.common.apps import MayanAppConfig
from mayan.apps.common.classes import ModelCopy
from mayan.apps.common.menus import (
    menu_list_facet, menu_multi_item, menu_object, menu_related,
    menu_secondary, menu_setup
)
from mayan.apps.databases.classes import (
    ModelFieldRelated, ModelProperty, ModelQueryFields
)
from mayan.apps.documents.links.document_type_links import link_document_type_list
from mayan.apps.documents.signals import signal_post_document_type_change
from mayan.apps.events.classes import EventModelRegistry, ModelEventType
from mayan.apps.navigation.classes import SourceColumn
from mayan.apps.rest_api.fields import DynamicSerializerField
from mayan.apps.views.html_widgets import TwoStateWidget

from .classes import (
    DocumentMetadataHelper, MetadataParser, MetadataValidator
)
from .events import (
    event_document_metadata_added, event_document_metadata_edited,
    event_document_metadata_removed, event_metadata_type_edited,
    event_metadata_type_relationship_updated
)
from .handlers import (
    handler_index_metadata_type_documents,
    handler_post_document_type_metadata_type_add,
    handler_post_document_type_metadata_type_delete,
    handler_post_document_type_change_metadata,
    handler_pre_metadata_type_delete
)
from .html_widgets import DocumentMetadataWidget
from .links import (
    link_metadata_add, link_metadata_edit, link_metadata_multiple_add,
    link_metadata_multiple_edit, link_metadata_multiple_remove,
    link_metadata_remove, link_metadata_list,
    link_document_type_metadata_type_relationship, link_metadata_type_create,
    link_metadata_type_multiple_delete, link_metadata_type_single_delete,
    link_metadata_type_document_type_relationship, link_metadata_type_edit,
    link_metadata_type_list
)
from .methods import method_document_get_metadata
from .permissions import (
    permission_document_metadata_add, permission_document_metadata_edit,
    permission_document_metadata_remove, permission_document_metadata_view,
    permission_metadata_type_delete, permission_metadata_type_edit,
    permission_metadata_type_view
)

logger = logging.getLogger(name=__name__)


class MetadataApp(MayanAppConfig):
    app_namespace = 'metadata'
    app_url = 'metadata'
    has_rest_api = True
    has_static_media = True
    has_tests = True
    name = 'mayan.apps.metadata'
    verbose_name = _('Metadata')

    def ready(self):
        super().ready()

        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )
        DocumentFileSearchResult = apps.get_model(
            app_label='documents', model_name='DocumentFileSearchResult'
        )
        DocumentFilePageSearchResult = apps.get_model(
            app_label='documents', model_name='DocumentFilePageSearchResult'
        )
        DocumentVersionSearchResult = apps.get_model(
            app_label='documents', model_name='DocumentVersionSearchResult'
        )
        DocumentVersionPageSearchResult = apps.get_model(
            app_label='documents',
            model_name='DocumentVersionPageSearchResult'
        )

        DocumentType = apps.get_model(
            app_label='documents', model_name='DocumentType'
        )

        DocumentMetadata = self.get_model(model_name='DocumentMetadata')
        DocumentTypeMetadataType = self.get_model(
            model_name='DocumentTypeMetadataType'
        )
        MetadataType = self.get_model(model_name='MetadataType')

        Document.add_to_class(
            name='metadata_value_of', value=DocumentMetadataHelper.constructor
        )
        Document.add_to_class(
            name='get_metadata', value=method_document_get_metadata
        )

        DynamicSerializerField.add_serializer(
            klass=MetadataType,
            serializer_class='mayan.apps.metadata.serializers.MetadataTypeSerializer'
        )

        EventModelRegistry.register(model=MetadataType)
        EventModelRegistry.register(model=DocumentTypeMetadataType)

        MetadataParser.load_modules()
        MetadataValidator.load_modules()

        ModelCopy(
            model=DocumentTypeMetadataType,
        ).add_fields(
            field_names=(
                'document_type', 'metadata_type', 'required'
            )
        )

        ModelCopy(
            model=MetadataType, bind_link=True, register_permission=True
        ).add_fields(
            field_names=(
                'name', 'label', 'default', 'lookup', 'validation', 'parser',
                'document_types'
            ),
        )

        ModelProperty(
            model=Document, name='metadata_value_of.< metadata type name >',
            description=_(
                'Return the value of a specific document metadata.'
            ), label=_('Metadata value of')
        )

        ModelFieldRelated(
            model=Document, name='metadata__metadata_type__name',
            label=_('Metadata type name')
        )
        ModelFieldRelated(
            model=Document, name='metadata__value',
            label=_('Metadata value')
        )

        ModelEventType.register(
            model=Document, event_types=(
                event_document_metadata_added,
                event_document_metadata_edited,
                event_document_metadata_removed,
            )
        )

        ModelEventType.register(
            model=MetadataType, event_types=(
                event_document_metadata_added,
                event_document_metadata_edited,
                event_document_metadata_removed,
                event_metadata_type_edited,
                event_metadata_type_relationship_updated
            )
        )

        ModelEventType.register(
            model=DocumentType, event_types=(
                event_metadata_type_relationship_updated,
            )
        )

        ModelPermission.register(
            model=Document, permissions=(
                permission_document_metadata_add,
                permission_document_metadata_edit,
                permission_document_metadata_remove,
                permission_document_metadata_view
            )
        )
        ModelPermission.register(
            model=MetadataType, permissions=(
                permission_acl_edit, permission_acl_view,
                permission_document_metadata_add,
                permission_document_metadata_edit,
                permission_document_metadata_remove,
                permission_document_metadata_view,
                permission_metadata_type_delete,
                permission_metadata_type_edit, permission_metadata_type_view
            )
        )
        ModelPermission.register_inheritance(
            model=DocumentMetadata, related='metadata_type',
        )

        model_query_fields_document = ModelQueryFields(model=Document)
        model_query_fields_document.add_prefetch_related_field(
            field_name='metadata'
        )

        # Columns

        SourceColumn(
            source=Document, label=_('Metadata'),
            widget=DocumentMetadataWidget
        )

        SourceColumn(
            attribute='document', source=DocumentFileSearchResult,
            label=_('Metadata'), widget=DocumentMetadataWidget
        )
        SourceColumn(
            attribute='document_file__document',
            source=DocumentFilePageSearchResult, label=_('Metadata'),
            widget=DocumentMetadataWidget
        )
        SourceColumn(
            attribute='document', source=DocumentVersionSearchResult,
            label=_('Metadata'), widget=DocumentMetadataWidget
        )
        SourceColumn(
            attribute='document_version__document',
            source=DocumentVersionPageSearchResult, label=_('Metadata'),
            widget=DocumentMetadataWidget
        )

        SourceColumn(
            attribute='metadata_type', is_identifier=True,
            is_sortable=True, source=DocumentMetadata
        )
        SourceColumn(
            attribute='value', include_label=True, is_sortable=True,
            source=DocumentMetadata
        )

        SourceColumn(
            attribute='is_required', include_label=True,
            source=DocumentMetadata, widget=TwoStateWidget
        )

        SourceColumn(
            attribute='label', is_identifier=True, is_sortable=True,
            source=MetadataType
        )
        SourceColumn(
            attribute='name', include_label=True, is_sortable=True,
            source=MetadataType
        )

        # Document metadata

        menu_list_facet.bind_links(
            links=(link_metadata_list,), sources=(Document,)
        )
        menu_multi_item.bind_links(
            links=(
                link_metadata_multiple_add, link_metadata_multiple_edit,
                link_metadata_multiple_remove
            ), sources=(Document,)
        )

        menu_secondary.bind_links(
            links=(
                link_metadata_add, link_metadata_edit, link_metadata_remove
            ), sources=(
                'metadata:metadata_add', 'metadata:metadata_edit',
                'metadata:metadata_list', 'metadata:metadata_remove'
            )
        )

        # Document type

        menu_list_facet.bind_links(
            links=(link_document_type_metadata_type_relationship,), sources=(
                DocumentType,
            )
        )

        menu_related.bind_links(
            links=(link_metadata_type_list,),
            sources=(
                DocumentType, 'documents:document_type_list',
                'documents:document_type_create'
            )
        )

        # Metadata type

        menu_list_facet.bind_links(
            links=(
                link_metadata_type_document_type_relationship,
            ), sources=(MetadataType,)
        )

        menu_multi_item.bind_links(
            links=(
                link_metadata_type_multiple_delete,
            ), sources=(MetadataType,)
        )

        menu_object.bind_links(
            links=(
                link_metadata_type_single_delete, link_metadata_type_edit
            ), sources=(MetadataType,)
        )

        menu_related.bind_links(
            links=(
                link_document_type_list,
            ), sources=(
                MetadataType, 'metadata:metadata_type_list',
                'metadata:metadata_type_create'
            )
        )

        menu_secondary.bind_links(
            links=(
                link_metadata_type_list,
                link_metadata_type_create
            ), sources=(
                MetadataType, 'metadata:metadata_type_list',
                'metadata:metadata_type_create'
            )
        )

        menu_setup.bind_links(links=(link_metadata_type_list,))

        # Signals

        post_delete.connect(
            dispatch_uid='metadata_handler_post_document_type_metadata_type_delete',
            receiver=handler_post_document_type_metadata_type_delete,
            sender=DocumentTypeMetadataType
        )
        post_save.connect(
            dispatch_uid='metadata_handler_post_document_type_metadata_type_add',
            receiver=handler_post_document_type_metadata_type_add,
            sender=DocumentTypeMetadataType
        )
        signal_post_document_type_change.connect(
            dispatch_uid='metadata_handler_post_document_type_change_metadata',
            receiver=handler_post_document_type_change_metadata,
            sender=Document
        )

        # Index updates

        post_save.connect(
            dispatch_uid='metadata_handler_index_metadata_type_documents',
            receiver=handler_index_metadata_type_documents,
            sender=MetadataType
        )
        pre_delete.connect(
            dispatch_uid='metadata_handler_pre_metadata_type_delete',
            receiver=handler_pre_metadata_type_delete,
            sender=MetadataType
        )
