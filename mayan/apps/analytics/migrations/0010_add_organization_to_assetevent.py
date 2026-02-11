from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0009_portal_roi_distribution_v3'),
        ('organizations', '0005_add_performance_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='assetevent',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                db_index=True,
                help_text='Organization this record belongs to',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='analytics_assetevent_set',
                to='organizations.organization',
                verbose_name='Organization'
            ),
        ),
    ]
