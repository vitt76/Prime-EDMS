from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0011_populate_assetevent_organization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assetevent',
            name='organization',
            field=models.ForeignKey(
                db_index=True,
                help_text='Organization this record belongs to',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='analytics_assetevent_set',
                to='organizations.organization',
                verbose_name='Organization'
            ),
        ),
        migrations.AddIndex(
            model_name='assetevent',
            index=models.Index(
                fields=['organization', 'event_type', '-timestamp'],
                name='idx_analytics_ae_org_type_ts'
            ),
        ),
        migrations.AddIndex(
            model_name='assetevent',
            index=models.Index(
                fields=['organization', 'document', '-timestamp'],
                name='idx_analytics_ae_org_doc_ts'
            ),
        ),
    ]
