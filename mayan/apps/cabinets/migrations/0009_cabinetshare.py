# Generated manually for Sprint 4.2 (CabinetShare public sharing).

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0003_populate_default_organization'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cabinets', '0008_make_organization_required'),
    ]

    operations = [
        migrations.CreateModel(
            name='CabinetShare',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('uuid', models.UUIDField(
                    db_index=True,
                    default=uuid.uuid4,
                    editable=False,
                    help_text='Unique public link identifier',
                    unique=True
                )),
                ('expires_at', models.DateTimeField(
                    blank=True,
                    help_text='When this share link expires',
                    null=True
                )),
                ('password_hash', models.CharField(
                    blank=True,
                    help_text='Hashed password for link protection',
                    max_length=128,
                    null=True
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('cabinet', models.ForeignKey(
                    help_text='Cabinet (collection) this share exposes',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='shares',
                    to='cabinets.cabinet'
                )),
                ('created_by', models.ForeignKey(
                    blank=True,
                    help_text='User who created this share',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='created_cabinet_shares',
                    to=settings.AUTH_USER_MODEL
                )),
                ('organization', models.ForeignKey(
                    help_text='Organization (tenant) this share belongs to',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='cabinet_shares',
                    to='organizations.organization'
                )),
            ],
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Cabinet share',
                'verbose_name_plural': 'Cabinet shares',
            },
        ),
        migrations.AddIndex(
            model_name='cabinetshare',
            index=models.Index(
                fields=['organization', '-created_at'],
                name='idx_cabinet_share_org_created',
            ),
        ),
    ]
