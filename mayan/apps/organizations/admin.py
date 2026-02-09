"""
Django Admin configuration for Organizations app.

Provides admin interfaces for Organization, Plan, Subscription,
UserOrganizationRole and DomainSettings management.
"""

from django.contrib import admin
from django.db.models import Count, Q
from django.utils.translation import ugettext_lazy as _

from .models import (
    DomainSettings, Organization, Plan, Subscription,
    UserOrganizationRole
)


class UserOrganizationRoleInline(admin.TabularInline):
    """Inline for managing organization members."""
    model = UserOrganizationRole
    extra = 1
    autocomplete_fields = ('user',)
    fields = ('user', 'role', 'is_default', 'joined_at')
    readonly_fields = ('joined_at',)


class DomainSettingsInline(admin.StackedInline):
    """Inline for managing custom domain settings."""
    model = DomainSettings
    extra = 0
    max_num = 1
    fields = (
        'custom_domain', 'is_verified', 'verification_token',
        'ssl_enabled', 'verified_at'
    )
    readonly_fields = ('verified_at',)


class SubscriptionInline(admin.StackedInline):
    """Inline for managing organization subscription."""
    model = Subscription
    extra = 0
    max_num = 1
    fields = (
        'plan', 'billing_cycle', 'status', 'amount', 'currency',
        'trial_ends_at', 'current_period_start', 'current_period_end',
        'payment_status', 'last_payment_at'
    )
    readonly_fields = ('last_payment_at',)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin for managing Organizations."""

    list_display = (
        'name', 'slug', 'status', 'deployment_mode', 'is_active',
        'get_member_count', 'get_storage_display', 'created_at'
    )
    list_filter = ('status', 'deployment_mode', 'is_active', 'industry')
    search_fields = ('name', 'slug', 'email')
    readonly_fields = ('id', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 25
    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'slug', 'description', 'email')
        }),
        (_('Status & Deployment'), {
            'fields': ('is_active', 'status', 'deployment_mode')
        }),
        (_('Business'), {
            'fields': ('phone', 'website', 'industry')
        }),
        (_('Quotas'), {
            'fields': (
                'storage_limit_gb', 'max_users', 'max_ai_analyses_monthly'
            )
        }),
        (_('Branding'), {
            'fields': ('logo', 'branding_color'),
            'classes': ('collapse',)
        }),
        (_('Owner'), {
            'fields': ('owner',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [
        UserOrganizationRoleInline,
        DomainSettingsInline,
        SubscriptionInline,
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _member_count=Count(
                'members', filter=Q(members__is_active=True)
            )
        )

    def get_member_count(self, obj):
        return getattr(obj, '_member_count', 0)
    get_member_count.short_description = _('Members')
    get_member_count.admin_order_field = '_member_count'

    def get_storage_display(self, obj):
        used = obj.get_storage_used_gb()
        limit = obj.storage_limit_gb
        if limit:
            return '{used} / {limit} GB'.format(used=used, limit=limit)
        return '{used} GB'.format(used=used)
    get_storage_display.short_description = _('Storage')


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    """Admin for managing Plans."""

    list_display = (
        'id', 'name', 'price_monthly', 'price_yearly', 'currency',
        'storage_gb', 'max_users', 'is_active', 'is_public', 'sort_order'
    )
    list_filter = ('is_active', 'is_public', 'currency')
    search_fields = ('id', 'name', 'description')
    list_editable = ('sort_order', 'is_active', 'is_public')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'description')
        }),
        (_('Pricing'), {
            'fields': (
                'price_monthly', 'price_yearly', 'currency'
            )
        }),
        (_('Resource Limits'), {
            'fields': (
                'storage_gb', 'max_users', 'max_ai_analyses_monthly',
                'max_documents'
            )
        }),
        (_('Features'), {
            'fields': (
                'has_advanced_ai', 'has_analytics', 'has_distribution',
                'has_custom_domain', 'has_api_access', 'has_workflow'
            )
        }),
        (_('Visibility'), {
            'fields': ('sort_order', 'is_active', 'is_public')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin for managing Subscriptions."""

    list_display = (
        'organization', 'plan', 'status', 'billing_cycle',
        'amount', 'payment_status', 'current_period_end'
    )
    list_filter = ('status', 'billing_cycle', 'payment_status')
    search_fields = (
        'organization__name', 'organization__slug', 'plan__name'
    )
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ('organization', 'plan')

    fieldsets = (
        (None, {
            'fields': ('id', 'organization', 'plan')
        }),
        (_('Billing'), {
            'fields': (
                'billing_cycle', 'amount', 'currency', 'payment_status',
                'last_payment_at'
            )
        }),
        (_('Status & Dates'), {
            'fields': (
                'status', 'trial_ends_at',
                'current_period_start', 'current_period_end',
                'cancelled_at'
            )
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserOrganizationRole)
class UserOrganizationRoleAdmin(admin.ModelAdmin):
    """Admin for managing User-Organization roles."""

    list_display = (
        'user', 'organization', 'role', 'is_default', 'joined_at'
    )
    list_filter = ('role', 'is_default')
    search_fields = (
        'user__username', 'user__email', 'organization__name'
    )
    autocomplete_fields = ('user', 'organization')
    readonly_fields = ('joined_at',)


@admin.register(DomainSettings)
class DomainSettingsAdmin(admin.ModelAdmin):
    """Admin for managing custom domain settings."""

    list_display = (
        'custom_domain', 'organization', 'is_verified',
        'ssl_enabled', 'created_at'
    )
    list_filter = ('is_verified', 'ssl_enabled')
    search_fields = ('custom_domain', 'organization__name')
    autocomplete_fields = ('organization',)
    readonly_fields = ('created_at', 'verified_at')
