# Generated manually on 2025-10-21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distribution', '0007_migrate_sharelink_to_rendition'),
    ]

    operations = [
        migrations.AlterField(
            model_name='renditionpreset',
            name='format',
            field=models.CharField(
                choices=[
                    ('jpeg', 'JPEG'),
                    ('png', 'PNG'),
                    ('webp', 'WebP'),
                    ('tiff', 'TIFF'),
                    ('pdf', 'PDF'),
                    ('mp4', 'MP4'),
                ],
                default='jpeg',
                help_text='Output format for the rendition',
                max_length=10
            ),
        ),
    ]
