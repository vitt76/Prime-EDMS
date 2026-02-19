# Sprint 3.3: Organization-level watermark settings

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0006_plan_cdn_cost_per_gb'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationWatermarkSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enabled', models.BooleanField(default=False, help_text='Apply watermark to preview and Share Link exports', verbose_name='Enabled')),
                ('text', models.CharField(blank=True, help_text='Watermark text (e.g. Confidential)', max_length=255, verbose_name='Text')),
                ('logo_url', models.URLField(blank=True, help_text='Optional logo image URL for watermark', max_length=500, verbose_name='Logo URL')),
                ('position', models.CharField(choices=[('top_left', 'Top left'), ('top_right', 'Top right'), ('bottom_left', 'Bottom left'), ('bottom_right', 'Bottom right'), ('center', 'Center')], default='bottom_right', max_length=32, verbose_name='Position')),
                ('opacity', models.FloatField(default=0.5, help_text='Opacity 0.0–1.0', verbose_name='Opacity')),
                ('font_size', models.IntegerField(blank=True, default=24, null=True, verbose_name='Font size')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('organization', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='watermark_settings', to='organizations.organization', verbose_name='Organization')),
            ],
            options={
                'verbose_name': 'Organization watermark settings',
                'verbose_name_plural': 'Organization watermark settings',
                'db_table': 'organizations_watermark_settings',
            },
        ),
    ]
