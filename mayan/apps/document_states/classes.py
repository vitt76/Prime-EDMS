import logging

from django.apps import apps
from django.db.utils import OperationalError, ProgrammingError
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.classes import PropertyHelper
from mayan.apps.databases.classes import BaseBackend
from mayan.apps.templating.classes import Template

from .exceptions import WorkflowStateActionError

__all__ = ('WorkflowAction',)
logger = logging.getLogger(name=__name__)


class DocumentStateHelper(PropertyHelper):
    @staticmethod
    @property
    def constructor(*args, **kwargs):
        return DocumentStateHelper(*args, **kwargs)

    def get_result(self, name):
        return self.instance.workflows.get(workflow__internal_name=name)


class WorkflowAction(BaseBackend):
    _loader_module_name = 'workflow_actions'
    fields = {}
    previous_dotted_paths = ()

    @classmethod
    def load_modules(cls):
        super().load_modules()

        for action_class in WorkflowAction.get_all():
            action_class.migrate()

    @classmethod
    def clean(cls, request, form_data=None):
        return form_data

    @classmethod
    def get_choices(cls):
        apps_name_map = {
            app.name: app for app in apps.get_app_configs()
        }

        # Match each workflow action to an app.
        apps_workflow_action_map = {}

        for klass in WorkflowAction.get_all():
            for app_name, app in apps_name_map.items():
                if klass.__module__.startswith(app_name):
                    apps_workflow_action_map.setdefault(app, [])
                    apps_workflow_action_map[app].append(
                        (klass.id(), klass.label)
                    )

        result = [
            (app.verbose_name, workflow_actions) for app, workflow_actions in apps_workflow_action_map.items()
        ]

        # Sort by app, then by workflow action.
        return sorted(result, key=lambda x: (x[0], x[1]))

    @classmethod
    def id(cls):
        return cls.backend_id

    @classmethod
    def migrate(cls):
        WorkflowStateAction = apps.get_model(
            app_label='document_states', model_name='WorkflowStateAction'
        )
        for previous_dotted_path in cls.previous_dotted_paths:
            try:
                WorkflowStateAction.objects.filter(
                    action_path=previous_dotted_path
                ).update(action_path=cls.id())
            except (OperationalError, ProgrammingError):
                # Ignore errors during the database migration and
                # quit further attempts.
                return

    def __init__(self, form_data=None):
        self.form_data = form_data

    def execute(self, context):
        raise NotImplementedError

    def get_fields(self):
        return getattr(self, 'fields', {})

    def get_field_order(self):
        return getattr(self, 'field_order', ())

    def get_media(self):
        return getattr(self, 'media', {})

    def get_form_schema(self, workflow_state, request=None):
        result = {
            'fields': self.get_fields(),
            'media': self.get_media(),
            'widgets': self.get_widgets(),
        }

        field_order = self.get_field_order()

        if field_order:
            result['field_order'] = field_order

        return result

    def get_widgets(self):
        return getattr(self, 'widgets', {})

    def render_field(self, field_name, context):
        try:
            result = Template(
                template_string=self.form_data.get(field_name, '')
            ).render(
                context=context
            )
        except Exception as exception:
            raise WorkflowStateActionError(
                _('%(field_name)s template error: %(exception)s') % {
                    'field_name': field_name, 'exception': exception
                }
            )

        logger.debug('%s template result: %s', field_name, result)

        return result
