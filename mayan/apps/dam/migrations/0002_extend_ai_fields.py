from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dam', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentaianalysis',
            name='categories',
            field=models.JSONField(blank=True, help_text='Categories assigned by AI as JSON array', null=True, verbose_name='Categories'),
        ),
        migrations.AddField(
            model_name='documentaianalysis',
            name='language',
            field=models.CharField(blank=True, help_text='Detected primary language (BCP-47)', max_length=20, verbose_name='Language'),
        ),
        migrations.AddField(
            model_name='documentaianalysis',
            name='people',
            field=models.JSONField(blank=True, help_text='People detected or mentioned, as JSON array', null=True, verbose_name='People'),
        ),
        migrations.AddField(
            model_name='documentaianalysis',
            name='locations',
            field=models.JSONField(blank=True, help_text='Locations detected or mentioned, as JSON array', null=True, verbose_name='Locations'),
        ),
        migrations.AddField(
            model_name='documentaianalysis',
            name='copyright_notice',
            field=models.TextField(blank=True, help_text='Copyright notice extracted or inferred by AI', null=True, verbose_name='Copyright Notice'),
        ),
        migrations.AddField(
            model_name='documentaianalysis',
            name='usage_rights',
            field=models.TextField(blank=True, help_text='Usage rights or license details inferred by AI', null=True, verbose_name='Usage Rights'),
        ),
        migrations.AddField(
            model_name='documentaianalysis',
            name='rights_expiry',
            field=models.DateField(blank=True, help_text='Date when usage rights expire', null=True, verbose_name='Rights Expiry'),
        ),
    ]

