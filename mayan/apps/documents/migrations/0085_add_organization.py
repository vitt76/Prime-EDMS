"""
Add organization FK to Document (Phase 1 of organizations integration).

Depends on organizations.0001_initial. The field is nullable until 0003 populates
and 0086 makes it required.
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0084_document_fulltext_search'),
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                db_index=True,
                help_text='Organization this document belongs to',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='documents',
                to='organizations.organization',
                verbose_name='Organization',
            ),
        ),
    ]
