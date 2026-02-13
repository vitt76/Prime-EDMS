"""Tests for AssetEventTrackingMiddleware (tenant-aware tracking)."""

from unittest.mock import MagicMock, patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from mayan.apps.analytics.middleware import AssetEventTrackingMiddleware


class AssetEventTrackingMiddlewareTestCase(TestCase):
    """Test that tracking middleware calls track_asset_event_async.delay with organization_id."""

    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.middleware = AssetEventTrackingMiddleware(get_response=lambda r: HttpResponse(status=200))

    @patch('mayan.apps.analytics.middleware.track_asset_event_async')
    def test_process_response_calls_task_with_organization_id(self, mock_task):
        org_id = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
        request = self.factory.get('/api/v4/documents/42/')
        request.organization = MagicMock(pk=org_id)
        request.user = MagicMock(is_authenticated=True, pk=10)
        request.resolver_match = MagicMock(kwargs={'document_id': 42})
        response = HttpResponse(status=200)

        result = self.middleware.process_response(request, response)

        self.assertEqual(result.status_code, 200)
        mock_task.delay.assert_called_once()
        call_kwargs = mock_task.delay.call_args[1]
        self.assertEqual(call_kwargs.get('organization_id'), org_id)
        self.assertEqual(call_kwargs.get('document_id'), 42)
        self.assertEqual(call_kwargs.get('event_type'), 'view')

    @patch('mayan.apps.analytics.middleware.track_asset_event_async')
    def test_process_response_no_track_without_organization(self, mock_task):
        request = self.factory.get('/api/v4/documents/42/')
        request.organization = None
        request.resolver_match = MagicMock(kwargs={'document_id': 42})
        response = HttpResponse(status=200)

        self.middleware.process_response(request, response)

        mock_task.delay.assert_not_called()

    @patch('mayan.apps.analytics.middleware.track_asset_event_async')
    def test_process_response_no_track_on_4xx(self, mock_task):
        request = self.factory.get('/api/v4/documents/42/')
        request.organization = MagicMock(pk='aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee')
        request.resolver_match = MagicMock(kwargs={'document_id': 42})
        response = HttpResponse(status=404)

        self.middleware.process_response(request, response)

        mock_task.delay.assert_not_called()
