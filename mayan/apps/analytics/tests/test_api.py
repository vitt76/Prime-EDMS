"""Tests for analytics API (tenant-scoped dashboard)."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from mayan.apps.documents.models import Document, DocumentType
from mayan.apps.organizations.models import Organization

from mayan.apps.analytics.models import AssetEvent

User = get_user_model()


class AnalyticsDashboardIsolationTestCase(TestCase):
    """Dashboard returns only metrics for the organization in X-Organization-Id."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.superuser = User.objects.create_superuser(
            username='admin', password='admin', email='admin@test.com'
        )
        self.client.force_authenticate(user=self.superuser)

        self.org_a = Organization.objects.create(
            name='Org A',
            slug='org-a',
            email='org-a@test.com',
            is_active=True,
            status='active',
        )
        self.org_b = Organization.objects.create(
            name='Org B',
            slug='org-b',
            email='org-b@test.com',
            is_active=True,
            status='active',
        )

        doc_type = DocumentType.objects.create(label='Test')
        self.doc_a = Document.objects.create(
            document_type=doc_type,
            label='Doc A',
            organization=self.org_a,
        )
        self.doc_b = Document.objects.create(
            document_type=doc_type,
            label='Doc B',
            organization=self.org_b,
        )

        for _ in range(3):
            AssetEvent.objects.create(
                organization=self.org_a,
                document=self.doc_a,
                event_type=AssetEvent.EVENT_TYPE_VIEW,
            )
        for _ in range(2):
            AssetEvent.objects.create(
                organization=self.org_b,
                document=self.doc_b,
                event_type=AssetEvent.EVENT_TYPE_VIEW,
            )

    def test_dashboard_metrics_isolation(self):
        """With X-Organization-Id for org A, response has only org A metrics."""
        response = self.client.get(
            '/api/v4/headless/analytics/dashboard/',
            HTTP_X_ORGANIZATION_ID=str(self.org_a.pk),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        data = response.data
        self.assertEqual(data['organization'], str(self.org_a.pk))
        self.assertEqual(data['organization_name'], 'Org A')
        self.assertEqual(data['total_documents'], 1)
        self.assertEqual(len(data['top_documents']), 1)
        self.assertEqual(
            data['top_documents'][0]['document_id'],
            self.doc_a.pk,
        )
        self.assertEqual(data['top_documents'][0]['view_count'], 3)

    def test_dashboard_org_b_returns_org_b_metrics(self):
        """With X-Organization-Id for org B, response has only org B metrics."""
        response = self.client.get(
            '/api/v4/headless/analytics/dashboard/',
            HTTP_X_ORGANIZATION_ID=str(self.org_b.pk),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        data = response.data
        self.assertEqual(data['organization'], str(self.org_b.pk))
        self.assertEqual(data['organization_name'], 'Org B')
        self.assertEqual(data['total_documents'], 1)
        self.assertEqual(len(data['top_documents']), 1)
        self.assertEqual(
            data['top_documents'][0]['document_id'],
            self.doc_b.pk,
        )
        self.assertEqual(data['top_documents'][0]['view_count'], 2)

    def test_dashboard_returns_400_without_organization(self):
        """GET dashboard without X-Organization-Id returns 400 and message about organization context."""
        response = self.client.get('/api/v4/headless/analytics/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertIn('detail', response.data)
        self.assertIn('Organization', str(response.data['detail']))

    def test_dashboard_returns_200_with_empty_metrics(self):
        """Dashboard returns 200 with zero/empty metrics when org has no documents or events."""
        org_empty = Organization.objects.create(
            name='Empty Org',
            slug='empty-org',
            email='empty@test.com',
            is_active=True,
            status='active',
        )
        response = self.client.get(
            '/api/v4/headless/analytics/dashboard/',
            HTTP_X_ORGANIZATION_ID=str(org_empty.pk),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        data = response.data
        self.assertEqual(data['organization'], str(org_empty.pk))
        self.assertEqual(data['organization_name'], 'Empty Org')
        self.assertEqual(data['total_documents'], 0)
        self.assertEqual(len(data['top_documents']), 0)
        self.assertEqual(data['active_users_30d'], 0)
