from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class MarketingCMSApp(AppConfig):
    app_namespace = 'marketing_cms'
    has_rest_api = True
    has_tests = True
    name = 'mayan.apps.marketing_cms'
    verbose_name = _('Marketing CMS')
    verbose_name_plural = _('Marketing CMS')
