# Phase 5.1 Sprint 1 Backend: orientation filter (DocumentFile width/height)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0086_make_organization_required'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentfile',
            name='width',
            field=models.PositiveIntegerField(
                blank=True,
                editable=False,
                help_text='Image/page width in pixels (first page). Used for orientation filter.',
                null=True,
                verbose_name='Width'
            ),
        ),
        migrations.AddField(
            model_name='documentfile',
            name='height',
            field=models.PositiveIntegerField(
                blank=True,
                editable=False,
                help_text='Image/page height in pixels (first page). Used for orientation filter.',
                null=True,
                verbose_name='Height'
            ),
        ),
    ]
