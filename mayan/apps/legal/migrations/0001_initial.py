from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='UserConsentLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP address')),
                ('user_agent', models.TextField(blank=True, default='', verbose_name='User-Agent')),
                ('consent_type', models.CharField(
                    choices=[
                        ('full', 'Accept all'),
                        ('necessary', 'Necessary only'),
                        ('rejected', 'Rejected')
                    ],
                    db_index=True,
                    max_length=20,
                    verbose_name='Consent type'
                )),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Timestamp')),
                ('session_id', models.CharField(blank=True, default='', max_length=255, verbose_name='Session ID')),
                ('url_referer', models.URLField(blank=True, default='', max_length=2048, verbose_name='URL referer')),
            ],
            options={
                'verbose_name': 'User consent log entry',
                'verbose_name_plural': 'User consent log',
                'ordering': ('-timestamp',),
                'app_label': 'legal',
            },
        ),
    ]
