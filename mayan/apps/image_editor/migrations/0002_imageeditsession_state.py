from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('image_editor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='imageeditsession',
            name='state',
            field=models.JSONField(blank=True, default=dict, verbose_name='Состояние редактора'),
        ),
    ]


