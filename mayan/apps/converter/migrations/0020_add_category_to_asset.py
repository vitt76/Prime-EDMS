from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('converter', '0019_auto_20200819_0852'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='category',
            field=models.CharField(
                blank=True, help_text='Optional category for the asset (e.g., watermark, logo)',
                max_length=32, verbose_name='Category'
            ),
        ),
    ]
