"""
Django management command to generate renditions for all existing publications.

Usage:
    python manage.py generate_publication_renditions
    python manage.py generate_publication_renditions --publication-id 1
    python manage.py generate_publication_renditions --all
"""

import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from mayan.apps.distribution.models import Publication, RenditionPreset, Recipient

logger = logging.getLogger(name=__name__)


class Command(BaseCommand):
    help = 'Generate renditions for all publications (or specific publication)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--publication-id',
            type=int,
            help='Generate renditions for specific publication ID'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Generate renditions for all publications'
        )
        parser.add_argument(
            '--create-default-preset',
            action='store_true',
            help='Create default preset for publications without presets'
        )

    def handle(self, *args, **options):
        publication_id = options.get('publication_id')
        process_all = options.get('all', False)
        create_default = options.get('create_default_preset', True)

        # Получаем или создаем дефолтный пресет
        default_preset = None
        if create_default:
            default_preset = self._get_or_create_default_preset()

        if publication_id:
            # Обрабатываем конкретную публикацию
            try:
                publication = Publication.objects.get(pk=publication_id)
                self._process_publication(publication, default_preset)
            except Publication.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Publication with ID {publication_id} not found')
                )
        elif process_all:
            # Обрабатываем все публикации
            publications = Publication.objects.all()
            total = publications.count()
            self.stdout.write(f'Processing {total} publications...')
            
            processed = 0
            for publication in publications:
                try:
                    self._process_publication(publication, default_preset)
                    processed += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Publication {publication.id} ({publication.title}): '
                            f'{publication.items.count()} items, '
                            f'{publication.presets.count()} presets'
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'✗ Failed to process publication {publication.id}: {e}'
                        )
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nCompleted: {processed}/{total} publications processed'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Please specify --publication-id <id> or --all flag'
                )
            )

    def _get_or_create_default_preset(self):
        """Get or create default rendition preset for images."""
        # Ищем существующий дефолтный пресет
        default_preset = RenditionPreset.objects.filter(
            resource_type='image',
            name__icontains='default'
        ).first()
        
        if not default_preset:
            # Создаем или получаем дефолтного получателя
            default_recipient, _ = Recipient.objects.get_or_create(
                email='system@mayan-edms.local',
                defaults={
                    'name': 'System Default',
                    'organization': 'Mayan EDMS'
                }
            )
            
            # Создаем дефолтный пресет
            default_preset = RenditionPreset.objects.create(
                resource_type='image',
                format='jpeg',
                name='Default JPEG',
                description='Default preset for campaign publications',
                quality=85,
                width=1920,
                height=None,
                crop=False,
                recipient=default_recipient
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created default preset: {default_preset.name}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Using existing default preset: {default_preset.name}')
            )
        
        return default_preset

    def _process_publication(self, publication, default_preset):
        """Process a single publication: add default preset if needed and generate renditions."""
        with transaction.atomic():
            # Если у публикации нет пресетов, добавляем дефолтный
            if not publication.presets.exists() and default_preset:
                publication.presets.add(default_preset)
                self.stdout.write(
                    f'  Added default preset to publication {publication.id}'
                )
            
            # Генерируем рендишены для всех элементов
            if publication.presets.exists():
                items_count = publication.items.count()
                presets_count = publication.presets.count()
                
                if items_count > 0:
                    publication.generate_all_renditions()
                    self.stdout.write(
                        f'  Generated renditions for {items_count} items '
                        f'with {presets_count} presets'
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  Publication {publication.id} has no items'
                        )
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'  Publication {publication.id} has no presets'
                    )
                )

