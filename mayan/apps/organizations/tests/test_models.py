"""
Unit tests for organizations module models.

Tests cover:
- Organization CRUD operations
- Plan creation and defaults
- Subscription lifecycle
- DomainSettings verification
- UserOrganizationRole management
- Quota enforcement methods
"""

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from ..models import (
    DomainSettings, Organization, Plan, Subscription,
    UserOrganizationRole,
    ORGANIZATION_STATUS_ACTIVE, ORGANIZATION_STATUS_TRIAL,
    ORGANIZATION_STATUS_SUSPENDED,
    SUBSCRIPTION_STATUS_TRIAL, SUBSCRIPTION_STATUS_ACTIVE,
)

User = get_user_model()


class PlanTestCase(TestCase):
    """Tests for Plan model."""

    def test_plan_creation(self):
        """Plan can be created with required fields."""
        plan = Plan.objects.create(
            id='plan-test',
            name='Test Plan',
            price_monthly=29,
            price_yearly=290,
            storage_gb=50,
            max_users=3,
            max_ai_analyses_monthly=100
        )
        self.assertEqual(plan.name, 'Test Plan')
        self.assertEqual(plan.price_monthly, 29)
        self.assertTrue(plan.is_active)
        self.assertTrue(plan.is_public)

    def test_plan_str_representation(self):
        """Plan string representation includes name and price."""
        plan = Plan.objects.create(
            id='plan-str',
            name='Pro Plan',
            price_monthly=99
        )
        self.assertIn('Pro Plan', str(plan))
        self.assertIn('99', str(plan))

    def test_plan_defaults(self):
        """Plan has sensible defaults."""
        plan = Plan.objects.create(
            id='plan-defaults',
            name='Default Plan'
        )
        self.assertEqual(plan.currency, 'RUB')
        self.assertEqual(plan.storage_gb, 50)
        self.assertEqual(plan.max_users, 3)
        self.assertFalse(plan.has_advanced_ai)
        self.assertTrue(plan.has_api_access)

    def test_plan_feature_flags(self):
        """Plan feature flags work correctly."""
        plan = Plan.objects.create(
            id='plan-features',
            name='Enterprise',
            has_advanced_ai=True,
            has_analytics=True,
            has_distribution=True,
            has_custom_domain=True,
            has_workflow=True
        )
        self.assertTrue(plan.has_advanced_ai)
        self.assertTrue(plan.has_analytics)
        self.assertTrue(plan.has_distribution)
        self.assertTrue(plan.has_custom_domain)
        self.assertTrue(plan.has_workflow)

    def test_plan_ordering(self):
        """Plans are ordered by sort_order then price."""
        plan_c = Plan.objects.create(
            id='plan-c', name='C', sort_order=3, price_monthly=10
        )
        plan_a = Plan.objects.create(
            id='plan-a', name='A', sort_order=1, price_monthly=30
        )
        plan_b = Plan.objects.create(
            id='plan-b', name='B', sort_order=2, price_monthly=20
        )
        plans = list(Plan.objects.all())
        self.assertEqual(plans[0], plan_a)
        self.assertEqual(plans[1], plan_b)
        self.assertEqual(plans[2], plan_c)


