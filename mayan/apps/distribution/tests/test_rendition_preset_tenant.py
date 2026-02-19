"""
Sprint 3.3: Tests for tenant-scoped RenditionPreset list (organization filter).
"""
from rest_framework.test import APIClient, APITestCase

from mayan.apps.organizations.models import Organization
from mayan.apps.distribution.models import Recipient, RenditionPreset


class RenditionPresetTenantTestCase(APITestCase):
    """Preset list is filtered by request.organization (global + org)."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.org1 = Organization.objects.create(
            name='Org One',
            slug='org-one',
            email='one@example.com',
            status='active',
            deployment_mode='standalone',
        )
        self.recipient, _ = Recipient.objects.get_or_create(
            email='preset-recipient@test.com',
            defaults={'name': 'Preset Recipient'},
        )
        self.user = self._create_user()
        self.client.force_authenticate(user=self.user)

    def _create_user(self):
        from django.contrib.auth import get_user_model
        return get_user_model().objects.create_user(
            username='presetuser',
            password='testpass123',
        )

    def test_preset_queryset_includes_global_and_org(self):
        """Global preset (organization=null) and org-specific preset both visible for that org."""
        global_preset = RenditionPreset.objects.create(
            name='Global Preset Tenant Test',
            resource_type='image',
            format='jpeg',
            recipient=self.recipient,
            organization=None,
        )
        org_preset = RenditionPreset.objects.create(
            name='Org Preset Tenant Test',
            resource_type='image',
            format='png',
            recipient=self.recipient,
            organization=self.org1,
        )
        from mayan.apps.distribution.views.preset_views import _preset_queryset_for_request
        from rest_framework.test import APIRequestFactory
        from rest_framework.request import Request
        factory = APIRequestFactory()
        req = factory.get('/api/v4/distribution/rendition_presets/')
        req.user = self.user
        req.organization = self.org1
        request = Request(req)
        qs = _preset_queryset_for_request(request)
        ids = list(qs.values_list('pk', flat=True))
        self.assertIn(global_preset.pk, ids, 'Global preset should be visible')
        self.assertIn(org_preset.pk, ids, 'Org preset should be visible for its org')
