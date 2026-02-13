"""
Tests for NotificationConsumer (WebSocket) organization validation.

- Connect with valid token + organization_id (user in org) -> accepted, correct group.
- Connect without organization_id -> close with code 4003.
- Connect with organization_id of org user is not in -> close with code 4003.
"""

from asgiref.sync import async_to_sync
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TestCase

from mayan.apps.notifications.consumers import (
    NotificationConsumer,
    WS_CLOSE_ORG_DENIED,
)

User = get_user_model()


class NotificationConsumerOrganizationTest(TestCase):
    """Test NotificationConsumer connect with organization_id."""

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='wsuser',
            email='ws@example.com',
            password='testpass123',
        )
        try:
            from rest_framework.authtoken.models import Token
            self.token = Token.objects.create(user=self.user)
        except Exception:
            self.token = None

        try:
            from mayan.apps.organizations.models import Organization, UserOrganizationRole
            self.org = Organization.objects.create(
                name='WS Test Org',
                slug='ws-test-org',
                email='ws@example.com',
                status='active',
                deployment_mode='saas',
            )
            UserOrganizationRole.objects.create(
                user=self.user,
                organization=self.org,
                role=UserOrganizationRole.ROLE_OWNER,
                is_default=True,
            )
            self.other_org = Organization.objects.create(
                name='Other Org',
                slug='other-org',
                email='other@example.com',
                status='active',
                deployment_mode='saas',
            )
        except Exception:
            self.org = None
            self.other_org = None

    def _get_application(self):
        from channels.routing import URLRouter
        from django.urls import path
        from mayan.apps.notifications.consumers import NotificationConsumer
        return URLRouter([
            path('ws/notifications/', NotificationConsumer.as_asgi()),
        ])

    @async_to_sync
    async def test_connect_without_organization_id_closes(self):
        """Connect without organization_id in query -> connection closed (4003)."""
        if not self.token:
            self.skipTest('DRF Token not available')

        application = self._get_application()
        communicator = WebsocketCommunicator(
            application,
            'ws/notifications/?token={}'.format(self.token.key),
        )
        connected, _ = await communicator.connect()
        self.assertFalse(connected, msg='Connection must be rejected when organization_id is missing')
        self.assertEqual(communicator.close_code, WS_CLOSE_ORG_DENIED)

    @async_to_sync
    async def test_connect_with_valid_org_accepted(self):
        """Connect with valid token and organization_id (user in org) -> accepted."""
        if not self.token or not self.org:
            self.skipTest('Token or Organization not available')

        application = self._get_application()
        communicator = WebsocketCommunicator(
            application,
            'ws/notifications/?token={}&organization_id={}'.format(
                self.token.key, self.org.pk
            ),
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected, msg='Connection should be accepted')
        await communicator.disconnect()

    @async_to_sync
    async def test_connect_wrong_org_closes(self):
        """Connect with organization_id of org user is not in -> close 4003."""
        if not self.token or not self.other_org:
            self.skipTest('Token or Organization not available')

        application = self._get_application()
        communicator = WebsocketCommunicator(
            application,
            'ws/notifications/?token={}&organization_id={}'.format(
                self.token.key, self.other_org.pk
            ),
        )
        connected, _ = await communicator.connect()
        self.assertFalse(connected, msg='Connection must be rejected when user not in org')
        self.assertEqual(communicator.close_code, WS_CLOSE_ORG_DENIED)

    @async_to_sync
    async def test_connect_without_token_closes(self):
        """Connect without token -> connection closed (not accepted)."""
        if not self.org:
            self.skipTest('Organization not available')

        application = self._get_application()
        communicator = WebsocketCommunicator(
            application,
            'ws/notifications/?organization_id={}'.format(self.org.pk),
        )
        connected, _ = await communicator.connect()
        self.assertFalse(connected)
