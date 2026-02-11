from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dam', '0006_add_json_gin_indexes'),
        ('organizations', '0005_add_performance_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentaianalysis',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                db_index=True,
                help_text='Organization this record belongs to',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='dam_documentaianalysis_set',
                to='organizations.organization',
                verbose_name='Organization'
            ),
        ),
    ]
