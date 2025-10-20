from django.apps import apps
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.classes import ModelPermission
from mayan.apps.common.apps import MayanAppConfig
from mayan.apps.common.menus import (
    menu_list_facet, menu_multi_item, menu_object, menu_secondary, menu_tools
)
from mayan.apps.databases.classes import ModelFieldRelated, ModelProperty
from mayan.apps.documents.signals import signal_post_document_file_upload
from mayan.apps.events.classes import ModelEventType
from mayan.apps.navigation.classes import SourceColumn

from .classes import FileMetadataHelper
from .drivers import *  # NOQA
from .events import (
    event_file_metadata_document_file_finished,
    event_file_metadata_document_file_submitted
)
from .handlers import (
    handler_initialize_new_document_type_file_metadata_settings,
    process_document_file_metadata
)
from .links import (
    link_document_file_metadata_driver_list,
    link_document_file_metadata_driver_attribute_list,
    link_document_file_metadata_single_submit,
    link_document_file_metadata_submit_multiple,
    link_document_type_file_metadata_settings,
    link_document_type_file_metadata_submit
)
from .methods import (
    method_document_file_metadata_submit,
    method_document_file_metadata_submit_single,
    method_get_document_file_metadata, method_get_document_file_file_metadata
)
from .permissions import (
    permission_document_type_file_metadata_setup,
    permission_file_metadata_submit, permission_file_metadata_view
)


class FileMetadataApp(MayanAppConfig):
    app_namespace = 'file_metadata'
    app_url = 'file_metadata'
    has_tests = True
    name = 'mayan.apps.file_metadata'
    verbose_name = _('File metadata')

    def ready(self):
        super().ready()

        FileMetadataEntry = self.get_model(model_name='FileMetadataEntry')
        DocumentFileDriverEntry = self.get_model(
            model_name='DocumentFileDriverEntry'
        )
        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )
        DocumentFile = apps.get_model(
            app_label='documents', model_name='DocumentFile'
        )
        DocumentTypeSettings = self.get_model(
            model_name='DocumentTypeSettings'
        )
        DocumentType = apps.get_model(
            app_label='documents', model_name='DocumentType'
        )

        Document.add_to_class(
            name='file_metadata_value_of',
            value=FileMetadataHelper.constructor
        )
        Document.add_to_class(
            name='get_file_metadata',
            value=method_get_document_file_metadata
        )
        Document.add_to_class(
            name='submit_for_file_metadata_processing',
            value=method_document_file_metadata_submit
        )
        DocumentFile.add_to_class(
            name='get_file_metadata',
            value=method_get_document_file_file_metadata
        )
        DocumentFile.add_to_class(
            name='submit_for_file_metadata_processing',
            value=method_document_file_metadata_submit_single
        )

        ModelEventType.register(
            model=Document, event_types=(
                event_file_metadata_document_file_finished,
                event_file_metadata_document_file_submitted
            )
        )

        ModelFieldRelated(
            label=_('File metadata key'), model=Document,
            name='files__file_metadata_drivers__entries__key'
        )
        ModelFieldRelated(
            label=_('File metadata value'), model=Document,
            name='files__file_metadata_drivers__entries__value'
        )

        ModelPermission.register(
            model=Document, permissions=(
                permission_file_metadata_submit,
                permission_file_metadata_view
            )
        )
        ModelPermission.register(
            model=DocumentType, permissions=(
                permission_document_type_file_metadata_setup,
                permission_file_metadata_submit,
                permission_file_metadata_view
            )
        )
        ModelPermission.register_inheritance(
            model=DocumentTypeSettings, related='document_type'
        )
        ModelPermission.register_inheritance(
            model=DocumentFileDriverEntry, related='document_file'
        )

        ModelProperty(
            model=Document,
            name='file_metadata_value_of.< underscore separated driver name and property name >',
            description=_(
                'Return the value of a specific file metadata.'
            ), label=_('File metadata value of')
        )

        SourceColumn(
            attribute='key', is_identifier=True, source=FileMetadataEntry
        )
        SourceColumn(
            attribute='value', include_label=True, source=FileMetadataEntry
        )
        SourceColumn(
            attribute='driver', is_identifier=True,
            source=DocumentFileDriverEntry
        )
        SourceColumn(
            attribute='driver__internal_name', include_label=True,
            source=DocumentFileDriverEntry
        )
        SourceColumn(
            attribute='get_attribute_count', include_label=True,
            source=DocumentFileDriverEntry
        )

        menu_tools.bind_links(
            links=(link_document_type_file_metadata_submit,)
        )

        # Document file

        menu_list_facet.bind_links(
            links=(link_document_file_metadata_driver_list,),
            sources=(DocumentFile,)
        )

        menu_multi_item.bind_links(
            links=(link_document_file_metadata_submit_multiple,),
            sources=(DocumentFile,)
        )

        menu_secondary.bind_links(
            links=(link_document_file_metadata_single_submit,), sources=(
                'file_metadata:document_file_metadata_driver_list',
                'file_metadata:document_file_metadata_driver_attribute_list'
            )
        )

        # Document file driver

        menu_object.bind_links(
            links=(link_document_file_metadata_driver_attribute_list,),
            sources=(DocumentFileDriverEntry,)
        )

        # Document type

        menu_list_facet.bind_links(
            links=(link_document_type_file_metadata_settings,),
            sources=(DocumentType,)
        )

        post_save.connect(
            dispatch_uid='file_metadata_handler_initialize_new_document_type_file_metadata_settings',
            receiver=handler_initialize_new_document_type_file_metadata_settings,
            sender=DocumentType
        )
        signal_post_document_file_upload.connect(
            dispatch_uid='file_metadata_process_document_file_metadata',
            receiver=process_document_file_metadata,
            sender=DocumentFile
        )
