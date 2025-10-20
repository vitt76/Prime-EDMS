from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.classes import ModelPermission
from mayan.apps.acls.permissions import (
    permission_acl_edit, permission_acl_view
)
from mayan.apps.common.apps import MayanAppConfig
from mayan.apps.common.classes import ModelCopy
from mayan.apps.common.menus import (
    menu_list_facet, menu_object, menu_related, menu_secondary, menu_setup
)
from mayan.apps.documents.links.document_type_links import link_document_type_list
from mayan.apps.events.classes import EventModelRegistry, ModelEventType
from mayan.apps.navigation.classes import SourceColumn
from mayan.apps.rest_api.fields import DynamicSerializerField
from mayan.apps.views.html_widgets import TwoStateWidget

from .events import event_smart_link_edited
from .links import (
    link_document_type_smart_links, link_smart_link_create,
    link_smart_link_condition_create, link_smart_link_condition_delete,
    link_smart_link_condition_edit, link_smart_link_condition_list,
    link_smart_link_delete, link_smart_link_document_types,
    link_smart_link_edit, link_smart_link_instance_view,
    link_document_smart_link_instance_list, link_smart_link_list,
    link_smart_link_setup
)
from .permissions import (
    permission_resolved_smart_link_view, permission_smart_link_delete,
    permission_smart_link_edit, permission_smart_link_view
)


class LinkingApp(MayanAppConfig):
    app_namespace = 'linking'
    app_url = 'smart_links'
    has_rest_api = True
    has_tests = True
    name = 'mayan.apps.linking'
    verbose_name = _('Linking')

    def ready(self):
        super().ready()

        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )
        DocumentType = apps.get_model(
            app_label='documents', model_name='DocumentType'
        )

        ResolvedSmartLink = self.get_model(model_name='ResolvedSmartLink')
        SmartLink = self.get_model(model_name='SmartLink')
        SmartLinkCondition = self.get_model(model_name='SmartLinkCondition')

        DynamicSerializerField.add_serializer(
            klass=SmartLink,
            serializer_class='mayan.apps.linking.serializers.SmartLinkSerializer'
        )

        EventModelRegistry.register(model=SmartLink)
        EventModelRegistry.register(model=SmartLinkCondition)

        ModelCopy(
            model=SmartLinkCondition
        ).add_fields(
            field_names=(
                'enabled', 'expression', 'foreign_document_data',
                'inclusion', 'negated', 'operator', 'smart_link'
            )
        )
        ModelCopy(
            model=SmartLink, bind_link=True, register_permission=True
        ).add_fields(
            field_names=(
                'conditions', 'dynamic_label', 'document_types', 'enabled',
                'label'
            )
        )

        ModelEventType.register(
            event_types=(event_smart_link_edited,), model=SmartLink
        )

        ModelPermission.register(
            model=Document, permissions=(
                permission_resolved_smart_link_view,
            )
        )
        ModelPermission.register(
            model=SmartLink, permissions=(
                permission_acl_edit, permission_acl_view,
                permission_resolved_smart_link_view,
                permission_smart_link_delete, permission_smart_link_edit,
                permission_smart_link_view
            )
        )
        ModelPermission.register_inheritance(
            model=SmartLinkCondition, related='smart_link',
        )

        SourceColumn(
            func=lambda context: context['object'].get_label_for(
                document=context['document']
            ), is_identifier=True, label=_('Label'),
            source=ResolvedSmartLink
        )

        source_column_smart_link_label = SourceColumn(
            attribute='label', is_identifier=True, is_sortable=True,
            source=SmartLink
        )
        source_column_smart_link_label.add_exclude(source=ResolvedSmartLink)
        source_column_smart_link_dynamic_label = SourceColumn(
            attribute='dynamic_label', include_label=True, is_sortable=True,
            source=SmartLink
        )
        source_column_smart_link_dynamic_label.add_exclude(
            source=ResolvedSmartLink
        )
        source_column_smart_link_enabled = SourceColumn(
            attribute='enabled', include_label=True, is_sortable=True,
            source=SmartLink, widget=TwoStateWidget
        )
        source_column_smart_link_enabled.add_exclude(
            source=ResolvedSmartLink
        )
        SourceColumn(
            attribute='get_full_label', is_identifier=True,
            source=SmartLinkCondition
        )
        SourceColumn(
            attribute='enabled', include_label=True, is_sortable=True,
            source=SmartLinkCondition, widget=TwoStateWidget
        )

        # Document

        menu_list_facet.bind_links(
            links=(link_document_smart_link_instance_list,),
            sources=(Document,)
        )

        # Document type

        menu_list_facet.bind_links(
            links=(link_document_type_smart_links,), sources=(DocumentType,)
        )

        menu_related.bind_links(
            links=(link_smart_link_list,),
            sources=(
                DocumentType, 'documents:document_type_list',
                'documents:document_type_create'
            )
        )

        # Resolved smart link

        menu_object.bind_links(
            links=(link_smart_link_instance_view,),
            sources=(ResolvedSmartLink,)
        )

        # Smart link

        menu_list_facet.bind_links(
            exclude=(ResolvedSmartLink,),
            links=(
                link_smart_link_document_types, link_smart_link_condition_list
            ), sources=(SmartLink,)
        )

        menu_object.bind_links(
            exclude=(ResolvedSmartLink,),
            links=(
                link_smart_link_delete, link_smart_link_edit
            ), sources=(SmartLink,)
        )

        menu_related.bind_links(
            links=(link_document_type_list,),
            sources=(
                SmartLink, 'linking:smart_link_list',
                'linking:smart_link_create'
            )
        )

        menu_secondary.bind_links(
            links=(link_smart_link_list, link_smart_link_create),
            sources=(
                SmartLink, 'linking:smart_link_list',
                'linking:smart_link_create'
            )
        )

        # Smart link condition

        menu_object.bind_links(
            links=(
                link_smart_link_condition_edit,
                link_smart_link_condition_delete
            ), sources=(SmartLinkCondition,)
        )

        menu_secondary.bind_links(
            links=(link_smart_link_condition_create,),
            sources=(
                'linking:smart_link_condition_list',
                'linking:smart_link_condition_create',
                'linking:smart_link_condition_edit',
                'linking:smart_link_condition_delete'
            )
        )

        # Setup

        menu_setup.bind_links(links=(link_smart_link_setup,))
