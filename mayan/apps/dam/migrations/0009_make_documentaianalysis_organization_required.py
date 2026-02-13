from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dam', '0008_populate_documentaianalysis_organization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentaianalysis',
            name='organization',
            field=models.ForeignKey(
                db_index=True,
                help_text='Organization this record belongs to',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='dam_documentaianalysis_set',
                to='organizations.organization',
                verbose_name='Organization'
            ),
        ),
        migrations.AddIndex(
            model_name='documentaianalysis',
            index=models.Index(
                fields=['organization', '-created'],
                name='idx_ai_analysis_org_created'
            ),
        ),
    ]
