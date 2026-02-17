import logging
from datetime import timedelta
from decimal import Decimal

from celery import shared_task
from django.apps import apps as django_apps
from django.conf import settings
from django.db.models import Avg, Count, Q, Sum
from django.core.mail import EmailMessage
from django.utils import timezone
from typing import Optional

from mayan.apps.documents.models import Document
from mayan.apps.organizations.models import Organization
from mayan.apps.organizations.tasks import TenantAwareTask

from .models import (
    ApprovalWorkflowEvent, AnalyticsAlert, AnalyticsReportTask,
    AssetDailyMetrics, AssetEvent, CampaignDailyMetrics, CDNDailyCost, CDNRate,
    OrganizationBandwidthDaily, SearchDailyMetrics, SearchQuery, SearchSession,
    UserDailyMetrics, CampaignEngagementEvent, DistributionEvent
)
from .realtime import notify_analytics_refresh
from .services import link_download_to_latest_search_session
from .utils import get_geo_from_ip
from .providers.registry import AnalyticsProviderRegistry, register_default_providers
from .reports import CampaignPDFReport

logger = logging.getLogger(name=__name__)


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=30,
    queue='documents',
    base=TenantAwareTask,
)
def track_asset_event_async(
    self,
    organization_id: str,
    user_id: Optional[int],
    document_id: Optional[int],
    event_type: str,
    ip_address: str = '',
    user_agent: str = '',
    referrer: str = '',
    metadata: Optional[dict] = None,
    search_session_id: Optional[str] = None,
    bandwidth_bytes: Optional[int] = None,
    **kwargs
) -> None:
    """Create a single AssetEvent asynchronously (e.g. from middleware).

    TenantAwareTask sets tenant context from organization_id in kwargs.
    Stores ip_address in metadata for geo enrichment; links download to SearchSession when possible.
    """
    import uuid as uuid_module
    try:
        org_id = kwargs.get('organization_id') or organization_id
        if not org_id:
            logger.warning('track_asset_event_async: missing organization_id')
            return
        if not document_id:
            logger.warning('track_asset_event_async: missing document_id')
            return
        try:
            organization = Organization.objects.get(pk=org_id)
        except (Organization.DoesNotExist, ValueError, TypeError):
            logger.warning('track_asset_event_async: organization_id=%s not found', org_id)
            return
        document = Document.objects.filter(pk=document_id).first()
        if not document:
            logger.warning('track_asset_event_async: document_id=%s not found', document_id)
            return
        org_from_doc = getattr(document, 'organization_id', None)
        if org_from_doc is not None and org_from_doc != organization.pk:
            logger.warning(
                'track_asset_event_async: document %s does not belong to org %s',
                document_id, org_id
            )
            return

        if event_type == AssetEvent.EVENT_TYPE_DOWNLOAD and bandwidth_bytes is None:
            try:
                latest_file = document.files.order_by('-timestamp').first()
                if latest_file and getattr(latest_file, 'size', None) is not None:
                    bandwidth_bytes = latest_file.size
            except Exception:
                pass

        meta = (metadata or {}).copy()
        if ip_address:
            meta['ip_address'] = ip_address[:45]

        parsed_session_uuid = None
        if search_session_id:
            try:
                parsed_session_uuid = uuid_module.UUID(search_session_id)
            except (ValueError, TypeError):
                parsed_session_uuid = None

        event = AssetEvent.objects.create(
            organization_id=organization.pk,
            document_id=document_id,
            user_id=user_id,
            event_type=event_type,
            channel='api',
            user_department='',
            intended_use='',
            metadata=meta,
            search_session_id=parsed_session_uuid,
            bandwidth_bytes=bandwidth_bytes,
        )

        if event_type == AssetEvent.EVENT_TYPE_DOWNLOAD and user_id:
            user = None
            try:
                User = django_apps.get_model(settings.AUTH_USER_MODEL)
                user = User.objects.filter(pk=user_id).first()
            except Exception:
                pass
            if parsed_session_uuid and user:
                try:
                    session = SearchSession.objects_unfiltered.filter(
                        pk=parsed_session_uuid,
                        organization_id=organization.pk,
                        user_id=user_id,
                    ).first()
                    if session:
                        delta_seconds = int((event.timestamp - session.started_at).total_seconds())
                        session.ended_at = event.timestamp
                        session.last_download_event = event
                        session.time_to_find_seconds = max(0, delta_seconds)
                        session.save(update_fields=('ended_at', 'last_download_event', 'time_to_find_seconds'))
                except Exception as exc:
                    logger.debug('track_asset_event_async: could not update SearchSession: %s', exc)
            elif user:
                link_download_to_latest_search_session(
                    user=user,
                    download_event=event,
                    max_window_minutes=30,
                )
    except Exception as exc:
        logger.exception('track_asset_event_async failed: %s', exc)
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=60,
    queue='documents',
    base=TenantAwareTask,
)
def generate_analytics_report(self, report_task_id: int, **kwargs) -> None:
    """Generate analytics report (JSON) and save to MEDIA_ROOT; update task status."""
    import json
    import os

    organization_id = kwargs.get('organization_id')
    if not organization_id:
        logger.warning('generate_analytics_report: missing organization_id')
        return
    try:
        report_task = AnalyticsReportTask.objects_unfiltered.get(pk=report_task_id)
    except AnalyticsReportTask.DoesNotExist:
        logger.warning('generate_analytics_report: task %s not found', report_task_id)
        return
    if str(report_task.organization_id) != str(organization_id):
        logger.warning(
            'generate_analytics_report: task %s org %s != %s',
            report_task_id, report_task.organization_id, organization_id
        )
        return
    report_task.status = AnalyticsReportTask.STATUS_PROCESSING
    report_task.save(update_fields=['status'])

    try:
        params = report_task.parameters or {}
        date_range = params.get('date_range') or {}
        date_from = date_range.get('date_from') or date_range.get('from')
        date_to = date_range.get('date_to') or date_range.get('to')
        from django.utils.dateparse import parse_date
        from django.db.models import Sum

        qs = AssetEvent.objects_unfiltered.filter(organization_id=report_task.organization_id)
        if date_from:
            qs = qs.filter(timestamp__date__gte=parse_date(date_from))
        if date_to:
            qs = qs.filter(timestamp__date__lte=parse_date(date_to))

        by_type = dict(
            qs.values('event_type').annotate(cnt=Count('id')).values_list('event_type', 'cnt')
        )
        total_events = qs.count()
        report_data = {
            'report_type': report_task.report_type,
            'organization_id': str(report_task.organization_id),
            'date_range': {'from': date_from, 'to': date_to},
            'total_events': total_events,
            'by_event_type': by_type,
        }

        # User Activity: DAU, MAU, Churn (inactive > 30 days).
        try:
            from django.utils.dateparse import parse_date as _parse_date
            end_date = timezone.now().date()
            if date_to:
                try:
                    end_date = _parse_date(date_to) or end_date
                except Exception:
                    pass
            thirty_days_ago = end_date - timedelta(days=30)
            org_id = report_task.organization_id
            events_org = AssetEvent.objects_unfiltered.filter(
                organization_id=org_id,
                user_id__isnull=False,
            )
            dau = {}
            if date_from and date_to:
                try:
                    start_d = _parse_date(date_from)
                    end_d = _parse_date(date_to) or end_date
                    if start_d and end_d:
                        d = start_d
                        while d <= end_d:
                            cnt = events_org.filter(timestamp__date=d).values('user_id').distinct().count()
                            dau[d.isoformat()] = cnt
                            d = d + timedelta(days=1)
                except Exception:
                    pass
            mau = events_org.filter(timestamp__date__gte=thirty_days_ago).values('user_id').distinct().count()
            churn_period_days = 30
            active_user_ids = set(
                events_org.filter(timestamp__date__gte=thirty_days_ago)
                .values_list('user_id', flat=True)
                .distinct()
            )
            try:
                UserOrganizationRole = django_apps.get_model('organizations', 'UserOrganizationRole')
                org_member_ids = set(
                    UserOrganizationRole.objects.filter(organization_id=org_id)
                    .values_list('user_id', flat=True)
                    .distinct()
                )
                churn_count = len(org_member_ids - active_user_ids)
            except Exception:
                churn_count = 0
            report_data['user_activity'] = {
                'dau': dau,
                'mau': mau,
                'churn_count': churn_count,
                'churn_period_days': churn_period_days,
            }
        except Exception as ua_exc:
            logger.debug('generate_analytics_report user_activity failed: %s', ua_exc)
            report_data['user_activity'] = {'dau': {}, 'mau': 0, 'churn_count': 0, 'churn_period_days': 30}

        from django.conf import settings
        media_root = getattr(settings, 'MEDIA_ROOT', None) or ''
        reports_dir = os.path.join(media_root, 'reports', str(report_task.organization_id))
        os.makedirs(reports_dir, exist_ok=True)
        filename = f'{report_task_id}.json'
        file_path = os.path.join(reports_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        report_task.status = AnalyticsReportTask.STATUS_COMPLETED
        report_task.file_path = file_path
        report_task.completed_at = timezone.now()
        report_task.save(update_fields=['status', 'file_path', 'completed_at'])
    except Exception as exc:
        logger.exception('generate_analytics_report failed: %s', exc)
        report_task.status = AnalyticsReportTask.STATUS_FAILED
        report_task.completed_at = timezone.now()
        report_task.save(update_fields=['status', 'completed_at'])
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=120, queue='analytics')
def enrich_event_geo_data(self, event_id: Optional[int] = None, batch_size: int = 500, **kwargs) -> int:
    """Enrich AssetEvent metadata with country/city from IP using GeoIP2.

    If event_id is set, process that single event. Otherwise process up to batch_size
    events that have metadata.ip_address but no metadata.country.
    """
    ip_cache = {}

    def resolve_geo(ip):
        if not ip:
            return '', ''
        if ip in ip_cache:
            return ip_cache[ip]
        country, city = get_geo_from_ip(ip)
        ip_cache[ip] = (country, city)
        return country, city

    if event_id is not None:
        try:
            event = AssetEvent.objects_unfiltered.filter(pk=event_id).first()
        except Exception:
            return 0
        if not event:
            return 0
        meta = (event.metadata or {}).copy()
        ip = meta.get('ip_address')
        if not ip or meta.get('country'):
            return 0
        country, city = resolve_geo(ip)
        meta['country'] = country
        meta['city'] = city
        event.metadata = meta
        event.save(update_fields=['metadata'])
        return 1

    processed = 0
    for event in AssetEvent.objects_unfiltered.only('id', 'metadata').iterator(chunk_size=200):
        if processed >= batch_size:
            break
        meta = event.metadata or {}
        ip = meta.get('ip_address')
        if not ip or meta.get('country'):
            continue
        country, city = resolve_geo(ip)
        meta = dict(meta)
        meta['country'] = country
        meta['city'] = city
        event.metadata = meta
        event.save(update_fields=['metadata'])
        processed += 1
    return processed


