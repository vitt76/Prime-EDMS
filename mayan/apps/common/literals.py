from django.conf import settings

from django.utils.translation import ugettext_lazy as _

import mayan

DEFAULT_COMMON_COLLAPSE_LIST_MENU_LIST_FACET = False
DEFAULT_COMMON_COLLAPSE_LIST_MENU_OBJECT = False
DEFAULT_COMMON_DISABLE_LOCAL_STORAGE = False
DEFAULT_COMMON_DISABLED_APPS = settings.COMMON_DISABLED_APPS
DEFAULT_COMMON_EXTRA_APPS = settings.COMMON_EXTRA_APPS
DEFAULT_COMMON_EXTRA_APPS_PRE = settings.COMMON_EXTRA_APPS_PRE
DEFAULT_COMMON_HOME_VIEW = 'common:home'
DEFAULT_COMMON_HOME_VIEW_DASHBOARD_NAME = 'user'
DEFAULT_COMMON_PROJECT_TITLE = mayan.__title__
DEFAULT_COMMON_PROJECT_URL = mayan.__website__

EMPTY_LABEL = '---------'

MESSAGE_DEPRECATION_WARNING = _(
    'This feature has been deprecated and will be removed in a future version.'
)

TIME_DELTA_UNIT_DAYS = 'days'
TIME_DELTA_UNIT_HOURS = 'hours'
TIME_DELTA_UNIT_MINUTES = 'minutes'

TIME_DELTA_UNIT_CHOICES = (
    (TIME_DELTA_UNIT_DAYS, _('Days')),
    (TIME_DELTA_UNIT_HOURS, _('Hours')),
    (TIME_DELTA_UNIT_MINUTES, _('Minutes')),
)
