import logging
from datetime import timedelta
from decimal import Decimal

from celery import shared_task
from django.apps import apps as django_apps
from django.conf import settings
from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone
from typing import Optional

from mayan.apps.documents.models import Document

from .models import (
    ApprovalWorkflowEvent, AnalyticsAlert, AssetDailyMetrics, AssetEvent,
    CampaignDailyMetrics, CDNDailyCost, CDNRate, SearchDailyMetrics, SearchQuery,
    SearchSession, UserDailyMetrics, CampaignEngagementEvent
)
from .realtime import notify_analytics_refresh

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

    try:
        notify_analytics_refresh(reason='aggregate_daily_metrics')
    except Exception:
        pass

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
        try:
            notify_analytics_refresh(reason='aggregate_search_daily_metrics')
        except Exception:
            pass
        return 1

    # Success definition (enterprise DAM): success if user clicked or downloaded after search.
    successful_searches = qs.filter(
        Q(was_downloaded=True) | Q(was_clicked_result_document_id__isnull=False)
    ).count()
    null_searches = qs.filter(results_count=0).count()

    click_count = qs.filter(was_clicked_result_document_id__isnull=False).count()
    ctr = None
    if total_searches:
        ctr = round((click_count / total_searches) * 100, 2)

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
            'ctr': ctr,
            'avg_response_time_ms': avg_response_time_ms,
            'top_queries': top_queries,
            'null_queries': null_queries,
        }
    )

    try:
        notify_analytics_refresh(reason='aggregate_search_daily_metrics')
    except Exception:
        pass

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
    deleted_search_sessions = 0
    deleted_asset_daily_metrics = 0
    deleted_search_daily_metrics = 0
    deleted_user_daily_metrics = 0

    try:
        deleted_asset_events, _ = AssetEvent.objects.filter(timestamp__lt=cutoff).delete()
    except Exception as exc:
        logger.exception('Failed to cleanup AssetEvent rows: %s', exc)

    try:
        deleted_search_queries, _ = SearchQuery.objects.filter(timestamp__lt=cutoff).delete()
    except Exception as exc:
        logger.exception('Failed to cleanup SearchQuery rows: %s', exc)

    try:
        deleted_search_sessions, _ = SearchSession.objects.filter(started_at__lt=cutoff).delete()
    except Exception as exc:
        logger.exception('Failed to cleanup SearchSession rows: %s', exc)

    # Optional retention for aggregated tables.
    try:
        agg_days = int(getattr(settings, 'ANALYTICS_AGGREGATED_RETENTION_DAYS', 365))
        agg_cutoff = timezone.now().date() - timedelta(days=agg_days)
    except Exception:
        agg_cutoff = None

    if agg_cutoff:
        try:
            deleted_asset_daily_metrics, _ = AssetDailyMetrics.objects.filter(date__lt=agg_cutoff).delete()
        except Exception as exc:
            logger.exception('Failed to cleanup AssetDailyMetrics rows: %s', exc)
        try:
            deleted_search_daily_metrics, _ = SearchDailyMetrics.objects.filter(date__lt=agg_cutoff).delete()
        except Exception as exc:
            logger.exception('Failed to cleanup SearchDailyMetrics rows: %s', exc)
        try:
            deleted_user_daily_metrics, _ = UserDailyMetrics.objects.filter(date__lt=agg_cutoff).delete()
        except Exception as exc:
            logger.exception('Failed to cleanup UserDailyMetrics rows: %s', exc)

    try:
        notify_analytics_refresh(reason='cleanup_old_events')
    except Exception:
        pass

    return {
        'cutoff': cutoff.isoformat(),
        'aggregated_cutoff': agg_cutoff.isoformat() if agg_cutoff else None,
        'deleted_asset_events': deleted_asset_events,
        'deleted_search_queries': deleted_search_queries,
        'deleted_search_sessions': deleted_search_sessions,
        'deleted_asset_daily_metrics': deleted_asset_daily_metrics,
        'deleted_search_daily_metrics': deleted_search_daily_metrics,
        'deleted_user_daily_metrics': deleted_user_daily_metrics,
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

    # 4) Metadata completeness (Content Intelligence MVP).
    try:
        required = getattr(settings, 'ANALYTICS_REQUIRED_METADATA_TYPES', []) or []
        required = [str(x).strip() for x in required if str(x).strip()]
        if required:
            DocumentMetadata = django_apps.get_model('metadata', 'DocumentMetadata')
            recent_docs = (
                Document.valid.filter(in_trash=False)
                .order_by('-datetime_created')
                .values_list('pk', flat=True)[:500]
            )
            for doc_id in recent_docs:
                meta = list(
                    DocumentMetadata.objects.filter(document_id=doc_id)
                    .select_related('metadata_type')
                    .values_list('metadata_type__name', 'metadata_type__label', 'value')
                )
                present = set()
                for name, label, value in meta:
                    if (value or '').strip():
                        present.add((name or '').strip())
                        present.add((label or '').strip())

                missing = [m for m in required if m not in present]
                if not missing:
                    continue

                exists = AnalyticsAlert.objects.filter(
                    alert_type='metadata_incomplete',
                    document_id=doc_id,
                    resolved_at__isnull=True
                ).exists()
                if exists:
                    continue

                AnalyticsAlert.objects.create(
                    alert_type='metadata_incomplete',
                    severity=AnalyticsAlert.SEVERITY_WARNING,
                    title='Metadata completeness issue',
                    message=f'Missing required metadata fields: {", ".join(missing[:10])}',
                    document_id=doc_id,
                    metadata={'missing': missing, 'required': required},
                )
                created += 1
    except Exception as exc:
        logger.exception('Failed generating metadata completeness alerts: %s', exc)

    try:
        notify_analytics_refresh(reason='generate_analytics_alerts')
    except Exception:
        pass
    return {'created': created}


@shared_task(bind=True, max_retries=3, default_retry_delay=60, queue='documents')
def aggregate_user_daily_metrics(self, date_iso: str = '') -> int:
    """Aggregate user-level metrics, including Avg Search-to-Find Time.

    Args:
        date_iso: Optional ISO date (YYYY-MM-DD). If omitted, aggregates for yesterday.

    Returns:
        Number of users aggregated (rows upserted).
    """
    if date_iso:
        target_date = timezone.datetime.fromisoformat(date_iso).date()
    else:
        target_date = timezone.now().date() - timedelta(days=1)

    sessions_qs = SearchSession.objects.filter(
        started_at__date=target_date,
        time_to_find_seconds__isnull=False
    )

    user_ids = list(sessions_qs.values_list('user_id', flat=True).distinct())
    upserts = 0
    for user_id in user_ids:
        avg_seconds = sessions_qs.filter(user_id=user_id).aggregate(
            avg=Avg('time_to_find_seconds')
        )['avg']
        avg_minutes = int((avg_seconds or 0) / 60) if avg_seconds is not None else None

        UserDailyMetrics.objects.update_or_create(
            user_id=user_id,
            date=target_date,
            defaults={
                'avg_search_to_find_minutes': avg_minutes
            }
        )
        upserts += 1

    try:
        notify_analytics_refresh(reason='aggregate_user_daily_metrics')
    except Exception:
        pass

    return upserts


@shared_task(bind=True, max_retries=3, default_retry_delay=60, queue='documents')
def calculate_cdn_daily_costs(self, date_iso: str = '') -> int:
    """Calculate daily CDN cost rollups based on bandwidth and configured rates.

    Notes:
        This is a Phase 2 best-effort implementation. Channels are derived from
        `AssetDailyMetrics.top_channel` (or 'default' if empty).

    Args:
        date_iso: Optional ISO date (YYYY-MM-DD). If omitted, calculates for yesterday.

    Returns:
        Number of rows upserted in CDNDailyCost.
    """
    if date_iso:
        target_date = timezone.datetime.fromisoformat(date_iso).date()
    else:
        target_date = timezone.now().date() - timedelta(days=1)

    rates = list(
        CDNRate.objects.filter(effective_from__lte=target_date).filter(
            Q(effective_to__isnull=True) | Q(effective_to__gte=target_date)
        )
    )

    def pick_rate(channel: str) -> Optional[CDNRate]:
        for rate in rates:
            if rate.channel == channel:
                return rate
        for rate in rates:
            if rate.channel == 'default':
                return rate
        return None

    rows = (
        AssetDailyMetrics.objects.filter(date=target_date)
        .values('top_channel')
        .annotate(total_gb=Sum('cdn_bandwidth_gb'))
    )

    upserts = 0
    for row in rows:
        channel = (row.get('top_channel') or '').strip() or 'default'
        total_gb = float(row.get('total_gb') or 0.0)
        if total_gb <= 0:
            continue

        rate = pick_rate(channel=channel)
        if not rate:
            continue

        cost = (Decimal(str(total_gb)) * rate.cost_per_gb_usd).quantize(Decimal('0.01'))

        CDNDailyCost.objects.update_or_create(
            date=target_date,
            region=rate.region,
            channel=channel,
            defaults={'bandwidth_gb': total_gb, 'cost_usd': cost}
        )
        upserts += 1

    try:
        notify_analytics_refresh(reason='calculate_cdn_daily_costs')
    except Exception:
        pass

    return upserts


@shared_task(bind=True, max_retries=3, default_retry_delay=60, queue='documents')
def aggregate_campaign_engagement_daily_metrics(self, date_iso: str = '') -> int:
    """Aggregate campaign/collection engagement (avg minutes) per day."""
    if date_iso:
        target_date = timezone.datetime.fromisoformat(date_iso).date()
    else:
        target_date = timezone.now().date() - timedelta(days=1)

    qs = CampaignEngagementEvent.objects.filter(started_at__date=target_date)
    rows = qs.values('campaign_id').annotate(avg_seconds=Avg('duration_seconds'))

    upserts = 0
    for row in rows:
        avg_seconds = row.get('avg_seconds')
        avg_minutes = None
        if avg_seconds is not None:
            avg_minutes = round(float(avg_seconds) / 60.0, 3)

        CampaignDailyMetrics.objects.update_or_create(
            campaign_id=row['campaign_id'],
            date=target_date,
            defaults={'avg_engagement_minutes': avg_minutes}
        )
        upserts += 1

    try:
        notify_analytics_refresh(reason='aggregate_campaign_engagement_daily_metrics')
    except Exception:
        pass

    return upserts
