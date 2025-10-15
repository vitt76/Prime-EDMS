# Generated manually for distribution app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Title of the publication', max_length=255, verbose_name='Title')),
                ('description', models.TextField(blank=True, help_text='Description of the publication', verbose_name='Description')),
                ('access_policy', models.CharField(choices=[('public', 'Public (token access)'), ('login', 'Login required'), ('both', 'Both public and login access')], default='public', help_text='Access policy for this publication', max_length=16, verbose_name='Access policy')),
                ('expires_at', models.DateTimeField(blank=True, help_text='Expiration date and time', null=True, verbose_name='Expires at')),
                ('max_downloads', models.IntegerField(blank=True, help_text='Maximum total downloads allowed', null=True, verbose_name='Max downloads')),
                ('downloads_count', models.IntegerField(default=0, help_text='Total downloads count', verbose_name='Downloads count')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('owner', models.ForeignKey(help_text='Owner of this publication', on_delete=django.db.models.deletion.CASCADE, related_name='publications', to=settings.AUTH_USER_MODEL, verbose_name='Owner')),
            ],
            options={
                'verbose_name': 'Publication',
                'verbose_name_plural': 'Publications',
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='Recipient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(help_text='Email address of the recipient', max_length=254, unique=True, verbose_name='Email')),
                ('name', models.CharField(blank=True, help_text='Full name of the recipient', max_length=255, verbose_name='Name')),
                ('organization', models.CharField(blank=True, help_text='Organization name', max_length=255, verbose_name='Organization')),
                ('locale', models.CharField(blank=True, help_text='Preferred language locale (e.g., en, ru)', max_length=10, verbose_name='Locale')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
            ],
            options={
                'verbose_name': 'Recipient',
                'verbose_name_plural': 'Recipients',
                'ordering': ['name', 'email'],
            },
        ),
        migrations.CreateModel(
            name='RenditionPreset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resource_type', models.CharField(choices=[('image', 'Image'), ('video', 'Video'), ('document', 'Document')], help_text='Type of resource this preset applies to', max_length=32, verbose_name='Resource type')),
                ('format', models.CharField(choices=[('jpeg', 'JPEG'), ('png', 'PNG'), ('tiff', 'TIFF'), ('pdf', 'PDF'), ('mp4', 'MP4')], help_text='Output format', max_length=16, verbose_name='Format')),
                ('width', models.IntegerField(blank=True, help_text='Maximum width in pixels (None for auto)', null=True, verbose_name='Width')),
                ('height', models.IntegerField(blank=True, help_text='Maximum height in pixels (None for auto)', null=True, verbose_name='Height')),
                ('quality', models.IntegerField(blank=True, help_text='Quality setting (0-100 for images, None for others)', null=True, verbose_name='Quality')),
                ('watermark', models.JSONField(blank=True, default=dict, help_text='Watermark settings as JSON', verbose_name='Watermark')),
                ('name', models.CharField(help_text='Unique name for this preset', max_length=255, unique=True, verbose_name='Name')),
                ('description', models.TextField(blank=True, help_text='Description of this preset', verbose_name='Description')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
            ],
            options={
                'verbose_name': 'Rendition Preset',
                'verbose_name_plural': 'Rendition Presets',
                'ordering': ['resource_type', 'format', 'name'],
            },
        ),
        migrations.CreateModel(
            name='ShareLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(default='f79b4d8e-8e9b-4b7a-9f7c-8e8b7a9f7c8e', help_text='Unique access token', max_length=64, unique=True, verbose_name='Token')),
                ('expires_at', models.DateTimeField(blank=True, help_text='Expiration date and time', null=True, verbose_name='Expires at')),
                ('max_downloads', models.IntegerField(blank=True, help_text='Maximum downloads allowed for this link', null=True, verbose_name='Max downloads')),
                ('downloads_count', models.IntegerField(default=0, help_text='Current downloads count', verbose_name='Downloads count')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('last_accessed', models.DateTimeField(blank=True, help_text='Last access timestamp', null=True, verbose_name='Last accessed')),
                ('publication', models.ForeignKey(help_text='Publication this link provides access to', on_delete=django.db.models.deletion.CASCADE, related_name='share_links', to='distribution.publication', verbose_name='Publication')),
                ('recipient', models.ForeignKey(blank=True, help_text='Specific recipient (None for general link)', null=True, on_delete=django.db.models.deletion.SET_NULL, to='distribution.recipient', verbose_name='Recipient')),
            ],
            options={
                'verbose_name': 'Share Link',
                'verbose_name_plural': 'Share Links',
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='RecipientList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the recipient list', max_length=255, verbose_name='Name')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('internal_users', models.ManyToManyField(blank=True, help_text='Internal users in this list', related_name='distribution_lists', to=settings.AUTH_USER_MODEL, verbose_name='Internal users')),
                ('owner', models.ForeignKey(help_text='Owner of this list', on_delete=django.db.models.deletion.CASCADE, related_name='owned_recipient_lists', to=settings.AUTH_USER_MODEL, verbose_name='Owner')),
                ('recipients', models.ManyToManyField(blank=True, help_text='External recipients in this list', related_name='recipient_lists', to='distribution.recipient', verbose_name='Recipients')),
            ],
            options={
                'verbose_name': 'Recipient List',
                'verbose_name_plural': 'Recipient Lists',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='PublicationItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('document_file', models.ForeignKey(help_text='Document file to include in publication', on_delete=django.db.models.deletion.CASCADE, to='documents.documentfile', verbose_name='Document file')),
                ('publication', models.ForeignKey(help_text='Publication this item belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='items', to='distribution.publication', verbose_name='Publication')),
            ],
            options={
                'verbose_name': 'Publication Item',
                'verbose_name_plural': 'Publication Items',
                'ordering': ['created'],
            },
        ),
        migrations.AddField(
            model_name='publication',
            name='presets',
            field=models.ManyToManyField(blank=True, help_text='Rendition presets to generate', related_name='publications', to='distribution.renditionpreset', verbose_name='Presets'),
        ),
        migrations.AddField(
            model_name='publication',
            name='recipient_lists',
            field=models.ManyToManyField(blank=True, help_text='Recipient lists for this publication', related_name='publications', to='distribution.recipientlist', verbose_name='Recipient lists'),
        ),
        migrations.CreateModel(
            name='AccessLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(choices=[('view', 'View'), ('download', 'Download')], help_text='Type of access event', max_length=16, verbose_name='Event')),
                ('ip_address', models.GenericIPAddressField(help_text='IP address of the client', verbose_name='IP address')),
                ('user_agent', models.TextField(blank=True, help_text='User agent string', verbose_name='User agent')),
                ('timestamp', models.DateTimeField(auto_now_add=True, help_text='When the access occurred', verbose_name='Timestamp')),
                ('share_link', models.ForeignKey(help_text='Share link that was accessed', on_delete=django.db.models.deletion.CASCADE, related_name='access_logs', to='distribution.sharelink', verbose_name='Share link')),
            ],
            options={
                'verbose_name': 'Access Log',
                'verbose_name_plural': 'Access Logs',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='GeneratedRendition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_path', models.CharField(help_text='Path to the generated file', max_length=500, verbose_name='File path')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', help_text='Generation status', max_length=16, verbose_name='Status')),
                ('file_size', models.BigIntegerField(blank=True, help_text='File size in bytes', null=True, verbose_name='File size')),
                ('checksum', models.CharField(blank=True, help_text='File checksum (MD5 or SHA256)', max_length=128, verbose_name='Checksum')),
                ('error_message', models.TextField(blank=True, help_text='Error message if generation failed', verbose_name='Error message')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('preset', models.ForeignKey(help_text='Preset used to generate this rendition', on_delete=django.db.models.deletion.CASCADE, to='distribution.renditionpreset', verbose_name='Preset')),
                ('publication_item', models.ForeignKey(help_text='Publication item this rendition is for', on_delete=django.db.models.deletion.CASCADE, related_name='renditions', to='distribution.publicationitem', verbose_name='Publication item')),
            ],
            options={
                'verbose_name': 'Generated Rendition',
                'verbose_name_plural': 'Generated Renditions',
                'ordering': ['-created'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='publicationitem',
            unique_together={('publication', 'document_file')},
        ),
        migrations.AlterUniqueTogether(
            name='generatedrendition',
            unique_together={('publication_item', 'preset')},
        ),
    ]
