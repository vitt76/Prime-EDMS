"""Tests for async analytics report generation."""

import os

from django.test import TestCase
from rest_framework import status

from mayan.apps.documents.models import Document, DocumentType
from mayan.apps.organizations.tests.mixins import SaaSTenantTestHarnessMixin

from mayan.apps.analytics.models import AssetEvent, AnalyticsReportTask
from mayan.apps.analytics.tasks import (
    generate_analytics_report, track_asset_event_async
)


class AnalyticsReportGenerationTestCase(
    SaaSTenantTestHarnessMixin, TestCase
):
    """Report task is created and task runs to completion."""

    use_temporary_media_root = True

    def setUp(self):
        super().setUp()
        self.org = self.create_organization(
            name='Report Org',
            slug='report-org',
        )
        self.user = self.create_user_in_organization(
            username='reportuser',
            organization=self.org,
            is_default=True,
            is_superuser=True,
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

    def test_track_asset_event_async_apply_accepts_organization_id_kwarg(self):
        """TenantAwareTask should accept organization_id in kwargs without signature errors."""
        before_count = AssetEvent.objects.count()

        result = track_asset_event_async.apply(kwargs={
            'organization_id': str(self.org.pk),
            'user_id': self.user.pk,
            'document_id': self.document.pk,
            'event_type': AssetEvent.EVENT_TYPE_VIEW,
            'metadata': {'source': 'test'},
        })

        self.assertTrue(result.successful())
        self.assertEqual(AssetEvent.objects.count(), before_count + 1)


class AnalyticsReportAPITestCase(
    SaaSTenantTestHarnessMixin, TestCase
):
    """POST generate returns 202 and creates a report task."""

    def setUp(self):
        super().setUp()
        self.org = self.create_organization(
            name='API Report Org',
            slug='api-report-org',
        )
        self.user = self.create_user_in_organization(
            username='apiuser',
            organization=self.org,
            is_default=True,
            is_superuser=True,
        )
        self.client = self.api_client_for(self.user)

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
