# Sprint 5.1: Apply watermark on document download

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0007_organizationwatermarksettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationwatermarksettings',
            name='apply_on_download',
            field=models.BooleanField(
                default=False,
                help_text='When enabled, serve watermarked rendition for document downloads (Sprint 5.1)',
                verbose_name='Apply on download'
            ),
        ),
    ]
