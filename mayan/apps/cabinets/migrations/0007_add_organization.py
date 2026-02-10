"""
Add organization FK to Cabinet (Phase 1 of organizations integration).

Depends on organizations.0001_initial.
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cabinets', '0006_auto_20210525_0604'),
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cabinet',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                db_index=True,
                help_text='Organization this cabinet belongs to',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='cabinets',
                to='organizations.organization',
                verbose_name='Organization',
            ),
        ),
        migrations.AlterUniqueTogether(
            name='cabinet',
            unique_together={('organization', 'parent', 'label')},
        ),
    ]
