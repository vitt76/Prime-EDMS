import uuid
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


class Recipient(models.Model):
    """
    Получатель материалов (внешний email).
    """
    email = models.EmailField(
        unique=True,
        help_text=_('Email address of the recipient')
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Full name of the recipient')
    )
    organization = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Organization name')
    )
    locale = models.CharField(
        max_length=10,
        blank=True,
        help_text=_('Preferred language locale (e.g., en, ru)')
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name', 'email']
        verbose_name = _('Recipient')
        verbose_name_plural = _('Recipients')

    def __str__(self):
        return self.name or self.email


class RecipientList(models.Model):
    """
    Список получателей для публикаций.
    """
    name = models.CharField(
        max_length=255,
        help_text=_('Name of the recipient list')
    )
    recipients = models.ManyToManyField(
        Recipient,
        blank=True,
        related_name='recipient_lists',
        help_text=_('External recipients in this list')
    )
    internal_users = models.ManyToManyField(
        User,
        blank=True,
        related_name='distribution_lists',
        help_text=_('Internal users in this list')
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_recipient_lists',
        help_text=_('Owner of this list')
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('Recipient List')
        verbose_name_plural = _('Recipient Lists')

    def __str__(self):
        return self.name


class RenditionPreset(models.Model):
    """
    Пресет для генерации рендишенов.
    """
    RESOURCE_TYPE_CHOICES = [
        ('image', _('Image')),
        ('video', _('Video')),
        ('document', _('Document')),
    ]

    FORMAT_CHOICES = [
        ('jpeg', 'JPEG'),
        ('png', 'PNG'),
        ('tiff', 'TIFF'),
        ('pdf', 'PDF'),
        ('mp4', 'MP4'),
    ]

    FILTER_CHOICES = [
        ('grayscale', _('Grayscale')),
        ('invert', _('Invert')),
        ('autocontrast', _('Auto contrast')),
        ('equalize', _('Equalize')),
        ('posterize', _('Posterize')),
        ('solarize', _('Solarize')),
    ]

    resource_type = models.CharField(
        max_length=32,
        choices=RESOURCE_TYPE_CHOICES,
        help_text=_('Type of resource this preset applies to')
    )
    format = models.CharField(
        max_length=16,
        choices=FORMAT_CHOICES,
        help_text=_('Output format')
    )
    width = models.IntegerField(
        null=True,
        blank=True,
        help_text=_('Maximum width in pixels (None for auto)')
    )
    height = models.IntegerField(
        null=True,
        blank=True,
        help_text=_('Maximum height in pixels (None for auto)')
    )
    quality = models.IntegerField(
        null=True,
        blank=True,
        help_text=_('Quality setting (0-100 for images, None for others)')
    )
    crop = models.BooleanField(
        default=False,
        help_text=_('Crop to exact size when width and height are specified')
    )
    dpi_x = models.IntegerField(
        null=True,
        blank=True,
        help_text=_('Horizontal DPI value')
    )
    dpi_y = models.IntegerField(
        null=True,
        blank=True,
        help_text=_('Vertical DPI value')
    )
    filters = models.JSONField(
        default=list,
        blank=True,
        help_text=_('List of image filters to apply')
    )
    watermark = models.JSONField(
        default=dict,
        blank=True,
        help_text=_('Watermark settings as JSON')
    )
    adjust_brightness = models.FloatField(
        null=True,
        blank=True,
        help_text=_('Brightness factor (1.0 = original)')
    )
    adjust_contrast = models.FloatField(
        null=True,
        blank=True,
        help_text=_('Contrast factor (1.0 = original)')
    )
    adjust_color = models.FloatField(
        null=True,
        blank=True,
        help_text=_('Color saturation factor (1.0 = original)')
    )
    adjust_sharpness = models.FloatField(
        null=True,
        blank=True,
        help_text=_('Sharpness factor (1.0 = original)')
    )
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text=_('Unique name for this preset')
    )
    description = models.TextField(
        blank=True,
        help_text=_('Description of this preset')
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['resource_type', 'format', 'name']
        verbose_name = _('Rendition Preset')
        verbose_name_plural = _('Rendition Presets')

    def __str__(self):
        return f"{self.resource_type} → {self.format} ({self.name})"

    def generate_rendition(self, publication_item):
        """
        Создает и запускает генерацию rendition'а для указанного publication item.
        """
        from .tasks import generate_rendition_task

        # Создаем GeneratedRendition объект
        rendition, created = GeneratedRendition.objects.get_or_create(
            publication_item=publication_item,
            preset=self,
            defaults={'status': 'pending'}
        )

        # Если уже существует и не в состоянии pending, не запускаем
        if not created and rendition.status not in ['pending', 'failed']:
            return rendition

        # Запускаем задачу
        generate_rendition_task.delay(rendition.id)

        return rendition


class Publication(models.Model):
    """
    Публикация материалов.
    """
    ACCESS_POLICY_CHOICES = [
        ('public', _('Public (token access)')),
        ('login', _('Login required')),
        ('both', _('Both public and login access')),
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='publications',
        help_text=_('Owner of this publication')
    )
    title = models.CharField(
        max_length=255,
        help_text=_('Title of the publication')
    )
    description = models.TextField(
        blank=True,
        help_text=_('Description of the publication')
    )
    access_policy = models.CharField(
        max_length=16,
        choices=ACCESS_POLICY_CHOICES,
        default='public',
        help_text=_('Access policy for this publication')
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('Expiration date and time')
    )
    max_downloads = models.IntegerField(
        null=True,
        blank=True,
        help_text=_('Maximum total downloads allowed')
    )
    presets = models.ManyToManyField(
        RenditionPreset,
        blank=True,
        related_name='publications',
        help_text=_('Rendition presets to generate')
    )
    recipient_lists = models.ManyToManyField(
        RecipientList,
        blank=True,
        related_name='publications',
        help_text=_('Recipient lists for this publication')
    )
    downloads_count = models.IntegerField(
        default=0,
        help_text=_('Total downloads count')
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        verbose_name = _('Publication')
        verbose_name_plural = _('Publications')

    def __str__(self):
        return self.title

    def generate_all_renditions(self):
        """
        Запускает генерацию всех rendition'ов для всех items публикации.
        """
        for item in self.items.all():
            for preset in self.presets.all():
                preset.generate_rendition(item)


class PublicationItem(models.Model):
    """
    Элемент публикации (ссылка на файл документа).
    """
    publication = models.ForeignKey(
        Publication,
        on_delete=models.CASCADE,
        related_name='items',
        help_text=_('Publication this item belongs to')
    )
    document_file = models.ForeignKey(
        'documents.DocumentFile',
        on_delete=models.CASCADE,
        help_text=_('Document file to include in publication')
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['publication', 'document_file']
        ordering = ['created']
        verbose_name = _('Publication Item')
        verbose_name_plural = _('Publication Items')

    def __str__(self):
        return f"{self.publication.title} → {self.document_file}"


class ShareLink(models.Model):
    """
    Ссылка для доступа к публикации.
    """
    publication = models.ForeignKey(
        Publication,
        on_delete=models.CASCADE,
        related_name='share_links',
        help_text=_('Publication this link provides access to')
    )
    token = models.CharField(
        max_length=64,
        unique=True,
        default=lambda: str(uuid.uuid4()),
        help_text=_('Unique access token')
    )
    recipient = models.ForeignKey(
        Recipient,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=_('Specific recipient (None for general link)')
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('Expiration date and time')
    )
    max_downloads = models.IntegerField(
        null=True,
        blank=True,
        help_text=_('Maximum downloads allowed for this link')
    )
    downloads_count = models.IntegerField(
        default=0,
        help_text=_('Current downloads count')
    )
    created = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('Last access timestamp')
    )

    class Meta:
        ordering = ['-created']
        verbose_name = _('Share Link')
        verbose_name_plural = _('Share Links')

    def __str__(self):
        return f"{self.publication.title} → {self.token[:8]}..."

    def is_valid(self):
        """
        Check if the share link is still valid.
        """
        from django.utils import timezone

        # Check expiration
        if self.expires_at and timezone.now() > self.expires_at:
            return False

        # Check download limit
        if self.max_downloads and self.downloads_count >= self.max_downloads:
            return False

        return True

    def can_download(self):
        """
        Check if download is allowed (valid and under limit).
        """
        return self.is_valid()

    def record_access(self, request):
        """
        Record access to this share link.
        """
        from django.utils import timezone
        from mayan.apps.distribution.models import AccessLog

        # Update last accessed
        self.last_accessed = timezone.now()
        self.save(update_fields=['last_accessed'])

        # Create access log
        AccessLog.objects.create(
            share_link=self,
            event='view',
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            timestamp=timezone.now()
        )

    def record_download(self, request, rendition=None):
        """
        Record download from this share link.
        """
        from django.utils import timezone
        from mayan.apps.distribution.models import AccessLog

        # Increment download count
        self.downloads_count += 1
        self.last_accessed = timezone.now()
        self.save(update_fields=['downloads_count', 'last_accessed'])

        # Create access log entry
        AccessLog.objects.create(
            share_link=self,
            rendition=rendition,
            event='download',
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            timestamp=timezone.now()
        )

    def _get_client_ip(self, request):
        """
        Get client IP address from request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class GeneratedRendition(models.Model):
    """
    Сгенерированный рендишен.
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
    ]

    publication_item = models.ForeignKey(
        PublicationItem,
        on_delete=models.CASCADE,
        related_name='renditions',
        help_text=_('Publication item this rendition is for')
    )
    preset = models.ForeignKey(
        RenditionPreset,
        on_delete=models.CASCADE,
        help_text=_('Preset used to generate this rendition')
    )
    file = models.FileField(
        upload_to='renditions/distribution/',
        null=True,
        blank=True,
        help_text=_('Generated rendition file')
    )
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default='pending',
        help_text=_('Generation status')
    )
    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        help_text=_('File size in bytes')
    )
    checksum = models.CharField(
        max_length=128,
        blank=True,
        help_text=_('File checksum (MD5 or SHA256)')
    )
    error_message = models.TextField(
        blank=True,
        help_text=_('Error message if generation failed')
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['publication_item', 'preset']
        ordering = ['-created']
        verbose_name = _('Generated Rendition')
        verbose_name_plural = _('Generated Renditions')

    def __str__(self):
        return f"{self.publication_item} → {self.preset}"

    def get_download_url(self):
        if not self.file:
            return None
        try:
            return self.file.storage.url(self.file.name)
        except Exception:
            return None


class AccessLog(models.Model):
    """
    Лог доступа к публикациям.
    """
    EVENT_CHOICES = [
        ('view', _('View')),
        ('download', _('Download')),
    ]

    share_link = models.ForeignKey(
        ShareLink,
        on_delete=models.CASCADE,
        related_name='access_logs',
        help_text=_('Share link that was accessed')
    )
    rendition = models.ForeignKey(
        GeneratedRendition,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=_('Rendition that was downloaded (for download events)')
    )
    event = models.CharField(
        max_length=16,
        choices=EVENT_CHOICES,
        help_text=_('Type of access event')
    )
    ip_address = models.GenericIPAddressField(
        help_text=_('IP address of the client')
    )
    user_agent = models.TextField(
        blank=True,
        help_text=_('User agent string')
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When the access occurred')
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('Access Log')
        verbose_name_plural = _('Access Logs')

    def __str__(self):
        return f"{self.share_link} → {self.event} @ {self.timestamp}"