@shared_task(
    bind=True, max_retries=3, default_retry_delay=60, queue='documents',
    base=TenantAwareTask
)
def aggregate_daily_metrics(self, date_iso: str = '', **kwargs) -> int:
    """Aggregate raw AssetEvent rows into AssetDailyMetrics.

    Sprint 3: Organization-aware via TenantAwareTask base class.

    Args:
        date_iso: Optional ISO date (YYYY-MM-DD). If omitted, aggregates for yesterday.
        **kwargs: May contain organization_id (consumed by TenantAwareTask).

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


@shared_task(
    bind=True, max_retries=3, default_retry_delay=60, queue='documents',
    base=TenantAwareTask
)
def generate_analytics_alerts(self, days: int = 90, **kwargs) -> dict:
    """Generate basic analytics alerts (Phase 2 MVP).

    Sprint 3: Organization-aware via TenantAwareTask base class.

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


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=5,
    queue='analytics',
)
def sync_external_metrics(
    self,
    days: int = 7,
    limit_assets: int = 500,
) -> dict:
    """Sync external channel metrics (Adapter/Strategy; stubs for now).

    Strategy:
    - Determine active channels from recent `DistributionEvent` rows.
    - For each active channel that has an enabled provider, fetch mock metrics.
    - Persist as new `DistributionEvent` rows using `bulk_create`.
    """
    register_default_providers()

    enabled = set(getattr(settings, 'ANALYTICS_EXTERNAL_PROVIDERS_ENABLED', []) or [])
    if not enabled:
        return {'created': 0, 'reason': 'no_enabled_providers'}

    date_from = timezone.now() - timedelta(days=int(days))
    active_channels = list(
        DistributionEvent.objects.filter(occurred_at__gte=date_from)
        .values_list('channel', flat=True).distinct()
    )
    if not active_channels:
        active_channels = list(enabled)

    created_events = []
    provider_errors = 0
    for channel in active_channels:
        provider = AnalyticsProviderRegistry.get_by_channel(channel)
        if not provider:
            provider = AnalyticsProviderRegistry.get_by_provider_id(channel)
        if not provider or provider.provider_id not in enabled:
            continue

        doc_ids = list(
            DistributionEvent.objects.filter(channel=channel, occurred_at__gte=date_from)
            .exclude(document_id__isnull=True)
            .values_list('document_id', flat=True)
            .distinct()[: int(limit_assets)]
        )
        if not doc_ids:
            continue

        for document_id in doc_ids:
            try:
                metrics = provider.fetch_metrics(asset_id=int(document_id))
            except Exception:
                provider_errors += 1
                continue

            created_events.append(
                DistributionEvent(
                    channel=channel,
                    event_type=DistributionEvent.EVENT_TYPE_DELIVERED,
                    status=DistributionEvent.STATUS_OK,
                    sync_status=str(metrics.get('sync_status') or 'ok'),
                    last_sync_error=str(metrics.get('last_sync_error') or ''),
                    retry_count=int(metrics.get('retry_count') or 0),
                    document_id=int(document_id),
                    views=metrics.get('views'),
                    clicks=metrics.get('clicks'),
                    conversions=metrics.get('conversions'),
                    bandwidth_bytes=metrics.get('bandwidth_bytes'),
                    latency_ms=metrics.get('latency_ms'),
                    external_id=str(metrics.get('external_id') or ''),
                    occurred_at=timezone.now(),
                    metadata=metrics.get('metadata') or {'provider': provider.provider_id, 'mock': True},
                )
            )

    if created_events:
        try:
            DistributionEvent.objects.bulk_create(created_events, batch_size=1000)
        except Exception as exc:
            logger.exception('sync_external_metrics bulk_create failed: %s', exc)
            raise

    try:
        notify_analytics_refresh(reason='sync_external_metrics')
    except Exception:
        pass

    logger.info(
        'sync_external_metrics finished: created=%d provider_errors=%d enabled=%s window_days=%d',
        len(created_events), provider_errors, sorted(enabled), int(days)
    )

    if provider_errors and not created_events:
        # Trigger autoretry when all providers fail to fetch.
        raise RuntimeError('sync_external_metrics: all providers failed')

    return {
        'created': len(created_events),
        'window_days': int(days),
        'providers_enabled': sorted(enabled),
    }


