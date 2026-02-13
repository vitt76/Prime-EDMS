from django.db import migrations


def populate_organization(apps, schema_editor):
    ShareLink = apps.get_model('distribution', 'ShareLink')
    Organization = apps.get_model('organizations', 'Organization')

    queryset = ShareLink.objects.filter(organization__isnull=True).select_related(
        'rendition__publication_item__document_file__document',
    )

    for share_link in queryset.iterator():
        try:
            rendition = share_link.rendition
            if not rendition:
                continue
            pub_item = getattr(rendition, 'publication_item', None)
            if not pub_item:
                continue
            doc_file = getattr(pub_item, 'document_file', None)
            if not doc_file:
                continue
            document = getattr(doc_file, 'document', None)
            if not document:
                continue
            organization_id = getattr(document, 'organization_id', None)
            if organization_id:
                share_link.organization_id = organization_id
                share_link.save(update_fields=['organization'])
        except Exception:
            continue

    # Сироты: привязать к default организации
    default_org = Organization.objects.filter(slug='default').first()
    if default_org:
        ShareLink.objects.filter(organization__isnull=True).update(organization=default_org)


class Migration(migrations.Migration):

    dependencies = [
        ('distribution', '0012_add_organization_to_sharelink'),
        ('documents', '0086_make_organization_required'),
    ]

    operations = [
        migrations.RunPython(populate_organization, migrations.RunPython.noop),
    ]
