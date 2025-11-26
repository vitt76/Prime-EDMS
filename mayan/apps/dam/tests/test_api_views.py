import copy
from unittest.mock import patch

from django.core.cache import cache
from django.test.utils import override_settings
from django.conf import settings

from rest_framework import status

from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.tests.mixins.document_mixins import DocumentTestMixin
from mayan.apps.rest_api.tests.base import BaseAPITestCase

from ..api_views import GENERIC_AI_ERROR_MESSAGE


class DocumentAIAnalysisAPIViewTestMixin:
    def _request_ai_analysis_analyze_view(self):
        return self.post(
            viewname='dam:ai-analysis-analyze',
            data={'document_id': self._test_document.pk}
        )

    def _request_ai_analysis_bulk_analyze_view(self, document_ids):
        return self.post(
            viewname='dam:ai-analysis-bulk-analyze',
            data={'document_ids': document_ids}
        )


class DocumentAIAnalysisAPIViewTestCase(
    DocumentAIAnalysisAPIViewTestMixin, DocumentTestMixin, BaseAPITestCase
):
    def setUp(self):
        super().setUp()
        cache.clear()

    def test_ai_analysis_analyze_view_throttled(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_view
        )

        rest_settings = copy.deepcopy(settings.REST_FRAMEWORK)
        rest_settings['DEFAULT_THROTTLE_RATES'] = {
            **rest_settings.get('DEFAULT_THROTTLE_RATES', {}),
            'anon': '100/day',
            'user': '100/day',
            'ai_analysis': '1/hour'
        }

        with override_settings(REST_FRAMEWORK=rest_settings):
            with patch('mayan.apps.dam.api_views.analyze_document_with_ai.delay'):
                first_response = self._request_ai_analysis_analyze_view()
                self.assertEqual(first_response.status_code, status.HTTP_200_OK)

                throttled_response = self._request_ai_analysis_analyze_view()
                self.assertEqual(throttled_response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_ai_analysis_analyze_view_masks_internal_errors(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_view
        )

        with patch(
            'mayan.apps.dam.api_views.analyze_document_with_ai.delay',
            side_effect=Exception('sensitive failure')
        ):
            response = self._request_ai_analysis_analyze_view()

        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        self.assertEqual(response.data['error'], GENERIC_AI_ERROR_MESSAGE)

    def test_bulk_analyze_rejects_payload_over_limit(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_view
        )

        document_ids = [self._test_document.pk] * 101

        with patch('mayan.apps.dam.api_views.bulk_analyze_documents.delay') as mock_task:
            response = self._request_ai_analysis_bulk_analyze_view(
                document_ids=document_ids
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Maximum of', response.data['document_ids'][0])
        mock_task.assert_not_called()

    def test_bulk_analyze_masks_internal_errors(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_view
        )

        with patch(
            'mayan.apps.dam.api_views.bulk_analyze_documents.delay',
            side_effect=Exception('unexpected failure')
        ):
            response = self._request_ai_analysis_bulk_analyze_view(
                document_ids=[self._test_document.pk]
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        self.assertEqual(response.data['error'], GENERIC_AI_ERROR_MESSAGE)

