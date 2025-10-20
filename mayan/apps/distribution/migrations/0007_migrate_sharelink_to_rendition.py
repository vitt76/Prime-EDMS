# Generated manually on 2025-10-20

from django.db import migrations, models
import django.db.models.deletion


def populate_rendition_field(apps, schema_editor):
    """Populate rendition field for existing ShareLink records"""
    ShareLink = apps.get_model('distribution', 'ShareLink')
    GeneratedRendition = apps.get_model('distribution', 'GeneratedRendition')

    # For existing ShareLink records, set rendition to the first available rendition
    # This is a fallback - in practice, you might need more sophisticated logic
    first_rendition = GeneratedRendition.objects.first()
    if first_rendition:
        ShareLink.objects.filter(rendition__isnull=True).update(rendition=first_rendition)


class Migration(migrations.Migration):

    dependencies = [
        ('distribution', '0006_add_recipient_to_renditionpreset'),
    ]

    operations = [
        # Add the rendition field as nullable first
        migrations.AddField(
            model_name='sharelink',
            name='rendition',
            field=models.ForeignKey(
                'GeneratedRendition',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='share_links',
                help_text='Rendition this link provides access to'
            ),
        ),

        # Populate the rendition field with default data
        migrations.RunPython(populate_rendition_field, migrations.RunPython.noop),

        # Remove the old publication field
        migrations.RemoveField(
            model_name='sharelink',
            name='publication',
        ),

        # Make rendition field non-nullable
        migrations.AlterField(
            model_name='sharelink',
            name='rendition',
            field=models.ForeignKey(
                'GeneratedRendition',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='share_links',
                help_text='Rendition this link provides access to'
            ),
        ),
    ]
