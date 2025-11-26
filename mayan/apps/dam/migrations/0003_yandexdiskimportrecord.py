from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cabinets', '0006_auto_20210525_0604'),
        ('documents', '0083_document_composite_indexes'),
        ('dam', '0002_extend_ai_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='YandexDiskImportRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(help_text='Full Yandex Disk path of the imported file.', max_length=1024, unique=True, verbose_name='Yandex Disk path')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('cabinet', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cabinets.Cabinet', verbose_name='Cabinet')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='yandex_disk_records', to='documents.Document', verbose_name='Document')),
            ],
            options={
                'verbose_name': 'Yandex Disk import record',
                'verbose_name_plural': 'Yandex Disk import records',
            },
        ),
    ]

