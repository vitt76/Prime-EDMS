# Generated for Analytics Transformation Feature 1.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0015_populate_searchsession_organization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='searchsession',
            name='organization',
            field=models.ForeignKey(
                db_index=True,
                help_text='Organization this session belongs to',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='analytics_search_sessions',
                to='organizations.organization',
                verbose_name='Organization'
            ),
        ),
        migrations.AddIndex(
            model_name='searchsession',
            index=models.Index(
                fields=['organization', 'user', '-started_at'],
                name='idx_anal_ss_org_usr_ts'
            ),
        ),
    ]
