import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone

from .models import (
    ApprovalWorkflowEvent, AnalyticsAlert, AssetDailyMetrics, AssetEvent,
    SearchDailyMetrics, SearchQuery
)

logger = logging.getLogger(name=__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60, queue='documents')
def aggregate_daily_metrics(self, date_iso: str = '') -> int:
    """Aggregate raw AssetEvent rows into AssetDailyMetrics.

    Args:
        date_iso: Optional ISO date (YYYY-MM-DD). If omitted, aggregates for yesterday.

    Returns:
        Number of documents aggregated (rows upserted).
    """
    if date_iso:
        target_date = timezone.datetime.fromisoformat(date_iso).date()
    else:
        target_date = timezone.now().date() - timedelta(days=1)

    rows = (
        AssetEvent.objects.filter(timestamp__date=target_date)
        .values('document_id')
        .annotate(
            downloads=Count('id', filter=Q(event_type=AssetEvent.EVENT_TYPE_DOWNLOAD)),
            views=Count('id', filter=Q(event_type=AssetEvent.EVENT_TYPE_VIEW)),
            shares=Count('id', filter=Q(event_type=AssetEvent.EVENT_TYPE_SHARE)),
            bandwidth_bytes=Sum('bandwidth_bytes', filter=Q(event_type=AssetEvent.EVENT_TYPE_DELIVER)),
        )
    )

    # Precompute top channel per document for the date (best-effort).
    top_channel_map = {}
    for row in (
        AssetEvent.objects.filter(timestamp__date=target_date)
        .exclude(channel='')
        .values('document_id', 'channel')
        .annotate(count=Count('id'))
        .order_by('document_id', '-count')
    ):
        document_id = row['document_id']
        if document_id not in top_channel_map:
            top_channel_map[document_id] = row.get('channel') or ''

    upserts = 0
    for row in rows:
        bandwidth_bytes = row.get('bandwidth_bytes') or 0
        metrics, _ = AssetDailyMetrics.objects.update_or_create(
            document_id=row['document_id'],
            date=target_date,
            defaults={
                'downloads': row.get('downloads') or 0,
                'views': row.get('views') or 0,
                'shares': row.get('shares') or 0,
                'cdn_bandwidth_gb': round(bandwidth_bytes / (1024 ** 3), 6) if bandwidth_bytes else 0.0,
            }
        )

        # Compute derived fields.
        metrics.performance_score = metrics.calculate_performance_score()
        metrics.top_channel = top_channel_map.get(metrics.document_id, '') or ''
        metrics.save(update_fields=('performance_score', 'top_channel'))
        upserts += 1

    return upserts


@shared_task(bind=True, max_retries=3, default_retry_delay=60, queue='documents')
def aggregate_search_daily_metrics(self, date_iso: str = '') -> int:
    """Aggregate raw SearchQuery rows into SearchDailyMetrics.

    Args:
        date_iso: Optional ISO date (YYYY-MM-DD). If omitted, aggregates for yesterday.

    Returns:
        1 if aggregated for the date (row upserted), otherwise 0.
    """
    if date_iso:
        target_date = timezone.datetime.fromisoformat(date_iso).date()
    else:
        target_date = timezone.now().date() - timedelta(days=1)

    qs = SearchQuery.objects.filter(timestamp__date=target_date)

    total_searches = qs.count()
    if not total_searches:
        SearchDailyMetrics.objects.update_or_create(
            date=target_date,
            defaults={
                'total_searches': 0,
                'successful_searches': 0,
                'null_searches': 0,
                'ctr': None,
                'avg_response_time_ms': None,
                'top_queries': [],
                'null_queries': [],
            }
        )
        return 1

    successful_searches = qs.filter(results_count__gt=0).count()
    null_searches = qs.filter(results_count=0).count()

    avg_response_time_ms = qs.aggregate(
        avg=Avg('response_time_ms')
    )['avg']
    if avg_response_time_ms is not None:
        avg_response_time_ms = int(avg_response_time_ms)

    top_queries = list(
        qs.values('query_text').annotate(count=Count('id')).order_by('-count')[:20]
    )
    null_queries = list(
        qs.filter(results_count=0).values('query_text').annotate(count=Count('id')).order_by('-count')[:20]
    )

    SearchDailyMetrics.objects.update_or_create(
        date=target_date,
        defaults={
            'total_searches': total_searches,
            'successful_searches': successful_searches,
            'null_searches': null_searches,
            'ctr': None,
            'avg_response_time_ms': avg_response_time_ms,
            'top_queries': top_queries,
            'null_queries': null_queries,
        }
    )

    return 1


