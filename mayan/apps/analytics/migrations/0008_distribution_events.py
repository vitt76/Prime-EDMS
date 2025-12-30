from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('analytics', '0007_performance_indexes_v2'),
        ('documents', '0084_document_fulltext_search'),
    ]

    operations = [
        migrations.CreateModel(
            name='DistributionEvent',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('channel', models.CharField(db_index=True, max_length=50)),
                ('event_type', models.CharField(choices=[('synced', 'Synced'), ('converted', 'Converted'), ('published', 'Published'), ('delivered', 'Delivered'), ('error', 'Error')], db_index=True, max_length=50)),
                ('status', models.CharField(choices=[('ok', 'OK'), ('warning', 'Warning'), ('error', 'Error'), ('syncing', 'Syncing')], db_index=True, max_length=20)),
                ('views', models.PositiveIntegerField(blank=True, null=True)),
                ('clicks', models.PositiveIntegerField(blank=True, null=True)),
                ('conversions', models.PositiveIntegerField(blank=True, null=True)),
                ('revenue_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True)),
                ('currency', models.CharField(blank=True, default='', max_length=10)),
                ('bandwidth_bytes', models.BigIntegerField(blank=True, null=True)),
                ('latency_ms', models.IntegerField(blank=True, null=True)),
                ('external_id', models.CharField(blank=True, db_index=True, default='', max_length=255)),
                ('occurred_at', models.DateTimeField(db_index=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('campaign', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='analytics_distribution_events', to='analytics.campaign')),
                ('document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='analytics_distribution_events', to='documents.document')),
            ],
            options={
                'db_table': 'analytics_distribution_events',
            },
        ),
        migrations.AddIndex(
            model_name='distributionevent',
            index=models.Index(fields=['channel', '-occurred_at'], name='analytics_di_channel_7c3038_idx'),
        ),
        migrations.AddIndex(
            model_name='distributionevent',
            index=models.Index(fields=['event_type', '-occurred_at'], name='analytics_di_event_t_7a9c8f_idx'),
        ),
        migrations.AddIndex(
            model_name='distributionevent',
            index=models.Index(fields=['status', '-occurred_at'], name='analytics_di_status_61e7aa_idx'),
        ),
        migrations.AddIndex(
            model_name='distributionevent',
            index=models.Index(fields=['document', '-occurred_at'], name='analytics_di_documen_b9e2f1_idx'),
        ),
        migrations.AddIndex(
            model_name='distributionevent',
            index=models.Index(fields=['campaign', '-occurred_at'], name='analytics_di_campaig_7b38e2_idx'),
        ),
    ]


