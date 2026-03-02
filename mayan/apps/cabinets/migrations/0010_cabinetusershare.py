# Generated for Sprint 3 (Cabinet share with users in org).

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0003_populate_default_organization'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cabinets', '0009_cabinetshare'),
    ]

    operations = [
        migrations.CreateModel(
            name='CabinetUserShare',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('cabinet', models.ForeignKey(
                    help_text='Cabinet shared with the user',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='user_shares',
                    to='cabinets.cabinet'
                )),
                ('user', models.ForeignKey(
                    help_text='User who has been granted access',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='cabinet_user_shares',
                    to=settings.AUTH_USER_MODEL
                )),
                ('organization', models.ForeignKey(
                    help_text='Organization (tenant) for isolation',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='cabinet_user_shares',
                    to='organizations.organization'
                )),
                ('shared_by', models.ForeignKey(
                    blank=True,
                    help_text='User who shared the cabinet',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='cabinet_shares_granted',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Cabinet user share',
                'verbose_name_plural': 'Cabinet user shares',
                'unique_together': {('cabinet', 'user')},
            },
        ),
        migrations.AddIndex(
            model_name='cabinetusershare',
            index=models.Index(
                fields=['user', 'organization'],
                name='idx_cabinet_user_share_user_org',
            ),
        ),
    ]
