import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0084_document_fulltext_search'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('analytics', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, serialize=False)),
                ('label', models.CharField(max_length=255, db_index=True)),
                ('description', models.TextField(blank=True, default='')),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('active', 'Active'), ('completed', 'Completed'), ('archived', 'Archived')], db_index=True, default='draft', max_length=50)),
                ('start_date', models.DateField(blank=True, db_index=True, null=True)),
                ('end_date', models.DateField(blank=True, db_index=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('cost_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ('revenue_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ('currency', models.CharField(blank=True, default='RUB', max_length=10)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='analytics_campaigns_created', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'analytics_campaigns',
            },
        ),
        migrations.CreateModel(
            name='SearchDailyMetrics',
            fields=[
                ('date', models.DateField(primary_key=True, serialize=False)),
                ('total_searches', models.PositiveIntegerField(default=0)),
                ('successful_searches', models.PositiveIntegerField(default=0)),
                ('null_searches', models.PositiveIntegerField(default=0)),
                ('ctr', models.FloatField(blank=True, null=True)),
                ('avg_response_time_ms', models.IntegerField(blank=True, null=True)),
                ('top_queries', models.JSONField(blank=True, default=list)),
                ('null_queries', models.JSONField(blank=True, default=list)),
            ],
            options={
                'db_table': 'analytics_search_daily_metrics',
            },
        ),
        migrations.CreateModel(
            name='SearchQuery',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('query_text', models.CharField(db_index=True, max_length=500)),
                ('search_type', models.CharField(choices=[('keyword', 'Keyword'), ('filter', 'Filter'), ('faceted', 'Faceted'), ('ai', 'AI')], db_index=True, default='keyword', max_length=50)),
                ('results_count', models.IntegerField(blank=True, null=True)),
                ('response_time_ms', models.IntegerField(blank=True, null=True)),
                ('filters_applied', models.JSONField(blank=True, default=dict)),
                ('was_clicked_result_document_id', models.IntegerField(blank=True, null=True)),
                ('click_position', models.IntegerField(blank=True, null=True)),
                ('time_to_click_seconds', models.IntegerField(blank=True, null=True)),
                ('was_downloaded', models.BooleanField(default=False)),
                ('time_to_download_seconds', models.IntegerField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('user_department', models.CharField(blank=True, db_index=True, default='', max_length=100)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='analytics_search_queries', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'analytics_search_queries',
            },
        ),
        migrations.CreateModel(
            name='UserDailyMetrics',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('date', models.DateField(db_index=True)),
                ('logins', models.PositiveIntegerField(default=0)),
                ('searches', models.PositiveIntegerField(default=0)),
                ('downloads', models.PositiveIntegerField(default=0)),
                ('search_success_rate', models.FloatField(blank=True, null=True)),
                ('avg_search_to_find_minutes', models.IntegerField(blank=True, null=True)),
                ('user_department', models.CharField(blank=True, db_index=True, default='', max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analytics_daily_metrics', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'analytics_user_daily_metrics',
                'unique_together': {('user', 'date')},
            },
        ),
        migrations.CreateModel(
            name='UserSession',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('session_key', models.CharField(blank=True, db_index=True, default='', max_length=128)),
                ('login_timestamp', models.DateTimeField(db_index=True)),
                ('logout_timestamp', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('session_duration_seconds', models.IntegerField(blank=True, null=True)),
                ('geo_country', models.CharField(blank=True, default='', max_length=2)),
                ('geo_city', models.CharField(blank=True, default='', max_length=100)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True, default='')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analytics_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'analytics_user_sessions',
            },
        ),
        migrations.CreateModel(
            name='CampaignAsset',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('sequence', models.PositiveIntegerField(default=0)),
                ('added_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='campaign_assets', to='analytics.campaign')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='campaign_memberships', to='documents.document')),
            ],
            options={
                'db_table': 'analytics_campaign_assets',
                'unique_together': {('campaign', 'document')},
            },
        ),
        migrations.CreateModel(
            name='CampaignDailyMetrics',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('date', models.DateField(db_index=True)),
                ('views', models.PositiveIntegerField(default=0)),
                ('downloads', models.PositiveIntegerField(default=0)),
                ('shares', models.PositiveIntegerField(default=0)),
                ('roi', models.FloatField(blank=True, null=True)),
                ('channel_breakdown', models.JSONField(blank=True, default=dict)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_metrics', to='analytics.campaign')),
                ('top_document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='campaign_top_document_metrics', to='documents.document')),
            ],
            options={
                'db_table': 'analytics_campaign_daily_metrics',
                'unique_together': {('campaign', 'date')},
            },
        ),
        migrations.AddIndex(
            model_name='campaign',
            index=models.Index(fields=['status', '-updated_at'], name='analytics_c_status_1056e5_idx'),
        ),
        migrations.AddIndex(
            model_name='campaignasset',
            index=models.Index(fields=['campaign', 'sequence'], name='analytics_c_campaign_28f13e_idx'),
        ),
        migrations.AddIndex(
            model_name='campaignasset',
            index=models.Index(fields=['campaign', '-added_at'], name='analytics_c_campaign_5d0cb2_idx'),
        ),
        migrations.AddIndex(
            model_name='campaigndailymetrics',
            index=models.Index(fields=['campaign', '-date'], name='analytics_c_campaign_2d5a90_idx'),
        ),
        migrations.AddIndex(
            model_name='searchquery',
            index=models.Index(fields=['-timestamp'], name='analytics_s__timest_4130a5_idx'),
        ),
        migrations.AddIndex(
            model_name='searchquery',
            index=models.Index(fields=['search_type', '-timestamp'], name='analytics_s_search__8c8143_idx'),
        ),
        migrations.AddIndex(
            model_name='userdailymetrics',
            index=models.Index(fields=['date', 'user_department'], name='analytics_u_date_us_1a7e12_idx'),
        ),
        migrations.AddIndex(
            model_name='usersession',
            index=models.Index(fields=['user', '-login_timestamp'], name='analytics_u_user_-l_39b0b2_idx'),
        ),
        migrations.AddIndex(
            model_name='usersession',
            index=models.Index(fields=['login_timestamp'], name='analytics_u_login_t_31b099_idx'),
        ),
    ]


