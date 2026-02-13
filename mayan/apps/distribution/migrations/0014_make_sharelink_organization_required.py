from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('distribution', '0013_populate_sharelink_organization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sharelink',
            name='organization',
            field=models.ForeignKey(
                db_index=True,
                help_text='Organization this share link belongs to',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='distribution_sharelink_set',
                to='organizations.organization',
                verbose_name='Organization',
            ),
        ),
        migrations.AddIndex(
            model_name='sharelink',
            index=models.Index(fields=['organization'], name='distribution_sharelink_org_idx'),
        ),
        migrations.AddIndex(
            model_name='sharelink',
            index=models.Index(
                fields=['organization', '-created'],
                name='idx_distribution_sl_org_created',
            ),
        ),
    ]
