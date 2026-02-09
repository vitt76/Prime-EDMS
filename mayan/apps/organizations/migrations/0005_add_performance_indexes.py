"""
Sprint 4: Add performance indexes for UserOrganizationRole and DomainSettings.

Adds composite indexes to optimize frequent queries:
- UserOrganizationRole: (user, is_default) for middleware default org lookup
- UserOrganizationRole: (organization, role) for permission checks
- DomainSettings: (is_verified) for middleware domain resolution
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0004_make_organization_required'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='userorganizationrole',
            index=models.Index(
                fields=['user', 'is_default'],
                name='idx_uor_user_default'
            ),
        ),
        migrations.AddIndex(
            model_name='userorganizationrole',
            index=models.Index(
                fields=['organization', 'role'],
                name='idx_uor_org_role'
            ),
        ),
        migrations.AddIndex(
            model_name='domainsettings',
            index=models.Index(
                fields=['is_verified'],
                name='idx_domain_verified'
            ),
        ),
    ]
