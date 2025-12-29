from datetime import timedelta

from celery import shared_task
from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone

from .models import (
    AssetDailyMetrics, AssetEvent, SearchDailyMetrics, SearchQuery
)


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

    upserts = 0
    for row in rows:
        bandwidth_bytes = row.get('bandwidth_bytes') or 0
        AssetDailyMetrics.objects.update_or_create(
            document_id=row['document_id'],
            date=target_date,
            defaults={
                'downloads': row.get('downloads') or 0,
                'views': row.get('views') or 0,
                'shares': row.get('shares') or 0,
                'cdn_bandwidth_gb': round(bandwidth_bytes / (1024 ** 3), 6) if bandwidth_bytes else 0.0,
            }
        )
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

