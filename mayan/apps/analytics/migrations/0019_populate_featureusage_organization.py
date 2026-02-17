# Generated for Analytics Transformation Feature 3.

from django.db import migrations


def populate_featureusage_organization(apps, schema_editor):
    FeatureUsage = apps.get_model('analytics', 'FeatureUsage')
    UserOrganizationRole = apps.get_model('organizations', 'UserOrganizationRole')
    Organization = apps.get_model('organizations', 'Organization')

    default_org = None
    for fu in FeatureUsage.objects.filter(organization__isnull=True).iterator():
        if fu.user_id:
            uor = (
                UserOrganizationRole.objects.filter(user_id=fu.user_id)
                .order_by('-is_default')
                .values_list('organization_id', flat=True)
                .first()
            )
            if uor:
                fu.organization_id = uor
                fu.save(update_fields=['organization_id'])
                continue
        if default_org is None:
            default_org = Organization.objects.filter(is_active=True).values_list('pk', flat=True).first()
        if default_org:
            fu.organization_id = default_org
            fu.save(update_fields=['organization_id'])
    # Ensure no nulls remain (required for NOT NULL in next migration).
    if default_org is None:
        default_org = Organization.objects.values_list('pk', flat=True).first()
    if default_org:
        FeatureUsage.objects.filter(organization__isnull=True).update(organization_id=default_org)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0018_add_organization_to_featureusage'),
        ('organizations', '0006_plan_cdn_cost_per_gb'),
    ]

    operations = [
        migrations.RunPython(populate_featureusage_organization, noop),
    ]
