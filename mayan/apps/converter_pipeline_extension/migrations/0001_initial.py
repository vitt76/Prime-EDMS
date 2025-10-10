# Migration for Converter Pipeline Extension

from django.db import migrations, models
import django.db.models.deletion


def load_initial_format_data(apps, schema_editor):
    """Load initial data for supported formats"""
    ConversionFormatSupport = apps.get_model('converter_pipeline_extension', 'ConversionFormatSupport')

    # RAW images
    raw_formats = [
        ('image/x-canon-cr2', 'Canon CR2', 'raw_image', 'dcraw', 10),
        ('image/x-nikon-nef', 'Nikon NEF', 'raw_image', 'libraw', 10),
        ('image/x-sony-arw', 'Sony ARW', 'raw_image', 'libraw', 10),
        ('image/x-adobe-dng', 'Adobe DNG', 'raw_image', 'libraw', 10),
    ]

    # Video formats
    video_formats = [
        ('video/mp4', 'MP4 Video', 'video', 'ffmpeg', 20),
        ('video/avi', 'AVI Video', 'video', 'ffmpeg', 20),
        ('video/mov', 'QuickTime MOV', 'video', 'ffmpeg', 20),
    ]

    # Archive formats
    archive_formats = [
        ('application/zip', 'ZIP Archive', 'archive', 'zip', 40),
        ('application/x-rar', 'RAR Archive', 'archive', 'unrar', 40),
    ]

    # Create all formats
    all_formats = raw_formats + video_formats + archive_formats

    for mime_type, format_name, category, backend, priority in all_formats:
        ConversionFormatSupport.objects.create(
            mime_type=mime_type,
            format_name=format_name,
            category=category,
            converter_backend=backend,
            priority=priority,
            is_enabled=True
        )


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='DocumentConversionMetadata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_format', models.CharField(max_length=255, verbose_name='Original Format')),
                ('conversion_status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20, verbose_name='Conversion Status')),
                ('converter_used', models.CharField(blank=True, max_length=255, verbose_name='Converter Used')),
                ('preview_generated', models.BooleanField(default=False, verbose_name='Preview Generated')),
                ('conversion_started', models.DateTimeField(null=True, blank=True, verbose_name='Conversion Started')),
                ('conversion_completed', models.DateTimeField(null=True, blank=True, verbose_name='Conversion Completed')),
                ('metadata', models.JSONField(default=dict, blank=True, verbose_name='Additional Metadata')),
                ('document', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='conversion_metadata', to='documents.document', verbose_name='Document')),
            ],
            options={
                'verbose_name': 'Document Conversion Metadata',
                'verbose_name_plural': 'Document Conversion Metadata',
            },
        ),

        migrations.CreateModel(
            name='ConversionFormatSupport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mime_type', models.CharField(max_length=100, unique=True, verbose_name='MIME Type')),
                ('format_name', models.CharField(max_length=50, verbose_name='Format Name')),
                ('category', models.CharField(choices=[('image', 'Image'), ('raw_image', 'RAW Image'), ('video', 'Video'), ('audio', 'Audio'), ('archive', 'Archive'), ('document', 'Document')], max_length=20, verbose_name='Category')),
                ('converter_backend', models.CharField(max_length=50, verbose_name='Converter Backend')),
                ('is_enabled', models.BooleanField(default=True, verbose_name='Is Enabled')),
                ('priority', models.PositiveIntegerField(default=100, help_text='Lower values = higher priority', verbose_name='Priority')),
            ],
            options={
                'verbose_name': 'Conversion Format Support',
                'verbose_name_plural': 'Conversion Format Supports',
                'ordering': ['priority', 'mime_type'],
            },
        ),

        migrations.RunPython(
            code=load_initial_format_data,
            reverse_code=migrations.RunPython.noop,
        ),
    ]