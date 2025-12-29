import uuid
import math

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

    def calculate_performance_score(self) -> float:
        """Calculate composite performance score (0-10) for the day.

        The score is a weighted, capped aggregation of the most important usage
        signals. We use logarithmic scaling for high-volume metrics to avoid
        outliers dominating the score.

        Weights (Phase 1-2 default):
        - Downloads: 40%
        - Views: 30%
        - Shares: 20%
        - CDN Bandwidth: 10%
        """
        downloads_score = min(10.0, math.log1p(self.downloads) * 2.0) if self.downloads else 0.0
        views_score = min(10.0, math.log1p(self.views) * 1.5) if self.views else 0.0
        shares_score = min(10.0, float(self.shares) * 2.0) if self.shares else 0.0
        bandwidth_score = min(10.0, float(self.cdn_bandwidth_gb) * 0.5) if self.cdn_bandwidth_gb else 0.0

        score = (
            downloads_score * 0.4 +
            views_score * 0.3 +
            shares_score * 0.2 +
            bandwidth_score * 0.1
        )
        return round(float(score), 2)


class Campaign(models.Model):
    """Marketing campaign or collection grouping documents (Level 2)."""

    STATUS_DRAFT = 'draft'
    STATUS_ACTIVE = 'active'
    STATUS_COMPLETED = 'completed'
    STATUS_ARCHIVED = 'archived'

    STATUS_CHOICES = (
        (STATUS_DRAFT, _('Draft')),
        (STATUS_ACTIVE, _('Active')),
        (STATUS_COMPLETED, _('Completed')),
        (STATUS_ARCHIVED, _('Archived')),
    )

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    label = models.CharField(max_length=255, db_index=True, verbose_name=_('Label'))
    description = models.TextField(blank=True, default='', verbose_name=_('Description'))
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default=STATUS_DRAFT, db_index=True,
        verbose_name=_('Status')
    )
    start_date = models.DateField(blank=True, null=True, db_index=True, verbose_name=_('Start date'))
    end_date = models.DateField(blank=True, null=True, db_index=True, verbose_name=_('End date'))

    created_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='analytics_campaigns_created',
        verbose_name=_('Created by')
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, db_index=True, verbose_name=_('Updated at'))

    # ROI inputs (Phase 2: manual; external integrations will come later).
    cost_amount = models.DecimalField(
        max_digits=14, decimal_places=2, blank=True, null=True,
        verbose_name=_('Cost amount')
    )
    revenue_amount = models.DecimalField(
        max_digits=14, decimal_places=2, blank=True, null=True,
        verbose_name=_('Revenue amount')
    )
    currency = models.CharField(
        max_length=10, blank=True, default='RUB', verbose_name=_('Currency')
    )

    class Meta:
        db_table = 'analytics_campaigns'
        verbose_name = _('Campaign')
        verbose_name_plural = _('Campaigns')
        indexes = (
            models.Index(fields=('status', '-updated_at')),
        )

    def __str__(self):
        return self.label

    def get_roi(self):
        """Return ROI ratio as revenue / cost, or None if not computable."""
        if not self.cost_amount or self.cost_amount == 0:
            return None
        if self.revenue_amount is None:
            return None
        return float(self.revenue_amount / self.cost_amount)


class CampaignAsset(models.Model):
    """Documents attached to a campaign (Level 2)."""

    campaign = models.ForeignKey(
        to='analytics.Campaign',
        on_delete=models.CASCADE,
        related_name='campaign_assets',
        verbose_name=_('Campaign')
    )
    document = models.ForeignKey(
        to='documents.Document',
        on_delete=models.CASCADE,
        related_name='campaign_memberships',
        verbose_name=_('Document')
    )
    sequence = models.PositiveIntegerField(default=0, verbose_name=_('Sequence'))
    added_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_('Added at'))

    class Meta:
        db_table = 'analytics_campaign_assets'
        verbose_name = _('Campaign asset')
        verbose_name_plural = _('Campaign assets')
        unique_together = (('campaign', 'document'),)
        indexes = (
            models.Index(fields=('campaign', 'sequence')),
            models.Index(fields=('campaign', '-added_at')),
        )

    def __str__(self):
        return f'{self.campaign_id} - {self.document_id}'


