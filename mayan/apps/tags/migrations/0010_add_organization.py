"""
Add organization FK to Tag and update unique constraint (Phase 1 of organizations integration).

Depends on organizations.0001_initial.
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0009_alter_tag_color'),
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                db_index=True,
                help_text='Organization this tag belongs to',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='tags',
                to='organizations.organization',
                verbose_name='Organization',
            ),
        ),
        migrations.AlterField(
            model_name='tag',
            name='label',
            field=models.CharField(
                db_index=True,
                help_text='A short text used as the tag name.',
                max_length=128,
                verbose_name='Label',
            ),
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together={('organization', 'label')},
        ),
    ]
