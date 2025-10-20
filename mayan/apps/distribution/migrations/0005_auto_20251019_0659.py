from django.conf import settings
from django.db import migrations, models

import uuid

class Migration(migrations.Migration):
    dependencies = [
        ('distribution', '0004_remove_generatedrendition_file_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='renditionpreset',
            name='adjust_brightness',
            field=models.FloatField(
                blank=True,
                help_text='Brightness factor (1.0 = original)',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='renditionpreset',
            name='adjust_color',
            field=models.FloatField(
                blank=True,
                help_text='Color saturation factor (1.0 = original)',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='renditionpreset',
            name='adjust_contrast',
            field=models.FloatField(
                blank=True,
                help_text='Contrast factor (1.0 = original)',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='renditionpreset',
            name='adjust_sharpness',
            field=models.FloatField(
                blank=True,
                help_text='Sharpness factor (1.0 = original)',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='renditionpreset',
            name='crop',
            field=models.BooleanField(
                default=False,
                help_text='Crop to exact size when width and height are specified'
            ),
        ),
        migrations.AddField(
            model_name='renditionpreset',
            name='dpi_x',
            field=models.IntegerField(
                blank=True,
                help_text='Horizontal DPI value',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='renditionpreset',
            name='dpi_y',
            field=models.IntegerField(
                blank=True,
                help_text='Vertical DPI value',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='renditionpreset',
            name='filters',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='List of image filters to apply'
            ),
        ),
    ]
