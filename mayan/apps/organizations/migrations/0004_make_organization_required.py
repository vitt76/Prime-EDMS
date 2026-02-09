"""
Phase 3: Make organization FK required (NOT NULL) and add indexes.

After data migration (0003) has populated all records with the default
Organization, this migration enforces the NOT NULL constraint and adds
composite indexes for query performance.
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0003_populate_default_organization'),
    ]

    operations = [
        # --- Document: make organization required ---
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
            app_label='documents',
        ),

        # --- Tag: make organization required ---
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
            app_label='tags',
        ),

        # --- Cabinet: make organization required ---
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
            app_label='cabinets',
        ),

        # --- Composite indexes for performance ---
        migrations.AddIndex(
            model_name='document',
            index=models.Index(
                fields=['organization', '-datetime_created'],
                name='idx_doc_org_created',
            ),
            app_label='documents',
        ),
        migrations.AddIndex(
            model_name='tag',
            index=models.Index(
                fields=['organization', 'label'],
                name='idx_tag_org_label',
            ),
            app_label='tags',
        ),
        migrations.AddIndex(
            model_name='cabinet',
            index=models.Index(
                fields=['organization', 'label'],
                name='idx_cabinet_org_label',
            ),
            app_label='cabinets',
        ),
    ]
