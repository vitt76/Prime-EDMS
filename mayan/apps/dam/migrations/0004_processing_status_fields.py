"""
Phase B4: Add processing status tracking fields to DocumentAIAnalysis.

These fields enable frontend polling for real-time progress updates.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dam', '0003_yandexdiskimportrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentaianalysis',
            name='current_step',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Current processing step (e.g., "OCR scanning", "AI analysis")',
                max_length=100,
                verbose_name='Current Step'
            ),
        ),
        migrations.AddField(
            model_name='documentaianalysis',
            name='progress',
            field=models.PositiveSmallIntegerField(
                default=0,
                help_text='Processing progress percentage (0-100)',
                verbose_name='Progress'
            ),
        ),
        migrations.AddField(
            model_name='documentaianalysis',
            name='error_message',
            field=models.TextField(
                blank=True,
                null=True,
                help_text='Error message if analysis failed',
                verbose_name='Error Message'
            ),
        ),
        migrations.AddField(
            model_name='documentaianalysis',
            name='task_id',
            field=models.CharField(
                blank=True,
                null=True,
                help_text='Celery task ID for tracking',
                max_length=100,
                verbose_name='Task ID'
            ),
        ),
        # Add index on task_id for faster lookups
        migrations.AddIndex(
            model_name='documentaianalysis',
            index=models.Index(
                fields=['task_id'],
                name='dam_ai_task_id_idx'
            ),
        ),
        # Add index on analysis_status for filtering
        migrations.AddIndex(
            model_name='documentaianalysis',
            index=models.Index(
                fields=['analysis_status'],
                name='dam_ai_status_idx'
            ),
        ),
    ]