class CampaignDailyMetrics(models.Model):
    """Daily aggregated metrics for a campaign (Level 2)."""

    campaign = models.ForeignKey(
        to='analytics.Campaign',
        on_delete=models.CASCADE,
        related_name='daily_metrics',
        verbose_name=_('Campaign')
    )
    date = models.DateField(db_index=True, verbose_name=_('Date'))
    views = models.PositiveIntegerField(default=0, verbose_name=_('Views'))
    downloads = models.PositiveIntegerField(default=0, verbose_name=_('Downloads'))
    shares = models.PositiveIntegerField(default=0, verbose_name=_('Shares'))
    roi = models.FloatField(blank=True, null=True, verbose_name=_('ROI'))
    top_document = models.ForeignKey(
        to='documents.Document',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='campaign_top_document_metrics',
        verbose_name=_('Top document')
    )
    channel_breakdown = models.JSONField(blank=True, default=dict, verbose_name=_('Channel breakdown'))

    class Meta:
        db_table = 'analytics_campaign_daily_metrics'
        verbose_name = _('Campaign daily metrics')
        verbose_name_plural = _('Campaign daily metrics')
        unique_together = (('campaign', 'date'),)
        indexes = (
            models.Index(fields=('campaign', '-date')),
        )

    def __str__(self):
        return f'{self.campaign_id} - {self.date}'


class UserSession(models.Model):
    """User session tracking (Level 3)."""

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analytics_sessions',
        verbose_name=_('User')
    )
    session_key = models.CharField(max_length=128, blank=True, default='', db_index=True, verbose_name=_('Session key'))
    login_timestamp = models.DateTimeField(db_index=True, verbose_name=_('Login timestamp'))
    logout_timestamp = models.DateTimeField(blank=True, null=True, db_index=True, verbose_name=_('Logout timestamp'))
    session_duration_seconds = models.IntegerField(blank=True, null=True, verbose_name=_('Session duration (seconds)'))

    geo_country = models.CharField(max_length=2, blank=True, default='', verbose_name=_('Geo country'))
    geo_city = models.CharField(max_length=100, blank=True, default='', verbose_name=_('Geo city'))
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_('IP address'))
    user_agent = models.TextField(blank=True, default='', verbose_name=_('User agent'))

    class Meta:
        db_table = 'analytics_user_sessions'
        verbose_name = _('User session')
        verbose_name_plural = _('User sessions')
        indexes = (
            models.Index(fields=('user', '-login_timestamp')),
            models.Index(fields=('login_timestamp',)),
        )

    def __str__(self):
        return f'{self.user_id} - {self.login_timestamp}'


class UserDailyMetrics(models.Model):
    """Daily aggregated metrics for a user (Level 3)."""

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analytics_daily_metrics',
        verbose_name=_('User')
    )
    date = models.DateField(db_index=True, verbose_name=_('Date'))
    logins = models.PositiveIntegerField(default=0, verbose_name=_('Logins'))
    searches = models.PositiveIntegerField(default=0, verbose_name=_('Searches'))
    downloads = models.PositiveIntegerField(default=0, verbose_name=_('Downloads'))
    search_success_rate = models.FloatField(blank=True, null=True, verbose_name=_('Search success rate'))
    avg_search_to_find_minutes = models.IntegerField(blank=True, null=True, verbose_name=_('Avg search-to-find (minutes)'))

    user_department = models.CharField(max_length=100, blank=True, default='', db_index=True, verbose_name=_('User department'))

    class Meta:
        db_table = 'analytics_user_daily_metrics'
        verbose_name = _('User daily metrics')
        verbose_name_plural = _('User daily metrics')
        unique_together = (('user', 'date'),)
        indexes = (
            models.Index(fields=('date', 'user_department')),
        )

    def __str__(self):
        return f'{self.user_id} - {self.date}'


