from django.db import migrations


def populate_organization(apps, schema_editor):
    DocumentAIAnalysis = apps.get_model('dam', 'DocumentAIAnalysis')

    queryset = DocumentAIAnalysis.objects.select_related(
        'document'
    ).filter(organization__isnull=True)

    for analysis in queryset.iterator():
        document = getattr(analysis, 'document', None)
        if not document:
            continue

        organization_id = getattr(document, 'organization_id', None)
        if organization_id:
            analysis.organization_id = organization_id
            analysis.save(update_fields=['organization'])


class Migration(migrations.Migration):

    dependencies = [
        ('dam', '0007_add_organization_to_documentaianalysis'),
        ('documents', '0086_make_organization_required'),
    ]

    operations = [
        migrations.RunPython(populate_organization, migrations.RunPython.noop),
    ]
