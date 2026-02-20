"""
Sprint 1 Discovery UX: Tenant isolation for saved-searches and recently-viewed.
GET list/create/run require organization context (X-Organization-Id); returns 400 without.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from mayan.apps.documents.models import Document, DocumentType
from mayan.apps.organizations.models import Organization, UserOrganizationRole
from mayan.apps.saved_searches.models import SavedSearch

User = get_user_model()


class SavedSearchesTenantIsolationTestCase(TestCase):
    """Saved searches API requires organization and returns only current user's in that org."""

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

    def test_list_returns_400_without_organization(self):
        """GET saved-searches/ without X-Organization-Id returns 400."""
        response = self.client.get('/api/v4/headless/saved-searches/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertIn('detail', response.data)

    def test_list_returns_200_with_organization(self):
        """GET saved-searches/ with X-Organization-Id returns 200 and user's list."""
        SavedSearch.objects.create(
            user=self.user,
            organization=self.org,
            name='My search',
            query='test',
            filters={},
        )
        response = self.client.get(
            '/api/v4/headless/saved-searches/',
            HTTP_X_ORGANIZATION_ID=str(self.org.pk),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'My search')

    def test_post_returns_400_without_organization(self):
        """POST saved-searches/ without organization returns 400."""
        response = self.client.post(
            '/api/v4/headless/saved-searches/',
            {'name': 'New', 'query': '', 'filters': {}},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)


class RecentlyViewedTenantIsolationTestCase(TestCase):
    """Recently-viewed API requires organization context."""

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

    def test_returns_400_without_organization(self):
        """GET recently-viewed/ without X-Organization-Id returns 400."""
        response = self.client.get('/api/v4/headless/documents/recently-viewed/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertIn('detail', response.data)

    def test_returns_200_with_organization(self):
        """GET recently-viewed/ with X-Organization-Id returns 200 (results may be empty)."""
        response = self.client.get(
            '/api/v4/headless/documents/recently-viewed/',
            HTTP_X_ORGANIZATION_ID=str(self.org.pk),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
