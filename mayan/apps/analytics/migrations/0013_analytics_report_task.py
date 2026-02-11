import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0012_make_assetevent_organization_required'),
        ('organizations', '0005_add_performance_indexes'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalyticsReportTask',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('report_type', models.CharField(
                    choices=[
                        ('asset_usage', 'Asset usage'),
                        ('campaign_roi', 'Campaign ROI'),
                        ('user_activity', 'User activity'),
                    ],
                    db_index=True,
                    max_length=50,
                    verbose_name='Report type'
                )),
                ('parameters', models.JSONField(
                    blank=True,
                    default=dict,
                    verbose_name='Parameters'
                )),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pending'),
                        ('processing', 'Processing'),
                        ('completed', 'Completed'),
                        ('failed', 'Failed'),
                    ],
                    db_index=True,
                    default='pending',
                    max_length=20,
                    verbose_name='Status'
                )),
                ('file_path', models.CharField(
                    blank=True,
                    max_length=500,
                    null=True,
                    verbose_name='File path'
                )),
                ('created_at', models.DateTimeField(
                    auto_now_add=True,
                    db_index=True,
                    verbose_name='Created at'
                )),
                ('completed_at', models.DateTimeField(
                    blank=True,
                    null=True,
                    verbose_name='Completed at'
                )),
                ('organization', models.ForeignKey(
                    db_index=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='analytics_report_tasks',
                    to='organizations.organization',
                    verbose_name='Organization'
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='analytics_report_tasks',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='User'
                )),
            ],
            options={
                'verbose_name': 'Analytics report task',
                'verbose_name_plural': 'Analytics report tasks',
                'db_table': 'analytics_report_tasks',
            },
        ),
        migrations.AddIndex(
            model_name='analyticsreporttask',
            index=models.Index(
                fields=['organization', '-created_at'],
                name='idx_analytics_rt_org_created'
            ),
        ),
    ]
