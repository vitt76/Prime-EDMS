"""
ASGI config for the Mayan EDMS project.

It exposes the ASGI callable as a module-level variable named ``application``.
This file is used by Django Channels for WebSocket support.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings.production')

django_asgi_app = get_asgi_application()

try:
    from channels.auth import AuthMiddlewareStack
    from channels.routing import ProtocolTypeRouter, URLRouter
    from django.urls import path

    from mayan.apps.notifications.consumers import NotificationConsumer
    from mayan.apps.analytics.consumers import AnalyticsDashboardConsumer
except Exception:
    # Fallback: allow the project to run without channels installed.
    application = django_asgi_app
else:
    application = ProtocolTypeRouter(
        {
            'http': django_asgi_app,
            'websocket': AuthMiddlewareStack(
                URLRouter(
                    [
                        path('ws/notifications/', NotificationConsumer.as_asgi()),
                        path('ws/analytics/', AnalyticsDashboardConsumer.as_asgi()),
                    ]
                )
            ),
        }
    )
