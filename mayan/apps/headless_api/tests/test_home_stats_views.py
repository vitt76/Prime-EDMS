from rest_framework import status
from rest_framework.test import APITestCase

from mayan.apps.analytics.models import AssetEvent
from mayan.apps.documents.models import Document
from mayan.apps.documents.tests.mixins.document_mixins import DocumentTestMixin
from mayan.apps.organizations.tests.mixins import SaaSTenantTestHarnessMixin


class HomeStatsAPIViewTestCase(
    SaaSTenantTestHarnessMixin, DocumentTestMixin, APITestCase
):
    def setUp(self):
        super().setUp()

        # Create organizations
        self.org1 = self.create_organization(name='Org1', slug='org1')
        self.org2 = self.create_organization(name='Org2', slug='org2')

        # We need an admin user for the requests
        self.user = self.create_user_in_organization(
            username='home-stats-admin',
            organization=self.org1,
            is_default=True,
            is_superuser=True,
        )
        self.add_user_to_organization(
            user=self.user,
            organization=self.org2,
            is_default=False,
        )

        # Authenticate
        self.client = self.api_client_for(self.user)

        # Headers for org isolation
        self.headers_org1 = {'HTTP_X_ORGANIZATION_ID': str(self.org1.id)}
        self.headers_org2 = {'HTTP_X_ORGANIZATION_ID': str(self.org2.id)}

    def test_documents_stats_tenant_isolation(self):
        self._create_test_document_stub()
        doc = Document.objects.first()
        doc.organization = self.org1
        doc.save()

        # Query org1
        response = self.client.get('/api/v4/headless/documents/stats/', **self.headers_org1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 1)

        # Query org2
        response = self.client.get('/api/v4/headless/documents/stats/', **self.headers_org2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 0)

    def test_ai_stats_tenant_isolation(self):
        response = self.client.get('/api/v4/headless/documents/ai-stats/', **self.headers_org1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('analyzed', response.data)
        self.assertIn('queued', response.data)

    def test_inbox_stats_endpoint(self):
        response = self.client.get('/api/v4/headless/user/inbox-stats/', **self.headers_org1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('unread_total', response.data)

    def test_analytics_geography_route_is_exposed_in_live_api(self):
        self._create_test_document_stub()
        doc = Document.objects.first()
        doc.organization = self.org1
        doc.save()
        AssetEvent.objects.create(
            organization=self.org1,
            document=doc,
            event_type=AssetEvent.EVENT_TYPE_VIEW,
            metadata={'country': 'RU'},
        )

        response = self.client.get(
            '/api/v4/headless/analytics/dashboard/geography/',
            **self.headers_org1
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(
            response.data['results'],
            [{'country_code': 'RU', 'event_count': 1}]
        )

    def test_analytics_geography_requires_organization_context(self):
        response = self.client.get(
            '/api/v4/headless/analytics/dashboard/geography/'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_legacy_analytics_asset_bank_requires_organization_context(self):
        response = self.client.get(
            '/api/v4/headless/analytics/dashboard/assets/top-metrics/'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
