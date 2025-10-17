from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distribution', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='generatedrendition',
            name='file',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to='distribution_renditions/',
                verbose_name='Generated rendition file'
            ),
        ),
    ]
