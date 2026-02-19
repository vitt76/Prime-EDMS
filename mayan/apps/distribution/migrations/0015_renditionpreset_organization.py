# Sprint 3.3: Tenant-aware rendition presets

from django.db import migrations, models
import django.db.models.deletion


def create_default_presets(apps, schema_editor):
    """Create 3 default channel presets: Instagram 1:1, VK 1200, Печать A4."""
    Recipient = apps.get_model('distribution', 'Recipient')
    RenditionPreset = apps.get_model('distribution', 'RenditionPreset')

    recipient, _ = Recipient.objects.get_or_create(
        email='default-presets@system',
        defaults={'name': 'Default (presets)', 'organization': ''}
    )

    defaults = [
        {
            'name': 'Instagram 1:1 1080',
            'description': 'Квадрат 1080×1080 для Instagram',
            'resource_type': 'image',
            'format': 'webp',
            'width': 1080,
            'height': 1080,
            'crop': True,
            'quality': 85,
        },
        {
            'name': 'VK 1200',
            'description': 'Ширина 1200px для ВКонтакте',
            'resource_type': 'image',
            'format': 'jpeg',
            'width': 1200,
            'height': None,
            'crop': False,
            'quality': 88,
        },
        {
            'name': 'Печать A4 300 dpi',
            'description': 'A4 300 DPI для печати',
            'resource_type': 'image',
            'format': 'tiff',
            'width': 2480,
            'height': 3508,
            'dpi_x': 300,
            'dpi_y': 300,
            'crop': False,
            'quality': None,
        },
    ]
    for d in defaults:
        RenditionPreset.objects.get_or_create(
            name=d['name'],
            defaults={
                'recipient': recipient,
                'organization': None,
                'description': d['description'],
                'resource_type': d['resource_type'],
                'format': d['format'],
                'width': d.get('width'),
                'height': d.get('height'),
                'dpi_x': d.get('dpi_x'),
                'dpi_y': d.get('dpi_y'),
                'crop': d.get('crop', False),
                'quality': d.get('quality'),
            }
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    atomic = False  # Avoid "pending trigger events" on PostgreSQL when adding FK+index

    dependencies = [
        ('organizations', '0001_initial'),
        ('distribution', '0014_make_sharelink_organization_required'),
    ]

    operations = [
        migrations.AddField(
            model_name='renditionpreset',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                help_text='Organization (tenant). Null = global preset visible to all.',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='rendition_presets',
                to='organizations.organization'
            ),
        ),
        migrations.RunPython(create_default_presets, noop_reverse),
    ]
