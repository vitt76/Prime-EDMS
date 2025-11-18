import os
import logging
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Migrate existing document files from local storage to S3'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать что будет сделано без реального выполнения'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Размер батча для миграции (по умолчанию 10)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Ограничить количество файлов для миграции (для тестирования)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Принудительно выполнить миграцию, даже если файл уже существует в S3'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        limit = options['limit']
        force = options['force']

        self.stdout.write('🚀 Начинаем миграцию файлов в S3...')

        # 1. Проверить настройки S3
        try:
            from mayan.apps.storage.settings import (
                setting_s3_enabled, setting_s3_endpoint_url, setting_s3_access_key,
                setting_s3_secret_key, setting_s3_bucket_name, setting_s3_region_name,
                setting_s3_verify
            )

            if not setting_s3_enabled.value:
                raise CommandError('❌ S3 storage не включен. Включите STORAGE_S3_ENABLED в настройках.')

            s3_config = {
                'endpoint_url': setting_s3_endpoint_url.value,
                'access_key': setting_s3_access_key.value,
                'secret_key': setting_s3_secret_key.value,
                'bucket_name': setting_s3_bucket_name.value,
                'region_name': setting_s3_region_name.value,
                'verify': setting_s3_verify.value,
            }

            # Проверить обязательные параметры
            required_params = ['endpoint_url', 'access_key', 'secret_key', 'bucket_name']
            missing_params = [param for param in required_params if not s3_config.get(param)]
            if missing_params:
                raise CommandError(f'❌ Отсутствуют обязательные S3 параметры: {", ".join(missing_params)}')

        except ImportError as e:
            raise CommandError(f'❌ Не удалось импортировать S3 настройки: {e}')

        # 2. Проверить подключение к S3
        self.stdout.write('🔍 Проверяем подключение к S3...')
        try:
            from mayan.apps.storage.utils import validate_s3_connection
            success, message = validate_s3_connection(**s3_config)
            if not success:
                raise CommandError(f'❌ {message}')
            self.stdout.write(self.style.SUCCESS(message))
        except Exception as e:
            raise CommandError(f'❌ Ошибка проверки подключения к S3: {e}')

        # 3. Получить список документов для миграции
        try:
            from mayan.apps.documents.models import DocumentFile
            from mayan.apps.storage.storages import storage_document_files

            # Получить все файлы документов
            queryset = DocumentFile.objects.all().order_by('pk')

            if limit:
                queryset = queryset[:limit]

            total_files = queryset.count()
            self.stdout.write(f'📋 Найдено {total_files} файлов для миграции')

            if total_files == 0:
                self.stdout.write(self.style.WARNING('⚠️ Нет файлов для миграции'))
                return

        except Exception as e:
            raise CommandError(f'❌ Ошибка получения списка файлов: {e}')

        # 4. Выполнить миграцию
        migrated_count = 0
        error_count = 0
        skipped_count = 0

        try:
            for i, document_file in enumerate(queryset, 1):
                try:
                    with transaction.atomic():
                        file_name = document_file.file.name
                        self.stdout.write(f'[{i}/{total_files}] Обрабатываем: {file_name}')

                        # Проверить, существует ли файл уже в S3 (если не force)
                        if not force:
                            try:
                                # Попытаться получить объект из S3
                                import boto3
                                session = boto3.Session(
                                    aws_access_key_id=s3_config['access_key'],
                                    aws_secret_access_key=s3_config['secret_key'],
                                    region_name=s3_config['region_name']
                                )
                                s3 = session.client(
                                    's3',
                                    endpoint_url=s3_config['endpoint_url'],
                                    verify=s3_config['verify']
                                )
                                s3.head_object(Bucket=s3_config['bucket_name'], Key=file_name)
                                self.stdout.write(f'  ⏭️ Пропускаем (уже существует): {file_name}')
                                skipped_count += 1
                                continue
                            except s3.exceptions.NoSuchKey:
                                pass  # Файл не существует, продолжаем миграцию
                            except Exception as e:
                                self.stdout.write(f'  ⚠️ Ошибка проверки существования файла: {e}')
                                # Продолжаем миграцию

                        # Прочитать файл из текущего хранилища
                        try:
                            with storage_document_files.open(name=file_name, mode='rb') as source_file:
                                file_content = source_file.read()
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'  ❌ Ошибка чтения файла: {e}'))
                            error_count += 1
                            continue

                        if dry_run:
                            self.stdout.write(f'  📋 DRY RUN: Будет загружен файл {file_name} ({len(file_content)} байт)')
                        else:
                            # Загрузить файл в S3
                            try:
                                storage_document_files.save(name=file_name, content=file_content, max_length=None)
                                self.stdout.write(f'  ✅ Успешно загружен: {file_name}')
                                migrated_count += 1
                            except Exception as e:
                                self.stdout.write(self.style.ERROR(f'  ❌ Ошибка загрузки файла: {e}'))
                                error_count += 1
                                continue

                        # Обработка батчей
                        if i % batch_size == 0:
                            self.stdout.write(f'📊 Прогресс: {i}/{total_files} обработано')

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ❌ Критическая ошибка обработки файла: {e}'))
                    error_count += 1
                    continue

            # Итоговый отчет
            self.stdout.write('\n' + '='*50)
            self.stdout.write('📊 ИТОГИ МИГРАЦИИ:')
            self.stdout.write(f'✅ Успешно мигрировано: {migrated_count}')
            self.stdout.write(f'⏭️ Пропущено (уже существует): {skipped_count}')
            self.stdout.write(f'❌ Ошибок: {error_count}')
            self.stdout.write(f'📋 Всего обработано: {total_files}')

            if dry_run:
                self.stdout.write(self.style.WARNING('🔍 Это был тестовый запуск (DRY RUN)'))
            else:
                if error_count == 0:
                    self.stdout.write(self.style.SUCCESS('🎉 Миграция завершена успешно!'))
                else:
                    self.stdout.write(self.style.WARNING(f'⚠️ Миграция завершена с {error_count} ошибками'))

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\n⚠️ Миграция прервана пользователем'))
        except Exception as e:
            raise CommandError(f'❌ Критическая ошибка миграции: {e}')