class ApprovalWorkflowEvent(models.Model):
    """Approval workflow analytics events (Level 3).

    This model captures key timestamps for approval cycles:
    submission -> approval/rejection, plus attempt numbers for first-time-right.
    """

    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = (
        (STATUS_PENDING, _('Pending')),
        (STATUS_APPROVED, _('Approved')),
        (STATUS_REJECTED, _('Rejected')),
    )

    document = models.ForeignKey(
        to='documents.Document',
        on_delete=models.CASCADE,
        related_name='analytics_approval_events',
        verbose_name=_('Document')
    )
    workflow_instance = models.ForeignKey(
        to='document_states.WorkflowInstance',
        on_delete=models.CASCADE,
        related_name='analytics_approval_events',
        verbose_name=_('Workflow instance')
    )
    submitter = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='analytics_approval_submissions',
        verbose_name=_('Submitter')
    )
    approver = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='analytics_approval_actions',
        verbose_name=_('Approver')
    )

    submitted_at = models.DateTimeField(db_index=True, verbose_name=_('Submitted at'))
    approved_at = models.DateTimeField(blank=True, null=True, db_index=True, verbose_name=_('Approved at'))
    rejected_at = models.DateTimeField(blank=True, null=True, db_index=True, verbose_name=_('Rejected at'))
    approval_time_days = models.FloatField(blank=True, null=True, verbose_name=_('Approval time (days)'))
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, db_index=True, verbose_name=_('Status'))
    rejection_reason = models.TextField(blank=True, default='', verbose_name=_('Rejection reason'))
    attempt_number = models.PositiveIntegerField(default=1, verbose_name=_('Attempt number'))

    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_('Created at'))

    class Meta:
        db_table = 'analytics_approval_workflow_events'
        verbose_name = _('Approval workflow event')
        verbose_name_plural = _('Approval workflow events')
        indexes = (
            models.Index(fields=('document', '-submitted_at')),
            models.Index(fields=('workflow_instance', '-submitted_at')),
            models.Index(fields=('status', '-submitted_at')),
        )

    def __str__(self):
        return f'{self.document_id} - {self.status} - {self.submitted_at}'


class AnalyticsAlert(models.Model):
    """Analytics-driven alerts (Phase 2+)."""

    ALERT_TYPE_UNDERPERFORMING = 'underperforming_asset'
    ALERT_TYPE_NO_DOWNLOADS = 'no_downloads'
    ALERT_TYPE_APPROVAL_REJECTED = 'approval_rejected'
    ALERT_TYPE_STORAGE_LIMIT = 'storage_limit'

    SEVERITY_CRITICAL = 'critical'
    SEVERITY_WARNING = 'warning'
    SEVERITY_INFO = 'info'

    SEVERITY_CHOICES = (
        (SEVERITY_CRITICAL, _('Critical')),
        (SEVERITY_WARNING, _('Warning')),
        (SEVERITY_INFO, _('Info')),
    )

    alert_type = models.CharField(max_length=50, db_index=True, verbose_name=_('Alert type'))
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, db_index=True, verbose_name=_('Severity'))
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    message = models.TextField(blank=True, default='', verbose_name=_('Message'))

    document = models.ForeignKey(
        to='documents.Document',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='analytics_alerts',
        verbose_name=_('Document')
    )
    campaign = models.ForeignKey(
        to='analytics.Campaign',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='analytics_alerts',
        verbose_name=_('Campaign')
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_('Created at'))
    resolved_at = models.DateTimeField(blank=True, null=True, db_index=True, verbose_name=_('Resolved at'))
    metadata = models.JSONField(blank=True, default=dict, verbose_name=_('Metadata'))

    class Meta:
        db_table = 'analytics_alerts'
        verbose_name = _('Analytics alert')
        verbose_name_plural = _('Analytics alerts')
        indexes = (
            models.Index(fields=('alert_type', '-created_at')),
            models.Index(fields=('severity', '-created_at')),
            models.Index(fields=('resolved_at',)),
        )

    def __str__(self):
        return f'{self.alert_type} - {self.title}'


