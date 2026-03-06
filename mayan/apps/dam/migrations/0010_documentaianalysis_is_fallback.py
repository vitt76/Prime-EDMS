from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dam', '0009_make_documentaianalysis_organization_required'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentaianalysis',
            name='is_fallback',
            field=models.BooleanField(
                default=False,
                help_text='Indicates the analysis contains degraded fallback data',
                verbose_name='Is Fallback'
            ),
        ),
    ]
