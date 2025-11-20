"""
Django management command для мониторинга индексации документов.

Собирает метрики:
- Количество проиндексированных документов
- Время индексации
- Ошибки индексации
- Статус периодических задач
"""
import logging
import time
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone

from mayan.apps.documents.models import Document
from mayan.apps.documents.metrics import get_metrics

logger = logging.getLogger(name=__name__)


class Command(BaseCommand):
    help = 'Monitor document indexing metrics and status'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Monitoring interval in seconds (default: 60)'
        )
        parser.add_argument(
            '--duration',
            type=int,
            default=300,
            help='Monitoring duration in seconds (default: 300 = 5 minutes)'
        )
        parser.add_argument(
            '--once',
            action='store_true',
            help='Run once and exit (no continuous monitoring)'
        )

    def handle(self, *args, **options):
        interval = options['interval']
        duration = options['duration']
        once = options['once']

        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('Document Indexing Monitor'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write('')

        if once:
            self.print_metrics()
            return 0

        start_time = time.time()
        iteration = 0

        try:
            while (time.time() - start_time) < duration:
                iteration += 1
                self.stdout.write(f'\n--- Iteration {iteration} ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")}) ---')
                self.print_metrics()
                
                if (time.time() - start_time) < duration:
                    self.stdout.write(f'\nWaiting {interval} seconds...')
                    time.sleep(interval)

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nMonitoring stopped by user'))
            return 0

        self.stdout.write(self.style.SUCCESS(f'\nMonitoring completed after {duration} seconds'))
        return 0

    def print_metrics(self):
        """Print current indexing metrics."""
        try:
            metrics = get_metrics()
            
            # Get metrics data
            total_indexed = metrics.get_total_indexed()
            total_failed = metrics.get_total_failed()
            total_retries = metrics.get_total_retries()
            avg_duration = metrics.get_avg_duration()
            
            # Document statistics
            total_documents = Document.valid.count()
            total_in_trash = Document.objects.filter(in_trash=True).count()
            
            # Print metrics
            self.stdout.write(self.style.SUCCESS('Metrics:'))
            self.stdout.write(f'  Total indexed: {total_indexed}')
            self.stdout.write(f'  Total failed: {total_failed}')
            self.stdout.write(f'  Total retries: {total_retries}')
            if avg_duration:
                self.stdout.write(f'  Average duration: {avg_duration:.2f}s')
            
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('Document Statistics:'))
            self.stdout.write(f'  Total valid documents: {total_documents}')
            self.stdout.write(f'  Documents in trash: {total_in_trash}')
            
            # Check recent indexing activity
            self.stdout.write('')
            self.check_recent_activity()
            
            # Check periodic task status
            self.stdout.write('')
            self.check_periodic_task_status()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting metrics: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())

    def check_recent_activity(self):
        """Check recent indexing activity from logs or metrics."""
        try:
            # This is a placeholder - in production, you would check actual logs
            # or maintain a separate table for indexing history
            self.stdout.write(self.style.SUCCESS('Recent Activity:'))
            self.stdout.write('  (Check Celery logs for detailed activity)')
            
            # Check if there are documents that might need indexing
            # This is a simple heuristic - in production, maintain indexing status
            recent_docs = Document.valid.filter(
                date_added__gte=timezone.now() - timedelta(hours=1)
            ).count()
            
            if recent_docs > 0:
                self.stdout.write(f'  ⚠️  {recent_docs} documents added in last hour (may need indexing)')
            else:
                self.stdout.write('  ✅ No recent document additions')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error checking recent activity: {e}'))

    def check_periodic_task_status(self):
        """Check status of periodic reindexing task."""
        try:
            from mayan.celery import app as celery_app
            
            # Check beat schedule
            beat_schedule = celery_app.conf.beat_schedule
            periodic_task_found = False
            
            for task_name, task_config in beat_schedule.items():
                if 'reindex' in task_name.lower() or 'periodic' in task_name.lower():
                    periodic_task_found = True
                    schedule = task_config.get('schedule', {})
                    
                    self.stdout.write(self.style.SUCCESS('Periodic Task Status:'))
                    self.stdout.write(f'  Task: {task_name}')
                    self.stdout.write(f'  Schedule: {schedule}')
                    
                    # Check if task was recently executed
                    # In production, check Celery Beat logs or database
                    self.stdout.write('  Status: Scheduled (check Celery Beat logs for execution)')
                    break

            if not periodic_task_found:
                self.stdout.write(self.style.ERROR('  ❌ Periodic reindexing task not found in schedule'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error checking periodic task: {e}'))

