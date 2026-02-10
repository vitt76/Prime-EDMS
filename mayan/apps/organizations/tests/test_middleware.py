"""
Tests for TenantResolverMiddleware.

Tests cover:
- Exempt path bypassing
- Custom domain resolution
- Subdomain resolution
- User-based resolution
- Default organization fallback (standalone mode)
- Blocked access for suspended/archived organizations
"""

from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory, override_settings

from ..managers import get_current_organization
from ..middleware import TenantResolverMiddleware
from ..models import (
    DomainSettings, Organization, UserOrganizationRole
)

User = get_user_model()


def dummy_get_response(request):
    """Dummy get_response for middleware testing."""
    from django.http import HttpResponse
    return HttpResponse('OK')


class TenantResolverMiddlewareExemptPathsTestCase(TestCase):
    """Tests for path exemption."""

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = TenantResolverMiddleware(dummy_get_response)

    def test_health_check_exempt(self):
        """Health check path bypasses tenant resolution."""
        request = self.factory.get('/health/')
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(request.organization)

    def test_static_path_exempt(self):
        """Static files path bypasses tenant resolution."""
        request = self.factory.get('/static/css/style.css')
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(request.organization)

    def test_favicon_exempt(self):
        """Favicon path bypasses tenant resolution."""
        request = self.factory.get('/favicon.ico')
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(request.organization)


class TenantResolverMiddlewareStandaloneTestCase(TestCase):
    """Tests for standalone deployment mode."""

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = TenantResolverMiddleware(dummy_get_response)

    @patch('mayan.apps.organizations.middleware.DEPLOYMENT_MODE', 'STANDALONE')
    def test_standalone_creates_default_org(self):
        """Standalone mode creates and returns default organization."""
        request = self.factory.get('/api/v4/documents/')
        request.user = MagicMock(is_authenticated=False)

        response = self.middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(request.organization)
        self.assertEqual(request.organization.slug, 'default')
        self.assertEqual(request.organization.deployment_mode, 'standalone')

    @patch('mayan.apps.organizations.middleware.DEPLOYMENT_MODE', 'STANDALONE')
    def test_standalone_reuses_default_org(self):
        """Standalone mode reuses existing default organization."""
        # Create default org first
        default_org = Organization.objects.create(
            name='Default Organization',
            slug='default',
            email='admin@localhost',
            is_active=True,
            status='active',
            deployment_mode='standalone'
        )

        request = self.factory.get('/api/v4/documents/')
        request.user = MagicMock(is_authenticated=False)

        response = self.middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(request.organization.id, default_org.id)


class TenantResolverMiddlewareSaaSTestCase(TestCase):
    """Tests for SaaS deployment mode."""

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = TenantResolverMiddleware(dummy_get_response)
        self.org = Organization.objects.create(
            name='SaaS Org',
            slug='saas-org',
            email='admin@saas.com',
            is_active=True,
            status='active'
        )

    @patch('mayan.apps.organizations.middleware.DEPLOYMENT_MODE', 'SAAS')
    @patch('mayan.apps.organizations.middleware.SAAS_BASE_DOMAIN', 'dam-brand.com')
    def test_subdomain_resolution(self):
        """SaaS mode resolves organization by subdomain."""
        request = self.factory.get(
            '/api/v4/documents/',
            HTTP_HOST='saas-org.dam-brand.com'
        )
        request.user = MagicMock(is_authenticated=False)

        response = self.middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(request.organization, self.org)

    @patch('mayan.apps.organizations.middleware.DEPLOYMENT_MODE', 'SAAS')
    @patch('mayan.apps.organizations.middleware.SAAS_BASE_DOMAIN', 'dam-brand.com')
    def test_custom_domain_resolution(self):
        """SaaS mode resolves organization by custom domain."""
        DomainSettings.objects.create(
            organization=self.org,
            custom_domain='dam.company.com',
            is_verified=True
        )

        request = self.factory.get(
            '/api/v4/documents/',
            HTTP_HOST='dam.company.com'
        )
        request.user = MagicMock(is_authenticated=False)

        response = self.middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(request.organization, self.org)

    @patch('mayan.apps.organizations.middleware.DEPLOYMENT_MODE', 'SAAS')
    @patch('mayan.apps.organizations.middleware.SAAS_BASE_DOMAIN', 'dam-brand.com')
    def test_unverified_domain_not_resolved(self):
        """Unverified custom domains are not resolved."""
        DomainSettings.objects.create(
            organization=self.org,
            custom_domain='unverified.company.com',
            is_verified=False
        )

        request = self.factory.get(
            '/api/v4/documents/',
            HTTP_HOST='unverified.company.com'
        )
        request.user = MagicMock(is_authenticated=False)

        response = self.middleware(request)

        # Should fall through to default org, not the unverified domain
        self.assertNotEqual(
            getattr(request, 'organization', None),
            self.org
        )

    @patch('mayan.apps.organizations.middleware.DEPLOYMENT_MODE', 'SAAS')
    @patch('mayan.apps.organizations.middleware.SAAS_BASE_DOMAIN', 'dam-brand.com')
    def test_user_based_resolution(self):
        """SaaS mode resolves organization by authenticated user."""
        user = User.objects.create_user(
            username='saasuser', password='testpass123'
        )
        UserOrganizationRole.objects.create(
            user=user,
            organization=self.org,
            role='member',
            is_default=True
        )

        request = self.factory.get(
            '/api/v4/documents/',
            HTTP_HOST='unknown.domain.com'
        )
        request.user = user

        response = self.middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(request.organization, self.org)


