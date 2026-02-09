"""
Phase 1: Add nullable organization FK to core models.

Adds organization ForeignKey (nullable) to:
- documents.Document
- tags.Tag
- cabinets.Cabinet

Also updates unique constraints:
- tags.Tag: label unique -> unique_together (organization, label)
- cabinets.Cabinet: unique_together (parent, label) -> (organization, parent, label)
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
        ('documents', '0084_document_fulltext_search'),
        ('tags', '0009_alter_tag_color'),
        ('cabinets', '0006_auto_20210525_0604'),
    ]

    operations = [
        # --- Document: add organization FK ---
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
            app_label='documents',
        ),

        # --- Tag: add organization FK ---
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
            app_label='tags',
        ),

        # --- Tag: change unique constraint from label to (organization, label) ---
        migrations.AlterField(
            model_name='tag',
            name='label',
            field=models.CharField(
                db_index=True,
                help_text='A short text used as the tag name.',
                max_length=128,
                verbose_name='Label',
                # Remove unique=True; uniqueness will be enforced by
                # unique_together below.
            ),
            app_label='tags',
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together={('organization', 'label')},
            app_label='tags',
        ),

        # --- Cabinet: add organization FK ---
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
            app_label='cabinets',
        ),

        # --- Cabinet: update unique_together to include organization ---
        migrations.AlterUniqueTogether(
            name='cabinet',
            unique_together={('organization', 'parent', 'label')},
            app_label='cabinets',
        ),
    ]
