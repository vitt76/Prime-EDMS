from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.apps import MayanAppConfig


class SavedSearchesAppConfig(MayanAppConfig):
    name = 'mayan.apps.saved_searches'
    verbose_name = _('Saved searches')
    label = 'saved_searches'
