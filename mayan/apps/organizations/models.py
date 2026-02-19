"""
Multi-tenancy models for Prime-EDMS.

Provides Organization, Plan, Subscription, and DomainSettings models
for tenant isolation in SaaS and Standalone deployment modes.

Architecture: Shared Database + Shared Schema + ForeignKey isolation.
See: docs/transformation-2025/TZ_Django_Tenant_Isolation.md
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from mayan.apps.databases.model_mixins import ExtraDataModelMixin


# --- Constants ---

ORGANIZATION_STATUS_TRIAL = 'trial'
ORGANIZATION_STATUS_ACTIVE = 'active'
ORGANIZATION_STATUS_SUSPENDED = 'suspended'
ORGANIZATION_STATUS_ARCHIVED = 'archived'

ORGANIZATION_STATUS_CHOICES = (
    (ORGANIZATION_STATUS_TRIAL, _('Trial (free)')),
    (ORGANIZATION_STATUS_ACTIVE, _('Active (paid)')),
    (ORGANIZATION_STATUS_SUSPENDED, _('Suspended (payment issue)')),
    (ORGANIZATION_STATUS_ARCHIVED, _('Archived (deleted)')),
)

DEPLOYMENT_MODE_SAAS = 'saas'
DEPLOYMENT_MODE_STANDALONE = 'standalone'

DEPLOYMENT_MODE_CHOICES = (
    (DEPLOYMENT_MODE_SAAS, _('SaaS (Cloud)')),
    (DEPLOYMENT_MODE_STANDALONE, _('Standalone (On-Premises)')),
)

INDUSTRY_CHOICES = (
    ('media', _('Media & Entertainment')),
    ('marketing', _('Marketing Agency')),
    ('ecommerce', _('E-commerce')),
    ('healthcare', _('Healthcare')),
    ('legal', _('Legal')),
    ('education', _('Education')),
    ('government', _('Government')),
    ('other', _('Other')),
)

SUBSCRIPTION_STATUS_TRIAL = 'trial'
SUBSCRIPTION_STATUS_ACTIVE = 'active'
SUBSCRIPTION_STATUS_PAUSED = 'paused'
SUBSCRIPTION_STATUS_CANCELLED = 'cancelled'
SUBSCRIPTION_STATUS_EXPIRED = 'expired'

SUBSCRIPTION_STATUS_CHOICES = (
    (SUBSCRIPTION_STATUS_TRIAL, _('Trial')),
    (SUBSCRIPTION_STATUS_ACTIVE, _('Active')),
    (SUBSCRIPTION_STATUS_PAUSED, _('Paused')),
    (SUBSCRIPTION_STATUS_CANCELLED, _('Cancelled')),
    (SUBSCRIPTION_STATUS_EXPIRED, _('Expired')),
)

BILLING_CYCLE_MONTHLY = 'monthly'
BILLING_CYCLE_YEARLY = 'yearly'

BILLING_CYCLE_CHOICES = (
    (BILLING_CYCLE_MONTHLY, _('Monthly')),
    (BILLING_CYCLE_YEARLY, _('Yearly')),
)


# --- Models ---

class Plan(ExtraDataModelMixin, models.Model):
    """
    Tariff plan for Organizations.

    Defines pricing, resource limits, and available features.
    Plans are global (not tenant-aware) and managed by SuperAdmin.
    """
    id = models.CharField(
        primary_key=True,
        max_length=50,
        help_text=_('Unique plan identifier (e.g. plan-start, plan-pro)')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('Plan name'),
        help_text=_('Display name of the plan')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description'),
        help_text=_('Detailed description of the plan')
    )

    # Pricing
    price_monthly = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Monthly price'),
        help_text=_('Monthly price in default currency')
    )
    price_yearly = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Yearly price'),
        help_text=_('Yearly price in default currency')
    )
    currency = models.CharField(
        max_length=3,
        default='RUB',
        verbose_name=_('Currency'),
        help_text=_('ISO 4217 currency code')
    )

    # Resource limits
    storage_gb = models.IntegerField(
        default=50,
        verbose_name=_('Storage limit (GB)'),
        help_text=_('Maximum storage in gigabytes')
    )
    max_users = models.IntegerField(
        default=3,
        verbose_name=_('Max users'),
        help_text=_('Maximum number of active users')
    )
    max_ai_analyses_monthly = models.IntegerField(
        default=100,
        verbose_name=_('Max AI analyses per month'),
        help_text=_('Maximum number of AI analyses per month')
    )
    max_documents = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_('Max documents'),
        help_text=_('Maximum number of documents. NULL = unlimited')
    )
    cdn_cost_per_gb = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0.10,
        null=True,
        blank=True,
        verbose_name=_('CDN cost per GB (USD)'),
        help_text=_('Cost per GB for CDN/bandwidth billing. NULL = use system default.')
    )

    # Feature flags
    has_advanced_ai = models.BooleanField(
        default=False,
        verbose_name=_('Advanced AI'),
        help_text=_('Access to advanced AI providers (Claude, Gemini)')
    )
    has_analytics = models.BooleanField(
        default=False,
        verbose_name=_('Analytics'),
        help_text=_('Access to analytics dashboards')
    )
    has_distribution = models.BooleanField(
        default=False,
        verbose_name=_('Distribution'),
        help_text=_('Access to distribution module')
    )
    has_custom_domain = models.BooleanField(
        default=False,
        verbose_name=_('Custom domain'),
        help_text=_('Ability to use custom domain')
    )
    has_api_access = models.BooleanField(
        default=True,
        verbose_name=_('API access'),
        help_text=_('Access to REST API')
    )
    has_workflow = models.BooleanField(
        default=False,
        verbose_name=_('Workflow'),
        help_text=_('Access to workflow and approval features')
    )

    # Ordering and visibility
    sort_order = models.IntegerField(
        default=0,
        verbose_name=_('Sort order'),
        help_text=_('Display order on pricing page')
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_('Is active'),
        help_text=_('Whether this plan is available for new subscriptions')
    )
    is_public = models.BooleanField(
        default=True,
        verbose_name=_('Is public'),
        help_text=_('Whether this plan is visible on pricing page')
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )

    class Meta:
        db_table = 'organizations_plan'
        ordering = ('sort_order', 'price_monthly')
        verbose_name = _('Plan')
        verbose_name_plural = _('Plans')

    def __str__(self):
        return '{name} ({price}/mo)'.format(
            name=self.name,
            price=self.price_monthly
        )


class Organization(ExtraDataModelMixin, models.Model):
    """
    Tenant / Company for data isolation.

    Used for:
    1. Data isolation (all tenant-aware models have FK to Organization)
    2. Multi-tenancy (one backend serves N organizations)
    3. Subscription management (each Org has a Subscription)
    """

    # Primary key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Core fields
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('Name'),
        help_text=_('Organization name (unique)')
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name=_('Slug'),
        help_text=_('URL-friendly name for API and subdomains')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )

    # Business information
    email = models.EmailField(
        verbose_name=_('Email'),
        help_text=_('Organization administrator email')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Phone')
    )
    website = models.URLField(
        blank=True,
        verbose_name=_('Website')
    )
    industry = models.CharField(
        max_length=50,
        choices=INDUSTRY_CHOICES,
        default='other',
        verbose_name=_('Industry')
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_('Is active'),
        help_text=_('Whether this organization can use the system')
    )
    status = models.CharField(
        max_length=20,
        choices=ORGANIZATION_STATUS_CHOICES,
        default=ORGANIZATION_STATUS_TRIAL,
        db_index=True,
        verbose_name=_('Status')
    )

    # Deployment mode
    deployment_mode = models.CharField(
        max_length=20,
        choices=DEPLOYMENT_MODE_CHOICES,
        default=DEPLOYMENT_MODE_SAAS,
        editable=False,
        db_index=True,
        verbose_name=_('Deployment mode')
    )

    # Quotas (override Plan defaults)
    storage_limit_gb = models.IntegerField(
        default=100,
        null=True,
        blank=True,
        verbose_name=_('Storage limit (GB)'),
        help_text=_('NULL = unlimited. Overrides Plan quota.')
    )
    max_users = models.IntegerField(
        default=5,
        verbose_name=_('Max users'),
        help_text=_('Maximum active users')
    )
    max_ai_analyses_monthly = models.IntegerField(
        default=100,
        verbose_name=_('Max AI analyses per month'),
        help_text=_('Maximum AI operations per month')
    )

    # Branding
    logo = models.ImageField(
        upload_to='org-logos/',
        blank=True,
        null=True,
        verbose_name=_('Logo')
    )
    branding_color = models.CharField(
        max_length=7,
        default='#3B82F6',
        verbose_name=_('Branding color'),
        help_text=_('Primary color in #RRGGBB format')
    )

    # Owner (the user who created the organization)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_organizations',
        verbose_name=_('Owner')
    )

    # Members (many-to-many through UserOrganizationRole)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='UserOrganizationRole',
        related_name='organizations',
        verbose_name=_('Members')
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name=_('Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )

    class Meta:
        db_table = 'organizations_organization'
        ordering = ('-created_at',)
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')
        indexes = [
            models.Index(
                fields=['slug'],
                name='idx_org_slug'
            ),
            models.Index(
                fields=['is_active', 'status'],
                name='idx_org_active_status'
            ),
            models.Index(
                fields=['created_at'],
                name='idx_org_created'
            ),
        ]

    def __str__(self):
        return '{name} ({status})'.format(
            name=self.name,
            status=self.get_status_display()
        )

    # --- Cache key helpers ---

    CACHE_TTL = 300  # 5 minutes

    def _cache_key(self, metric):
        return 'org_{metric}_{pk}'.format(metric=metric, pk=self.pk)

    # --- Cached quota methods ---

    def get_storage_used_gb(self):
        """Get used storage in GB (cached for 5 min)."""
        from django.core.cache import cache
        from django.db.models import Sum

        cache_key = self._cache_key('storage')
        result = cache.get(cache_key)
        if result is not None:
            return result

        from mayan.apps.documents.models import DocumentFile

        total_bytes = DocumentFile.objects.filter(
            document__organization=self
        ).aggregate(total=Sum('size'))['total'] or 0

        result = round(total_bytes / (1024 ** 3), 2)
        cache.set(cache_key, result, timeout=self.CACHE_TTL)
        return result

    def get_active_users_count(self):
        """Get count of active users in this Organization (cached)."""
        from django.core.cache import cache

        cache_key = self._cache_key('users')
        result = cache.get(cache_key)
        if result is not None:
            return result

        result = self.members.filter(is_active=True).count()
        cache.set(cache_key, result, timeout=self.CACHE_TTL)
        return result

    def get_ai_analyses_this_month(self):
        """Get count of AI analyses performed this month (cached)."""
        from django.core.cache import cache
        from django.utils import timezone

        cache_key = self._cache_key('ai')
        result = cache.get(cache_key)
        if result is not None:
            return result

        from mayan.apps.dam.models import DocumentAIAnalysis

        current_month_start = timezone.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        result = DocumentAIAnalysis.objects.filter(
            document__organization=self,
            created_at__gte=current_month_start
        ).count()
        cache.set(cache_key, result, timeout=self.CACHE_TTL)
        return result

    # --- Cache invalidation helpers ---

    def invalidate_storage_cache(self):
        """Invalidate cached storage usage value."""
        from django.core.cache import cache
        cache.delete(self._cache_key('storage'))

    def invalidate_users_cache(self):
        """Invalidate cached user count value."""
        from django.core.cache import cache
        cache.delete(self._cache_key('users'))

    def invalidate_ai_cache(self):
        """Invalidate cached AI analyses count."""
        from django.core.cache import cache
        cache.delete(self._cache_key('ai'))

    # --- Quota check convenience methods ---

    def is_storage_exceeded(self):
        """Check if storage limit is exceeded."""
        if self.storage_limit_gb is None:
            return False
        return self.get_storage_used_gb() > self.storage_limit_gb

    def is_user_limit_exceeded(self):
        """Check if user limit is exceeded."""
        return self.get_active_users_count() >= self.max_users

    def can_perform_ai_analysis(self):
        """Check if AI analysis can be performed this month."""
        return self.get_ai_analyses_this_month() < \
            self.max_ai_analyses_monthly


class UserOrganizationRole(models.Model):
    """
    Through model for User-Organization many-to-many relationship.

    Defines the role a user has within an organization.
    """
    ROLE_OWNER = 'owner'
    ROLE_ADMIN = 'admin'
    ROLE_MEMBER = 'member'
    ROLE_VIEWER = 'viewer'

    ROLE_CHOICES = (
        (ROLE_OWNER, _('Owner')),
        (ROLE_ADMIN, _('Admin')),
        (ROLE_MEMBER, _('Member')),
        (ROLE_VIEWER, _('Viewer')),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organization_roles',
        verbose_name=_('User')
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name=_('Organization')
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_MEMBER,
        verbose_name=_('Role')
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_('Is default'),
        help_text=_('Whether this is the default organization for the user')
    )
    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Joined at')
    )

    class Meta:
        db_table = 'organizations_user_organization_role'
        unique_together = ('user', 'organization')
        verbose_name = _('User organization role')
        verbose_name_plural = _('User organization roles')
        indexes = [
            models.Index(
                fields=['user', 'is_default'],
                name='idx_uor_user_default'
            ),
            models.Index(
                fields=['organization', 'role'],
                name='idx_uor_org_role'
            ),
        ]

    def __str__(self):
        return '{user} - {org} ({role})'.format(
            user=self.user,
            org=self.organization.name,
            role=self.get_role_display()
        )


class Subscription(ExtraDataModelMixin, models.Model):
    """
    Subscription linking Organization to a Plan.

    Manages billing cycle, payment status, and trial periods.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name=_('Organization')
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        verbose_name=_('Plan')
    )

    # Billing
    billing_cycle = models.CharField(
        max_length=20,
        choices=BILLING_CYCLE_CHOICES,
        default=BILLING_CYCLE_MONTHLY,
        verbose_name=_('Billing cycle')
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Amount'),
        help_text=_('Current billing amount')
    )
    currency = models.CharField(
        max_length=3,
        default='RUB',
        verbose_name=_('Currency')
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_STATUS_CHOICES,
        default=SUBSCRIPTION_STATUS_TRIAL,
        db_index=True,
        verbose_name=_('Status')
    )

    # Dates
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Started at')
    )
    trial_ends_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Trial ends at')
    )
    current_period_start = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Current period start')
    )
    current_period_end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Current period end')
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Cancelled at')
    )

    # Payment
    payment_status = models.CharField(
        max_length=20,
        choices=(
            ('pending', _('Pending')),
            ('paid', _('Paid')),
            ('overdue', _('Overdue')),
            ('failed', _('Failed')),
        ),
        default='pending',
        verbose_name=_('Payment status')
    )
    last_payment_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last payment at')
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )

    class Meta:
        db_table = 'organizations_subscription'
        ordering = ('-created_at',)
        verbose_name = _('Subscription')
        verbose_name_plural = _('Subscriptions')

    def __str__(self):
        return '{org} - {plan} ({status})'.format(
            org=self.organization.name,
            plan=self.plan.name,
            status=self.get_status_display()
        )

    @property
    def is_trial(self):
        """Check if subscription is in trial period."""
        return self.status == SUBSCRIPTION_STATUS_TRIAL

    @property
    def is_active_subscription(self):
        """Check if subscription is active (trial or paid)."""
        return self.status in (
            SUBSCRIPTION_STATUS_TRIAL,
            SUBSCRIPTION_STATUS_ACTIVE
        )


