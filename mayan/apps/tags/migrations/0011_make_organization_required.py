"""
Make organization FK required and add composite index (Phase 3 of organizations integration).
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0010_add_organization'),
        ('organizations', '0003_populate_default_organization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='organization',
            field=models.ForeignKey(
                db_index=True,
                help_text='Organization this tag belongs to',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='tags',
                to='organizations.organization',
                verbose_name='Organization',
            ),
        ),
        migrations.AddIndex(
            model_name='tag',
            index=models.Index(
                fields=['organization', 'label'],
                name='idx_tag_org_label',
            ),
        ),
    ]
