# Generated for Analytics Transformation Feature 2 (CDN Cost per tenant).

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0016_make_searchsession_organization_required'),
        ('organizations', '0006_plan_cdn_cost_per_gb'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationBandwidthDaily',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_index=True, verbose_name='Date')),
                ('bandwidth_gb', models.FloatField(default=0.0, verbose_name='Bandwidth (GB)')),
                ('cost_usd', models.DecimalField(decimal_places=2, default=0.0, max_digits=14, verbose_name='Cost (USD)')),
                ('organization', models.ForeignKey(db_index=True, on_delete=django.db.models.deletion.CASCADE, related_name='analytics_bandwidth_daily', to='organizations.organization', verbose_name='Organization')),
            ],
            options={
                'verbose_name': 'Organization bandwidth daily',
                'verbose_name_plural': 'Organization bandwidth daily',
                'db_table': 'analytics_organization_bandwidth_daily',
                'unique_together': {('organization', 'date')},
            },
        ),
        migrations.AddIndex(
            model_name='organizationbandwidthdaily',
            index=models.Index(fields=['organization', '-date'], name='idx_anal_obd_org_date'),
        ),
    ]
