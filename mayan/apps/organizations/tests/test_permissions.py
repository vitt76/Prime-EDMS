"""
Tests for reusable DRF permission classes and X-Organization-Id header.

Sprint 3: Permission classes, middleware header resolution.
"""

from unittest.mock import MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory

from mayan.apps.organizations.models import (
    Organization, UserOrganizationRole
)
from mayan.apps.organizations.permission_classes import (
    IsOrganizationAdmin,
    IsOrganizationMember,
    IsOrganizationOwner,
    IsSuperAdminOrOrgAdmin,
)

User = get_user_model()


class PermissionClassesTestCase(TestCase):
    """Test reusable DRF permission classes."""

    def setUp(self):
        self.factory = RequestFactory()
        self.org = Organization.objects.create(
            name='Test Org',
            slug='test-org',
            email='test@example.com',
            is_active=True,
            status='active'
        )
        self.owner = User.objects.create_user(
            username='owner', password='pass123'
        )
        self.admin_user = User.objects.create_user(
            username='admin_user', password='pass123'
        )
        self.member = User.objects.create_user(
            username='member', password='pass123'
        )
        self.viewer = User.objects.create_user(
            username='viewer', password='pass123'
        )
        self.outsider = User.objects.create_user(
            username='outsider', password='pass123'
        )
        self.superadmin = User.objects.create_superuser(
            username='superadmin', password='pass123'
        )

        UserOrganizationRole.objects.create(
            user=self.owner, organization=self.org,
            role=UserOrganizationRole.ROLE_OWNER
        )
        UserOrganizationRole.objects.create(
            user=self.admin_user, organization=self.org,
            role=UserOrganizationRole.ROLE_ADMIN
        )
        UserOrganizationRole.objects.create(
            user=self.member, organization=self.org,
            role=UserOrganizationRole.ROLE_MEMBER
        )
        UserOrganizationRole.objects.create(
            user=self.viewer, organization=self.org,
            role=UserOrganizationRole.ROLE_VIEWER
        )

    def _make_request(self, user):
        request = self.factory.get('/test/')
        request.user = user
        request.organization = self.org
        return request

    # --- IsOrganizationMember ---
    def test_member_allows_owner(self):
        perm = IsOrganizationMember()
        request = self._make_request(self.owner)
        self.assertTrue(perm.has_permission(request, None))

    def test_member_allows_member(self):
        perm = IsOrganizationMember()
        request = self._make_request(self.member)
        self.assertTrue(perm.has_permission(request, None))

    def test_member_allows_viewer(self):
        perm = IsOrganizationMember()
        request = self._make_request(self.viewer)
        self.assertTrue(perm.has_permission(request, None))

    def test_member_denies_outsider(self):
        perm = IsOrganizationMember()
        request = self._make_request(self.outsider)
        self.assertFalse(perm.has_permission(request, None))

    def test_member_allows_superadmin(self):
        perm = IsOrganizationMember()
        request = self._make_request(self.superadmin)
        self.assertTrue(perm.has_permission(request, None))

    # --- IsOrganizationAdmin ---
    def test_admin_allows_owner(self):
        perm = IsOrganizationAdmin()
        request = self._make_request(self.owner)
        self.assertTrue(perm.has_permission(request, None))

    def test_admin_allows_admin(self):
        perm = IsOrganizationAdmin()
        request = self._make_request(self.admin_user)
        self.assertTrue(perm.has_permission(request, None))

    def test_admin_denies_member(self):
        perm = IsOrganizationAdmin()
        request = self._make_request(self.member)
        self.assertFalse(perm.has_permission(request, None))

    def test_admin_denies_viewer(self):
        perm = IsOrganizationAdmin()
        request = self._make_request(self.viewer)
        self.assertFalse(perm.has_permission(request, None))

    # --- IsOrganizationOwner ---
    def test_owner_allows_owner(self):
        perm = IsOrganizationOwner()
        request = self._make_request(self.owner)
        self.assertTrue(perm.has_permission(request, None))

    def test_owner_denies_admin(self):
        perm = IsOrganizationOwner()
        request = self._make_request(self.admin_user)
        self.assertFalse(perm.has_permission(request, None))

    # --- IsSuperAdminOrOrgAdmin ---
    def test_superadmin_or_org_admin_allows_superadmin(self):
        perm = IsSuperAdminOrOrgAdmin()
        request = self._make_request(self.superadmin)
        self.assertTrue(perm.has_permission(request, None))

    def test_superadmin_or_org_admin_allows_org_admin(self):
        perm = IsSuperAdminOrOrgAdmin()
        request = self._make_request(self.admin_user)
        self.assertTrue(perm.has_permission(request, None))

    def test_superadmin_or_org_admin_denies_member(self):
        perm = IsSuperAdminOrOrgAdmin()
        request = self._make_request(self.member)
        self.assertFalse(perm.has_permission(request, None))

    # --- Edge cases ---
    def test_no_organization_on_request(self):
        """Permission denied when request.organization is None."""
        perm = IsOrganizationMember()
        request = self.factory.get('/test/')
        request.user = self.member
        request.organization = None
        self.assertFalse(perm.has_permission(request, None))

    def test_unauthenticated_user(self):
        """Permission denied for anonymous user."""
        from django.contrib.auth.models import AnonymousUser
        perm = IsOrganizationMember()
        request = self.factory.get('/test/')
        request.user = AnonymousUser()
        request.organization = self.org
        self.assertFalse(perm.has_permission(request, None))


