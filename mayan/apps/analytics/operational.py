from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, Optional

from django.core.cache import cache
from django.utils import timezone


_CACHE_PREFIX = 'analytics:operational'
_DEFAULT_TTL = 60 * 60 * 24


def _cache_key(name: str) -> str:
    return f'{_CACHE_PREFIX}:{name}'


def _now_iso() -> str:
    return timezone.now().isoformat()


def record_marker(name: str, *, status: str = 'ok', payload: Optional[Dict[str, Any]] = None, ttl: int = _DEFAULT_TTL) -> None:
    """Persist a best-effort operational marker in cache."""
    cache.set(
        _cache_key(name),
        {
            'status': status,
            'timestamp': _now_iso(),
            'payload': payload or {},
        },
        timeout=ttl,
    )


def record_task_result(task_name: str, *, status: str = 'ok', payload: Optional[Dict[str, Any]] = None, ttl: int = _DEFAULT_TTL) -> None:
    """Persist both generic and task-specific execution markers."""
    marker_payload = payload or {}
    marker_name = 'task_success' if status == 'ok' else 'task_failure'
    specific_name = f'task:{task_name}:{"success" if status == "ok" else "failure"}'

    record_marker(
        marker_name,
        status=status,
        payload={
            'task': task_name,
            **marker_payload,
        },
        ttl=ttl,
    )
    record_marker(
        specific_name,
        status=status,
        payload=marker_payload,
        ttl=ttl,
    )


def increment_counter(name: str, *, delta: int = 1, ttl: int = _DEFAULT_TTL) -> None:
    """Increment a best-effort operational counter in cache."""
    key = _cache_key(name)
    try:
        cache.incr(key, delta)
    except ValueError:
        cache.set(key, delta, timeout=ttl)
    else:
        cache.touch(key, timeout=ttl)


def _get_stream_length() -> Optional[int]:
    try:
        from .event_stream import _get_redis_client, _get_stream_key, _is_enabled

        if not _is_enabled():
            return 0

        client = _get_redis_client()
        if not client:
            return None

        return int(client.xlen(_get_stream_key()))
    except Exception:
        return None


def _get_broker_snapshot() -> Dict[str, Any]:
    try:
        from celery import current_app as celery_app

        broker_url = getattr(celery_app.conf, 'broker_url', '') or ''
        transport = str(broker_url).split(':', 1)[0] if broker_url else ''
        snapshot = {
            'transport': transport,
            'reachable': None,
            'worker_count': None,
            'workers': [],
        }

        try:
            with celery_app.connection_for_read() as connection:
                connection.ensure_connection(max_retries=1)
            snapshot['reachable'] = True
        except Exception as exc:
            snapshot['reachable'] = False
            snapshot['error'] = str(exc)

        try:
            inspect = celery_app.control.inspect(timeout=1)
            ping = (inspect.ping() or {}) if inspect else {}
            snapshot['worker_count'] = len(ping)
            snapshot['workers'] = sorted(ping.keys())
        except Exception as exc:
            snapshot['inspect_error'] = str(exc)
            if snapshot['worker_count'] is None:
                snapshot['worker_count'] = 0 if snapshot['reachable'] else None

        return snapshot
    except Exception as exc:
        return {
            'transport': '',
            'reachable': None,
            'worker_count': None,
            'workers': [],
            'error': str(exc),
        }


def _get_indexing_snapshot() -> Dict[str, Any]:
    try:
        from mayan.apps.documents.metrics import get_metrics as get_indexing_metrics

        metrics = get_indexing_metrics().get_metrics()
        return {
            'total_operations': metrics.get('total_operations', 0),
            'index_success': metrics.get('index_success', 0),
            'index_failure': metrics.get('index_failure', 0),
            'retry_count': metrics.get('retry_count', 0),
            'cleanup_execution': cache.get('indexing_metrics_cleanup_execution', 0) or 0,
        }
    except Exception as exc:
        return {
            'error': str(exc),
        }


def get_operational_snapshot() -> Dict[str, Any]:
    """Build a lightweight analytics health snapshot for ops/smoke checks."""
    from .models import AnalyticsReportTask

    now = timezone.now()
    latest_report = AnalyticsReportTask.objects_unfiltered.filter(
        status=AnalyticsReportTask.STATUS_COMPLETED
    ).order_by('-completed_at').only('completed_at').first()

    failed_since = now - timedelta(hours=24)
    stale_pending_before = now - timedelta(minutes=30)

    latest_report_completed_at = getattr(latest_report, 'completed_at', None)
    latest_report_age_seconds = None
    if latest_report_completed_at:
        latest_report_age_seconds = max(
            0,
            int((now - latest_report_completed_at).total_seconds())
        )

    return {
        'stream': {
            'length': _get_stream_length(),
            'consumer': cache.get(_cache_key('consumer')),
            'public_ingest': cache.get(_cache_key('public_ingest')),
        },
        'tasks': {
            'last_success': cache.get(_cache_key('task_success')),
            'last_failure': cache.get(_cache_key('task_failure')),
            'track_asset_event_async': {
                'last_success': cache.get(_cache_key('task:track_asset_event_async:success')),
                'last_failure': cache.get(_cache_key('task:track_asset_event_async:failure')),
            },
            'generate_analytics_report': {
                'last_success': cache.get(_cache_key('task:generate_analytics_report:success')),
                'last_failure': cache.get(_cache_key('task:generate_analytics_report:failure')),
            },
        },
        'reports': {
            'pending': AnalyticsReportTask.objects_unfiltered.filter(
                status=AnalyticsReportTask.STATUS_PENDING
            ).count(),
            'processing': AnalyticsReportTask.objects_unfiltered.filter(
                status=AnalyticsReportTask.STATUS_PROCESSING
            ).count(),
            'failed_24h': AnalyticsReportTask.objects_unfiltered.filter(
                status=AnalyticsReportTask.STATUS_FAILED,
                completed_at__gte=failed_since,
            ).count(),
            'stale_pending': AnalyticsReportTask.objects_unfiltered.filter(
                status__in=(
                    AnalyticsReportTask.STATUS_PENDING,
                    AnalyticsReportTask.STATUS_PROCESSING,
                ),
                created_at__lt=stale_pending_before,
            ).count(),
            'latest_completed_at': (
                latest_report_completed_at.isoformat()
                if latest_report_completed_at else None
            ),
            'latest_completed_age_seconds': latest_report_age_seconds,
        },
        'broker': _get_broker_snapshot(),
        'indexing': _get_indexing_snapshot(),
        'counters': {
            'window_seconds': _DEFAULT_TTL,
            'public_events_recent': cache.get(_cache_key('public_events_total')) or 0,
            'consumer_batches_recent': cache.get(_cache_key('consumer_batches_total')) or 0,
        },
    }
