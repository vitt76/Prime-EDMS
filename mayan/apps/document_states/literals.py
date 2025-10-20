import os

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

BASE_WORKFLOW_TEMPLATE_STATE_ACTION_HELP_TEXT = _(
    'Can be a static value or a template. '
    'In addition to the workflow instance, the template '
    'receives the workflow instance context which itself '
    'includes the "entry_log" (containing '
    '"workflow_instance", "datetime", "transition", "user", '
    '"comment") and any values from workflow template '
    'fields.'
)

DEFAULT_GRAPHVIZ_DOT_PATH = '/usr/bin/dot'
DEFAULT_HTTP_ACTION_TIMEOUT = 4  # 4 seconds
DEFAULT_WORKFLOWS_IMAGE_CACHE_MAXIMUM_SIZE = 50 * 2 ** 20  # 50 Megabytes
DEFAULT_WORKFLOWS_IMAGE_CACHE_STORAGE_BACKEND = 'django.core.files.storage.FileSystemStorage'
DEFAULT_WORKFLOWS_IMAGE_CACHE_STORAGE_BACKEND_ARGUMENTS = {
    'location': os.path.join(settings.MEDIA_ROOT, 'workflows')
}

DEFAULT_WORKFLOWS_WORKFLOW_STATE_ESCALATION_CHECK_INTERVAL = 60 * 5  # 5 minutes

FIELD_TYPE_CHOICE_CHAR = 1
FIELD_TYPE_CHOICE_INTEGER = 2
FIELD_TYPE_CHOICES = (
    (FIELD_TYPE_CHOICE_CHAR, _('Character')),
    (FIELD_TYPE_CHOICE_INTEGER, _('Number (Integer)')),
)
FIELD_TYPE_MAPPING = {
    FIELD_TYPE_CHOICE_CHAR: 'django.forms.CharField',
    FIELD_TYPE_CHOICE_INTEGER: 'django.forms.IntegerField',
}

STORAGE_NAME_WORKFLOW_CACHE = 'document_states__workflowimagecache'

SYMBOL_MATH_CONDITIONAL = '&rarr;'

WIDGET_CLASS_TEXTAREA = 1
WIDGET_CLASS_CHOICES = (
    (WIDGET_CLASS_TEXTAREA, _('Text area')),
)
WIDGET_CLASS_MAPPING = {
    WIDGET_CLASS_TEXTAREA: 'django.forms.widgets.Textarea',
}

WORKFLOW_ACTION_ON_ENTRY = 1
WORKFLOW_ACTION_ON_EXIT = 2
WORKFLOW_ACTION_WHEN_CHOICES = (
    (WORKFLOW_ACTION_ON_ENTRY, _('On entry')),
    (WORKFLOW_ACTION_ON_EXIT, _('On exit')),
)
