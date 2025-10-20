from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('distribution', '0002_generatedrendition_file_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='accesslog',
            name='rendition',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='distribution.generatedrendition'
            ),
        ),
    ]
