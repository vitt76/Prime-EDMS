from django.db import models
from django.utils.translation import ugettext_lazy as _

from mayan.apps.documents.models import Document
from mayan.apps.databases.model_mixins import ExtraDataModelMixin


class DocumentAIAnalysis(ExtraDataModelMixin, models.Model):
    """
    AI analysis results for documents.

    Stores AI-generated metadata like descriptions, tags, colors, etc.
    Links to existing Document model without duplicating data.
    """
    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        related_name='ai_analysis',
        verbose_name=_('Document')
    )

    # Rights and governance
    copyright_notice = models.TextField(
        blank=True,
        null=True,
        help_text=_('Copyright notice extracted or inferred by AI'),
        verbose_name=_('Copyright Notice')
    )

    usage_rights = models.TextField(
        blank=True,
        null=True,
        help_text=_('Usage rights or license details inferred by AI'),
        verbose_name=_('Usage Rights')
    )

    rights_expiry = models.DateField(
        blank=True,
        null=True,
        help_text=_('Date when usage rights expire'),
        verbose_name=_('Rights Expiry')
    )

    # Taxonomy
    categories = models.JSONField(
        blank=True,
        null=True,
        help_text=_('Categories assigned by AI as JSON array'),
        verbose_name=_('Categories')
    )

    language = models.CharField(
        max_length=20,
        blank=True,
        help_text=_('Detected primary language (BCP-47)'),
        verbose_name=_('Language')
    )

    # Entities
    people = models.JSONField(
        blank=True,
        null=True,
        help_text=_('People detected or mentioned, as JSON array'),
        verbose_name=_('People')
    )

    locations = models.JSONField(
        blank=True,
        null=True,
        help_text=_('Locations detected or mentioned, as JSON array'),
        verbose_name=_('Locations')
    )

    # AI-generated content
    ai_description = models.TextField(
        blank=True,
        null=True,
        help_text=_('AI-generated description of the document content'),
        verbose_name=_('AI Description')
    )

    ai_tags = models.JSONField(
        blank=True,
        null=True,
        help_text=_('AI-generated tags as JSON array'),
        verbose_name=_('AI Tags')
    )

    dominant_colors = models.JSONField(
        blank=True,
        null=True,
        help_text=_('Dominant colors extracted by AI'),
        verbose_name=_('Dominant Colors')
    )

    alt_text = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_('AI-generated alt text for accessibility'),
        verbose_name=_('Alt Text')
    )

    # Analysis metadata
    ai_provider = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('AI provider used for analysis'),
        verbose_name=_('AI Provider')
    )

    analysis_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', _('Pending')),
            ('processing', _('Processing')),
            ('completed', _('Completed')),
            ('failed', _('Failed')),
        ],
        default='pending',
        help_text=_('Status of AI analysis'),
        verbose_name=_('Analysis Status')
    )
    
    # Phase B4: Processing progress tracking
    current_step = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text=_('Current processing step (e.g., "OCR scanning", "AI analysis")'),
        verbose_name=_('Current Step')
    )
    
    progress = models.PositiveSmallIntegerField(
        default=0,
        help_text=_('Processing progress percentage (0-100)'),
        verbose_name=_('Progress')
    )
    
    error_message = models.TextField(
        blank=True,
        null=True,
        help_text=_('Error message if analysis failed'),
        verbose_name=_('Error Message')
    )
    
    task_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Celery task ID for tracking'),
        verbose_name=_('Task ID')
    )

    # Timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    analysis_completed = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('When AI analysis was completed'),
        verbose_name=_('Analysis Completed')
    )

    class Meta:
        verbose_name = _('Document AI Analysis')
        verbose_name_plural = _('Document AI Analyses')

    def __str__(self):
        return f'AI Analysis for {self.document}'

    def get_ai_tags_list(self):
        """Get AI tags as a list"""
        if self.ai_tags and isinstance(self.ai_tags, list):
            return self.ai_tags
        return []

    def get_dominant_colors_list(self):
        """Get dominant colors as a list"""
        if self.dominant_colors and isinstance(self.dominant_colors, list):
            return self.dominant_colors
        return []


class DAMMetadataPreset(models.Model):
    """
    Preset configurations for DAM metadata.

    Defines which AI providers to use and what metadata to extract.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_('Name of the metadata preset'),
        verbose_name=_('Name')
    )

    description = models.TextField(
        blank=True,
        help_text=_('Description of this preset'),
        verbose_name=_('Description')
    )

    # AI providers configuration
    ai_providers = models.JSONField(
        default=dict,
        help_text=_('AI providers configuration as JSON'),
        verbose_name=_('AI Providers')
    )

    # Metadata fields to extract
    extract_description = models.BooleanField(
        default=True,
        help_text=_('Extract AI description'),
        verbose_name=_('Extract Description')
    )

    extract_tags = models.BooleanField(
        default=True,
        help_text=_('Extract AI tags'),
        verbose_name=_('Extract Tags')
    )

    extract_colors = models.BooleanField(
        default=True,
        help_text=_('Extract dominant colors'),
        verbose_name=_('Extract Colors')
    )

    extract_alt_text = models.BooleanField(
        default=True,
        help_text=_('Generate alt text'),
        verbose_name=_('Extract Alt Text')
    )

    # File type restrictions
    supported_mime_types = models.JSONField(
        default=list,
        help_text=_('Supported MIME types as JSON array'),
        verbose_name=_('Supported MIME Types')
    )

    # Enabled status
    is_enabled = models.BooleanField(
        default=True,
        help_text=_('Whether this preset is enabled'),
        verbose_name=_('Enabled')
    )

    class Meta:
        verbose_name = _('DAM Metadata Preset')
        verbose_name_plural = _('DAM Metadata Presets')

    def __str__(self):
        return self.name

    def is_applicable_to(self, document_file):
        """Check if this preset applies to the given document file"""
        if not self.supported_mime_types:
            return True

        mime_type = getattr(document_file, 'mimetype', '')
        return mime_type in self.supported_mime_types


class YandexDiskImportRecord(models.Model):
    """
    Track imported files from Yandex Disk to avoid duplicates.
    """
    path = models.CharField(
        max_length=1024,
        unique=True,
        help_text=_('Full Yandex Disk path of the imported file.'),
        verbose_name=_('Yandex Disk path')
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='yandex_disk_records',
        verbose_name=_('Document')
    )
    cabinet = models.ForeignKey(
        'cabinets.Cabinet',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_('Cabinet')
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Yandex Disk import record')
        verbose_name_plural = _('Yandex Disk import records')

    def __str__(self):
        return self.path