# Phase 5.3 Sprint 1 Backend: SavedSearch model (tenant-aware)

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organizations', '0006_plan_cdn_cost_per_gb'),
    ]

    operations = [
        migrations.CreateModel(
            name='SavedSearch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('query', models.CharField(blank=True, default='', help_text='Full-text search query (q)', max_length=512, verbose_name='Query')),
                ('filters', models.JSONField(blank=True, default=dict, help_text='Filters: orientation, document_type__label__in, tags__label__in, datetime_created__gte, etc.', verbose_name='Filters')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('notification_enabled', models.BooleanField(default=False, verbose_name='Notification enabled')),
                ('last_notified_at', models.DateTimeField(blank=True, null=True, verbose_name='Last notified at')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saved_searches', to='organizations.organization', verbose_name='Organization')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saved_searches', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Saved search',
                'verbose_name_plural': 'Saved searches',
            },
        ),
    ]
