"""
Make organization FK required and add composite index (Phase 3 of organizations integration).
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cabinets', '0007_add_organization'),
        ('organizations', '0003_populate_default_organization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cabinet',
            name='organization',
            field=models.ForeignKey(
                db_index=True,
                help_text='Organization this cabinet belongs to',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='cabinets',
                to='organizations.organization',
                verbose_name='Organization',
            ),
        ),
        migrations.AddIndex(
            model_name='cabinet',
            index=models.Index(
                fields=['organization', 'label'],
                name='idx_cabinet_org_label',
            ),
        ),
    ]
