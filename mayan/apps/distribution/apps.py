from mayan.apps.common.apps import MayanAppConfig
from django.utils.translation import ugettext_lazy as _


class DistributionApp(MayanAppConfig):
    """
    Distribution - модуль публикации материалов для Mayan EDMS.
    Управление получателями, пресетами рендишенов, токен-порталом.
    """
    app_namespace = 'distribution'
    app_url = 'distribution'
    has_rest_api = True
    has_static_media = False
    has_tests = True
    name = 'mayan.apps.distribution'
    verbose_name = _('Distribution Module')
    label = 'distribution'

    def ready(self):
        super().ready()
        print('📦 Distribution module loaded successfully!')

        # Force add ourselves to INSTALLED_APPS if not already there
        from django.conf import settings
        app_name = 'mayan.apps.distribution'
        if app_name not in settings.INSTALLED_APPS:
            settings.INSTALLED_APPS.append(app_name)
            print(f'✅ Added {app_name} to INSTALLED_APPS via ready()')
