from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.apps import MayanAppConfig


class AnalyticsApp(MayanAppConfig):
    """Corporate analytics module for MAD DAM."""

    app_namespace = 'analytics'
    has_rest_api = False
    has_tests = True
    name = 'mayan.apps.analytics'
    verbose_name = _('Analytics')
    label = 'analytics'

    def ready(self):
        super().ready()


