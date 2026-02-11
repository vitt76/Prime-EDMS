"""Tests for async analytics report generation."""

import os
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from mayan.apps.documents.models import Document, DocumentType
from mayan.apps.organizations.models import Organization

from mayan.apps.analytics.models import AssetEvent, AnalyticsReportTask
from mayan.apps.analytics.tasks import generate_analytics_report

User = get_user_model()


class AnalyticsReportGenerationTestCase(TestCase):
    """Report task is created and task runs to completion."""

    def setUp(self):
        super().setUp()
        self.media_root = tempfile.mkdtemp()
        self.org = Organization.objects.create(
            name='Report Org',
            slug='report-org',
            email='report@test.com',
            is_active=True,
            status='active',
        )
        self.user = User.objects.create_superuser(
            username='reportuser', password='pass', email='r@test.com'
        )
        doc_type = DocumentType.objects.create(label='Test')
        self.document = Document.objects.create(
            document_type=doc_type,
            label='Report Doc',
            organization=self.org,
        )
        AssetEvent.objects.create(
            organization=self.org,
            document=self.document,
            event_type=AssetEvent.EVENT_TYPE_VIEW,
        )

    def test_generate_analytics_report_task_sync(self):
        """Running the task synchronously completes and sets file_path."""
        with tempfile.TemporaryDirectory() as tmp:
            with override_settings(MEDIA_ROOT=tmp):
                task = AnalyticsReportTask.objects.create(
                    organization=self.org,
                    user=self.user,
                    report_type=AnalyticsReportTask.REPORT_TYPE_ASSET_USAGE,
                    parameters={'date_range': {}},
                    status=AnalyticsReportTask.STATUS_PENDING,
                )
                generate_analytics_report(
                    task.pk,
                    organization_id=str(self.org.pk),
                )
                task.refresh_from_db()
                self.assertEqual(task.status, AnalyticsReportTask.STATUS_COMPLETED)
                self.assertIsNotNone(task.file_path)
                self.assertIsNotNone(task.completed_at)
                self.assertTrue(
                    os.path.isfile(task.file_path),
                    'Report file should exist: %s' % task.file_path
                )


class AnalyticsReportAPITestCase(TestCase):
    """POST generate returns 202 and creates a report task."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            username='apiuser', password='pass', email='a@test.com'
        )
        self.client.force_authenticate(user=self.user)
        self.org = Organization.objects.create(
            name='API Report Org',
            slug='api-report-org',
            email='api-report@test.com',
            is_active=True,
            status='active',
        )

    def test_post_generate_returns_202_and_creates_task(self):
        """POST with X-Organization-Id creates task and returns task_id."""
        response = self.client.post(
            '/api/v4/headless/analytics/reports/generate/',
            {'report_type': 'asset_usage'},
            format='json',
            HTTP_X_ORGANIZATION_ID=str(self.org.pk),
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        data = response.data
        self.assertIn('task_id', data)
        self.assertEqual(data.get('status'), 'processing')
        task = AnalyticsReportTask.objects.get(pk=data['task_id'])
        self.assertEqual(task.organization_id, self.org.pk)
        self.assertEqual(task.user_id, self.user.pk)
        self.assertEqual(task.report_type, AnalyticsReportTask.REPORT_TYPE_ASSET_USAGE)
