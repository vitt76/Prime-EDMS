# Sprint 3.3: Publication.organization for org-level watermark

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0007_organizationwatermarksettings'),
        ('distribution', '0015_renditionpreset_organization'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                help_text='Organization (tenant) for watermark and isolation',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='publications',
                to='organizations.organization'
            ),
        ),
    ]