@shared_task(bind=True, max_retries=3, default_retry_delay=60, queue='analytics')
def send_campaign_pdf_report_email(
    self,
    *,
    campaign_id: str,
    email_to: str,
    days: int = 30,
) -> dict:
    """Generate and send a campaign PDF report to email (best-effort)."""
    pdf_bytes = CampaignPDFReport(campaign_id=campaign_id, days=int(days)).render()
    msg = EmailMessage(
        subject=f'Отчет по кампании {campaign_id}',
        body=f'PDF отчет по кампании (период: {days} дней).',
        to=[email_to],
    )
    msg.attach(filename=f'campaign-{campaign_id}.pdf', content=pdf_bytes, mimetype='application/pdf')
    sent = msg.send(fail_silently=True)
    return {'sent': bool(sent), 'email_to': email_to, 'campaign_id': campaign_id}


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
def calculate_organization_bandwidth_daily(self, date_iso: str = '') -> int:
    """Aggregate download bandwidth per organization per day and compute CDN cost.

    Uses Plan.cdn_cost_per_gb when set; otherwise ANALYTICS_CDN_COST_PER_GB (default 0.10 USD).
    """
    if date_iso:
        target_date = timezone.datetime.fromisoformat(date_iso).date()
    else:
        target_date = timezone.now().date() - timedelta(days=1)

    default_cost_per_gb = Decimal(
        str(getattr(settings, 'ANALYTICS_CDN_COST_PER_GB', 0.10))
    )

    rows = (
        AssetEvent.objects_unfiltered.filter(
            timestamp__date=target_date,
            event_type=AssetEvent.EVENT_TYPE_DOWNLOAD,
        )
        .exclude(bandwidth_bytes__isnull=True)
        .exclude(bandwidth_bytes=0)
        .values('organization_id')
        .annotate(total_bytes=Sum('bandwidth_bytes'))
    )

    upserts = 0
    for row in rows:
        org_id = row.get('organization_id')
        total_bytes = row.get('total_bytes') or 0
        if not org_id or total_bytes <= 0:
            continue
        bandwidth_gb = round(float(total_bytes) / (1024 ** 3), 6)
        cost_per_gb = default_cost_per_gb
        try:
            org = Organization.objects.filter(pk=org_id).select_related('subscription__plan').first()
            if org and getattr(org, 'subscription', None) and getattr(org.subscription, 'plan', None):
                plan = org.subscription.plan
                if getattr(plan, 'cdn_cost_per_gb', None) is not None:
                    cost_per_gb = Decimal(str(plan.cdn_cost_per_gb))
        except Exception:
            pass
        cost_usd = (Decimal(str(bandwidth_gb)) * cost_per_gb).quantize(Decimal('0.01'))
        OrganizationBandwidthDaily.objects.update_or_create(
            organization_id=org_id,
            date=target_date,
            defaults={'bandwidth_gb': bandwidth_gb, 'cost_usd': cost_usd}
        )
        upserts += 1

    try:
        notify_analytics_refresh(reason='calculate_organization_bandwidth_daily')
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
