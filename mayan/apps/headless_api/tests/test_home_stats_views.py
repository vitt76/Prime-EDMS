from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from mayan.apps.acls.classes import ModelPermission
from mayan.apps.documents.models import DocumentType, Document
from mayan.apps.documents.tests.mixins.document_mixins import DocumentTestMixin

from mayan.apps.organizations.models import Organization


@override_settings(DEPLOYMENT_MODE='saas')
class HomeStatsAPIViewTestCase(DocumentTestMixin, APITestCase):
    def setUp(self):
        super().setUp()
        
        # Create organizations
        self.org1 = Organization.objects.create(name='Org1', slug='org1', deployment_mode='saas')
        self.org2 = Organization.objects.create(name='Org2', slug='org2', deployment_mode='saas')
        
        # We need an admin user for the requests
        self._create_test_user()
        
        # Authenticate
        self.client.force_authenticate(user=self._test_user)
        
        # Headers for org isolation
        self.headers_org1 = {'HTTP_X_ORGANIZATION_ID': str(self.org1.id)}
        self.headers_org2 = {'HTTP_X_ORGANIZATION_ID': str(self.org2.id)}

    def test_documents_stats_tenant_isolation(self):
        # Create doc for org1 (assuming setup creates it properly with right org if we force it)
        # Actually standard test mixin might create with default org. We just update it.
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
