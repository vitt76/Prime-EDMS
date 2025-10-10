import logging
from pathlib import Path

from django.db import models
from django.utils.translation import ugettext_lazy as _

from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.documents.models import Document

logger = logging.getLogger(name=__name__)


class ExtendedDocumentProxy(Document):
    """
    Прокси модель для расширения Document функциональностью конвертации.
    Не создает новую таблицу в БД.
    """
    class Meta:
        proxy = True
        app_label = 'documents'  # Используем существующую таблицу

    @property
    def media_conversion_status(self):
        """Текущий статус конвертации медиа файлов"""
        try:
            metadata = self.conversion_metadata
            return metadata.conversion_status
        except DocumentConversionMetadata.DoesNotExist:
            return 'not_started'

    @property
    def supported_preview_formats(self):
        """Список поддерживаемых форматов preview для документа"""
        from .utils import get_supported_formats_for_document
        return get_supported_formats_for_document(self)

    def get_conversion_metadata(self):
        """Получить или создать метаданные конвертации"""
        metadata, created = DocumentConversionMetadata.objects.get_or_create(
            document=self,
            defaults={
                'original_format': self.file.mime_type if self.file else '',
                'conversion_status': 'pending'
            }
        )
        return metadata


class DocumentConversionMetadata(ExtraDataModelMixin, models.Model):
    """
    Метаданные конвертации документа.
    Хранит информацию о процессе конвертации медиа файлов.
    """
    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        related_name='conversion_metadata',
        verbose_name=_('Document')
    )

    original_format = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Original format')
    )

    conversion_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', _('Pending')),
            ('processing', _('Processing')),
            ('completed', _('Completed')),
            ('failed', _('Failed')),
            ('not_started', _('Not started')),
        ],
        default='not_started',
        verbose_name=_('Conversion status')
    )

    converter_used = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Converter used')
    )

    preview_generated = models.BooleanField(
        default=False,
        verbose_name=_('Preview generated')
    )

    conversion_started = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Conversion started')
    )

    conversion_completed = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Conversion completed')
    )

    # JSON поле для хранения дополнительной информации
    conversion_details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Conversion details')
    )

    class Meta:
        verbose_name = _('Document conversion metadata')
        verbose_name_plural = _('Document conversion metadata')

    def __str__(self):
        return f'Conversion metadata for {self.document}'

    def mark_as_processing(self, converter_name):
        """Отметить начало обработки"""
        from django.utils import timezone
        self.conversion_status = 'processing'
        self.converter_used = converter_name
        self.conversion_started = timezone.now()
        self.save(update_fields=['conversion_status', 'converter_used', 'conversion_started'])

    def mark_as_completed(self):
        """Отметить успешное завершение"""
        from django.utils import timezone
        self.conversion_status = 'completed'
        self.preview_generated = True
        self.conversion_completed = timezone.now()
        self.save(update_fields=['conversion_status', 'preview_generated', 'conversion_completed'])

    def mark_as_failed(self, error_details=None):
        """Отметить неудачу конвертации"""
        self.conversion_status = 'failed'
        if error_details:
            self.conversion_details.update({'error': str(error_details)})
        self.save(update_fields=['conversion_status', 'conversion_details'])


class ConversionFormatSupport(models.Model):
    """
    Справочник поддерживаемых форматов конвертации.
    """
    mime_type = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('MIME type')
    )

    format_name = models.CharField(
        max_length=50,
        verbose_name=_('Format name')
    )

    category = models.CharField(
        max_length=20,
        choices=[
            ('image', _('Image')),
            ('raw_image', _('RAW Image')),
            ('video', _('Video')),
            ('audio', _('Audio')),
            ('archive', _('Archive')),
            ('document', _('Document')),
        ],
        verbose_name=_('Category')
    )

    converter_backend = models.CharField(
        max_length=50,
        verbose_name=_('Converter backend')
    )

    is_enabled = models.BooleanField(
        default=True,
        verbose_name=_('Is enabled')
    )

    priority = models.PositiveIntegerField(
        default=100,
        help_text=_('Lower values = higher priority'),
        verbose_name=_('Priority')
    )

    class Meta:
        verbose_name = _('Conversion format support')
        verbose_name_plural = _('Conversion format supports')
        ordering = ['priority', 'mime_type']

    def __str__(self):
        return f'{self.format_name} ({self.mime_type})'

