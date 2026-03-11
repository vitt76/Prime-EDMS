from asgiref.sync import async_to_sync
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import path

from mayan.apps.analytics.consumers import (
    AnalyticsDashboardConsumer,
)
from mayan.apps.organizations.tests.mixins import SaaSTenantTestHarnessMixin

User = get_user_model()


class AnalyticsDashboardConsumerTest(
    SaaSTenantTestHarnessMixin, TestCase
):
    """Analytics websocket auth and tenant contract smoke tests."""

    def setUp(self):
        super().setUp()
        self.org = self.create_organization(
            name='Analytics WS Org',
            slug='analytics-ws-org',
        )
        self.other_org = self.create_organization(
            name='Analytics WS Other Org',
            slug='analytics-ws-other-org',
        )
        self.user = self.create_user_in_organization(
            username='analytics-ws-user',
            organization=self.org,
            is_default=True,
        )
        self.admin = self.create_user(
            username='analytics-ws-admin',
            is_superuser=True,
        )

        try:
            from rest_framework.authtoken.models import Token
            self.user_token = Token.objects.create(user=self.user)
            self.admin_token = Token.objects.create(user=self.admin)
        except Exception:
            self.user_token = None
            self.admin_token = None

    def _get_application(self):
        return URLRouter([
            path('ws/analytics/', AnalyticsDashboardConsumer.as_asgi()),
        ])

    @async_to_sync
    async def test_connect_requires_organization_for_regular_user(self):
        if not self.user_token:
            self.skipTest('DRF Token not available')

        communicator = WebsocketCommunicator(
            self._get_application(),
            f'/ws/analytics/?token={self.user_token.key}',
        )
        connected, _ = await communicator.connect()
        self.assertFalse(connected)

    @async_to_sync
    async def test_connect_rejects_user_outside_organization(self):
        if not self.user_token:
            self.skipTest('DRF Token not available')

        communicator = WebsocketCommunicator(
            self._get_application(),
            f'/ws/analytics/?token={self.user_token.key}&organization_id={self.other_org.pk}',
        )
        connected, _ = await communicator.connect()
        self.assertFalse(connected)

    @async_to_sync
    async def test_connect_accepts_valid_token_and_organization(self):
        if not self.user_token:
            self.skipTest('DRF Token not available')

        communicator = WebsocketCommunicator(
            self._get_application(),
            f'/ws/analytics/?token={self.user_token.key}&organization_id={self.org.pk}',
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        payload = await communicator.receive_json_from()
        self.assertEqual(payload['type'], 'analytics.connected')
        self.assertEqual(payload['organization_id'], str(self.org.pk))
        await communicator.disconnect()

    @async_to_sync
    async def test_admin_connect_without_organization_is_allowed(self):
        if not self.admin_token:
            self.skipTest('DRF Token not available')

        communicator = WebsocketCommunicator(
            self._get_application(),
            f'/ws/analytics/?token={self.admin_token.key}',
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        payload = await communicator.receive_json_from()
        self.assertEqual(payload['type'], 'analytics.connected')
        self.assertEqual(payload['group'], 'analytics_dashboard_all')
        self.assertTrue(payload['is_admin'])
        await communicator.disconnect()
