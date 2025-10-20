from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('distribution', '0003_accesslog_rendition_field'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='generatedrendition',
            name='file_path',
        ),
    ]
