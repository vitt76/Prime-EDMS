"""Tenant isolation tests for analytics (AssetEvent, dashboard, reports)."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from mayan.apps.documents.models import Document, DocumentType
from mayan.apps.organizations.managers import (
    clear_current_organization,
    set_current_organization,
)
from mayan.apps.organizations.models import Organization

from mayan.apps.analytics.models import AssetEvent, AnalyticsReportTask

User = get_user_model()


class AssetEventTenantIsolationTestCase(TestCase):
    """AssetEvent.objects is filtered by current organization context."""

    def setUp(self):
        super().setUp()
        self.org_a = Organization.objects.create(
            name='Isolation Org A',
            slug='iso-org-a',
            email='iso-a@test.com',
            is_active=True,
            status='active',
        )
        self.org_b = Organization.objects.create(
            name='Isolation Org B',
            slug='iso-org-b',
            email='iso-b@test.com',
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
        self.event_a1 = AssetEvent.objects.create(
            organization=self.org_a,
            document=self.doc_a,
            event_type=AssetEvent.EVENT_TYPE_VIEW,
        )
        self.event_a2 = AssetEvent.objects.create(
            organization=self.org_a,
            document=self.doc_a,
            event_type=AssetEvent.EVENT_TYPE_DOWNLOAD,
        )
        self.event_b1 = AssetEvent.objects.create(
            organization=self.org_b,
            document=self.doc_b,
            event_type=AssetEvent.EVENT_TYPE_VIEW,
        )

    def test_asset_event_isolation(self):
        """With context set to org A, AssetEvent.objects returns only org A events."""
        token = set_current_organization(self.org_a)
        try:
            ids = list(AssetEvent.objects.values_list('pk', flat=True))
            self.assertIn(self.event_a1.pk, ids)
            self.assertIn(self.event_a2.pk, ids)
            self.assertNotIn(self.event_b1.pk, ids)
            self.assertEqual(len(ids), 2)
        finally:
            clear_current_organization(token)


class DashboardMetricsTenantIsolationTestCase(TestCase):
    """Dashboard API returns only metrics for the organization in X-Organization-Id."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            username='dashboard_iso', password='pass', email='d@test.com'
        )
        self.client.force_authenticate(user=self.user)
        self.org_a = Organization.objects.create(
            name='Dashboard Org A',
            slug='dash-org-a',
            email='dash-a@test.com',
            is_active=True,
            status='active',
        )
        self.org_b = Organization.objects.create(
            name='Dashboard Org B',
            slug='dash-org-b',
            email='dash-b@test.com',
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
        for _ in range(2):
            AssetEvent.objects.create(
                organization=self.org_a,
                document=self.doc_a,
                event_type=AssetEvent.EVENT_TYPE_VIEW,
            )
        AssetEvent.objects.create(
            organization=self.org_b,
            document=self.doc_b,
            event_type=AssetEvent.EVENT_TYPE_VIEW,
        )

    def test_dashboard_metrics_isolation(self):
        """Request with X-Organization-Id for org A returns only org A metrics."""
        response = self.client.get(
            '/api/v4/headless/analytics/dashboard/',
            HTTP_X_ORGANIZATION_ID=str(self.org_a.pk),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data['organization'], str(self.org_a.pk))
        self.assertEqual(data['total_documents'], 1)
        self.assertEqual(len(data['top_documents']), 1)
        self.assertEqual(data['top_documents'][0]['document_id'], self.doc_a.pk)
        self.assertEqual(data['top_documents'][0]['view_count'], 2)


class ReportGenerationTenantIsolationTestCase(TestCase):
    """Report generation creates task for current org only; cannot access other org's report."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            username='report_iso', password='pass', email='ri@test.com'
        )
        self.client.force_authenticate(user=self.user)
        self.org1 = Organization.objects.create(
            name='Report Org 1',
            slug='report-org-1',
            email='r1@test.com',
            is_active=True,
            status='active',
        )
        self.org2 = Organization.objects.create(
            name='Report Org 2',
            slug='report-org-2',
            email='r2@test.com',
            is_active=True,
            status='active',
        )

    def test_report_generation_isolation(self):
        """POST with org1 creates AnalyticsReportTask with organization=org1."""
        response = self.client.post(
            '/api/v4/headless/analytics/reports/generate/',
            {'report_type': 'asset_usage'},
            format='json',
            HTTP_X_ORGANIZATION_ID=str(self.org1.pk),
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        task_id = response.data['task_id']
        task = AnalyticsReportTask.objects.get(pk=task_id)
        self.assertEqual(task.organization_id, self.org1.pk)
        self.assertEqual(task.user_id, self.user.pk)

    def test_report_status_only_own_org(self):
        """GET report status for another org's task returns 404."""
        task = AnalyticsReportTask.objects.create(
            organization=self.org1,
            user=self.user,
            report_type=AnalyticsReportTask.REPORT_TYPE_ASSET_USAGE,
            status=AnalyticsReportTask.STATUS_PENDING,
        )
        response = self.client.get(
            f'/api/v4/headless/analytics/reports/{task.pk}/',
            HTTP_X_ORGANIZATION_ID=str(self.org2.pk),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
