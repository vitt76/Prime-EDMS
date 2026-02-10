"""
Make organization FK required and add composite index (Phase 3 of organizations integration).

Runs after organizations.0003_populate_default_organization has populated all records.
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0085_add_organization'),
        ('organizations', '0003_populate_default_organization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='organization',
            field=models.ForeignKey(
                db_index=True,
                help_text='Organization this document belongs to',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='documents',
                to='organizations.organization',
                verbose_name='Organization',
            ),
        ),
        migrations.AddIndex(
            model_name='document',
            index=models.Index(
                fields=['organization', '-datetime_created'],
                name='idx_doc_org_created',
            ),
        ),
    ]