class TenantResolverMiddlewareAccessControlTestCase(TestCase):
    """Tests for organization access control."""

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = TenantResolverMiddleware(dummy_get_response)

    @patch('mayan.apps.organizations.middleware.DEPLOYMENT_MODE', 'SAAS')
    @patch('mayan.apps.organizations.middleware.SAAS_BASE_DOMAIN', 'dam-brand.com')
    def test_suspended_org_returns_403(self):
        """Suspended organization returns HTTP 403."""
        org = Organization.objects.create(
            name='Suspended Org',
            slug='suspended-org',
            email='admin@suspended.com',
            is_active=True,
            status='suspended'
        )

        request = self.factory.get(
            '/api/v4/documents/',
            HTTP_HOST='suspended-org.dam-brand.com'
        )
        request.user = MagicMock(is_authenticated=False)

        response = self.middleware(request)

        self.assertEqual(response.status_code, 403)

    @patch('mayan.apps.organizations.middleware.DEPLOYMENT_MODE', 'SAAS')
    @patch('mayan.apps.organizations.middleware.SAAS_BASE_DOMAIN', 'dam-brand.com')
    def test_inactive_org_returns_403(self):
        """Inactive organization returns HTTP 403."""
        org = Organization.objects.create(
            name='Inactive Org',
            slug='inactive-org',
            email='admin@inactive.com',
            is_active=False,
            status='active'
        )

        request = self.factory.get(
            '/api/v4/documents/',
            HTTP_HOST='inactive-org.dam-brand.com'
        )
        request.user = MagicMock(is_authenticated=False)

        response = self.middleware(request)

        self.assertEqual(response.status_code, 403)

    @patch('mayan.apps.organizations.middleware.DEPLOYMENT_MODE', 'SAAS')
    @patch('mayan.apps.organizations.middleware.SAAS_BASE_DOMAIN', 'dam-brand.com')
    def test_archived_org_returns_403(self):
        """Archived organization returns HTTP 403."""
        org = Organization.objects.create(
            name='Archived Org',
            slug='archived-org',
            email='admin@archived.com',
            is_active=True,
            status='archived'
        )

        request = self.factory.get(
            '/api/v4/documents/',
            HTTP_HOST='archived-org.dam-brand.com'
        )
        request.user = MagicMock(is_authenticated=False)

        response = self.middleware(request)

        self.assertEqual(response.status_code, 403)

    @patch('mayan.apps.organizations.middleware.DEPLOYMENT_MODE', 'SAAS')
    @patch('mayan.apps.organizations.middleware.SAAS_BASE_DOMAIN', 'dam-brand.com')
    def test_context_cleaned_up_after_request(self):
        """ContextVar is cleaned up after request processing."""
        org = Organization.objects.create(
            name='Context Org',
            slug='context-org',
            email='admin@context.com',
            is_active=True,
            status='active'
        )

        request = self.factory.get(
            '/api/v4/documents/',
            HTTP_HOST='context-org.dam-brand.com'
        )
        request.user = MagicMock(is_authenticated=False)

        self.middleware(request)

        # After request, context should be cleared
        self.assertIsNone(get_current_organization())

    @patch('mayan.apps.organizations.middleware.DEPLOYMENT_MODE', 'SAAS')
    @patch('mayan.apps.organizations.middleware.SAAS_BASE_DOMAIN', 'dam-brand.com')
    def test_context_cleaned_up_on_error(self):
        """ContextVar is cleaned up even when view raises exception."""
        def error_response(request):
            raise ValueError('Test error')

        middleware = TenantResolverMiddleware(error_response)

        org = Organization.objects.create(
            name='Error Org',
            slug='error-org',
            email='admin@error.com',
            is_active=True,
            status='active'
        )

        request = self.factory.get(
            '/api/v4/documents/',
            HTTP_HOST='error-org.dam-brand.com'
        )
        request.user = MagicMock(is_authenticated=False)

        with self.assertRaises(ValueError):
            middleware(request)

        # Context should still be cleaned up
        self.assertIsNone(get_current_organization())
