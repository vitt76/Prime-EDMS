from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0080_populate_file_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentfile',
            name='filename',
            field=models.CharField(
                blank=True, db_index=True, max_length=255,
                verbose_name='Filename'
            ),
        ),
    ]

