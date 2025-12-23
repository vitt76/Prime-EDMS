"""
Settings for Headless API app.

Defines configurable settings for cache TTL and versioning.
"""
from django.utils.translation import ugettext_lazy as _

from mayan.apps.smart_settings.classes import SettingNamespace

namespace = SettingNamespace(
    label=_('Headless API'), name='headless_api', version='0001'
)

setting_doc_type_config_cache_ttl = namespace.add_setting(
    default=3600,  # 1 час
    global_name='HEADLESS_DOC_TYPE_CONFIG_CACHE_TTL',
    help_text=_(
        'Time-to-live for document type configuration cache in seconds. '
        'Default: 3600 (1 hour). Increase for better performance, decrease for more frequent updates.'
    )
)

setting_doc_type_config_cache_version = namespace.add_setting(
    default='v1',
    global_name='HEADLESS_DOC_TYPE_CONFIG_CACHE_VERSION',
    help_text=_(
        'Cache version for document type configuration. '
        'Increment when API response schema changes to invalidate old cache entries.'
    )
)

