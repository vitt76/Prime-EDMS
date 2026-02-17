# Generated for Analytics Transformation Feature 1.

from django.db import migrations


def populate_searchsession_organization(apps, schema_editor):
    SearchSession = apps.get_model('analytics', 'SearchSession')
    UserOrganizationRole = apps.get_model('organizations', 'UserOrganizationRole')
    Organization = apps.get_model('organizations', 'Organization')

    sessions = SearchSession.objects.filter(organization__isnull=True).select_related('user')
    default_org = None

    for session in sessions.iterator():
        if not session.user_id:
            continue
        # Prefer user's default org, then any org the user belongs to.
        uor = (
            UserOrganizationRole.objects.filter(user_id=session.user_id)
            .order_by('-is_default')
            .values_list('organization_id', flat=True)
            .first()
        )
        if uor:
            session.organization_id = uor
            session.save(update_fields=['organization_id'])
            continue
        # Fallback: first active organization.
        if default_org is None:
            default_org = Organization.objects.filter(is_active=True).values_list('pk', flat=True).first()
        if default_org:
            session.organization_id = default_org
            session.save(update_fields=['organization_id'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0014_add_searchsession_org_assetevent_session'),
        ('organizations', '0005_add_performance_indexes'),
    ]

    operations = [
        migrations.RunPython(populate_searchsession_organization, noop),
    ]
