"""
Phase 2: Populate existing data with default Organization.

Creates a default Organization (slug='default') and binds all existing
Document, Tag, Cabinet records to it. Also creates UserOrganizationRole
entries for all existing users.

This migration is idempotent and safe to re-run.
"""

from django.db import migrations


def populate_default_organization(apps, schema_editor):
    """
    Forward migration: create default org and bind all existing data.
    """
    Organization = apps.get_model('organizations', 'Organization')
    UserOrganizationRole = apps.get_model(
        'organizations', 'UserOrganizationRole'
    )
    Plan = apps.get_model('organizations', 'Plan')
    Document = apps.get_model('documents', 'Document')
    Tag = apps.get_model('tags', 'Tag')
    Cabinet = apps.get_model('cabinets', 'Cabinet')
    User = apps.get_model('auth', 'User')

    # 1. Create default Plan if not exists
    default_plan, _ = Plan.objects.get_or_create(
        id='plan-default',
        defaults={
            'name': 'Default Plan',
            'description': 'Default plan for standalone installations',
            'price_monthly': 0,
            'price_yearly': 0,
            'currency': 'RUB',
            'storage_gb': 9999,
            'max_users': 9999,
            'max_ai_analyses_monthly': 999999,
            'has_advanced_ai': True,
            'has_analytics': True,
            'has_distribution': True,
            'has_custom_domain': False,
            'has_api_access': True,
            'has_workflow': True,
            'is_active': True,
            'is_public': False,
        }
    )

    # 2. Create default Organization if not exists
    default_org, created = Organization.objects.get_or_create(
        slug='default',
        defaults={
            'name': 'Default Organization',
            'email': 'admin@localhost',
            'is_active': True,
            'status': 'active',
            'deployment_mode': 'standalone',
            'storage_limit_gb': None,
            'max_users': 9999,
            'max_ai_analyses_monthly': 999999,
            'branding_color': '#3B82F6',
            'industry': 'other',
        }
    )

    db_alias = schema_editor.connection.alias

    # 3. Bind all Documents without organization to default
    Document.objects.using(db_alias).filter(
        organization__isnull=True
    ).update(organization=default_org)

    # 4. Bind all Tags without organization to default
    Tag.objects.using(db_alias).filter(
        organization__isnull=True
    ).update(organization=default_org)

    # 5. Bind all Cabinets without organization to default
    Cabinet.objects.using(db_alias).filter(
        organization__isnull=True
    ).update(organization=default_org)

    # 6. Create UserOrganizationRole for all existing users
    existing_users = User.objects.using(db_alias).all()
    roles_to_create = []

    existing_role_user_ids = set(
        UserOrganizationRole.objects.using(db_alias).filter(
            organization=default_org
        ).values_list('user_id', flat=True)
    )

    for user in existing_users:
        if user.pk not in existing_role_user_ids:
            role = 'owner' if user.is_superuser else 'member'
            roles_to_create.append(
                UserOrganizationRole(
                    user=user,
                    organization=default_org,
                    role=role,
                    is_default=True,
                )
            )

    if roles_to_create:
        UserOrganizationRole.objects.using(db_alias).bulk_create(
            roles_to_create, ignore_conflicts=True
        )


def reverse_populate(apps, schema_editor):
    """
    Reverse migration: set all organization FKs back to NULL.

    Does NOT delete the default Organization (it may be referenced
    by other data).
    """
    db_alias = schema_editor.connection.alias

    Document = apps.get_model('documents', 'Document')
    Tag = apps.get_model('tags', 'Tag')
    Cabinet = apps.get_model('cabinets', 'Cabinet')

    Document.objects.using(db_alias).all().update(organization=None)
    Tag.objects.using(db_alias).all().update(organization=None)
    Cabinet.objects.using(db_alias).all().update(organization=None)


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0002_add_organization_to_models'),
        ('documents', '0084_document_fulltext_search'),
        ('tags', '0009_alter_tag_color'),
        ('cabinets', '0006_auto_20210525_0604'),
        ('auth', '__latest__'),
    ]

    operations = [
        migrations.RunPython(
            populate_default_organization,
            reverse_populate,
        ),
    ]