class DomainSettings(models.Model):
    """
    Custom domain configuration for SaaS organizations.

    Allows organizations to use their own domain (e.g., dam.company.com)
    instead of the default subdomain.
    """
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name='domain_settings',
        verbose_name=_('Organization')
    )
    custom_domain = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('Custom domain'),
        help_text=_('Custom domain (e.g., dam.company.com)')
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Is verified'),
        help_text=_('Whether DNS verification has been completed')
    )
    verification_token = models.CharField(
        max_length=64,
        blank=True,
        verbose_name=_('Verification token'),
        help_text=_('DNS TXT record value for domain verification')
    )
    ssl_enabled = models.BooleanField(
        default=False,
        verbose_name=_('SSL enabled'),
        help_text=_('Whether SSL certificate is provisioned')
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Verified at')
    )

    class Meta:
        db_table = 'organizations_domain_settings'
        verbose_name = _('Domain settings')
        verbose_name_plural = _('Domain settings')
        indexes = [
            models.Index(
                fields=['custom_domain'],
                name='idx_domain_custom'
            ),
            models.Index(
                fields=['is_verified'],
                name='idx_domain_verified'
            ),
        ]

    def __str__(self):
        verified = _('verified') if self.is_verified else _('unverified')
        return '{domain} ({status})'.format(
            domain=self.custom_domain,
            status=verified
        )


