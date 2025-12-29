from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('analytics', '0004_analytics_alerts'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='assetevent',
            index=models.Index(fields=['document', 'event_type', '-timestamp'], name='analytics_ev_doc_type_ts_idx'),
        ),
    ]


