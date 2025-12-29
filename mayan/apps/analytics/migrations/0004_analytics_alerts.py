from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('analytics', '0003_approval_workflow_event'),
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalyticsAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alert_type', models.CharField(db_index=True, max_length=50, verbose_name='Alert type')),
                ('severity', models.CharField(choices=[('critical', 'Critical'), ('warning', 'Warning'), ('info', 'Info')], db_index=True, max_length=20, verbose_name='Severity')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('message', models.TextField(blank=True, default='', verbose_name='Message')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Created at')),
                ('resolved_at', models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Resolved at')),
                ('metadata', models.JSONField(blank=True, default=dict, verbose_name='Metadata')),
                ('campaign', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='analytics_alerts', to='analytics.campaign', verbose_name='Campaign')),
                ('document', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='analytics_alerts', to='documents.document', verbose_name='Document')),
            ],
            options={
                'verbose_name': 'Analytics alert',
                'verbose_name_plural': 'Analytics alerts',
                'db_table': 'analytics_alerts',
            },
        ),
        migrations.AddIndex(
            model_name='analyticsalert',
            index=models.Index(fields=['alert_type', '-created_at'], name='analytics_al_alert_t_1ab09c_idx'),
        ),
        migrations.AddIndex(
            model_name='analyticsalert',
            index=models.Index(fields=['severity', '-created_at'], name='analytics_al_severity_3d1c68_idx'),
        ),
        migrations.AddIndex(
            model_name='analyticsalert',
            index=models.Index(fields=['resolved_at'], name='analytics_al_resolved_8fdd22_idx'),
        ),
    ]