class OrganizationTestCase(TestCase):
    """Tests for Organization model."""

    def test_organization_creation(self):
        """Organization can be created with required fields."""
        org = Organization.objects.create(
            name='Test Organization',
            slug='test-org',
            email='admin@test.com'
        )
        self.assertEqual(org.name, 'Test Organization')
        self.assertEqual(org.slug, 'test-org')
        self.assertTrue(org.is_active)
        self.assertEqual(org.status, ORGANIZATION_STATUS_TRIAL)
        self.assertIsNotNone(org.id)  # UUID auto-generated

    def test_organization_slug_unique(self):
        """Organization slug must be unique."""
        Organization.objects.create(
            name='Org 1',
            slug='unique-slug',
            email='org1@test.com'
        )
        with self.assertRaises(IntegrityError):
            Organization.objects.create(
                name='Org 2',
                slug='unique-slug',
                email='org2@test.com'
            )

    def test_organization_name_unique(self):
        """Organization name must be unique."""
        Organization.objects.create(
            name='Same Name',
            slug='slug-1',
            email='org1@test.com'
        )
        with self.assertRaises(IntegrityError):
            Organization.objects.create(
                name='Same Name',
                slug='slug-2',
                email='org2@test.com'
            )

    def test_organization_str_representation(self):
        """Organization string includes name and status."""
        org = Organization.objects.create(
            name='My Org',
            slug='my-org',
            email='admin@my-org.com'
        )
        self.assertIn('My Org', str(org))

    def test_organization_defaults(self):
        """Organization has sensible defaults."""
        org = Organization.objects.create(
            name='Default Org',
            slug='default-org',
            email='admin@default.com'
        )
        self.assertEqual(org.status, ORGANIZATION_STATUS_TRIAL)
        self.assertTrue(org.is_active)
        self.assertEqual(org.deployment_mode, 'saas')
        self.assertEqual(org.storage_limit_gb, 100)
        self.assertEqual(org.max_users, 5)
        self.assertEqual(org.max_ai_analyses_monthly, 100)
        self.assertEqual(org.branding_color, '#3B82F6')
        self.assertEqual(org.industry, 'other')

    def test_organization_user_limit_check(self):
        """is_user_limit_exceeded returns True when limit reached."""
        org = Organization.objects.create(
            name='Small Org',
            slug='small-org',
            email='admin@small.com',
            max_users=2
        )

        user1 = User.objects.create_user(
            username='user1', password='testpass123'
        )
        user2 = User.objects.create_user(
            username='user2', password='testpass123'
        )

        UserOrganizationRole.objects.create(
            user=user1, organization=org, role='member'
        )
        UserOrganizationRole.objects.create(
            user=user2, organization=org, role='member'
        )

        self.assertTrue(org.is_user_limit_exceeded())

    def test_organization_user_limit_not_exceeded(self):
        """is_user_limit_exceeded returns False when under limit."""
        org = Organization.objects.create(
            name='Big Org',
            slug='big-org',
            email='admin@big.com',
            max_users=10
        )

        user1 = User.objects.create_user(
            username='user1', password='testpass123'
        )
        UserOrganizationRole.objects.create(
            user=user1, organization=org, role='member'
        )

        self.assertFalse(org.is_user_limit_exceeded())

    def test_organization_storage_unlimited(self):
        """Storage with None limit is never exceeded."""
        org = Organization.objects.create(
            name='Unlimited Org',
            slug='unlimited-org',
            email='admin@unlimited.com',
            storage_limit_gb=None
        )
        self.assertFalse(org.is_storage_exceeded())

    def test_organization_owner_relationship(self):
        """Organization can have an owner."""
        user = User.objects.create_user(
            username='owner', password='testpass123'
        )
        org = Organization.objects.create(
            name='Owned Org',
            slug='owned-org',
            email='admin@owned.com',
            owner=user
        )
        self.assertEqual(org.owner, user)
        self.assertIn(org, user.owned_organizations.all())


