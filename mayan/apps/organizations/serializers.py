"""
DRF Serializers for Organizations app.

Provides serializers for Organization, Plan, Subscription,
UserOrganizationRole, and CurrentOrganization endpoints.
"""

from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import (
    DomainSettings, Organization, Plan, Subscription,
    UserOrganizationRole
)

User = get_user_model()


class PlanSerializer(serializers.ModelSerializer):
    """Read-only serializer for Plan (tariff) listings."""

    class Meta:
        model = Plan
        fields = (
            'id', 'name', 'description',
            'price_monthly', 'price_yearly', 'currency',
            'storage_gb', 'max_users', 'max_ai_analyses_monthly',
            'max_documents',
            'has_advanced_ai', 'has_analytics', 'has_distribution',
            'has_custom_domain', 'has_api_access', 'has_workflow',
            'sort_order', 'is_active', 'is_public',
        )
        read_only_fields = fields


class MemberUserSerializer(serializers.ModelSerializer):
    """Lightweight user serializer for member listings."""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = fields


class UserOrganizationRoleSerializer(serializers.ModelSerializer):
    """Serializer for managing user-organization roles."""

    user_detail = MemberUserSerializer(source='user', read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        required=False
    )

    class Meta:
        model = UserOrganizationRole
        fields = (
            'id', 'user_detail', 'user_id', 'organization',
            'role', 'is_default', 'joined_at'
        )
        read_only_fields = ('id', 'joined_at', 'organization')


class DomainSettingsSerializer(serializers.ModelSerializer):
    """Serializer for custom domain settings."""

    class Meta:
        model = DomainSettings
        fields = (
            'custom_domain', 'is_verified', 'verification_token',
            'ssl_enabled', 'verified_at', 'created_at'
        )
        read_only_fields = (
            'is_verified', 'verification_token', 'ssl_enabled',
            'verified_at', 'created_at'
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for Subscription data."""

    plan_detail = PlanSerializer(source='plan', read_only=True)

    class Meta:
        model = Subscription
        fields = (
            'id', 'plan', 'plan_detail', 'billing_cycle',
            'amount', 'currency', 'status', 'payment_status',
            'started_at', 'trial_ends_at',
            'current_period_start', 'current_period_end',
            'cancelled_at', 'last_payment_at',
        )
        read_only_fields = (
            'id', 'started_at', 'cancelled_at', 'last_payment_at'
        )


class OrganizationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for Organization listings.

    Returns minimal data suitable for list views and dropdowns.
    Expects queryset annotated with ``member_count`` from the view.
    """

    member_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Organization
        fields = (
            'id', 'name', 'slug', 'status', 'deployment_mode',
            'is_active', 'industry', 'member_count', 'created_at'
        )
        read_only_fields = fields


class OrganizationSerializer(serializers.ModelSerializer):
    """
    Full serializer for Organization CRUD operations.

    Includes nested subscription and domain_settings data.
    """

    subscription = SubscriptionSerializer(read_only=True)
    domain_settings = DomainSettingsSerializer(read_only=True)
    member_count = serializers.IntegerField(read_only=True, default=0)
    storage_used_gb = serializers.SerializerMethodField()
    active_users_count = serializers.IntegerField(
        source='member_count', read_only=True, default=0
    )

    class Meta:
        model = Organization
        fields = (
            'id', 'name', 'slug', 'description', 'email', 'phone',
            'website', 'industry',
            'is_active', 'status', 'deployment_mode',
            'storage_limit_gb', 'max_users', 'max_ai_analyses_monthly',
            'logo', 'branding_color',
            'subscription', 'domain_settings',
            'member_count', 'storage_used_gb', 'active_users_count',
            'created_at', 'updated_at',
        )
        read_only_fields = (
            'id', 'deployment_mode', 'created_at', 'updated_at',
            'member_count', 'storage_used_gb', 'active_users_count',
        )

    def get_storage_used_gb(self, obj):
        return obj.get_storage_used_gb()


class CurrentOrganizationSerializer(serializers.ModelSerializer):
    """
    Serializer for the current organization endpoint.

    Returns the organization resolved from the request context,
    with subscription and quota info.
    """

    subscription = SubscriptionSerializer(read_only=True)
    storage_used_gb = serializers.SerializerMethodField()
    active_users_count = serializers.SerializerMethodField()
    is_storage_exceeded = serializers.SerializerMethodField()
    is_user_limit_exceeded = serializers.SerializerMethodField()
    can_perform_ai_analysis = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = (
            'id', 'name', 'slug', 'status', 'deployment_mode',
            'email', 'industry', 'logo', 'branding_color',
            'storage_limit_gb', 'max_users', 'max_ai_analyses_monthly',
            'subscription',
            'storage_used_gb', 'active_users_count',
            'is_storage_exceeded', 'is_user_limit_exceeded',
            'can_perform_ai_analysis',
        )
        read_only_fields = fields

    def get_storage_used_gb(self, obj):
        return obj.get_storage_used_gb()

    def get_active_users_count(self, obj):
        return obj.get_active_users_count()

    def get_is_storage_exceeded(self, obj):
        return obj.is_storage_exceeded()

    def get_is_user_limit_exceeded(self, obj):
        return obj.is_user_limit_exceeded()

    def get_can_perform_ai_analysis(self, obj):
        return obj.can_perform_ai_analysis()


class AddMemberSerializer(serializers.Serializer):
    """Serializer for adding a member to an organization."""

    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        help_text='ID of the user to add'
    )
    role = serializers.ChoiceField(
        choices=UserOrganizationRole.ROLE_CHOICES,
        default=UserOrganizationRole.ROLE_MEMBER,
        help_text='Role for the new member'
    )


class RemoveMemberSerializer(serializers.Serializer):
    """Serializer for removing a member from an organization."""

    user_id = serializers.IntegerField(
        help_text='ID of the user to remove'
    )

    def validate_user_id(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError(
                'user_id must be a positive integer.'
            )
        return value
