# Sprint 5.2: Allow AssetEvent without document (e.g. collection_share)

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0020_make_featureusage_organization_required'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assetevent',
            name='document',
            field=models.ForeignKey(
                blank=True,
                help_text='Optional; null for non-document events (e.g. collection_share)',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='analytics_events',
                to='documents.document',
                verbose_name='Document'
            ),
        ),
    ]
