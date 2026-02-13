from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('distribution', '0011_auto_20251225_1037'),
        ('organizations', '0005_add_performance_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='sharelink',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                db_index=True,
                help_text='Organization this share link belongs to',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='distribution_sharelink_set',
                to='organizations.organization',
                verbose_name='Organization',
            ),
        ),
    ]
