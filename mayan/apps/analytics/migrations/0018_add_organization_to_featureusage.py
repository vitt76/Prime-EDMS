# Generated for Analytics Transformation Feature 3.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0017_organizationbandwidthdaily'),
        ('organizations', '0006_plan_cdn_cost_per_gb'),
    ]

    operations = [
        migrations.AddField(
            model_name='featureusage',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                db_index=True,
                help_text='Organization this record belongs to',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='analytics_feature_usage',
                to='organizations.organization',
                verbose_name='Organization'
            ),
        ),
    ]