class OrganizationWatermarkSettings(models.Model):
    """
    Watermark settings for an organization (Sprint 3.3).

    When enabled, watermark is applied to preview and Share Link exports.
    """
    POSITION_CHOICES = [
        ('top_left', _('Top left')),
        ('top_right', _('Top right')),
        ('bottom_left', _('Bottom left')),
        ('bottom_right', _('Bottom right')),
        ('center', _('Center')),
    ]

    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name='watermark_settings',
        verbose_name=_('Organization')
    )
    enabled = models.BooleanField(
        default=False,
        verbose_name=_('Enabled'),
        help_text=_('Apply watermark to preview and Share Link exports')
    )
    apply_on_download = models.BooleanField(
        default=False,
        verbose_name=_('Apply on download'),
        help_text=_('When enabled, serve watermarked rendition for document downloads (Sprint 5.1)')
    )
    text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Text'),
        help_text=_('Watermark text (e.g. Confidential)')
    )
    logo_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name=_('Logo URL'),
        help_text=_('Optional logo image URL for watermark')
    )
    position = models.CharField(
        max_length=32,
        choices=POSITION_CHOICES,
        default='bottom_right',
        verbose_name=_('Position')
    )
    opacity = models.FloatField(
        default=0.5,
        verbose_name=_('Opacity'),
        help_text=_('Opacity 0.0–1.0')
    )
    font_size = models.IntegerField(
        null=True,
        blank=True,
        default=24,
        verbose_name=_('Font size')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'organizations_watermark_settings'
        verbose_name = _('Organization watermark settings')
        verbose_name_plural = _('Organization watermark settings')

    def __str__(self):
        return _('Watermark for {org}').format(org=self.organization.name)

    def to_watermark_dict(self):
        """Return dict compatible with distribution _apply_watermark (text, position, opacity, font_size)."""
        if not self.enabled or not self.text:
            return {}
        # Position as (x, y) from top-left; bottom_right etc. can be resolved in caller with image size
        pos_map = {
            'top_left': (10, 10),
            'top_right': (10, 10),   # caller may override with image width
            'bottom_left': (10, 10),
            'bottom_right': (10, 10),
            'center': (10, 10),
        }
        xy = pos_map.get(self.position, (10, 10))
        return {
            'text': self.text,
            'position': xy,
            'font_size': self.font_size or 24,
            'font_color': (255, 255, 255, int(255 * self.opacity)),
        }
