"""
Tests for HeadlessTaskStatusView.
"""
from unittest.mock import Mock, patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from mayan.apps.documents.tests.base import GenericDocumentViewTestCase


class HeadlessTaskStatusViewTestCase(GenericDocumentViewTestCase):
    """Test cases for HeadlessTaskStatusView."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self._test_case_user)
        self.task_id = 'test-task-id-123'

    @patch('mayan.apps.headless_api.views.task_status_views.AsyncResult')
    def test_get_pending_status(self, mock_async_result):
        """Test GET returns PENDING status correctly."""
        mock_result = Mock()
        mock_result.state = 'PENDING'
        mock_async_result.return_value = mock_result

        response = self.client.get(
            f'/api/v4/headless/tasks/{self.task_id}/status/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'PENDING')
        self.assertEqual(response.data['task_id'], self.task_id)
        self.assertIn('message', response.data)

    @patch('mayan.apps.headless_api.views.task_status_views.AsyncResult')
    def test_get_started_status(self, mock_async_result):
        """Test GET returns STARTED status correctly."""
        mock_result = Mock()
        mock_result.state = 'STARTED'
        mock_async_result.return_value = mock_result

        response = self.client.get(
            f'/api/v4/headless/tasks/{self.task_id}/status/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'STARTED')
        self.assertIn('message', response.data)

    @patch('mayan.apps.headless_api.views.task_status_views.AsyncResult')
    def test_get_success_status(self, mock_async_result):
        """Test GET returns SUCCESS status with result."""
        mock_result = Mock()
        mock_result.state = 'SUCCESS'
        mock_result.result = {
            'success': True,
            'document_id': 1,
            'file_id': 2,
            'version_id': 3
        }
        mock_async_result.return_value = mock_result

        response = self.client.get(
            f'/api/v4/headless/tasks/{self.task_id}/status/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'SUCCESS')
        self.assertIn('result', response.data)
        self.assertEqual(response.data['result']['success'], True)
        self.assertIn('message', response.data)

    @patch('mayan.apps.headless_api.views.task_status_views.AsyncResult')
    def test_get_failure_status(self, mock_async_result):
        """Test GET returns FAILURE status with error."""
        mock_result = Mock()
        mock_result.state = 'FAILURE'
        mock_result.info = Exception('Task failed')
        mock_async_result.return_value = mock_result

        response = self.client.get(
            f'/api/v4/headless/tasks/{self.task_id}/status/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'FAILURE')
        self.assertIn('error', response.data)
        self.assertIn('message', response.data)

    @patch('mayan.apps.headless_api.views.task_status_views.AsyncResult')
    def test_get_failure_status_with_dict_error(self, mock_async_result):
        """Test GET returns FAILURE status with dict error info."""
        mock_result = Mock()
        mock_result.state = 'FAILURE'
        mock_result.info = {'error': 'Custom error message'}
        mock_async_result.return_value = mock_result

        response = self.client.get(
            f'/api/v4/headless/tasks/{self.task_id}/status/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'FAILURE')
        self.assertIn('error', response.data)

    @patch('mayan.apps.headless_api.views.task_status_views.AsyncResult')
    def test_get_revoked_status(self, mock_async_result):
        """Test GET returns REVOKED status correctly."""
        mock_result = Mock()
        mock_result.state = 'REVOKED'
        mock_async_result.return_value = mock_result

        response = self.client.get(
            f'/api/v4/headless/tasks/{self.task_id}/status/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'REVOKED')
        self.assertIn('error', response.data)
        self.assertIn('message', response.data)

    @patch('mayan.apps.headless_api.views.task_status_views.AsyncResult')
    def test_get_invalid_task_id(self, mock_async_result):
        """Test GET returns 400 for invalid task_id."""
        mock_async_result.side_effect = Exception('Invalid task ID')

        response = self.client.get(
            f'/api/v4/headless/tasks/invalid-task-id/status/'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'invalid_task_id')

