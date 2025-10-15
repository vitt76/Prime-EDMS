from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.classes import ModelPermission
from mayan.apps.common.apps import MayanAppConfig
from mayan.apps.common.menus import (
    menu_list_facet, menu_object, menu_secondary, menu_tools, menu_topbar
)
from mayan.apps.navigation.classes import SourceColumn
from mayan.apps.views.html_widgets import ObjectLinkWidget, TwoStateWidget

from .classes import EventTypeNamespace
from .html_widgets import widget_event_actor_link, widget_event_type_link
from .links import (
    link_event_type_subscription_list, link_object_event_list_clear,
    link_object_event_list_export, link_event_list, link_event_list_clear,
    link_event_list_export, link_notification_mark_read,
    link_notification_mark_read_all, link_notification_list,
    link_user_object_subscription_list
)


class EventsApp(MayanAppConfig):
    app_namespace = 'events'
    app_url = 'events'
    has_rest_api = True
    has_tests = True
    name = 'mayan.apps.events'
    verbose_name = _('Events')

    def ready(self):
        super().ready()

        Action = apps.get_model(app_label='actstream', model_name='Action')
        Notification = self.get_model(model_name='Notification')
        ObjectEventSubscription = self.get_model(
            model_name='ObjectEventSubscription'
        )
        StoredEventType = self.get_model(model_name='StoredEventType')

        User = get_user_model()

        EventTypeNamespace.load_modules()

        # Typecast the related field because actstream uses CharFields for
        # the object_id the action_object, actor, and target fields.
        ModelPermission.register_inheritance(
            fk_field_cast=models.CharField, model=Action,
            related='action_object'
        )
        ModelPermission.register_inheritance(
            fk_field_cast=models.CharField, model=Action, related='actor'
        )
        ModelPermission.register_inheritance(
            fk_field_cast=models.CharField, model=Action, related='target'
        )

        ModelPermission.register_inheritance(
            fk_field_cast=models.CharField, model=Notification,
            related='action__action_object'
        )
        ModelPermission.register_inheritance(
            fk_field_cast=models.CharField, model=Notification,
            related='action__actor'
        )
        ModelPermission.register_inheritance(
            fk_field_cast=models.CharField, model=Notification,
            related='action__target'
        )

        ModelPermission.register_inheritance(
            model=ObjectEventSubscription, related='content_object'
        )

        # Add labels to Action model, they are not marked translatable in the
        # upstream package.
        SourceColumn(
            attribute='timestamp', is_identifier=True,
            is_sortable=True, label=_('Date and time'), name='timestamp',
            source=Action
        )
        SourceColumn(
            func=widget_event_actor_link, label=_('Actor'),
            include_label=True, source=Action
        )
        SourceColumn(
            func=widget_event_type_link, label=_('Event'),
            include_label=True, name='event_type', source=Action
        )
        SourceColumn(
            attribute='target', label=_('Target'), include_label=True,
            name='target', source=Action, widget=ObjectLinkWidget
        )
        SourceColumn(
            attribute='action_object', label=_('Action object'),
            include_label=True, source=Action, widget=ObjectLinkWidget
        )

        # Stored event type

        SourceColumn(
            source=StoredEventType, label=_('Namespace'), attribute='namespace'
        )
        SourceColumn(
            source=StoredEventType, label=_('Label'), attribute='label'
        )

        # Notification

        SourceColumn(
            attribute='action__timestamp', is_identifier=True,
            is_sortable=True, label=_('Date and time'), source=Notification
        )
        SourceColumn(
            func=widget_event_actor_link, label=_('Actor'),
            include_label=True, kwargs={'attribute': 'action'},
            source=Notification
        )
        SourceColumn(
            func=widget_event_type_link, label=_('Event'),
            include_label=True, kwargs={'attribute': 'action'},
            source=Notification
        )
        SourceColumn(
            attribute='action.target', label=_('Target'), include_label=True,
            source=Notification, widget=ObjectLinkWidget
        )
        SourceColumn(
            attribute='action.action_object', label=_('Action object'),
            include_label=True, source=Notification, widget=ObjectLinkWidget
        )
        SourceColumn(
            attribute='read', include_label=True, is_sortable=True,
            label=_('Seen'), source=Notification, widget=TwoStateWidget
        )

        # Object event subscription

        SourceColumn(
            attribute='content_object', include_label=True,
            label=_('Object'), source=ObjectEventSubscription,
            widget=ObjectLinkWidget
        )
        SourceColumn(
            attribute='stored_event_type', include_label=True,
            label=_('Event type'), source=ObjectEventSubscription
        )

        # Clear

        menu_secondary.bind_links(
            links=(link_event_list_clear,),
            sources=(
                'events:event_list',
                'events:event_list_clear',
            )
        )
        menu_secondary.bind_links(
            links=(link_object_event_list_clear,),
            sources=(
                'events:object_event_list',
                'events:object_event_list_clear'
            )
        )

        # Export

        menu_secondary.bind_links(
            links=(link_event_list_export,),
            sources=(
                'events:event_list',
                'events:event_list_export',
            )
        )
        menu_secondary.bind_links(
            links=(link_object_event_list_export,),
            sources=(
                'events:object_event_list',
                'events:object_event_list_export'
            )
        )

        # Notification

        menu_object.bind_links(
            links=(link_notification_mark_read,), sources=(Notification,)
        )

        menu_secondary.bind_links(
            links=(link_notification_mark_read_all,),
            sources=(
                'events:notification_mark_read',
                'events:notification_mark_read_all',
                'events:user_notifications_list'
            )
        )

        # Subscription

        menu_list_facet.bind_links(
            links=(
                link_event_type_subscription_list,
                link_user_object_subscription_list,
            ), sources=(User,)
        )

        # Other

        menu_topbar.bind_links(
            links=(link_notification_list,), position=30
        )
        menu_tools.bind_links(links=(link_event_list,))