@shared_task(bind=True, max_retries=3, default_retry_delay=60, queue='documents')
def cleanup_old_events(self, retention_days: int = 90) -> dict:
    """Delete raw analytics events older than retention window.

    Args:
        retention_days: Number of days to retain raw events.

    Returns:
        Dictionary with deletion counts (best-effort).
    """
    cutoff = timezone.now() - timedelta(days=int(retention_days))

    deleted_asset_events = 0
    deleted_search_queries = 0

    try:
        deleted_asset_events, _ = AssetEvent.objects.filter(timestamp__lt=cutoff).delete()
    except Exception as exc:
        logger.exception('Failed to cleanup AssetEvent rows: %s', exc)

    try:
        deleted_search_queries, _ = SearchQuery.objects.filter(timestamp__lt=cutoff).delete()
    except Exception as exc:
        logger.exception('Failed to cleanup SearchQuery rows: %s', exc)

    return {
        'cutoff': cutoff.isoformat(),
        'deleted_asset_events': deleted_asset_events,
        'deleted_search_queries': deleted_search_queries,
    }


@shared_task(bind=True, max_retries=3, default_retry_delay=60, queue='documents')
def generate_analytics_alerts(self, days: int = 90) -> dict:
    """Generate basic analytics alerts (Phase 2 MVP).

    Alerts:
    - Assets without downloads (archiving candidates)
    - Recent approval rejections
    - Storage near limit
    """
    created = 0
    now = timezone.now()
    date_from = (now - timedelta(days=int(days))).date()

    # 1) Assets without downloads in the window (from daily metrics).
    try:
        no_download_rows = (
            AssetDailyMetrics.objects.filter(date__gte=date_from)
            .values('document_id')
            .annotate(downloads=Sum('downloads'), views=Sum('views'))
            .filter(downloads=0)
            .order_by('-views')[:50]
        )
        for row in no_download_rows:
            doc_id = row['document_id']
            title = 'Asset without downloads'
            message = f'No downloads in last {days} days. Views: {int(row.get("views") or 0)}.'

            exists = AnalyticsAlert.objects.filter(
                alert_type=AnalyticsAlert.ALERT_TYPE_NO_DOWNLOADS,
                document_id=doc_id,
                resolved_at__isnull=True
            ).exists()
            if exists:
                continue

            AnalyticsAlert.objects.create(
                alert_type=AnalyticsAlert.ALERT_TYPE_NO_DOWNLOADS,
                severity=AnalyticsAlert.SEVERITY_INFO,
                title=title,
                message=message,
                document_id=doc_id,
                metadata={'days': int(days), 'views': int(row.get('views') or 0)},
            )
            created += 1
    except Exception as exc:
        logger.exception('Failed generating no-downloads alerts: %s', exc)

    # 2) Approval rejected in last 7 days.
    try:
        rejected_qs = ApprovalWorkflowEvent.objects.filter(
            status=ApprovalWorkflowEvent.STATUS_REJECTED,
            rejected_at__gte=now - timedelta(days=7)
        ).order_by('-rejected_at')[:50]
        for ev in rejected_qs:
            exists = AnalyticsAlert.objects.filter(
                alert_type=AnalyticsAlert.ALERT_TYPE_APPROVAL_REJECTED,
                document_id=ev.document_id,
                resolved_at__isnull=True
            ).exists()
            if exists:
                continue
            AnalyticsAlert.objects.create(
                alert_type=AnalyticsAlert.ALERT_TYPE_APPROVAL_REJECTED,
                severity=AnalyticsAlert.SEVERITY_WARNING,
                title='Approval rejected',
                message=(ev.rejection_reason or '').strip() or 'Approval rejected.',
                document_id=ev.document_id,
                metadata={'workflow_instance_id': ev.workflow_instance_id, 'attempt': ev.attempt_number},
            )
            created += 1
    except Exception as exc:
        logger.exception('Failed generating approval-rejected alerts: %s', exc)

    # 3) Storage limit warning (single global alert).
    try:
        from mayan.apps.documents.models import DocumentFile

        used_bytes = DocumentFile.valid.aggregate(total=Sum('size'))['total'] or 0
        storage_limit_gb = float(getattr(settings, 'ANALYTICS_STORAGE_LIMIT_GB', 1000.0))
        threshold_gb = float(getattr(settings, 'ANALYTICS_STORAGE_ALERT_THRESHOLD_GB', storage_limit_gb * 0.9))
        used_gb = float(used_bytes) / (1024 ** 3) if used_bytes else 0.0

        if storage_limit_gb and used_gb >= threshold_gb:
            exists = AnalyticsAlert.objects.filter(
                alert_type=AnalyticsAlert.ALERT_TYPE_STORAGE_LIMIT,
                resolved_at__isnull=True
            ).exists()
            if not exists:
                AnalyticsAlert.objects.create(
                    alert_type=AnalyticsAlert.ALERT_TYPE_STORAGE_LIMIT,
                    severity=AnalyticsAlert.SEVERITY_WARNING,
                    title='Storage near limit',
                    message='Projected storage usage is near the configured limit.',
                    metadata={'storage_limit_gb': storage_limit_gb, 'threshold_gb': threshold_gb, 'used_gb': round(used_gb, 3)},
                )
                created += 1
    except Exception as exc:
        logger.exception('Failed generating storage-limit alerts: %s', exc)

    return {'created': created}
