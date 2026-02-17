from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from mayan.apps.acls.tests.mixins import ACLTestCaseMixin
from mayan.apps.documents.models import Document
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.tests.mixins.document_mixins import DocumentTestMixin
from mayan.apps.organizations.managers import (
    clear_current_organization, set_current_organization
)
from mayan.apps.organizations.models import Organization, UserOrganizationRole
from mayan.apps.rest_api.tests.base import BaseAPITestCase

from ..models import DocumentAIAnalysis
from ..tasks import analyze_document_with_ai, bulk_analyze_documents

class DocumentAIAnalysisTenantIsolationTestCase(DocumentTestMixin, TestCase):
    """
    Tenant isolation checks for DAM model layer.
    """

    auto_create_test_document_type = True
    auto_upload_test_document = True

    def setUp(self):
        super().setUp()
        self.organization_a = Organization.objects.create(
            name='Tenant A',
            slug='tenant-a',
            email='tenant-a@example.com'
        )
        self.organization_b = Organization.objects.create(
            name='Tenant B',
            slug='tenant-b',
            email='tenant-b@example.com'
        )

        self.document_a = self._test_document
        self.document_a.organization = self.organization_a
        self.document_a.save(update_fields=['organization'])

        self._upload_test_document(label='tenant-b-document')
        self.document_b = self._test_document
        self.document_b.organization = self.organization_b
        self.document_b.save(update_fields=['organization'])

        self.analysis_a = DocumentAIAnalysis.objects_unfiltered.create(
            document=self.document_a,
            organization=self.organization_a,
            analysis_status='completed',
            ai_tags=['a']
        )
        self.analysis_b = DocumentAIAnalysis.objects_unfiltered.create(
            document=self.document_b,
            organization=self.organization_b,
            analysis_status='completed',
            ai_tags=['b']
        )

    def test_ai_analysis_filtered_by_current_organization(self):
        token = set_current_organization(self.organization_a)
        try:
            ids = set(DocumentAIAnalysis.objects.values_list('pk', flat=True))
        finally:
            clear_current_organization(token)

        self.assertIn(self.analysis_a.pk, ids)
        self.assertNotIn(self.analysis_b.pk, ids)

    def test_ai_analysis_organization_auto_bound_from_document(self):
        analysis = DocumentAIAnalysis.objects_unfiltered.create(
            document=self.document_a,
            analysis_status='pending'
        )
        self.assertEqual(analysis.organization_id, self.organization_a.pk)

    def test_documentfile_and_documentversion_scoped_via_document_queryset(self):
        token = set_current_organization(self.organization_a)
        try:
            tenant_documents = Document.objects.all()
            self.assertEqual(tenant_documents.count(), 1)

            document = tenant_documents.first()
            self.assertEqual(document.organization_id, self.organization_a.pk)
            self.assertTrue(
                all(
                    file_item.document.organization_id == self.organization_a.pk
                    for file_item in document.files.all()
                )
            )
            self.assertTrue(
                all(
                    version.document.organization_id == self.organization_a.pk
                    for version in document.versions.all()
                )
            )
        finally:
            clear_current_organization(token)


