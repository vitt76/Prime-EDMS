# Migration to add signals and handlers

from django.db import migrations


def create_signal_handlers(apps, schema_editor):
    """Create signal handlers for automatic conversion"""
    # This will be handled by the app's ready() method
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('converter_pipeline_extension', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            code=create_signal_handlers,
            reverse_code=migrations.RunPython.noop,
        ),
    ]

