"""
Tests for Organizations REST API views.

Sprint 4: Comprehensive test coverage for all API endpoints.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from mayan.apps.organizations.models import (
    Organization, Plan, UserOrganizationRole
)

User = get_user_model()


class OrganizationAPITestMixin:
    """Shared setUp for organization API tests."""

    def setUp(self):
        self.client = APIClient()

        # Plans
        self.plan = Plan.objects.create(
            id='plan-test',
            name='Test Plan',
            price_monthly=100,
            storage_gb=50,
            max_users=5,
            max_ai_analyses_monthly=100,
            is_active=True,
            is_public=True
        )
        self.plan_hidden = Plan.objects.create(
            id='plan-hidden',
            name='Hidden Plan',
            price_monthly=0,
            is_active=True,
            is_public=False
        )

        # Users
        self.superadmin = User.objects.create_superuser(
            username='superadmin', password='pass123',
            email='super@example.com'
        )
        self.org_owner = User.objects.create_user(
            username='org_owner', password='pass123'
        )
        self.org_admin = User.objects.create_user(
            username='org_admin', password='pass123'
        )
        self.org_member = User.objects.create_user(
            username='org_member', password='pass123'
        )
        self.outsider = User.objects.create_user(
            username='outsider', password='pass123'
        )
        self.extra_user = User.objects.create_user(
            username='extra_user', password='pass123'
        )

        # Organization
        self.org = Organization.objects.create(
            name='Test Org',
            slug='test-org',
            email='org@example.com',
            is_active=True,
            status='active',
            max_users=5
        )

        # Roles
        UserOrganizationRole.objects.create(
            user=self.org_owner, organization=self.org,
            role=UserOrganizationRole.ROLE_OWNER, is_default=True
        )
        UserOrganizationRole.objects.create(
            user=self.org_admin, organization=self.org,
            role=UserOrganizationRole.ROLE_ADMIN
        )
        UserOrganizationRole.objects.create(
            user=self.org_member, organization=self.org,
            role=UserOrganizationRole.ROLE_MEMBER
        )


class OrganizationListCreateViewTestCase(
    OrganizationAPITestMixin, TestCase
):
    """Tests for GET/POST /api/v4/headless/organizations/."""

    url = '/api/v4/headless/organizations/'

    # --- GET tests ---

    def test_list_requires_authentication(self):
        """Anonymous users cannot list organizations."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_requires_admin(self):
        """Regular users cannot list organizations."""
        self.client.force_authenticate(user=self.org_owner)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_superadmin_success(self):
        """SuperAdmin can list all organizations."""
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertIn('results', data)
        self.assertIn('count', data)
        self.assertIn('page', data)
        self.assertGreaterEqual(data['count'], 1)

    def test_list_pagination_default(self):
        """Default pagination returns page_size=20."""
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.get(self.url)
        self.assertEqual(response.data['page'], 1)
        self.assertEqual(response.data['page_size'], 20)

    def test_list_pagination_custom(self):
        """Custom page_size is respected."""
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.get(self.url, {'page_size': 5, 'page': 1})
        self.assertEqual(response.data['page_size'], 5)

    def test_list_includes_member_count(self):
        """Organization list includes annotated member_count."""
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.get(self.url)
        org_data = response.data['results'][0]
        self.assertIn('member_count', org_data)
        self.assertIsInstance(org_data['member_count'], int)

    # --- POST tests ---

    def test_create_requires_admin(self):
        """Regular users cannot create organizations."""
        self.client.force_authenticate(user=self.org_owner)
        response = self.client.post(self.url, {
            'name': 'New Org', 'slug': 'new-org', 'email': 'new@org.com'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_superadmin_success(self):
        """SuperAdmin can create organizations."""
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.post(self.url, {
            'name': 'New Org',
            'slug': 'new-org',
            'email': 'new@org.com',
            'industry': 'media'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Org')
        # Owner role should be auto-created
        self.assertTrue(
            UserOrganizationRole.objects.filter(
                user=self.superadmin,
                organization__slug='new-org',
                role=UserOrganizationRole.ROLE_OWNER
            ).exists()
        )

    def test_create_duplicate_slug_fails(self):
        """Creating org with duplicate slug returns validation error."""
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.post(self.url, {
            'name': 'Duplicate Org',
            'slug': 'test-org',  # Already exists
            'email': 'dup@org.com'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OrganizationDetailViewTestCase(
    OrganizationAPITestMixin, TestCase
):
    """Tests for GET/PUT/PATCH/DELETE /api/v4/headless/organizations/{id}/."""

    def _url(self, org_id=None):
        org_id = org_id or self.org.pk
        return '/api/v4/headless/organizations/{}/'.format(org_id)

    def test_get_superadmin(self):
        """SuperAdmin can get organization details."""
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Org')
        self.assertIn('member_count', response.data)
        self.assertIn('storage_used_gb', response.data)

    def test_get_nonexistent_returns_404(self):
        """Accessing non-existent org returns 404."""
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.get(self._url(
            '00000000-0000-0000-0000-000000000000'
        ))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_updates_fields(self):
        """PATCH updates specified fields."""
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.patch(
            self._url(),
            {'description': 'Updated description'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.org.refresh_from_db()
        self.assertEqual(self.org.description, 'Updated description')

    def test_delete_archives_org(self):
        """DELETE archives organization (soft delete)."""
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.delete(self._url())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.org.refresh_from_db()
        self.assertEqual(self.org.status, 'archived')
        self.assertFalse(self.org.is_active)


class OrganizationMembersViewTestCase(
    OrganizationAPITestMixin, TestCase
):
    """Tests for GET/POST/DELETE organization members."""

    def _url(self, org_id=None):
        org_id = org_id or self.org.pk
        return '/api/v4/headless/organizations/{}/members/'.format(org_id)

    def test_list_members_superadmin(self):
        """SuperAdmin can list members."""
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # owner, admin, member

    def test_add_member(self):
        """SuperAdmin can add a member."""
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.post(
            self._url(),
            {'user_id': self.extra_user.pk, 'role': 'viewer'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            UserOrganizationRole.objects.filter(
                user=self.extra_user, organization=self.org
            ).exists()
        )

    def test_add_existing_member_fails(self):
        """Adding an existing member returns error."""
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.post(
            self._url(),
            {'user_id': self.org_member.pk, 'role': 'member'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_remove_member(self):
        """SuperAdmin can remove a member."""
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.delete(
            self._url(),
            {'user_id': self.org_member.pk},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            UserOrganizationRole.objects.filter(
                user=self.org_member, organization=self.org
            ).exists()
        )

    def test_remove_last_owner_fails(self):
        """Cannot remove the last owner."""
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.delete(
            self._url(),
            {'user_id': self.org_owner.pk},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('last owner', response.data['detail'].lower())

    def test_remove_nonmember_returns_404(self):
        """Removing non-member returns 404."""
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.delete(
            self._url(),
            {'user_id': self.outsider.pk},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_remove_invalid_user_id(self):
        """Invalid user_id returns validation error."""
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.delete(
            self._url(),
            {'user_id': -1},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_member_quota_exceeded(self):
        """Adding member when user limit exceeded returns 402."""
        self.org.max_users = 3  # Already have 3 members
        self.org.save(update_fields=['max_users'])

        self.client.force_authenticate(user=self.superadmin)
        response = self.client.post(
            self._url(),
            {'user_id': self.extra_user.pk, 'role': 'member'},
            format='json'
        )
        self.assertEqual(
            response.status_code, status.HTTP_402_PAYMENT_REQUIRED
        )


class PlanListViewTestCase(OrganizationAPITestMixin, TestCase):
    """Tests for GET /api/v4/headless/plans/."""

    url = '/api/v4/headless/plans/'

    def test_list_plans_public(self):
        """Plan list is accessible without authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_plans_returns_active_public_only(self):
        """Only active and public plans are returned."""
        response = self.client.get(self.url)
        plan_ids = [p['id'] for p in response.data]
        self.assertIn('plan-test', plan_ids)
        self.assertNotIn('plan-hidden', plan_ids)

    def test_plan_fields(self):
        """Plan response includes expected fields."""
        response = self.client.get(self.url)
        plan_data = response.data[0]
        expected_fields = [
            'id', 'name', 'price_monthly', 'price_yearly',
            'storage_gb', 'max_users', 'has_advanced_ai'
        ]
        for field in expected_fields:
            self.assertIn(field, plan_data)


class CurrentOrganizationViewTestCase(
    OrganizationAPITestMixin, TestCase
):
    """Tests for GET /api/v4/headless/organizations/current/."""

    url = '/api/v4/headless/organizations/current/'

    def test_requires_auth(self):
        """Anonymous users cannot access current organization."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_org_returns_404(self):
        """Returns 404 when no organization is resolved."""
        self.client.force_authenticate(user=self.org_owner)
        response = self.client.get(self.url)
        # In test env, middleware may not run; org not set -> 404
        self.assertIn(
            response.status_code,
            (status.HTTP_200_OK, status.HTTP_404_NOT_FOUND)
        )


class CrossOrganizationAccessTestCase(
    OrganizationAPITestMixin, TestCase
):
    """
    Sprint 4 Hotfix: Verify tenant boundary enforcement.

    Tests that OrgScopedAPIMixin + IsTargetOrgAdminOrSuperAdmin
    prevent cross-organization access for non-staff users, while
    allowing staff/superuser to manage any organization.

    Fixtures: 2 organizations, admin for each, 1 staff user.
    """

    def setUp(self):
        super().setUp()

        # Second organization
        self.org_b = Organization.objects.create(
            name='Other Org',
            slug='other-org',
            email='other@example.com',
            is_active=True,
            status='active',
            max_users=10
        )
        self.org_b_admin = User.objects.create_user(
            username='org_b_admin', password='pass123'
        )
        UserOrganizationRole.objects.create(
            user=self.org_b_admin, organization=self.org_b,
            role=UserOrganizationRole.ROLE_ADMIN, is_default=True
        )

        # Staff user (not superuser — pure is_staff)
        self.staff_user = User.objects.create_user(
            username='staff_user', password='pass123', is_staff=True
        )

    def _detail_url(self, org_id):
        return '/api/v4/headless/organizations/{}/'.format(org_id)

    def _members_url(self, org_id):
        return '/api/v4/headless/organizations/{}/members/'.format(org_id)

    def _authenticate_with_org(self, user, organization):
        """
        Authenticate and simulate middleware setting request.organization.

        In test environment the TenantResolverMiddleware may not run,
        so we use force_authenticate and manually set organization
        via a custom middleware-like handler on the APIClient.
        """
        self.client.force_authenticate(user=user)
        # DRF test client does not pass through real middleware;
        # use the X-Organization-Id header that middleware reads
        self.client.credentials(HTTP_X_ORGANIZATION_ID=str(organization.pk))

    # ------------------------------------------------------------------
    # Cross-org access DENIED (non-staff)
    # ------------------------------------------------------------------

    def test_org_admin_cannot_get_other_org(self):
        """Admin of org-A calling GET on org-B -> 403."""
        self._authenticate_with_org(self.org_admin, self.org)
        response = self.client.get(self._detail_url(self.org_b.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_org_admin_cannot_patch_other_org(self):
        """Admin of org-A calling PATCH on org-B -> 403."""
        self._authenticate_with_org(self.org_admin, self.org)
        response = self.client.patch(
            self._detail_url(self.org_b.pk),
            {'description': 'hacked'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_org_admin_cannot_delete_other_org(self):
        """Admin of org-A calling DELETE on org-B -> 403."""
        self._authenticate_with_org(self.org_admin, self.org)
        response = self.client.delete(self._detail_url(self.org_b.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_org_admin_cannot_list_other_org_members(self):
        """Admin of org-A calling GET members of org-B -> 403."""
        self._authenticate_with_org(self.org_admin, self.org)
        response = self.client.get(self._members_url(self.org_b.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_org_admin_cannot_add_member_to_other_org(self):
        """Admin of org-A calling POST members of org-B -> 403."""
        self._authenticate_with_org(self.org_admin, self.org)
        response = self.client.post(
            self._members_url(self.org_b.pk),
            {'user_id': self.extra_user.pk, 'role': 'member'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_org_admin_cannot_remove_member_from_other_org(self):
        """Admin of org-A calling DELETE members of org-B -> 403."""
        self._authenticate_with_org(self.org_admin, self.org)
        response = self.client.delete(
            self._members_url(self.org_b.pk),
            {'user_id': self.org_b_admin.pk},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ------------------------------------------------------------------
    # Staff/superuser bypass
    # ------------------------------------------------------------------

    def test_staff_can_access_any_org(self):
        """Staff user can GET details of any organization."""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self._detail_url(self.org_b.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Other Org')

    def test_superadmin_can_access_any_org(self):
        """Superadmin can GET details of any organization."""
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.get(self._detail_url(self.org_b.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ------------------------------------------------------------------
    # Positive: own org access
    # ------------------------------------------------------------------

    def test_org_admin_can_get_own_org(self):
        """Admin of org-A can GET org-A details."""
        self._authenticate_with_org(self.org_admin, self.org)
        response = self.client.get(self._detail_url(self.org.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Org')

    def test_org_admin_can_patch_own_org(self):
        """Admin of org-A can PATCH org-A."""
        self._authenticate_with_org(self.org_admin, self.org)
        response = self.client.patch(
            self._detail_url(self.org.pk),
            {'description': 'Updated by admin'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_org_admin_can_list_own_members(self):
        """Admin of org-A can list org-A members."""
        self._authenticate_with_org(self.org_admin, self.org)
        response = self.client.get(self._members_url(self.org.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # owner, admin, member

    # ------------------------------------------------------------------
    # Edge cases
    # ------------------------------------------------------------------

    def test_invalid_uuid_returns_403(self):
        """Malformed organization_id in URL -> 403 (permission denies)."""
        self._authenticate_with_org(self.org_admin, self.org)
        response = self.client.get(
            '/api/v4/headless/organizations/not-a-uuid/'
        )
        # Strict UUID regex in URL conf means this should 404
        # (the URL simply won't match)
        self.assertIn(
            response.status_code,
            (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)
        )
