from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('documents', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetEvent',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('event_type', models.CharField(choices=[('download', 'Download'), ('view', 'View'), ('share', 'Share'), ('upload', 'Upload'), ('deliver', 'Deliver')], db_index=True, max_length=50, verbose_name='Event type')),
                ('user_department', models.CharField(blank=True, default='', max_length=100, verbose_name='User department')),
                ('channel', models.CharField(blank=True, default='', help_text='Examples: dam_interface, public_link, portal, api', max_length=50, verbose_name='Channel')),
                ('intended_use', models.CharField(blank=True, default='', help_text='Examples: email, social, print, web', max_length=50, verbose_name='Intended use')),
                ('bandwidth_bytes', models.BigIntegerField(blank=True, null=True, verbose_name='Bandwidth (bytes)')),
                ('latency_seconds', models.IntegerField(blank=True, null=True, verbose_name='Latency (seconds)')),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Timestamp')),
                ('metadata', models.JSONField(blank=True, default=dict, verbose_name='Metadata')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analytics_events', to='documents.document', verbose_name='Document')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='analytics_asset_events', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Asset event',
                'verbose_name_plural': 'Asset events',
                'db_table': 'analytics_asset_events',
            },
        ),
        migrations.CreateModel(
            name='AssetDailyMetrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_index=True, verbose_name='Date')),
                ('downloads', models.PositiveIntegerField(default=0, verbose_name='Downloads')),
                ('views', models.PositiveIntegerField(default=0, verbose_name='Views')),
                ('shares', models.PositiveIntegerField(default=0, verbose_name='Shares')),
                ('cdn_bandwidth_gb', models.FloatField(default=0.0, verbose_name='CDN bandwidth (GB)')),
                ('performance_score', models.FloatField(default=0.0, verbose_name='Performance score')),
                ('top_channel', models.CharField(blank=True, default='', max_length=50, verbose_name='Top channel')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analytics_daily_metrics', to='documents.document', verbose_name='Document')),
            ],
            options={
                'verbose_name': 'Asset daily metrics',
                'verbose_name_plural': 'Asset daily metrics',
                'db_table': 'analytics_asset_daily_metrics',
            },
        ),
        migrations.AddIndex(
            model_name='assetevent',
            index=models.Index(fields=['document', '-timestamp'], name='analytics_as_document_86c97a_idx'),
        ),
        migrations.AddIndex(
            model_name='assetevent',
            index=models.Index(fields=['event_type', 'timestamp'], name='analytics_as_event_ty_8a4d6b_idx'),
        ),
        migrations.AddIndex(
            model_name='assetevent',
            index=models.Index(fields=['user', 'timestamp'], name='analytics_as_user_id_6fd7d3_idx'),
        ),
        migrations.AddIndex(
            model_name='assetdailymetrics',
            index=models.Index(fields=['date', '-performance_score'], name='analytics_as_date_06a6c4_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='assetdailymetrics',
            unique_together={('document', 'date')},
        ),
    ]


