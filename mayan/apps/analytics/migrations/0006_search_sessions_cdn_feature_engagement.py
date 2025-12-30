import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('analytics', '0005_performance_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaigndailymetrics',
            name='avg_engagement_minutes',
            field=models.FloatField(blank=True, null=True, verbose_name='Avg engagement (minutes)'),
        ),
        migrations.AddField(
            model_name='searchquery',
            name='search_session_id',
            field=models.UUIDField(blank=True, db_index=True, null=True, verbose_name='Search session ID'),
        ),
        migrations.CreateModel(
            name='SearchSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('started_at', models.DateTimeField(db_index=True, verbose_name='Started at')),
                ('ended_at', models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Ended at')),
                ('time_to_find_seconds', models.IntegerField(blank=True, null=True, verbose_name='Time to find (seconds)')),
                ('first_search_query', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='first_search_sessions', to='analytics.searchquery', verbose_name='First search query')),
                ('last_download_event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='search_sessions_download', to='analytics.assetevent', verbose_name='Last download event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analytics_search_sessions', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'db_table': 'analytics_search_sessions',
            },
        ),
        migrations.CreateModel(
            name='CDNRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region', models.CharField(db_index=True, default='default', max_length=50, verbose_name='Region')),
                ('channel', models.CharField(db_index=True, default='default', max_length=50, verbose_name='Channel')),
                ('cost_per_gb_usd', models.DecimalField(decimal_places=4, default=0.1, max_digits=10, verbose_name='Cost per GB (USD)')),
                ('effective_from', models.DateField(db_index=True, verbose_name='Effective from')),
                ('effective_to', models.DateField(blank=True, db_index=True, null=True, verbose_name='Effective to')),
            ],
            options={
                'db_table': 'analytics_cdn_rates',
                'unique_together': {('region', 'channel', 'effective_from')},
            },
        ),
        migrations.CreateModel(
            name='CDNDailyCost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_index=True, verbose_name='Date')),
                ('region', models.CharField(default='default', max_length=50, verbose_name='Region')),
                ('channel', models.CharField(default='default', max_length=50, verbose_name='Channel')),
                ('bandwidth_gb', models.FloatField(default=0.0, verbose_name='Bandwidth (GB)')),
                ('cost_usd', models.DecimalField(decimal_places=2, default=0.0, max_digits=14, verbose_name='Cost (USD)')),
            ],
            options={
                'db_table': 'analytics_cdn_daily_costs',
                'unique_together': {('date', 'region', 'channel')},
            },
        ),
        migrations.CreateModel(
            name='FeatureUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feature_name', models.CharField(db_index=True, max_length=100, verbose_name='Feature name')),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Timestamp')),
                ('was_successful', models.BooleanField(default=True, verbose_name='Was successful')),
                ('metadata', models.JSONField(blank=True, default=dict, verbose_name='Metadata')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='analytics_feature_usage', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'db_table': 'analytics_feature_usage',
            },
        ),
        migrations.CreateModel(
            name='CampaignEngagementEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started_at', models.DateTimeField(db_index=True, verbose_name='Started at')),
                ('ended_at', models.DateTimeField(db_index=True, verbose_name='Ended at')),
                ('duration_seconds', models.PositiveIntegerField(verbose_name='Duration (seconds)')),
                ('metadata', models.JSONField(blank=True, default=dict, verbose_name='Metadata')),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='engagement_events', to='analytics.campaign', verbose_name='Campaign')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='analytics_campaign_engagement_events', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'db_table': 'analytics_campaign_engagement_events',
            },
        ),
        migrations.AddIndex(
            model_name='searchsession',
            index=models.Index(fields=['user', '-started_at'], name='analytics_searchsess_user_started_idx'),
        ),
        migrations.AddIndex(
            model_name='searchsession',
            index=models.Index(fields=['ended_at'], name='analytics_searchsess_ended_idx'),
        ),
        migrations.AddIndex(
            model_name='cdnrate',
            index=models.Index(fields=['channel', 'effective_from'], name='analytics_cdnrate_channel_from_idx'),
        ),
        migrations.AddIndex(
            model_name='cdndailycost',
            index=models.Index(fields=['date', 'channel'], name='analytics_cdn_daily_date_channel_idx'),
        ),
        migrations.AddIndex(
            model_name='cdndailycost',
            index=models.Index(fields=['date', 'region'], name='analytics_cdn_daily_date_region_idx'),
        ),
        migrations.AddIndex(
            model_name='featureusage',
            index=models.Index(fields=['feature_name', '-timestamp'], name='analytics_featuse_feat_ts_idx'),
        ),
        migrations.AddIndex(
            model_name='featureusage',
            index=models.Index(fields=['user', '-timestamp'], name='analytics_featuse_user_ts_idx'),
        ),
        migrations.AddIndex(
            model_name='campaignengagementevent',
            index=models.Index(fields=['campaign', '-started_at'], name='analytics_campevent_campaign_started_idx'),
        ),
        migrations.AddIndex(
            model_name='campaignengagementevent',
            index=models.Index(fields=['campaign', '-ended_at'], name='analytics_campevent_campaign_ended_idx'),
        ),
    ]


