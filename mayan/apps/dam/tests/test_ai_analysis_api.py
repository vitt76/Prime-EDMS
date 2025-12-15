import json
from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APIClient

from mayan.apps.acls.tests.mixins import ACLTestCaseMixin
from mayan.apps.documents.models import Document
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.tests.mixins.document_mixins import DocumentTestMixin
from mayan.apps.rest_api.tests.base import BaseAPITestCase

from ..models import DocumentAIAnalysis


class AIAnalysisAPITestCase(ACLTestCaseMixin, DocumentTestMixin, BaseAPITestCase):
    """
    Comprehensive tests for AI Analysis API endpoints.
    Tests throttling, ACL checks, error handling, and audit logging.
    """
    auto_create_test_document_type = True
    auto_upload_test_document = True
    auto_create_test_role = True

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self._test_case_user)

    def _grant_analysis_access(self, document=None):
        """Grant analysis permission to test user for document."""
        if document is None:
            document = self._test_document
        self.grant_access(
            obj=document,
            permission=self._test_permission
        )

    def _create_test_analysis(self, document=None):
        """Create a test DocumentAIAnalysis instance."""
        if document is None:
            document = self._test_document
        return DocumentAIAnalysis.objects.create(
            document=document,
            ai_description="Test analysis",
            ai_tags=['test'],
            analysis_status='completed'
        )

    def test_analyze_returns_202_accepted(self):
        """Test analyze endpoint returns 202 with proper structure."""
        self._grant_view_access(self._test_document)
        self._grant_analysis_access(self._test_document)

        url = '/api/dam/ai-analysis/analyze/'
        data = {
            'document_id': self._test_document.pk,
            'ai_service': 'openai',
            'analysis_type': 'classification'
        }

        with patch('mayan.apps.dam.api_views.analyze_document_with_ai.delay') as mock_task:
            mock_task.return_value.id = 'test-task-id'
            response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('success', response.data)
        self.assertIn('analysis_id', response.data)
        self.assertIn('status', response.data)
        self.assertIn('document_id', response.data)
        self.assertIn('created_at', response.data)
        self.assertEqual(response.data['status'], 'pending')
        self.assertEqual(response.data['document_id'], self._test_document.pk)

    def test_analyze_checks_view_permissions(self):
        """Test analyze endpoint checks document view permission."""
        # Don't grant view permission - should fail
        # self._grant_view_access(self._test_document)  # Intentionally not called
        self._grant_analysis_access(self._test_document)

        url = '/api/dam/ai-analysis/analyze/'
        data = {'document_id': self._test_document.pk}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error_code'], 'PERMISSION_DENIED')

    def test_analyze_checks_analysis_permissions(self):
        """Test analyze endpoint checks document analysis permission."""
        self._grant_view_access(self._test_document)
        # Don't grant analysis permission - should fail
        # self._grant_analysis_access(self._test_document)  # Intentionally not called

        url = '/api/dam/ai-analysis/analyze/'
        data = {'document_id': self._test_document.pk}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error_code'], 'PERMISSION_DENIED')

    def test_analyze_document_not_found(self):
        """Test analyze endpoint returns 404 for non-existent document."""
        url = '/api/dam/ai-analysis/analyze/'
        data = {'document_id': 99999}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error_code'], 'NOT_FOUND')

    def test_analyze_unsupported_document_type(self):
        """Test analyze rejects unsupported document types."""
        self._grant_view_access(self._test_document)
        self._grant_analysis_access(self._test_document)

        # Mock unsupported MIME type
        with patch.object(self._test_document.latest_version.file, 'mimetype', 'application/unsupported'):
            url = '/api/dam/ai-analysis/analyze/'
            data = {'document_id': self._test_document.pk}

            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['error_code'], 'UNSUPPORTED_DOC_TYPE')

    def test_analyze_validation_error(self):
        """Test analyze endpoint handles validation errors."""
        self._grant_view_access(self._test_document)
        self._grant_analysis_access(self._test_document)

        url = '/api/dam/ai-analysis/analyze/'
        data = {
            'document_id': 'not_an_integer',
            'ai_service': 'invalid_service'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 'VALIDATION_ERROR')
        self.assertIn('details', response.data)

    def test_reanalyze_returns_202_accepted(self):
        """Test reanalyze endpoint returns 202 with proper structure."""
        analysis = self._create_test_analysis()
        self._grant_view_access(self._test_document)
        self._grant_analysis_access(self._test_document)

        url = '/api/dam/ai-analysis/reanalyze/'
        data = {'analysis_id': analysis.pk}

        with patch('mayan.apps.dam.api_views.analyze_document_with_ai.delay') as mock_task:
            mock_task.return_value.id = 'test-reanalysis-id'
            response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('success', response.data)
        self.assertIn('new_analysis_id', response.data)
        self.assertEqual(response.data['status'], 'pending')

    def test_reanalyze_checks_acl_critical_security(self):
        """CRITICAL: Test reanalyze checks ACL permissions (was missing!)."""
        analysis = self._create_test_analysis()
        self._grant_view_access(self._test_document)
        # Intentionally NOT granting analysis permission

        url = '/api/dam/ai-analysis/reanalyze/'
        data = {'analysis_id': analysis.pk}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error_code'], 'PERMISSION_DENIED')

    def test_reanalyze_analysis_not_found(self):
        """Test reanalyze returns 404 for non-existent analysis."""
        url = '/api/dam/ai-analysis/reanalyze/'
        data = {'analysis_id': 99999}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error_code'], 'NOT_FOUND')

    def test_reanalyze_missing_analysis_id(self):
        """Test reanalyze requires analysis_id parameter."""
        url = '/api/dam/ai-analysis/reanalyze/'
        data = {}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 'MISSING_PARAMETER')

    def test_reanalyze_rate_limiting(self):
        """Test reanalyze enforces rate limiting between analyses."""
        analysis = self._create_test_analysis()
        self._grant_view_access(self._test_document)
        self._grant_analysis_access(self._test_document)

        url = '/api/dam/ai-analysis/reanalyze/'
        data = {'analysis_id': analysis.pk}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(response.data['error_code'], 'RATE_LIMITED')

    def test_reanalyze_force_bypasses_rate_limit(self):
        """Test force parameter bypasses rate limiting."""
        analysis = self._create_test_analysis()
        self._grant_view_access(self._test_document)
        self._grant_analysis_access(self._test_document)

        url = '/api/dam/ai-analysis/reanalyze/'
        data = {'analysis_id': analysis.pk, 'force': True}

        with patch('mayan.apps.dam.api_views.analyze_document_with_ai.delay') as mock_task:
            mock_task.return_value.id = 'test-force-reanalysis-id'
            response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_error_responses_have_error_codes(self):
        """Test all error responses include error_code field."""
        # Test analyze with missing permissions
        url = '/api/dam/ai-analysis/analyze/'
        data = {'document_id': self._test_document.pk}

        response = self.client.post(url, data, format='json')
        self.assertIn('error_code', response.data)

        # Test reanalyze with invalid analysis_id
        url = '/api/dam/ai-analysis/reanalyze/'
        data = {'analysis_id': 'invalid'}

        response = self.client.post(url, data, format='json')
        self.assertIn('error_code', response.data)

    def test_analyze_logs_audit_trail(self):
        """Test analyze endpoint logs audit information."""
        self._grant_view_access(self._test_document)
        self._grant_analysis_access(self._test_document)

        url = '/api/dam/ai-analysis/analyze/'
        data = {
            'document_id': self._test_document.pk,
            'ai_service': 'openai',
            'analysis_type': 'classification'
        }

        with patch('mayan.apps.dam.api_views.analyze_document_with_ai.delay') as mock_task:
            mock_task.return_value.id = 'test-logging-id'
            with patch('mayan.apps.dam.api_views.logger') as mock_logger:
                response = self.client.post(url, data, format='json')

                # Verify logging was called
                mock_logger.info.assert_called()
                call_args = mock_logger.info.call_args
                self.assertIn('user_id', call_args.kwargs['extra'])
                self.assertIn('document_id', call_args.kwargs['extra'])
                self.assertIn('task_id', call_args.kwargs['extra'])
                self.assertEqual(call_args.kwargs['extra']['ai_service'], 'openai')

    def test_reanalyze_logs_audit_trail(self):
        """Test reanalyze endpoint logs audit information."""
        analysis = self._create_test_analysis()
        self._grant_view_access(self._test_document)
        self._grant_analysis_access(self._test_document)

        url = '/api/dam/ai-analysis/reanalyze/'
        data = {'analysis_id': analysis.pk}

        with patch('mayan.apps.dam.api_views.analyze_document_with_ai.delay') as mock_task:
            mock_task.return_value.id = 'test-reanalyze-logging-id'
            with patch('mayan.apps.dam.api_views.logger') as mock_logger:
                response = self.client.post(url, data, format='json')

                # Verify logging was called
                mock_logger.info.assert_called()
                call_args = mock_logger.info.call_args
                self.assertIn('user_id', call_args.kwargs['extra'])
                self.assertIn('previous_analysis_id', call_args.kwargs['extra'])
                self.assertIn('new_task_id', call_args.kwargs['extra'])

    def test_unauthorized_operations_logged_as_warnings(self):
        """Test unauthorized operations are logged as warnings."""
        # Test analyze without permission
        url = '/api/dam/ai-analysis/analyze/'
        data = {'document_id': self._test_document.pk}

        with patch('mayan.apps.dam.api_views.logger') as mock_logger:
            response = self.client.post(url, data, format='json')

            # Verify warning was logged
            mock_logger.warning.assert_called()
            call_args = mock_logger.warning.call_args
            self.assertIn('user_id', call_args.kwargs['extra'])

    def test_bulk_analyze_endpoint_exists(self):
        """Test bulk analyze endpoint exists and handles requests."""
        self._grant_view_access(self._test_document)
        self._grant_analysis_access(self._test_document)

        url = '/api/dam/ai-analysis/bulk-analyze/'
        data = {
            'document_ids': [self._test_document.pk],
            'ai_service': 'openai',
            'analysis_type': 'classification'
        }

        with patch('mayan.apps.dam.api_views.bulk_analyze_documents.delay') as mock_task:
            mock_task.return_value.id = 'test-bulk-id'
            response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('bulk_analysis_id', response.data)

    def test_helper_methods_work_correctly(self):
        """Test _is_analyzable and _can_reanalyze helper methods."""
        from mayan.apps.dam.api_views import DocumentAIAnalysisViewSet

        # Test _is_analyzable
        self.assertTrue(DocumentAIAnalysisViewSet._is_analyzable(self._test_document))

        # Mock unsupported type
        with patch.object(self._test_document.latest_version.file, 'mimetype', 'application/unsupported'):
            self.assertFalse(DocumentAIAnalysisViewSet._is_analyzable(self._test_document))

        # Test _can_reanalyze
        old_analysis = self._create_test_analysis()
        # Fresh analysis should not be reanalyzable immediately
        self.assertFalse(DocumentAIAnalysisViewSet._can_reanalyze(old_analysis))


















