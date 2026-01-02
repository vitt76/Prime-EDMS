"""Analytics extra API views (non-headless).

This module contains webhook endpoints for external analytics providers.
They are designed to be lightweight and never block on DB writes:
webhooks publish to Redis Streams; the consumer persists events in PostgreSQL.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Iterable, List, Optional

from django.conf import settings
from django.http import StreamingHttpResponse
from django.utils import timezone
from django.db import connection

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ratelimit.decorators import ratelimit

from .event_stream import publish_asset_event
from .models import AssetEvent

logger = logging.getLogger(__name__)


class EmailClickWebhookView(APIView):
    """POST /api/v4/analytics/webhooks/email/click/

    Supports:
      - SendGrid Event Webhook (expects list of events)
      - Generic provider payloads containing document_id/asset_id

    Security:
      - Optional shared secret header: X-Analytics-Webhook-Secret
    """

    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        secret = (getattr(settings, 'ANALYTICS_EMAIL_WEBHOOK_SECRET', '') or '').strip()
        if secret:
            provided = (request.headers.get('X-Analytics-Webhook-Secret') or '').strip()
            if provided != secret:
                return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        payload = request.data
        events: List[Dict[str, Any]] = []
        if isinstance(payload, list):
            events = payload
        elif isinstance(payload, dict):
            # Accept a single event or wrapper with "events"
            if isinstance(payload.get('events'), list):
                events = payload.get('events') or []
            else:
                events = [payload]
        else:
            return Response({'detail': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)

        published = 0
        errors = 0
        for ev in events:
            try:
                doc_id = ev.get('document_id') or ev.get('asset_id') or ev.get('documentId')
                if not doc_id:
                    # SendGrid click event often has URL; support query param document_id=...
                    url = (ev.get('url') or ev.get('link') or '').strip()
                    if url and 'document_id=' in url:
                        try:
                            doc_id = int(url.split('document_id=')[1].split('&')[0])
                        except Exception:
                            doc_id = None
                doc_id = int(doc_id)
            except Exception:
                errors += 1
                continue

            provider = (getattr(settings, 'ANALYTICS_EMAIL_PROVIDER', '') or '').strip().lower() or 'unknown'
            publish_asset_event(
                document_id=doc_id,
                event_type=AssetEvent.EVENT_TYPE_EMAIL_CLICK,
                user_id=None,
                user_department='',
                channel='email',
                intended_use='',
                latency_seconds=None,
                bandwidth_bytes=None,
                metadata={
                    'provider': provider,
                    'event': ev.get('event') or ev.get('type') or 'click',
                    'email': ev.get('email') or ev.get('recipient') or '',
                    'url': ev.get('url') or ev.get('link') or '',
                    'campaign_id': ev.get('campaign_id') or ev.get('campaign') or '',
                    'timestamp': ev.get('timestamp') or timezone.now().isoformat(),
                }
            )
            published += 1

        logger.info('email_click_webhook processed: published=%d errors=%d', published, errors)
        return Response({'published': published, 'errors': errors}, status=status.HTTP_200_OK)


class AnalyticsEventsExportView(APIView):
    """GET /api/v4/analytics/export/events/

    Produces JSON Lines for BI systems (cursor-based pagination).

    Query params:
      - start_date (YYYY-MM-DD)
      - end_date (YYYY-MM-DD)
      - event_type (optional)
      - user_id (optional)
      - cursor (last seen id, optional)
      - limit (max 5000)
    """

    permission_classes = (AllowAny,)

    @ratelimit(key='ip', rate='1/m', block=True)
    def get(self, request, *args, **kwargs):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        event_type = (request.query_params.get('event_type') or '').strip()
        user_id = request.query_params.get('user_id')
        cursor = request.query_params.get('cursor')
        limit = min(int(request.query_params.get('limit') or 1000), 5000)

        qs = AssetEvent.objects.all().order_by('id')
        if cursor:
            try:
                qs = qs.filter(id__gt=int(cursor))
            except Exception:
                return Response({'detail': 'Invalid cursor'}, status=status.HTTP_400_BAD_REQUEST)

        if start_date:
            qs = qs.filter(timestamp__date__gte=start_date)
        if end_date:
            qs = qs.filter(timestamp__date__lte=end_date)
        if event_type:
            qs = qs.filter(event_type=event_type)
        if user_id:
            qs = qs.filter(user_id=user_id)

        rows = list(
            qs.values(
                'id', 'document_id', 'event_type', 'user_id', 'user_department', 'channel',
                'intended_use', 'bandwidth_bytes', 'latency_seconds', 'timestamp', 'metadata'
            )[:limit]
        )

        def gen():
            for row in rows:
                row['timestamp'] = row['timestamp'].isoformat() if row.get('timestamp') else None
                yield json.dumps(row, ensure_ascii=False) + '\n'

        response = StreamingHttpResponse(gen(), content_type='application/x-ndjson')
        if rows:
            response['X-Next-Cursor'] = str(rows[-1]['id'])
        response['Cache-Control'] = 'no-store'
        return response


class AnalyticsHealthCheckView(APIView):
    """GET /api/v4/analytics/health/

    Lightweight health check for monitoring (Prometheus/Grafana probes).
    """

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        overall_ok = True

        # Redis stream connectivity / lag (best-effort).
        redis_status = {'status': 'unknown', 'stream_length': None}
        try:
            from django_redis import get_redis_connection
            conn = get_redis_connection('default')
            stream_key = getattr(settings, 'ANALYTICS_EVENT_STREAM_KEY', 'dam:analytics:events')
            redis_status['stream_length'] = int(conn.xlen(stream_key))
            redis_status['status'] = 'connected'
        except Exception as exc:
            overall_ok = False
            redis_status['status'] = 'error'
            redis_status['error'] = str(exc)

        # Database connectivity / latency.
        db_status = {'status': 'unknown', 'latency_ms': None}
        try:
            import time
            t0 = time.perf_counter()
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
            db_status['latency_ms'] = int((time.perf_counter() - t0) * 1000)
            db_status['status'] = 'connected'
        except Exception as exc:
            overall_ok = False
            db_status['status'] = 'error'
            db_status['error'] = str(exc)

        # Last aggregation timestamp (best-effort).
        last_aggregation = None
        try:
            from .models import AssetDailyMetrics
            row = AssetDailyMetrics.objects.order_by('-date').values_list('date', flat=True).first()
            if row:
                last_aggregation = timezone.make_aware(timezone.datetime.combine(row, timezone.datetime.min.time())).isoformat()
        except Exception:
            last_aggregation = None

        data = {
            'status': 'healthy' if overall_ok else 'degraded',
            'redis_streams': redis_status,
            'database': db_status,
            'last_aggregation': last_aggregation,
        }
        return Response(data, status=status.HTTP_200_OK if overall_ok else status.HTTP_503_SERVICE_UNAVAILABLE)


