import uuid

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('events', '0009_alter_objecteventsubscription_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(max_length=64, unique=True, verbose_name='Event type')),
                ('title_template', models.CharField(max_length=255, verbose_name='Title template')),
                ('message_template', models.TextField(blank=True, default='', verbose_name='Message template')),
                ('icon_type', models.CharField(blank=True, default='info', max_length=50, verbose_name='Icon type')),
                ('icon_url', models.URLField(blank=True, default='', verbose_name='Icon URL')),
                ('default_priority', models.CharField(blank=True, default='NORMAL', max_length=20, verbose_name='Default priority')),
                ('recipients_config', models.JSONField(blank=True, default=dict, verbose_name='Recipients config')),
                ('actions', models.JSONField(blank=True, default=list, verbose_name='Actions')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated')),
            ],
            options={
                'verbose_name': 'Notification template',
                'verbose_name_plural': 'Notification templates',
                'db_table': 'notifications_template',
            },
        ),
        migrations.CreateModel(
            name='NotificationPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notifications_enabled', models.BooleanField(default=True, verbose_name='Notifications enabled')),
                ('email_notifications_enabled', models.BooleanField(default=True, verbose_name='Email notifications enabled')),
                ('push_notifications_enabled', models.BooleanField(default=True, verbose_name='Push notifications enabled')),
                ('email_digest_enabled', models.BooleanField(default=False, verbose_name='Email digest enabled')),
                ('email_digest_frequency', models.CharField(blank=True, default='never', max_length=20, verbose_name='Email digest frequency')),
                ('quiet_hours_enabled', models.BooleanField(default=False, verbose_name='Quiet hours enabled')),
                ('quiet_hours_start', models.TimeField(blank=True, null=True, verbose_name='Quiet hours start')),
                ('quiet_hours_end', models.TimeField(blank=True, null=True, verbose_name='Quiet hours end')),
                ('notification_language', models.CharField(blank=True, default='ru', max_length=10, verbose_name='Notification language')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated')),
                ('user', models.OneToOneField(on_delete=models.deletion.CASCADE, related_name='notification_preference', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Notification preference',
                'verbose_name_plural': 'Notification preferences',
                'db_table': 'notifications_preference',
            },
        ),
        migrations.CreateModel(
            name='NotificationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=50, verbose_name='Action')),
                ('action_data', models.JSONField(blank=True, default=dict, verbose_name='Action data')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='UUID')),
                ('notification', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='logs', to='events.notification', verbose_name='Notification')),
            ],
            options={
                'verbose_name': 'Notification log',
                'verbose_name_plural': 'Notification logs',
                'db_table': 'notifications_log',
            },
        ),
        migrations.AddIndex(
            model_name='notificationtemplate',
            index=models.Index(fields=['event_type'], name='notif_tpl_event_type_idx'),
        ),
        migrations.AddIndex(
            model_name='notificationpreference',
            index=models.Index(fields=['user'], name='notif_pref_user_idx'),
        ),
        migrations.AddIndex(
            model_name='notificationlog',
            index=models.Index(fields=['notification', '-timestamp'], name='notif_log_notif_ts_idx'),
        ),
    ]


