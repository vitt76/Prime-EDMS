"""
Django management command для проверки статуса сервисов.

Проверяет:
- Celery workers (все очереди)
- Celery Beat (периодические задачи)
- Статус регистрации обработчиков
- Конфигурацию очередей
"""
import logging
import sys

from django.core.management.base import BaseCommand
from django.apps import apps

from mayan.celery import app as celery_app

logger = logging.getLogger(name=__name__)


class Command(BaseCommand):
    help = 'Check status of Celery workers, Beat, and handlers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed information'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('Service Status Check'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write('')

        detailed = options['detailed']
        all_ok = True

        # Check Celery workers
        self.stdout.write(self.style.WARNING('1. Checking Celery Workers...'))
        workers_ok = self.check_celery_workers(detailed)
        if not workers_ok:
            all_ok = False
        self.stdout.write('')

        # Check Celery Beat
        self.stdout.write(self.style.WARNING('2. Checking Celery Beat...'))
        beat_ok = self.check_celery_beat(detailed)
        if not beat_ok:
            all_ok = False
        self.stdout.write('')

        # Check queue configuration
        self.stdout.write(self.style.WARNING('3. Checking Queue Configuration...'))
        queues_ok = self.check_queue_configuration(detailed)
        if not queues_ok:
            all_ok = False
        self.stdout.write('')

        # Check handlers registration
        self.stdout.write(self.style.WARNING('4. Checking Handler Registration...'))
        handlers_ok = self.check_handlers_registration(detailed)
        if not handlers_ok:
            all_ok = False
        self.stdout.write('')

        # Summary
        self.stdout.write(self.style.SUCCESS('=' * 80))
        if all_ok:
            self.stdout.write(self.style.SUCCESS('All services are OK'))
            return 0
        else:
            self.stdout.write(self.style.ERROR('Some services have issues. Check output above.'))
            return 1

    def check_celery_workers(self, detailed):
        """Check if Celery workers are running and can be inspected."""
        try:
            inspect = celery_app.control.inspect()
            
            # Get active workers
            active = inspect.active()
            if active is None:
                self.stdout.write(self.style.ERROR('  ❌ Cannot connect to Celery workers'))
                self.stdout.write('     Make sure Celery workers are running')
                return False

            if not active:
                self.stdout.write(self.style.ERROR('  ❌ No active Celery workers found'))
                return False

            self.stdout.write(self.style.SUCCESS(f'  ✅ Found {len(active)} active worker(s)'))

            if detailed:
                for worker_name, tasks in active.items():
                    self.stdout.write(f'     Worker: {worker_name}')
                    if tasks:
                        self.stdout.write(f'       Active tasks: {len(tasks)}')
                        for task in tasks[:3]:  # Show first 3 tasks
                            self.stdout.write(f'         - {task.get("name", "unknown")}')

            # Check registered queues
            registered = inspect.registered()
            if registered:
                search_queue_found = False
                periodic_queue_found = False
                
                for worker_name, tasks in registered.items():
                    for task_name in tasks:
                        if 'search' in task_name.lower():
                            search_queue_found = True
                        if 'periodic' in task_name.lower() or 'reindex' in task_name.lower():
                            periodic_queue_found = True

                if search_queue_found:
                    self.stdout.write(self.style.SUCCESS('  ✅ Search queue tasks registered'))
                else:
                    self.stdout.write(self.style.WARNING('  ⚠️  Search queue tasks not found (may be normal if no tasks queued)'))

                if periodic_queue_found:
                    self.stdout.write(self.style.SUCCESS('  ✅ Periodic reindexing tasks registered'))
                else:
                    self.stdout.write(self.style.WARNING('  ⚠️  Periodic reindexing tasks not found'))

            return True

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error checking workers: {e}'))
            if detailed:
                import traceback
                self.stdout.write(traceback.format_exc())
            return False

    def check_celery_beat(self, detailed):
        """Check Celery Beat configuration and scheduled tasks."""
        try:
            # Check beat schedule
            beat_schedule = celery_app.conf.beat_schedule
            
            if not beat_schedule:
                self.stdout.write(self.style.WARNING('  ⚠️  No tasks in beat schedule'))
                return False

            # Look for periodic reindexing task
            periodic_task_found = False
            for task_name, task_config in beat_schedule.items():
                if 'reindex' in task_name.lower() or 'periodic' in task_name.lower():
                    periodic_task_found = True
                    schedule = task_config.get('schedule', 'unknown')
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Found periodic reindexing task: {task_name}'))
                    if detailed:
                        self.stdout.write(f'     Schedule: {schedule}')
                        self.stdout.write(f'     Task: {task_config.get("task", "unknown")}')

            if not periodic_task_found:
                self.stdout.write(self.style.ERROR('  ❌ Periodic reindexing task not found in beat schedule'))
                self.stdout.write('     Make sure task_periodic_reindex_documents is registered')
                return False

            if detailed:
                self.stdout.write(f'  Total scheduled tasks: {len(beat_schedule)}')

            self.stdout.write(self.style.SUCCESS('  ✅ Celery Beat configuration OK'))
            self.stdout.write('     Note: This only checks configuration, not if Beat process is running')
            self.stdout.write('     Check process: ps aux | grep celery.*beat')

            return True

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error checking Celery Beat: {e}'))
            if detailed:
                import traceback
                self.stdout.write(traceback.format_exc())
            return False

    def check_queue_configuration(self, detailed):
        """Check queue configuration."""
        try:
            from mayan.apps.documents.queues import queue_documents_periodic
            from mayan.apps.documents.settings import setting_indexing_periodic_reindex_interval

            # Check periodic queue
            self.stdout.write(self.style.SUCCESS('  ✅ Documents periodic queue configured'))
            
            # Check interval setting
            interval = setting_indexing_periodic_reindex_interval.value
            hours = interval / 3600
            self.stdout.write(self.style.SUCCESS(f'  ✅ Periodic reindex interval: {interval}s ({hours:.1f} hours)'))

            if detailed:
                self.stdout.write(f'     Queue name: {queue_documents_periodic.name}')
                self.stdout.write(f'     Worker: {queue_documents_periodic.worker}')

            return True

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error checking queue configuration: {e}'))
            if detailed:
                import traceback
                self.stdout.write(traceback.format_exc())
            return False

    def check_handlers_registration(self, detailed):
        """Check if handlers are properly registered."""
        try:
            from django.db.models.signals import post_save
            from mayan.apps.documents.models import Document
            from mayan.apps.documents.indexing_coordinator import is_coordinator_active

            # Check if coordinator is active
            coordinator_active = is_coordinator_active()
            if coordinator_active:
                self.stdout.write(self.style.SUCCESS('  ✅ DocumentIndexCoordinator is active'))
            else:
                self.stdout.write(self.style.ERROR('  ❌ DocumentIndexCoordinator is not active'))
                return False

            # Check registered receivers
            receivers = post_save._live_receivers(sender=Document)
            coordinator_handler_found = False

            for receiver in receivers:
                # Check by function name
                if hasattr(receiver, '__name__'):
                    if 'coordinate_document_index' in receiver.__name__:
                        coordinator_handler_found = True
                        break

            if coordinator_handler_found:
                self.stdout.write(self.style.SUCCESS('  ✅ Coordinator handler registered'))
            else:
                self.stdout.write(self.style.WARNING('  ⚠️  Coordinator handler not found (may be registered with different name)'))

            if detailed:
                self.stdout.write(f'     Total receivers for Document.post_save: {len(receivers)}')
                for i, receiver in enumerate(receivers[:5]):  # Show first 5
                    receiver_name = getattr(receiver, '__name__', str(receiver))
                    self.stdout.write(f'       {i+1}. {receiver_name}')

            return coordinator_active

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error checking handlers: {e}'))
            if detailed:
                import traceback
                self.stdout.write(traceback.format_exc())
            return False

