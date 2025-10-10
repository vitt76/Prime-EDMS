import logging

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

logger = logging.getLogger(name=__name__)


class Command(BaseCommand):
    """
    Управление Converter Pipeline Extension.

    Доступные действия:
    - enable: Включить расширение
    - disable: Отключить расширение
    - status: Показать статус
    - cleanup: Очистить данные расширения
    """

    help = 'Manage Converter Pipeline Extension'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['enable', 'disable', 'status', 'cleanup'],
            help='Action to perform'
        )

    def handle(self, *args, **options):
        action = options['action']

        if action == 'enable':
            self.enable_extension()
        elif action == 'disable':
            self.disable_extension()
        elif action == 'status':
            self.show_status()
        elif action == 'cleanup':
            self.cleanup_extension()

    def enable_extension(self):
        """Включить расширение."""
        self.stdout.write('Enabling Converter Pipeline Extension...')

        try:
            # Проверить что все зависимости установлены
            self._check_dependencies()

            # Зарегистрировать сигналы
            self._register_signals()

            # Обновить настройки
            self._update_settings()

            self.stdout.write(
                self.style.SUCCESS('Converter Pipeline Extension enabled successfully')
            )

        except Exception as e:
            raise CommandError(f'Failed to enable extension: {e}')

    def disable_extension(self):
        """Отключить расширение."""
        self.stdout.write('Disabling Converter Pipeline Extension...')

        try:
            # Отменить регистрацию сигналов
            self._unregister_signals()

            # Остановить активные задачи
            self._stop_active_tasks()

            self.stdout.write(
                self.style.SUCCESS('Converter Pipeline Extension disabled successfully')
            )
            self.stdout.write(
                self.style.WARNING('Note: Extension data is preserved. Use "cleanup" to remove it.')
            )

        except Exception as e:
            raise CommandError(f'Failed to disable extension: {e}')

    def show_status(self):
        """Показать статус расширения."""
        self.stdout.write('Converter Pipeline Extension Status:')
        self.stdout.write('=' * 50)

        # Проверить включено ли расширение
        is_enabled = self._check_if_enabled()
        status = self.style.SUCCESS('ENABLED') if is_enabled else self.style.ERROR('DISABLED')
        self.stdout.write(f'Status: {status}')

        # Показать статистику
        try:
            from ...models import DocumentConversionMetadata, ConversionFormatSupport

            total_conversions = DocumentConversionMetadata.objects.count()
            completed_conversions = DocumentConversionMetadata.objects.filter(
                conversion_status='completed'
            ).count()
            failed_conversions = DocumentConversionMetadata.objects.filter(
                conversion_status='failed'
            ).count()

            self.stdout.write(f'Total conversions: {total_conversions}')
            self.stdout.write(f'Completed: {completed_conversions}')
            self.stdout.write(f'Failed: {failed_conversions}')

            supported_formats = ConversionFormatSupport.objects.filter(is_enabled=True).count()
            self.stdout.write(f'Supported formats: {supported_formats}')

        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not get statistics: {e}'))

        # Проверить зависимости
        deps_ok = self._check_dependencies_silent()
        deps_status = self.style.SUCCESS('OK') if deps_ok else self.style.ERROR('ISSUES')
        self.stdout.write(f'Dependencies: {deps_status}')

        if not deps_ok:
            self.stdout.write('Run "check" command for details.')

    def cleanup_extension(self):
        """Очистить все данные расширения."""
        self.stdout.write(
            self.style.WARNING('This will permanently delete all extension data!')
        )

        # Запросить подтверждение
        confirm = input('Are you sure? Type "yes" to confirm: ')
        if confirm != 'yes':
            self.stdout.write('Operation cancelled.')
            return

        try:
            with transaction.atomic():
                # Удалить все метаданные конвертации
                from ...models import DocumentConversionMetadata, ConversionFormatSupport

                metadata_count = DocumentConversionMetadata.objects.count()
                DocumentConversionMetadata.objects.all().delete()

                format_count = ConversionFormatSupport.objects.count()
                ConversionFormatSupport.objects.all().delete()

                # Очистить кэш preview
                self._clear_preview_cache()

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Cleanup completed. Removed {metadata_count} conversion records '
                        f'and {format_count} format definitions.'
                    )
                )

        except Exception as e:
            raise CommandError(f'Cleanup failed: {e}')

    def _check_dependencies(self):
        """Проверить зависимости."""
        required_commands = ['dcraw', 'ffmpeg', 'ffprobe', 'convert']
        missing = []

        import subprocess
        for cmd in required_commands:
            try:
                subprocess.run([cmd, '--version'], capture_output=True, check=True, timeout=5)
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                missing.append(cmd)

        if missing:
            raise CommandError(f'Missing required dependencies: {", ".join(missing)}')

    def _check_dependencies_silent(self):
        """Проверить зависимости без вывода ошибок."""
        try:
            self._check_dependencies()
            return True
        except CommandError:
            return False

    def _register_signals(self):
        """Зарегистрировать сигналы."""
        # Сигналы регистрируются автоматически в apps.py
        # Здесь можно добавить дополнительную логику если нужно
        pass

    def _unregister_signals(self):
        """Отменить регистрацию сигналов."""
        # В Django сигналы автоматически отключаются при перезагрузке
        # Здесь можно добавить дополнительную логику если нужно
        pass

    def _update_settings(self):
        """Обновить настройки."""
        # Здесь можно обновить настройки Mayan EDMS если нужно
        pass

    def _stop_active_tasks(self):
        """Остановить активные задачи."""
        # Остановить Celery задачи если возможно
        pass

    def _check_if_enabled(self):
        """Проверить включено ли расширение."""
        try:
            from django.apps import apps
            app_config = apps.get_app_config('converter_pipeline_extension')
            return True
        except:
            return False

    def _clear_preview_cache(self):
        """Очистить кэш preview."""
        try:
            from mayan.apps.file_caching.models import CachePartition

            # Найти и удалить partitions связанные с converter pipeline
            partitions = CachePartition.objects.filter(
                cache__defined_storage_name__icontains='converter_pipeline'
            )

            for partition in partitions:
                partition.delete()

        except Exception as e:
            logger.warning(f'Failed to clear preview cache: {e}')

