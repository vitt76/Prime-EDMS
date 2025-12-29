from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class AssetEvent(models.Model):
    """Raw analytics events for a single document (Level 1)."""

    EVENT_TYPE_DOWNLOAD = 'download'
    EVENT_TYPE_VIEW = 'view'
    EVENT_TYPE_SHARE = 'share'
    EVENT_TYPE_UPLOAD = 'upload'
    EVENT_TYPE_DELIVER = 'deliver'

    EVENT_TYPE_CHOICES = (
        (EVENT_TYPE_DOWNLOAD, _('Download')),
        (EVENT_TYPE_VIEW, _('View')),
        (EVENT_TYPE_SHARE, _('Share')),
        (EVENT_TYPE_UPLOAD, _('Upload')),
        (EVENT_TYPE_DELIVER, _('Deliver')),
    )

    id = models.BigAutoField(primary_key=True)
    document = models.ForeignKey(
        to='documents.Document',
        on_delete=models.CASCADE,
        related_name='analytics_events',
        verbose_name=_('Document')
    )
    event_type = models.CharField(
        max_length=50, choices=EVENT_TYPE_CHOICES, db_index=True,
        verbose_name=_('Event type')
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='analytics_asset_events',
        verbose_name=_('User')
    )
    user_department = models.CharField(
        max_length=100, blank=True, default='',
        verbose_name=_('User department')
    )
    channel = models.CharField(
        max_length=50, blank=True, default='',
        help_text=_('Examples: dam_interface, public_link, portal, api'),
        verbose_name=_('Channel')
    )
    intended_use = models.CharField(
        max_length=50, blank=True, default='',
        help_text=_('Examples: email, social, print, web'),
        verbose_name=_('Intended use')
    )
    bandwidth_bytes = models.BigIntegerField(
        blank=True, null=True, verbose_name=_('Bandwidth (bytes)')
    )
    latency_seconds = models.IntegerField(
        blank=True, null=True, verbose_name=_('Latency (seconds)')
    )
    timestamp = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name=_('Timestamp')
    )
    metadata = models.JSONField(
        blank=True, default=dict, verbose_name=_('Metadata')
    )

    class Meta:
        db_table = 'analytics_asset_events'
        verbose_name = _('Asset event')
        verbose_name_plural = _('Asset events')
        indexes = (
            models.Index(fields=('document', '-timestamp')),
            models.Index(fields=('event_type', 'timestamp')),
            models.Index(fields=('user', 'timestamp')),
        )

    def __str__(self):
        return f'{self.event_type} - {self.document_id}'


class AssetDailyMetrics(models.Model):
    """Daily aggregated metrics for a single document (Level 1)."""

    document = models.ForeignKey(
        to='documents.Document',
        on_delete=models.CASCADE,
        related_name='analytics_daily_metrics',
        verbose_name=_('Document')
    )
    date = models.DateField(db_index=True, verbose_name=_('Date'))
    downloads = models.PositiveIntegerField(default=0, verbose_name=_('Downloads'))
    views = models.PositiveIntegerField(default=0, verbose_name=_('Views'))
    shares = models.PositiveIntegerField(default=0, verbose_name=_('Shares'))
    cdn_bandwidth_gb = models.FloatField(default=0.0, verbose_name=_('CDN bandwidth (GB)'))
    performance_score = models.FloatField(default=0.0, verbose_name=_('Performance score'))
    top_channel = models.CharField(max_length=50, blank=True, default='', verbose_name=_('Top channel'))

    class Meta:
        db_table = 'analytics_asset_daily_metrics'
        verbose_name = _('Asset daily metrics')
        verbose_name_plural = _('Asset daily metrics')
        unique_together = (('document', 'date'),)
        indexes = (
            models.Index(fields=('date', '-performance_score')),
        )

    def __str__(self):
        return f'{self.document_id} - {self.date}'


