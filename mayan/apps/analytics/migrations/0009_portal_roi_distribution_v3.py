from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('analytics', '0008_distribution_events'),
        ('documents', '0001_initial'),
        ('distribution', '0011_auto_20251225_1037'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PortalSession',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('session_key', models.CharField(blank=True, db_index=True, default='', max_length=128, verbose_name='Session key')),
                ('ip_address', models.CharField(blank=True, db_index=True, default='', max_length=64, verbose_name='IP address')),
                ('user_agent', models.TextField(blank=True, default='', verbose_name='User agent')),
                ('started_at', models.DateTimeField(db_index=True, verbose_name='Started at')),
                ('last_seen_at', models.DateTimeField(db_index=True, verbose_name='Last seen at')),
                ('views', models.PositiveIntegerField(default=0, verbose_name='Views')),
                ('downloads', models.PositiveIntegerField(default=0, verbose_name='Downloads')),
                ('metadata', models.JSONField(blank=True, default=dict, verbose_name='Metadata')),
                ('campaign', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='portal_sessions', to='analytics.campaign', verbose_name='Campaign')),
                ('document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='portal_sessions', to='documents.document', verbose_name='Document')),
                ('publication', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='analytics_portal_sessions', to='distribution.publication', verbose_name='Publication')),
                ('share_link', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='analytics_portal_sessions', to='distribution.sharelink', verbose_name='Share link')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='portal_sessions', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'db_table': 'analytics_portal_sessions',
                'verbose_name': 'Portal session',
                'verbose_name_plural': 'Portal sessions',
            },
        ),
        migrations.CreateModel(
            name='UserCostProfile',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('hourly_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=12, verbose_name='Hourly rate')),
                ('currency', models.CharField(blank=True, default='USD', max_length=10, verbose_name='Currency')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cost_profile', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'db_table': 'analytics_user_cost_profiles',
                'verbose_name': 'User cost profile',
                'verbose_name_plural': 'User cost profiles',
            },
        ),
        migrations.CreateModel(
            name='DocumentCostProfile',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('production_cost', models.DecimalField(decimal_places=2, default=0.0, max_digits=14, verbose_name='Production cost')),
                ('currency', models.CharField(blank=True, default='USD', max_length=10, verbose_name='Currency')),
                ('document', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cost_profile', to='documents.document', verbose_name='Document')),
            ],
            options={
                'db_table': 'analytics_document_cost_profiles',
                'verbose_name': 'Document cost profile',
                'verbose_name_plural': 'Document cost profiles',
            },
        ),
        migrations.AddField(
            model_name='distributionevent',
            name='sync_status',
            field=models.CharField(blank=True, db_index=True, default='', max_length=50, verbose_name='Sync status'),
        ),
        migrations.AddField(
            model_name='distributionevent',
            name='last_sync_error',
            field=models.TextField(blank=True, default='', verbose_name='Last sync error'),
        ),
        migrations.AddField(
            model_name='distributionevent',
            name='retry_count',
            field=models.PositiveIntegerField(default=0, verbose_name='Retry count'),
        ),
        migrations.AddIndex(
            model_name='portalsession',
            index=models.Index(fields=('share_link', '-last_seen_at'), name='analytics_po_share_l_0c6bdc_idx'),
        ),
        migrations.AddIndex(
            model_name='portalsession',
            index=models.Index(fields=('publication', '-last_seen_at'), name='analytics_po_publica_91c5e4_idx'),
        ),
        migrations.AddIndex(
            model_name='portalsession',
            index=models.Index(fields=('document', '-last_seen_at'), name='analytics_po_documen_0bb6d7_idx'),
        ),
        migrations.AddIndex(
            model_name='portalsession',
            index=models.Index(fields=('campaign', '-last_seen_at'), name='analytics_po_campaig_aeeb0e_idx'),
        ),
    ]