class DocumentAIAnalysisTenantApiTestCase(
    ACLTestCaseMixin, DocumentTestMixin, BaseAPITestCase
):
    """
    API-level tenant filtering checks using X-Organization-Id.
    """

    auto_create_test_document_type = True
    auto_upload_test_document = True
    auto_create_test_role = True

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self._test_case_user)

        self.organization_a = Organization.objects.create(
            name='API Tenant A',
            slug='api-tenant-a',
            email='api-tenant-a@example.com'
        )
        self.organization_b = Organization.objects.create(
            name='API Tenant B',
            slug='api-tenant-b',
            email='api-tenant-b@example.com'
        )
        UserOrganizationRole.objects.create(
            user=self._test_case_user,
            organization=self.organization_a,
            role='member',
            is_default=True
        )
        UserOrganizationRole.objects.create(
            user=self._test_case_user,
            organization=self.organization_b,
            role='member'
        )

        self.document_a = self._test_document
        self.document_a.organization = self.organization_a
        self.document_a.save(update_fields=['organization'])
        self.grant_access(
            obj=self.document_a, permission=permission_document_view
        )

        self._upload_test_document(label='api-tenant-b-document')
        self.document_b = self._test_document
        self.document_b.organization = self.organization_b
        self.document_b.save(update_fields=['organization'])
        self.grant_access(
            obj=self.document_b, permission=permission_document_view
        )

        self.analysis_a = DocumentAIAnalysis.objects_unfiltered.create(
            document=self.document_a,
            organization=self.organization_a,
            analysis_status='completed',
            ai_tags=['a']
        )
        DocumentAIAnalysis.objects_unfiltered.create(
            document=self.document_b,
            organization=self.organization_b,
            analysis_status='completed',
            ai_tags=['b']
        )

    def test_ai_analysis_list_filtered_by_header_organization(self):
        response = self.client.get(
            '/api/dam/ai-analysis/',
            HTTP_X_ORGANIZATION_ID=str(self.organization_a.pk)
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = response.data
        results = payload.get('results', payload)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], self.analysis_a.pk)
        self.assertEqual(
            str(results[0]['organization']), str(self.organization_a.pk)
        )

    def test_ai_analysis_detail_cross_tenant_returns_404(self):
        """With X-Organization-Id for org A, GET analysis of org B by id returns 404."""
        analysis_b = DocumentAIAnalysis.objects_unfiltered.get(
            document=self.document_b
        )
        response = self.client.get(
            f'/api/dam/ai-analysis/{analysis_b.pk}/',
            HTTP_X_ORGANIZATION_ID=str(self.organization_a.pk),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class DocumentAIAnalysisTenantTaskTestCase(DocumentTestMixin, TestCase):
    """
    Task-level propagation checks for organization context.
    """

    auto_create_test_document_type = True
    auto_upload_test_document = True

    def setUp(self):
        super().setUp()
        self.organization = Organization.objects.create(
            name='Task Tenant',
            slug='task-tenant',
            email='task-tenant@example.com'
        )
        self.document = self._test_document
        self.document.organization = self.organization
        self.document.save(update_fields=['organization'])

    @patch('mayan.apps.dam.tasks.reindex_document_assets')
    @patch('mayan.apps.dam.tasks.update_document_metadata_from_ai')
    @patch('mayan.apps.dam.tasks.perform_ai_analysis')
    def test_analyze_task_sets_document_analysis_organization(
        self, mock_perform_ai_analysis, mock_update_metadata, mock_reindex
    ):
        mock_perform_ai_analysis.return_value = {
            'description': 'test',
            'tags': ['tenant'],
            'colors': [],
            'alt_text': 'tenant',
            'categories': [],
            'language': '',
            'people': [],
            'locations': [],
            'copyright': '',
            'usage_rights': '',
            'provider': 'mock'
        }

        analyze_document_with_ai(
            document_id=self.document.pk,
            organization_id=str(self.organization.pk)
        )

        analysis = DocumentAIAnalysis.objects_unfiltered.get(document=self.document)
        self.assertEqual(analysis.organization_id, self.organization.pk)

    @patch('mayan.apps.dam.tasks.analyze_document_with_ai.delay')
    def test_bulk_task_propagates_organization_to_child_tasks(self, mock_delay):
        token = set_current_organization(self.organization)
        try:
            bulk_analyze_documents(document_ids=[self.document.pk])
        finally:
            clear_current_organization(token)

        mock_delay.assert_called_once()
        _, call_kwargs = mock_delay.call_args
        self.assertEqual(
            call_kwargs.get('organization_id'),
            str(self.organization.pk)
        )