class UserOrganizationRoleTestCase(TestCase):
    """Tests for UserOrganizationRole through model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.org = Organization.objects.create(
            name='Test Org',
            slug='test-org',
            email='admin@test.com'
        )

    def test_role_creation(self):
        """UserOrganizationRole can be created."""
        role = UserOrganizationRole.objects.create(
            user=self.user,
            organization=self.org,
            role='member'
        )
        self.assertEqual(role.role, 'member')
        self.assertFalse(role.is_default)

    def test_role_unique_per_user_org(self):
        """User can only have one role per organization."""
        UserOrganizationRole.objects.create(
            user=self.user,
            organization=self.org,
            role='member'
        )
        with self.assertRaises(IntegrityError):
            UserOrganizationRole.objects.create(
                user=self.user,
                organization=self.org,
                role='admin'
            )

    def test_user_multiple_organizations(self):
        """User can belong to multiple organizations."""
        org2 = Organization.objects.create(
            name='Org 2',
            slug='org-2',
            email='admin@org2.com'
        )
        UserOrganizationRole.objects.create(
            user=self.user,
            organization=self.org,
            role='member'
        )
        UserOrganizationRole.objects.create(
            user=self.user,
            organization=org2,
            role='admin'
        )
        self.assertEqual(self.user.organization_roles.count(), 2)

    def test_role_str_representation(self):
        """UserOrganizationRole string includes user, org, and role."""
        role = UserOrganizationRole.objects.create(
            user=self.user,
            organization=self.org,
            role='admin'
        )
        role_str = str(role)
        self.assertIn(str(self.user), role_str)
        self.assertIn(self.org.name, role_str)

    def test_members_through_organization(self):
        """Organization.members works through UserOrganizationRole."""
        UserOrganizationRole.objects.create(
            user=self.user,
            organization=self.org,
            role='member'
        )
        self.assertIn(self.user, self.org.members.all())


class SubscriptionTestCase(TestCase):
    """Tests for Subscription model."""

    def setUp(self):
        self.plan = Plan.objects.create(
            id='plan-test',
            name='Test Plan',
            price_monthly=29,
            storage_gb=50,
            max_users=3
        )
        self.org = Organization.objects.create(
            name='Test Org',
            slug='test-org',
            email='admin@test.com'
        )

    def test_subscription_creation(self):
        """Subscription can be created."""
        sub = Subscription.objects.create(
            organization=self.org,
            plan=self.plan,
            amount=29
        )
        self.assertEqual(sub.status, SUBSCRIPTION_STATUS_TRIAL)
        self.assertEqual(sub.billing_cycle, 'monthly')
        self.assertEqual(sub.currency, 'RUB')

    def test_subscription_is_trial(self):
        """is_trial returns True for trial subscriptions."""
        sub = Subscription.objects.create(
            organization=self.org,
            plan=self.plan
        )
        self.assertTrue(sub.is_trial)

    def test_subscription_is_active(self):
        """is_active_subscription returns True for trial and active."""
        sub = Subscription.objects.create(
            organization=self.org,
            plan=self.plan,
            status=SUBSCRIPTION_STATUS_ACTIVE
        )
        self.assertTrue(sub.is_active_subscription)
        self.assertFalse(sub.is_trial)

    def test_subscription_one_per_org(self):
        """Organization can only have one subscription."""
        Subscription.objects.create(
            organization=self.org,
            plan=self.plan
        )
        with self.assertRaises(IntegrityError):
            Subscription.objects.create(
                organization=self.org,
                plan=self.plan
            )

    def test_plan_protection(self):
        """Plan cannot be deleted when subscriptions exist."""
        Subscription.objects.create(
            organization=self.org,
            plan=self.plan
        )
        from django.db.models import ProtectedError
        with self.assertRaises(ProtectedError):
            self.plan.delete()


class DomainSettingsTestCase(TestCase):
    """Tests for DomainSettings model."""

    def setUp(self):
        self.org = Organization.objects.create(
            name='Domain Org',
            slug='domain-org',
            email='admin@domain.com'
        )

    def test_domain_creation(self):
        """DomainSettings can be created."""
        domain = DomainSettings.objects.create(
            organization=self.org,
            custom_domain='dam.company.com'
        )
        self.assertEqual(domain.custom_domain, 'dam.company.com')
        self.assertFalse(domain.is_verified)
        self.assertFalse(domain.ssl_enabled)

    def test_domain_unique(self):
        """Custom domain must be unique."""
        DomainSettings.objects.create(
            organization=self.org,
            custom_domain='unique.domain.com'
        )
        org2 = Organization.objects.create(
            name='Org 2',
            slug='org-2',
            email='admin@org2.com'
        )
        with self.assertRaises(IntegrityError):
            DomainSettings.objects.create(
                organization=org2,
                custom_domain='unique.domain.com'
            )

    def test_domain_str_representation(self):
        """DomainSettings string includes domain and verification status."""
        domain = DomainSettings.objects.create(
            organization=self.org,
            custom_domain='dam.company.com',
            is_verified=True
        )
        self.assertIn('dam.company.com', str(domain))