class SearchQuery(models.Model):
    """Raw search query logs (Level 4)."""

    SEARCH_TYPE_KEYWORD = 'keyword'
    SEARCH_TYPE_FILTER = 'filter'
    SEARCH_TYPE_FACETED = 'faceted'
    SEARCH_TYPE_AI = 'ai'

    SEARCH_TYPE_CHOICES = (
        (SEARCH_TYPE_KEYWORD, _('Keyword')),
        (SEARCH_TYPE_FILTER, _('Filter')),
        (SEARCH_TYPE_FACETED, _('Faceted')),
        (SEARCH_TYPE_AI, _('AI')),
    )

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='analytics_search_queries',
        verbose_name=_('User')
    )
    query_text = models.CharField(max_length=500, db_index=True, verbose_name=_('Query text'))
    search_type = models.CharField(
        max_length=50, choices=SEARCH_TYPE_CHOICES, default=SEARCH_TYPE_KEYWORD,
        db_index=True, verbose_name=_('Search type')
    )
    results_count = models.IntegerField(blank=True, null=True, verbose_name=_('Results count'))
    response_time_ms = models.IntegerField(blank=True, null=True, verbose_name=_('Response time (ms)'))
    filters_applied = models.JSONField(blank=True, default=dict, verbose_name=_('Filters applied'))

    was_clicked_result_document_id = models.IntegerField(blank=True, null=True, verbose_name=_('Clicked document ID'))
    click_position = models.IntegerField(blank=True, null=True, verbose_name=_('Click position'))
    time_to_click_seconds = models.IntegerField(blank=True, null=True, verbose_name=_('Time to click (seconds)'))

    was_downloaded = models.BooleanField(default=False, verbose_name=_('Was downloaded'))
    time_to_download_seconds = models.IntegerField(blank=True, null=True, verbose_name=_('Time to download (seconds)'))

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_('Timestamp'))
    user_department = models.CharField(max_length=100, blank=True, default='', db_index=True, verbose_name=_('User department'))

    class Meta:
        db_table = 'analytics_search_queries'
        verbose_name = _('Search query')
        verbose_name_plural = _('Search queries')
        indexes = (
            models.Index(fields=('-timestamp',)),
            models.Index(fields=('search_type', '-timestamp')),
        )

    def __str__(self):
        return f'{self.query_text} - {self.timestamp}'


class SearchDailyMetrics(models.Model):
    """Daily aggregated search metrics (Level 4)."""

    date = models.DateField(primary_key=True, verbose_name=_('Date'))
    total_searches = models.PositiveIntegerField(default=0, verbose_name=_('Total searches'))
    successful_searches = models.PositiveIntegerField(default=0, verbose_name=_('Successful searches'))
    null_searches = models.PositiveIntegerField(default=0, verbose_name=_('Null searches'))
    ctr = models.FloatField(blank=True, null=True, verbose_name=_('CTR'))
    avg_response_time_ms = models.IntegerField(blank=True, null=True, verbose_name=_('Avg response time (ms)'))
    top_queries = models.JSONField(blank=True, default=list, verbose_name=_('Top queries'))
    null_queries = models.JSONField(blank=True, default=list, verbose_name=_('Null queries'))

    class Meta:
        db_table = 'analytics_search_daily_metrics'
        verbose_name = _('Search daily metrics')
        verbose_name_plural = _('Search daily metrics')

    def __str__(self):
        return str(self.date)

