from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('distribution', '0005_auto_20251019_0659'),
    ]

    operations = [
        migrations.AddField(
            model_name='renditionpreset',
            name='recipient',
            field=models.ForeignKey(
                help_text='Associated recipient for this preset',
                on_delete=django.db.models.deletion.CASCADE,
                to='distribution.recipient'
            ),
        ),
    ]
