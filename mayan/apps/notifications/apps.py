from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.apps import MayanAppConfig


class NotificationsApp(MayanAppConfig):
    """Notification Center integration for MAD DAM."""

    app_namespace = 'notifications'
    has_rest_api = False
    has_tests = True
    name = 'mayan.apps.notifications'
    verbose_name = _('Notification Center')
    label = 'notifications'

    def ready(self):
        super().ready()
        # Import signals to register receivers.
        from . import signals  # noqa: F401


