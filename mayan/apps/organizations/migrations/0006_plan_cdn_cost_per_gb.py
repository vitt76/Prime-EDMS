# Generated for Analytics Transformation Feature 2 (CDN Cost).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0005_add_performance_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='cdn_cost_per_gb',
            field=models.DecimalField(
                blank=True,
                decimal_places=4,
                default=0.10,
                help_text='Cost per GB for CDN/bandwidth billing. NULL = use system default.',
                max_digits=10,
                null=True,
                verbose_name='CDN cost per GB (USD)'
            ),
        ),
    ]
