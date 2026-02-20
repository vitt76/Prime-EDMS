"""
Sprint 2 Productivity & UX: Tenant isolation for headless favorites API.

GET list and POST toggle require organization context (X-Organization-Id);
returns 400 without. Toggle returns 403 when document belongs to another org.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from mayan.apps.documents.models import Document, DocumentType, FavoriteDocument
from mayan.apps.organizations.models import Organization, UserOrganizationRole

User = get_user_model()


class HeadlessFavoritesTenantIsolationTestCase(TestCase):
    """Headless favorites API requires organization and isolates by tenant."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.org = Organization.objects.create(
            name='Test Org',
            slug='test-org',
            email='test@example.com',
            is_active=True,
            status='active',
        )
        self.user = User.objects.create_user(username='user1', password='testpass123')
        UserOrganizationRole.objects.create(
            user=self.user,
            organization=self.org,
            role=UserOrganizationRole.ROLE_MEMBER,
        )
        self.client.force_authenticate(user=self.user)
        self.document_type = DocumentType.objects.create(label='Test Type')
        self.document = Document.objects.create(
            document_type=self.document_type,
            label='Test Doc',
        )
        if hasattr(Document, 'organization_id'):
            self.document.organization_id = self.org.pk
            self.document.save(update_fields=['organization_id'])

    def test_list_returns_400_without_organization(self):
        """GET headless/favorites/ without X-Organization-Id returns 400."""
        response = self.client.get('/api/v4/headless/favorites/')
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.data
        )
        self.assertIn('detail', response.data)

    def test_list_returns_200_with_organization(self):
        """GET headless/favorites/ with X-Organization-Id returns 200."""
        response = self.client.get(
            '/api/v4/headless/favorites/',
            HTTP_X_ORGANIZATION_ID=str(self.org.pk),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)

    def test_toggle_returns_400_without_organization(self):
        """POST headless/favorites/<id>/ without organization returns 400."""
        response = self.client.post(
            '/api/v4/headless/favorites/{}/'.format(self.document.pk),
        )
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.data
        )
        self.assertIn('detail', response.data)

    def test_toggle_returns_200_with_organization(self):
        """POST headless/favorites/<id>/ with organization toggles favorite."""
        response = self.client.post(
            '/api/v4/headless/favorites/{}/'.format(self.document.pk),
            HTTP_X_ORGANIZATION_ID=str(self.org.pk),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIn('favorited', response.data)
        self.assertTrue(response.data['favorited'])
        self.assertTrue(
            FavoriteDocument.objects.filter(
                user=self.user, document=self.document
            ).exists()
        )

    def test_toggle_returns_403_for_document_from_other_org(self):
        """POST toggle for document in another org returns 403 when Document has organization."""
        if not hasattr(Document, 'organization_id'):
            self.skipTest('Document has no organization_id (organizations patch not applied)')
        other_org = Organization.objects.create(
            name='Other Org',
            slug='other-org',
            email='other@example.com',
            is_active=True,
            status='active',
        )
        doc_other = Document.objects.create(
            document_type=self.document_type,
            label='Doc Other Org',
        )
        doc_other.organization_id = other_org.pk
        doc_other.save(update_fields=['organization_id'])
        response = self.client.post(
            '/api/v4/headless/favorites/{}/'.format(doc_other.pk),
            HTTP_X_ORGANIZATION_ID=str(self.org.pk),
        )
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN, response.data
        )
        self.assertFalse(
            FavoriteDocument.objects.filter(
                user=self.user, document=doc_other
            ).exists()
        )
