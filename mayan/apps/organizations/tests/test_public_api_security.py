"""
Sprint 4 Security: Public API must not leak tenant data.

Unauthenticated public endpoints (legal consent, share link portal, etc.)
must not return organization_id, document lists, or any tenant-scoped data.
"""

from rest_framework import status
from rest_framework.test import APIClient

from django.test import TestCase


class PublicAPINoTenantDataLeakTestCase(TestCase):
    """Public API responses must not contain tenant-scoped data."""

    def setUp(self):
        self.client = APIClient()
        # No authentication - public endpoints

    def test_public_legal_consent_returns_no_tenant_data(self):
        """POST /api/v4/public/legal/consent/ (unauthenticated) must not return org/documents."""
        response = self.client.post(
            '/api/v4/public/legal/consent/',
            data={
                'consent_type': 'full',
                'session_id': '',
                'url_referer': '',
            },
            format='json',
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            'Public consent endpoint should accept unauthenticated POST'
        )
        data = response.json()
        # Must not expose tenant-scoped fields
        self.assertNotIn(
            'organization_id',
            data,
            'Public API response must not contain organization_id'
        )
        self.assertNotIn(
            'organizations',
            data,
            'Public API response must not contain organizations list'
        )
        self.assertNotIn(
            'documents',
            data,
            'Public API response must not contain documents list'
        )
        # Legal consent returns only status
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'ok')
