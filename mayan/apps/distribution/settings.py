from django.utils.translation import ugettext_lazy as _

from mayan.apps.smart_settings.classes import SettingNamespace

namespace = SettingNamespace(label=_('Distribution'), name='distribution')

setting_distribution_storage = namespace.add_setting(
    default='s3',
    global_name='DISTRIBUTION_STORAGE',
    help_text=_(
        'Storage location for generated distribution renditions. '
        'Supported values: "local" and "s3".'
    )
)

