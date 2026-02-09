"""
Initial migration for organizations module.

Creates the core multi-tenancy models:
- Plan (tariff plans)
- Organization (tenants)
- UserOrganizationRole (user-org membership)
- Subscription (org-plan billing)
- DomainSettings (custom domains)
"""

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # 1. Plan (no FK dependencies)
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.CharField(
                    help_text='Unique plan identifier (e.g. plan-start, plan-pro)',
                    max_length=50,
                    primary_key=True,
                    serialize=False
                )),
                ('name', models.CharField(
                    help_text='Display name of the plan',
                    max_length=100,
                    verbose_name='Plan name'
                )),
                ('description', models.TextField(
                    blank=True,
                    verbose_name='Description'
                )),
                ('price_monthly', models.DecimalField(
                    decimal_places=2,
                    default=0,
                    max_digits=10,
                    verbose_name='Monthly price'
                )),
                ('price_yearly', models.DecimalField(
                    decimal_places=2,
                    default=0,
                    max_digits=10,
                    verbose_name='Yearly price'
                )),
                ('currency', models.CharField(
                    default='RUB',
                    max_length=3,
                    verbose_name='Currency'
                )),
                ('storage_gb', models.IntegerField(
                    default=50,
                    verbose_name='Storage limit (GB)'
                )),
                ('max_users', models.IntegerField(
                    default=3,
                    verbose_name='Max users'
                )),
                ('max_ai_analyses_monthly', models.IntegerField(
                    default=100,
                    verbose_name='Max AI analyses per month'
                )),
                ('max_documents', models.IntegerField(
                    blank=True,
                    null=True,
                    verbose_name='Max documents'
                )),
                ('has_advanced_ai', models.BooleanField(
                    default=False,
                    verbose_name='Advanced AI'
                )),
                ('has_analytics', models.BooleanField(
                    default=False,
                    verbose_name='Analytics'
                )),
                ('has_distribution', models.BooleanField(
                    default=False,
                    verbose_name='Distribution'
                )),
                ('has_custom_domain', models.BooleanField(
                    default=False,
                    verbose_name='Custom domain'
                )),
                ('has_api_access', models.BooleanField(
                    default=True,
                    verbose_name='API access'
                )),
                ('has_workflow', models.BooleanField(
                    default=False,
                    verbose_name='Workflow'
                )),
                ('sort_order', models.IntegerField(
                    default=0,
                    verbose_name='Sort order'
                )),
                ('is_active', models.BooleanField(
                    db_index=True,
                    default=True,
                    verbose_name='Is active'
                )),
                ('is_public', models.BooleanField(
                    default=True,
                    verbose_name='Is public'
                )),
                ('created_at', models.DateTimeField(
                    auto_now_add=True,
                    verbose_name='Created at'
                )),
                ('updated_at', models.DateTimeField(
                    auto_now=True,
                    verbose_name='Updated at'
                )),
            ],
            options={
                'db_table': 'organizations_plan',
                'ordering': ('sort_order', 'price_monthly'),
                'verbose_name': 'Plan',
                'verbose_name_plural': 'Plans',
            },
        ),

        # 2. Organization (depends on AUTH_USER_MODEL for owner)
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False
                )),
                ('name', models.CharField(
                    max_length=255,
                    unique=True,
                    verbose_name='Name'
                )),
                ('slug', models.SlugField(
                    max_length=100,
                    unique=True,
                    verbose_name='Slug'
                )),
                ('description', models.TextField(
                    blank=True,
                    verbose_name='Description'
                )),
                ('email', models.EmailField(
                    max_length=254,
                    verbose_name='Email'
                )),
                ('phone', models.CharField(
                    blank=True,
                    max_length=20,
                    verbose_name='Phone'
                )),
                ('website', models.URLField(
                    blank=True,
                    verbose_name='Website'
                )),
                ('industry', models.CharField(
                    choices=[
                        ('media', 'Media & Entertainment'),
                        ('marketing', 'Marketing Agency'),
                        ('ecommerce', 'E-commerce'),
                        ('healthcare', 'Healthcare'),
                        ('legal', 'Legal'),
                        ('education', 'Education'),
                        ('government', 'Government'),
                        ('other', 'Other'),
                    ],
                    default='other',
                    max_length=50,
                    verbose_name='Industry'
                )),
                ('is_active', models.BooleanField(
                    db_index=True,
                    default=True,
                    verbose_name='Is active'
                )),
                ('status', models.CharField(
                    choices=[
                        ('trial', 'Trial (free)'),
                        ('active', 'Active (paid)'),
                        ('suspended', 'Suspended (payment issue)'),
                        ('archived', 'Archived (deleted)'),
                    ],
                    db_index=True,
                    default='trial',
                    max_length=20,
                    verbose_name='Status'
                )),
                ('deployment_mode', models.CharField(
                    choices=[
                        ('saas', 'SaaS (Cloud)'),
                        ('standalone', 'Standalone (On-Premises)'),
                    ],
                    db_index=True,
                    default='saas',
                    editable=False,
                    max_length=20,
                    verbose_name='Deployment mode'
                )),
                ('storage_limit_gb', models.IntegerField(
                    blank=True,
                    default=100,
                    null=True,
                    verbose_name='Storage limit (GB)'
                )),
                ('max_users', models.IntegerField(
                    default=5,
                    verbose_name='Max users'
                )),
                ('max_ai_analyses_monthly', models.IntegerField(
                    default=100,
                    verbose_name='Max AI analyses per month'
                )),
                ('logo', models.ImageField(
                    blank=True,
                    null=True,
                    upload_to='org-logos/',
                    verbose_name='Logo'
                )),
                ('branding_color', models.CharField(
                    default='#3B82F6',
                    max_length=7,
                    verbose_name='Branding color'
                )),
                ('created_at', models.DateTimeField(
                    auto_now_add=True,
                    db_index=True,
                    verbose_name='Created at'
                )),
                ('updated_at', models.DateTimeField(
                    auto_now=True,
                    verbose_name='Updated at'
                )),
                ('owner', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='owned_organizations',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Owner'
                )),
            ],
            options={
                'db_table': 'organizations_organization',
                'ordering': ('-created_at',),
                'verbose_name': 'Organization',
                'verbose_name_plural': 'Organizations',
            },
        ),

        # 3. UserOrganizationRole (through model)
        migrations.CreateModel(
            name='UserOrganizationRole',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('role', models.CharField(
                    choices=[
                        ('owner', 'Owner'),
                        ('admin', 'Admin'),
                        ('member', 'Member'),
                        ('viewer', 'Viewer'),
                    ],
                    default='member',
                    max_length=20,
                    verbose_name='Role'
                )),
                ('is_default', models.BooleanField(
                    default=False,
                    verbose_name='Is default'
                )),
                ('joined_at', models.DateTimeField(
                    auto_now_add=True,
                    verbose_name='Joined at'
                )),
                ('organization', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='user_roles',
                    to='organizations.organization',
                    verbose_name='Organization'
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='organization_roles',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='User'
                )),
            ],
            options={
                'db_table': 'organizations_user_organization_role',
                'verbose_name': 'User organization role',
                'verbose_name_plural': 'User organization roles',
                'unique_together': {('user', 'organization')},
            },
        ),

        # 4. Add members M2M to Organization (through UserOrganizationRole)
        migrations.AddField(
            model_name='organization',
            name='members',
            field=models.ManyToManyField(
                related_name='organizations',
                through='organizations.UserOrganizationRole',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Members'
            ),
        ),

        # 5. Subscription (depends on Organization and Plan)
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False
                )),
                ('billing_cycle', models.CharField(
                    choices=[
                        ('monthly', 'Monthly'),
                        ('yearly', 'Yearly'),
                    ],
                    default='monthly',
                    max_length=20,
                    verbose_name='Billing cycle'
                )),
                ('amount', models.DecimalField(
                    decimal_places=2,
                    default=0,
                    max_digits=10,
                    verbose_name='Amount'
                )),
                ('currency', models.CharField(
                    default='RUB',
                    max_length=3,
                    verbose_name='Currency'
                )),
                ('status', models.CharField(
                    choices=[
                        ('trial', 'Trial'),
                        ('active', 'Active'),
                        ('paused', 'Paused'),
                        ('cancelled', 'Cancelled'),
                        ('expired', 'Expired'),
                    ],
                    db_index=True,
                    default='trial',
                    max_length=20,
                    verbose_name='Status'
                )),
                ('started_at', models.DateTimeField(
                    auto_now_add=True,
                    verbose_name='Started at'
                )),
                ('trial_ends_at', models.DateTimeField(
                    blank=True,
                    null=True,
                    verbose_name='Trial ends at'
                )),
                ('current_period_start', models.DateTimeField(
                    blank=True,
                    null=True,
                    verbose_name='Current period start'
                )),
                ('current_period_end', models.DateTimeField(
                    blank=True,
                    null=True,
                    verbose_name='Current period end'
                )),
                ('cancelled_at', models.DateTimeField(
                    blank=True,
                    null=True,
                    verbose_name='Cancelled at'
                )),
                ('payment_status', models.CharField(
                    choices=[
                        ('pending', 'Pending'),
                        ('paid', 'Paid'),
                        ('overdue', 'Overdue'),
                        ('failed', 'Failed'),
                    ],
                    default='pending',
                    max_length=20,
                    verbose_name='Payment status'
                )),
                ('last_payment_at', models.DateTimeField(
                    blank=True,
                    null=True,
                    verbose_name='Last payment at'
                )),
                ('created_at', models.DateTimeField(
                    auto_now_add=True,
                    verbose_name='Created at'
                )),
                ('updated_at', models.DateTimeField(
                    auto_now=True,
                    verbose_name='Updated at'
                )),
                ('organization', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='subscription',
                    to='organizations.organization',
                    verbose_name='Organization'
                )),
                ('plan', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='subscriptions',
                    to='organizations.plan',
                    verbose_name='Plan'
                )),
            ],
            options={
                'db_table': 'organizations_subscription',
                'ordering': ('-created_at',),
                'verbose_name': 'Subscription',
                'verbose_name_plural': 'Subscriptions',
            },
        ),

        # 6. DomainSettings (depends on Organization)
        migrations.CreateModel(
            name='DomainSettings',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('custom_domain', models.CharField(
                    max_length=255,
                    unique=True,
                    verbose_name='Custom domain'
                )),
                ('is_verified', models.BooleanField(
                    default=False,
                    verbose_name='Is verified'
                )),
                ('verification_token', models.CharField(
                    blank=True,
                    max_length=64,
                    verbose_name='Verification token'
                )),
                ('ssl_enabled', models.BooleanField(
                    default=False,
                    verbose_name='SSL enabled'
                )),
                ('created_at', models.DateTimeField(
                    auto_now_add=True,
                    verbose_name='Created at'
                )),
                ('verified_at', models.DateTimeField(
                    blank=True,
                    null=True,
                    verbose_name='Verified at'
                )),
                ('organization', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='domain_settings',
                    to='organizations.organization',
                    verbose_name='Organization'
                )),
            ],
            options={
                'db_table': 'organizations_domain_settings',
                'verbose_name': 'Domain settings',
                'verbose_name_plural': 'Domain settings',
            },
        ),

        # 7. Indexes for Organization
        migrations.AddIndex(
            model_name='organization',
            index=models.Index(
                fields=['slug'],
                name='idx_org_slug'
            ),
        ),
        migrations.AddIndex(
            model_name='organization',
            index=models.Index(
                fields=['is_active', 'status'],
                name='idx_org_active_status'
            ),
        ),
        migrations.AddIndex(
            model_name='organization',
            index=models.Index(
                fields=['created_at'],
                name='idx_org_created'
            ),
        ),

        # 8. Index for DomainSettings
        migrations.AddIndex(
            model_name='domainsettings',
            index=models.Index(
                fields=['custom_domain'],
                name='idx_domain_custom'
            ),
        ),
    ]
