from django.db import migrations


def populate_organization(apps, schema_editor):
    AssetEvent = apps.get_model('analytics', 'AssetEvent')

    queryset = AssetEvent.objects.select_related('document').filter(
        organization__isnull=True
    )

    for event in queryset.iterator():
        document = getattr(event, 'document', None)
        if not document:
            continue
        organization_id = getattr(document, 'organization_id', None)
        if organization_id:
            event.organization_id = organization_id
            event.save(update_fields=['organization'])


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0010_add_organization_to_assetevent'),
        ('documents', '0086_make_organization_required'),
    ]

    operations = [
        migrations.RunPython(populate_organization, migrations.RunPython.noop),
    ]
