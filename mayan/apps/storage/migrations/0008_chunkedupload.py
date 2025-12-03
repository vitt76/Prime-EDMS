"""
Migration for ChunkedUpload model.
Phase B3.2 - Chunked Upload API Support.
"""
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('storage', '0007_auto_20210218_0708'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChunkedUpload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('upload_id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True, verbose_name='Upload ID')),
                ('filename', models.CharField(max_length=512, verbose_name='Filename')),
                ('total_size', models.BigIntegerField(help_text='Total file size in bytes', verbose_name='Total Size')),
                ('content_type', models.CharField(default='application/octet-stream', max_length=255, verbose_name='Content Type')),
                ('uploaded_size', models.BigIntegerField(default=0, help_text='Bytes uploaded so far', verbose_name='Uploaded Size')),
                ('chunks_received', models.PositiveIntegerField(default=0, verbose_name='Chunks Received')),
                ('status', models.CharField(choices=[
                    ('pending', 'Pending'),
                    ('uploading', 'Uploading'),
                    ('completed', 'Completed'),
                    ('aborted', 'Aborted'),
                    ('failed', 'Failed')
                ], db_index=True, default='pending', max_length=20, verbose_name='Status')),
                ('s3_upload_id', models.CharField(blank=True, help_text='S3 Multipart Upload ID', max_length=255, null=True, verbose_name='S3 Upload ID')),
                ('s3_key', models.CharField(blank=True, help_text='S3 object key for the uploaded file', max_length=1024, null=True, verbose_name='S3 Key')),
                ('parts_info', models.JSONField(blank=True, default=list, help_text='JSON array of uploaded parts metadata', verbose_name='Parts Info')),
                ('datetime_created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('datetime_updated', models.DateTimeField(auto_now=True, verbose_name='Updated')),
                ('datetime_completed', models.DateTimeField(blank=True, null=True, verbose_name='Completed')),
                ('document_id', models.PositiveIntegerField(blank=True, help_text='ID of created document after successful upload', null=True, verbose_name='Document ID')),
                ('error_message', models.TextField(blank=True, null=True, verbose_name='Error Message')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Chunked Upload',
                'verbose_name_plural': 'Chunked Uploads',
                'ordering': ['-datetime_created'],
            },
        ),
        migrations.AddIndex(
            model_name='chunkedupload',
            index=models.Index(fields=['upload_id'], name='storage_chu_upload__86b1d5_idx'),
        ),
        migrations.AddIndex(
            model_name='chunkedupload',
            index=models.Index(fields=['status', 'datetime_created'], name='storage_chu_status_5c3b4e_idx'),
        ),
        migrations.AddIndex(
            model_name='chunkedupload',
            index=models.Index(fields=['user', 'status'], name='storage_chu_user_id_3f1a2b_idx'),
        ),
    ]

