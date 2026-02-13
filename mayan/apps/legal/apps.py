from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class LegalApp(AppConfig):
    app_namespace = 'legal'
    has_rest_api = True
    has_tests = True
    name = 'mayan.apps.legal'
    verbose_name = _('Legal')
    verbose_name_plural = _('Legal')
