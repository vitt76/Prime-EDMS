"""
Sprint 3.3: Tests for OrganizationWatermarkSettingsView (GET/PATCH organization/watermark/).
"""
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from mayan.apps.organizations.models import Organization, OrganizationWatermarkSettings


class OrganizationWatermarkSettingsViewTestCase(APITestCase):
    """GET and PATCH /api/v4/headless/organization/watermark/."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.org = Organization.objects.create(
            name='Watermark Test Org',
            slug='watermark-org',
            email='wm@example.com',
            status='active',
            deployment_mode='standalone',
        )
        self.user = self._create_user()
        self.client.force_authenticate(user=self.user)

    def _create_user(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.create_user(
            username='wmuser',
            password='testpass123',
        )

    def test_get_returns_structure_or_400(self):
        """GET returns 200 with expected keys when org is set, or 400 when not."""
        response = self.client.get('/api/v4/headless/organization/watermark/')
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            self.assertIn('detail', response.data)
            return
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in ('enabled', 'text', 'position', 'opacity'):
            self.assertIn(key, response.data)

    def test_patch_updates_settings_when_org_set(self):
        """PATCH updates settings when request has organization (e.g. from middleware)."""
        ws, _ = OrganizationWatermarkSettings.objects.get_or_create(
            organization=self.org,
            defaults={'enabled': False, 'text': '', 'position': 'bottom_right', 'opacity': 0.5},
        )
        # Simulate request with organization (e.g. middleware sets it)
        from mayan.apps.headless_api.views.watermark_settings_views import OrganizationWatermarkSettingsView
        from rest_framework.request import Request
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        req = factory.patch(
            '/api/v4/headless/organization/watermark/',
            {'enabled': True, 'text': 'Confidential'},
            format='json',
        )
        req.user = self.user
        req.organization = self.org
        request = Request(req)
        view = OrganizationWatermarkSettingsView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['enabled'], True)
        self.assertEqual(response.data['text'], 'Confidential')
        ws.refresh_from_db()
        self.assertTrue(ws.enabled)
        self.assertEqual(ws.text, 'Confidential')
