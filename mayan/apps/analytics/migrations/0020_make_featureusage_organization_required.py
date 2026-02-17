# Generated for Analytics Transformation Feature 3.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0019_populate_featureusage_organization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='featureusage',
            name='organization',
            field=models.ForeignKey(
                db_index=True,
                help_text='Organization this record belongs to',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='analytics_feature_usage',
                to='organizations.organization',
                verbose_name='Organization'
            ),
        ),
        migrations.AddIndex(
            model_name='featureusage',
            index=models.Index(
                fields=['organization', 'feature_name', '-timestamp'],
                name='idx_anal_fu_org_feat_ts'
            ),
        ),
    ]
