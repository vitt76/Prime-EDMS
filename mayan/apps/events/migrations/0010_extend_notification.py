import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('events', '0009_alter_objecteventsubscription_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='uuid',
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='message',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='icon_type',
            field=models.CharField(blank=True, default='info', max_length=50),
        ),
        migrations.AddField(
            model_name='notification',
            name='icon_url',
            field=models.URLField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='notification',
            name='event_type',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='event_data',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='priority',
            field=models.CharField(blank=True, default='NORMAL', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='state',
            field=models.CharField(blank=True, default='CREATED', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='actions',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='content_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='contenttypes.contenttype'
            ),
        ),
        migrations.AddField(
            model_name='notification',
            name='object_id',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='read_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='archived_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='is_mutable',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='is_removable',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='metadata',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user', 'state'], name='events_notif_user_state_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user', 'event_type'], name='events_notif_user_event_type_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user', 'read'], name='events_notif_user_read_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['priority'], name='events_notif_priority_idx'),
        ),
    ]