class XOrganizationIdHeaderTestCase(TestCase):
    """Test X-Organization-Id header resolution in middleware."""

    def setUp(self):
        self.org1 = Organization.objects.create(
            name='Org One', slug='org-one',
            email='one@example.com', is_active=True, status='active'
        )
        self.org2 = Organization.objects.create(
            name='Org Two', slug='org-two',
            email='two@example.com', is_active=True, status='active'
        )
        self.user = User.objects.create_user(
            username='testuser', password='pass123'
        )
        self.superadmin = User.objects.create_superuser(
            username='superadmin', password='pass123'
        )

        UserOrganizationRole.objects.create(
            user=self.user, organization=self.org1,
            role=UserOrganizationRole.ROLE_MEMBER
        )
        # user is NOT a member of org2

    def test_valid_header_resolves_org(self):
        """Valid X-Organization-Id header should resolve to correct org."""
        from mayan.apps.organizations.middleware import (
            TenantResolverMiddleware
        )

        middleware = TenantResolverMiddleware(lambda r: None)
        factory = RequestFactory()
        request = factory.get(
            '/test/',
            HTTP_X_ORGANIZATION_ID=str(self.org1.pk)
        )
        request.user = self.user

        result = middleware._resolve_by_header(request)
        self.assertEqual(result, self.org1)

    def test_non_member_header_returns_none(self):
        """X-Organization-Id for org user is NOT a member of returns None."""
        from mayan.apps.organizations.middleware import (
            TenantResolverMiddleware
        )

        middleware = TenantResolverMiddleware(lambda r: None)
        factory = RequestFactory()
        request = factory.get(
            '/test/',
            HTTP_X_ORGANIZATION_ID=str(self.org2.pk)
        )
        request.user = self.user

        result = middleware._resolve_by_header(request)
        self.assertIsNone(result)

    def test_superadmin_can_access_any_org(self):
        """Superadmin can use X-Organization-Id for any org."""
        from mayan.apps.organizations.middleware import (
            TenantResolverMiddleware
        )

        middleware = TenantResolverMiddleware(lambda r: None)
        factory = RequestFactory()
        request = factory.get(
            '/test/',
            HTTP_X_ORGANIZATION_ID=str(self.org2.pk)
        )
        request.user = self.superadmin

        result = middleware._resolve_by_header(request)
        self.assertEqual(result, self.org2)

    def test_invalid_org_id_returns_none(self):
        """Invalid X-Organization-Id returns None."""
        from mayan.apps.organizations.middleware import (
            TenantResolverMiddleware
        )

        middleware = TenantResolverMiddleware(lambda r: None)
        factory = RequestFactory()
        request = factory.get(
            '/test/',
            HTTP_X_ORGANIZATION_ID='00000000-0000-0000-0000-000000000000'
        )
        request.user = self.user

        result = middleware._resolve_by_header(request)
        self.assertIsNone(result)
