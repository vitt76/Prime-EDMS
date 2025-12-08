"""
Headless API Django App Configuration

This app provides SPA-friendly REST endpoints that Mayan EDMS doesn't expose natively.
It acts as a Backend-for-Frontend (BFF) layer between Vue.js frontend and Mayan core.
"""

from django.apps import apps
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from django.apps import AppConfig


class HeadlessAPIApp(AppConfig):
    """
    Headless API application configuration.

    This app extends Mayan EDMS with SPA-compatible endpoints for:
    - Password change functionality
    - Document type configuration exposure
    - Personalized activity feeds
    """

    app_url = 'headless'
    app_namespace = 'headless_api'
    has_rest_api = True
    has_tests = True
    name = 'mayan.apps.headless_api'
    verbose_name = _('Headless API')
    verbose_name_plural = _('Headless APIs')

    def ready(self):
        """
        Initialize the headless API app.

        This method is called when Django starts and all apps are loaded.
        Used for signal registration and API URL registration.
        """
        super().ready()

        # Log that headless API is ready
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Headless API app initialized and ready for SPA integration")
