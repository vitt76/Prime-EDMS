import logging

from django.apps import apps
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.classes import ModelPermission
from mayan.apps.common.apps import MayanAppConfig
from mayan.apps.common.menus import (
    menu_list_facet, menu_multi_item, menu_secondary, menu_tools
)
from mayan.apps.databases.classes import ModelFieldRelated, ModelProperty
from mayan.apps.documents.signals import signal_post_document_file_upload
from mayan.apps.events.classes import ModelEventType
from mayan.apps.logging.classes import ErrorLog

from .events import (
    event_parsing_document_file_content_deleted,
    event_parsing_document_file_submitted,
    event_parsing_document_file_finished
)
from .handlers import (
    handler_initialize_new_parsing_settings, handler_parse_document_file
)
from .links import (
    link_document_file_content_detail, link_document_file_content_download,
    link_document_file_content_multiple_delete,
    link_document_file_content_single_delete,
    link_document_file_page_content_detail,
    link_document_file_parsing_multiple_submit,
    link_document_file_parsing_single_submit,
    link_document_type_parsing_settings, link_document_type_parsing_submit
)
from .methods import (
    method_document_content, method_document_file_content,
    method_document_file_parsing_submit, method_document_parsing_submit
)
from .permissions import (
    permission_document_file_content_view,
    permission_document_type_parsing_setup, permission_document_file_parse
)

logger = logging.getLogger(name=__name__)


class DocumentParsingApp(MayanAppConfig):
    app_namespace = 'document_parsing'
    app_url = 'parsing'
    has_rest_api = True
    has_tests = True
    name = 'mayan.apps.document_parsing'
    verbose_name = _('Document parsing')

    def ready(self):
        super().ready()

        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )
        DocumentFile = apps.get_model(
            app_label='documents', model_name='DocumentFile'
        )
        DocumentFilePage = apps.get_model(
            app_label='documents', model_name='DocumentFilePage'
        )
        DocumentType = apps.get_model(
            app_label='documents', model_name='DocumentType'
        )
        DocumentTypeSettings = self.get_model(
            model_name='DocumentTypeSettings'
        )

        Document.add_to_class(
            name='content', value=method_document_content
        )
        Document.add_to_class(
            name='submit_for_parsing', value=method_document_parsing_submit
        )
        DocumentFile.add_to_class(
            name='content', value=method_document_file_content
        )
        DocumentFile.add_to_class(
            name='submit_for_parsing',
            value=method_document_file_parsing_submit
        )

        ModelEventType.register(
            model=Document, event_types=(
                event_parsing_document_file_content_deleted,
                event_parsing_document_file_submitted,
                event_parsing_document_file_finished
            )
        )
        ModelEventType.register(
            model=DocumentFile, event_types=(
                event_parsing_document_file_content_deleted,
                event_parsing_document_file_submitted,
                event_parsing_document_file_finished
            )
        )

        ModelFieldRelated(
            model=Document, name='files__file_pages__content__content'
        )

        ModelProperty(
            description=_(
                'A generator returning the document file\'s pages parsed content.'
            ), label=_('Content'), model=Document,
            name='content'
        )

        ModelPermission.register(
            model=DocumentFile, permissions=(
                permission_document_file_content_view,
                permission_document_file_parse
            )
        )
        ModelPermission.register(
            model=DocumentType, permissions=(
                permission_document_type_parsing_setup,
            )
        )
        ModelPermission.register_inheritance(
            model=DocumentTypeSettings, related='document_type',
        )

        error_log = ErrorLog(app_config=self)
        error_log.register_model(model=DocumentFile)

        menu_list_facet.bind_links(
            links=(link_document_file_content_detail,), sources=(DocumentFile,)
        )
        menu_list_facet.bind_links(
            links=(link_document_file_page_content_detail,),
            sources=(DocumentFilePage,)
        )
        menu_list_facet.bind_links(
            links=(link_document_type_parsing_settings,),
            sources=(DocumentType,)
        )
        menu_multi_item.bind_links(
            links=(
                link_document_file_content_multiple_delete,
                link_document_file_parsing_multiple_submit
            ), sources=(DocumentFile,)
        )
        menu_secondary.bind_links(
            links=(
                link_document_file_content_single_delete,
                link_document_file_content_download,
                link_document_file_parsing_single_submit
            ),
            sources=(
                'document_parsing:document_file_content_view',
                'document_parsing:document_file_content_single_delete',
                'document_parsing:document_file_content_download',
                'document_parsing:document_file_parsing_single_submit'
            )
        )
        menu_tools.bind_links(
            links=(
                link_document_type_parsing_submit,
            )
        )

        post_save.connect(
            dispatch_uid='document_parsing_handler_initialize_new_parsing_settings',
            receiver=handler_initialize_new_parsing_settings,
            sender=DocumentType
        )
        signal_post_document_file_upload.connect(
            dispatch_uid='document_parsing_handler_parse_document_file',
            receiver=handler_parse_document_file,
            sender=DocumentFile
        )
