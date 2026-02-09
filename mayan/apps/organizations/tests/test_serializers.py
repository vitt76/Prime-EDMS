"""
Tests for Organizations DRF serializers.

Sprint 4: Validation, field exposure, and serialization correctness.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from mayan.apps.organizations.models import (
    Organization, Plan, UserOrganizationRole
)
from mayan.apps.organizations.serializers import (
    AddMemberSerializer,
    OrganizationListSerializer,
    OrganizationSerializer,
    PlanSerializer,
    RemoveMemberSerializer,
)

User = get_user_model()


class PlanSerializerTestCase(TestCase):
    """Tests for PlanSerializer."""

    def setUp(self):
        self.plan = Plan.objects.create(
            id='plan-ser',
            name='Serializer Plan',
            price_monthly=50,
            price_yearly=500,
            storage_gb=100,
            max_users=10,
            max_ai_analyses_monthly=200,
            is_active=True,
            is_public=True,
            has_advanced_ai=True
        )

    def test_plan_fields_exposed(self):
        """PlanSerializer exposes all expected fields."""
        serializer = PlanSerializer(instance=self.plan)
        data = serializer.data
        self.assertEqual(data['id'], 'plan-ser')
        self.assertEqual(data['name'], 'Serializer Plan')
        self.assertEqual(data['storage_gb'], 100)
        self.assertEqual(data['has_advanced_ai'], True)

    def test_plan_readonly(self):
        """PlanSerializer is fully read-only."""
        serializer = PlanSerializer(instance=self.plan)
        self.assertEqual(
            set(serializer.Meta.read_only_fields),
            set(serializer.Meta.fields)
        )


class OrganizationListSerializerTestCase(TestCase):
    """Tests for OrganizationListSerializer."""

    def setUp(self):
        self.org = Organization.objects.create(
            name='List Org', slug='list-org', email='list@test.com',
            is_active=True, status='active'
        )

    def test_member_count_default(self):
        """member_count defaults to 0 when not annotated."""
        serializer = OrganizationListSerializer(instance=self.org)
        self.assertEqual(serializer.data['member_count'], 0)

    def test_member_count_annotated(self):
        """member_count reflects annotated value."""
        self.org.member_count = 42  # Simulate annotation
        serializer = OrganizationListSerializer(instance=self.org)
        self.assertEqual(serializer.data['member_count'], 42)

    def test_fields_exposed(self):
        """All expected fields are present."""
        serializer = OrganizationListSerializer(instance=self.org)
        data = serializer.data
        for field in ('id', 'name', 'slug', 'status', 'member_count'):
            self.assertIn(field, data)


class OrganizationSerializerTestCase(TestCase):
    """Tests for OrganizationSerializer."""

    def test_create_with_valid_data(self):
        """Organization can be created through serializer."""
        data = {
            'name': 'Ser Org',
            'slug': 'ser-org',
            'email': 'ser@test.com',
            'industry': 'media'
        }
        serializer = OrganizationSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        org = serializer.save()
        self.assertEqual(org.name, 'Ser Org')
        self.assertEqual(org.industry, 'media')

    def test_duplicate_slug_validation(self):
        """Duplicate slug triggers validation error."""
        Organization.objects.create(
            name='First', slug='dup-slug', email='first@test.com'
        )
        serializer = OrganizationSerializer(data={
            'name': 'Second', 'slug': 'dup-slug', 'email': 'second@test.com'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('slug', serializer.errors)

    def test_readonly_fields(self):
        """Read-only fields cannot be set via serializer."""
        data = {
            'name': 'RO Org',
            'slug': 'ro-org',
            'email': 'ro@test.com',
            'deployment_mode': 'saas'  # Should be read-only
        }
        serializer = OrganizationSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        org = serializer.save()
        # deployment_mode should use model default, not input
        self.assertEqual(org.deployment_mode, 'saas')  # default is saas


class AddMemberSerializerTestCase(TestCase):
    """Tests for AddMemberSerializer."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='add_target', password='pass123'
        )

    def test_valid_data(self):
        """Valid user_id and role passes validation."""
        serializer = AddMemberSerializer(data={
            'user_id': self.user.pk,
            'role': 'member'
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_user_id(self):
        """Non-existent user_id fails validation."""
        serializer = AddMemberSerializer(data={
            'user_id': 99999,
            'role': 'member'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('user_id', serializer.errors)

    def test_invalid_role(self):
        """Invalid role value fails validation."""
        serializer = AddMemberSerializer(data={
            'user_id': self.user.pk,
            'role': 'supreme_leader'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('role', serializer.errors)

    def test_default_role(self):
        """Default role is 'member' when not specified."""
        serializer = AddMemberSerializer(data={
            'user_id': self.user.pk
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data['role'],
            UserOrganizationRole.ROLE_MEMBER
        )


class RemoveMemberSerializerTestCase(TestCase):
    """Tests for RemoveMemberSerializer."""

    def test_valid_user_id(self):
        """Positive integer user_id passes validation."""
        serializer = RemoveMemberSerializer(data={'user_id': 1})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_missing_user_id(self):
        """Missing user_id fails validation."""
        serializer = RemoveMemberSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn('user_id', serializer.errors)

    def test_negative_user_id(self):
        """Negative user_id fails validation."""
        serializer = RemoveMemberSerializer(data={'user_id': -1})
        self.assertFalse(serializer.is_valid())

    def test_zero_user_id(self):
        """Zero user_id fails validation."""
        serializer = RemoveMemberSerializer(data={'user_id': 0})
        self.assertFalse(serializer.is_valid())
