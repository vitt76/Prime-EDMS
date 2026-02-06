"""Consume analytics events from Redis Streams and persist them to PostgreSQL.

This command implements the "Event Stream" ingestion layer for analytics:
  - producers XADD into a single stream (default: dam:analytics:events)
  - this consumer reads batches (XREADGROUP) and persists with bulk_create

Design goals:
  - high throughput (batching)
  - low latency (blocking reads)
  - best-effort (never crash core system on analytics data issues)
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from django_redis import get_redis_connection

from mayan.apps.analytics.cache import invalidate_asset_analytics_cache
from mayan.apps.analytics.models import AssetEvent, PortalSession, UserSession
from mayan.apps.analytics.realtime import notify_analytics_refresh
from mayan.apps.analytics.metrics import analytics_events_processed_total, analytics_redis_stream_lag

logger = logging.getLogger(name=__name__)


def _to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        if isinstance(value, (bytes, bytearray)):
            value = value.decode('utf-8', errors='ignore')
        value = str(value).strip()
        if not value:
            return default
        return int(float(value))
    except Exception:
        return default


def _to_str(value: Any) -> str:
    if value is None:
        return ''
    if isinstance(value, (bytes, bytearray)):
        return value.decode('utf-8', errors='ignore')
    return str(value)


def _to_json(value: Any) -> dict:
    if not value:
        return {}
    try:
        if isinstance(value, (bytes, bytearray)):
            value = value.decode('utf-8', errors='ignore')
        if isinstance(value, dict):
            return value
        return json.loads(str(value))
    except Exception:
        return {}


def _to_dt(value: Any) -> Optional[datetime]:
    text = _to_str(value).strip()
    if not text:
        return None
    try:
        # Support ISO with 'Z'
        return timezone.datetime.fromisoformat(text.replace('Z', '+00:00'))
    except Exception:
        return None


class Command(BaseCommand):
    help = 'Consume analytics events from Redis Streams and persist them to PostgreSQL.'

    def add_arguments(self, parser):
        parser.add_argument('--stream', default=getattr(settings, 'ANALYTICS_EVENT_STREAM_KEY', 'dam:analytics:events'))
        parser.add_argument('--group', default=getattr(settings, 'ANALYTICS_EVENT_STREAM_GROUP', 'analytics'))
        parser.add_argument('--consumer', default=getattr(settings, 'ANALYTICS_EVENT_STREAM_CONSUMER', 'consumer-1'))
        parser.add_argument('--count', type=int, default=500)
        parser.add_argument('--block-ms', type=int, default=5000)
        parser.add_argument('--once', action='store_true', help='Process one batch and exit.')

    def handle(self, *args, **options):
        stream = str(options['stream'])
        group = str(options['group'])
        consumer = str(options['consumer'])
        count = int(options['count'])
        block_ms = int(options['block_ms'])
        once = bool(options['once'])

        client = get_redis_connection('default')

        # Ensure group exists.
        try:
            client.xgroup_create(name=stream, groupname=group, id='0', mkstream=True)
        except Exception:
            # Likely BUSYGROUP; ignore.
            pass

        self.stdout.write(self.style.SUCCESS(f'Consuming analytics stream="{stream}" group="{group}" consumer="{consumer}"'))

        while True:
            try:
                messages = client.xreadgroup(
                    groupname=group,
                    consumername=consumer,
                    streams={stream: '>'},
                    count=count,
                    block=block_ms,
                )
            except Exception as exc:
                logger.error('Redis xreadgroup failed: %s', exc)
                if once:
                    return
                continue

            if not messages:
                if once:
                    return
                continue

            # messages: [(stream_name, [(id, {field: value})...])]
            entries: List[Tuple[str, Dict[str, Any]]] = []
            for _stream_name, batch in messages:
                for entry_id, fields in batch:
                    entries.append((_to_str(entry_id), fields or {}))

            asset_events: List[AssetEvent] = []
            user_logins: List[UserSession] = []
            user_logouts: List[Dict[str, Any]] = []
            download_document_ids: List[int] = []
            portal_updates: List[Dict[str, Any]] = []

            # Parse.
            for entry_id, fields in entries:
                kind = _to_str(fields.get(b'kind') or fields.get('kind')).strip()
                if kind == 'asset_event':
                    document_id = _to_int(fields.get(b'document_id') or fields.get('document_id'))
                    event_type = _to_str(fields.get(b'event_type') or fields.get('event_type')).strip()
                    if not document_id or not event_type:
                        continue

                    user_id = _to_int(fields.get(b'user_id') or fields.get('user_id')) or None
                    user_department = _to_str(fields.get(b'user_department') or fields.get('user_department'))
                    channel = _to_str(fields.get(b'channel') or fields.get('channel'))
                    intended_use = _to_str(fields.get(b'intended_use') or fields.get('intended_use'))
                    bandwidth_bytes = _to_int(fields.get(b'bandwidth_bytes') or fields.get('bandwidth_bytes')) or None
                    latency_seconds = _to_int(fields.get(b'latency_seconds') or fields.get('latency_seconds')) or None
                    metadata = _to_json(fields.get(b'metadata') or fields.get('metadata'))

                    asset_events.append(
                        AssetEvent(
                            document_id=document_id,
                            event_type=event_type,
                            user_id=user_id,
                            user_department=user_department or '',
                            channel=channel or '',
                            intended_use=intended_use or '',
                            bandwidth_bytes=bandwidth_bytes,
                            latency_seconds=latency_seconds,
                            metadata=metadata or {},
                        )
                    )

                    if event_type == AssetEvent.EVENT_TYPE_DOWNLOAD:
                        download_document_ids.append(document_id)
                elif kind == 'user_session':
                    action = _to_str(fields.get(b'action') or fields.get('action')).strip()
                    user_id = _to_int(fields.get(b'user_id') or fields.get('user_id'))
                    if not user_id or not action:
                        continue

                    session_key = _to_str(fields.get(b'session_key') or fields.get('session_key'))
                    ts = _to_dt(fields.get(b'timestamp') or fields.get('timestamp')) or timezone.now()

                    if action == 'login':
                        user_logins.append(
                            UserSession(
                                user_id=user_id,
                                session_key=session_key or '',
                                login_timestamp=ts,
                                geo_country=_to_str(fields.get(b'geo_country') or fields.get('geo_country')),
                                geo_city=_to_str(fields.get(b'geo_city') or fields.get('geo_city')),
                                ip_address=_to_str(fields.get(b'ip_address') or fields.get('ip_address')),
                                user_agent=_to_str(fields.get(b'user_agent') or fields.get('user_agent')),
                            )
                        )
                    elif action == 'logout':
                        user_logouts.append({'user_id': user_id, 'session_key': session_key or '', 'timestamp': ts})
                elif kind == 'portal_event':
                    event_type = _to_str(fields.get(b'event_type') or fields.get('event_type')).strip()
                    occurred_at = _to_dt(fields.get(b'occurred_at') or fields.get('occurred_at')) or timezone.now()
                    document_id = _to_int(fields.get(b'document_id') or fields.get('document_id')) or None
                    share_link_id = _to_int(fields.get(b'share_link_id') or fields.get('share_link_id')) or None
                    publication_id = _to_int(fields.get(b'publication_id') or fields.get('publication_id')) or None
                    campaign_id = _to_str(fields.get(b'campaign_id') or fields.get('campaign_id')).strip()
                    user_id = _to_int(fields.get(b'user_id') or fields.get('user_id')) or None
                    session_key = _to_str(fields.get(b'session_key') or fields.get('session_key'))
                    ip_address = _to_str(fields.get(b'ip_address') or fields.get('ip_address'))
                    user_agent = _to_str(fields.get(b'user_agent') or fields.get('user_agent'))
                    bandwidth_bytes = _to_int(fields.get(b'bandwidth_bytes') or fields.get('bandwidth_bytes')) or None
                    metadata = _to_json(fields.get(b'metadata') or fields.get('metadata'))

                    # Persist AssetEvent with channel='portal' to unify analytics.
                    if document_id and event_type in ('view', 'download'):
                        mapped = AssetEvent.EVENT_TYPE_VIEW if event_type == 'view' else AssetEvent.EVENT_TYPE_DOWNLOAD
                        asset_events.append(
                            AssetEvent(
                                document_id=document_id,
                                event_type=mapped,
                                user_id=user_id,
                                user_department='',
                                channel='portal',
                                intended_use='',
                                bandwidth_bytes=None,
                                latency_seconds=None,
                                metadata={
                                    'share_link_id': share_link_id,
                                    'publication_id': publication_id,
                                    **(metadata or {}),
                                },
                            )
                        )
                        if mapped == AssetEvent.EVENT_TYPE_DOWNLOAD:
                            download_document_ids.append(int(document_id))

                        # Best-effort: if we have bandwidth, also record a delivery event.
                        if bandwidth_bytes:
                            asset_events.append(
                                AssetEvent(
                                    document_id=document_id,
                                    event_type=AssetEvent.EVENT_TYPE_DELIVER,
                                    user_id=user_id,
                                    user_department='',
                                    channel='portal',
                                    intended_use='',
                                    bandwidth_bytes=bandwidth_bytes,
                                    latency_seconds=None,
                                    metadata={
                                        'share_link_id': share_link_id,
                                        'publication_id': publication_id,
                                        **(metadata or {}),
                                    },
                                )
                            )

                    portal_updates.append(
                        {
                            'occurred_at': occurred_at,
                            'document_id': document_id,
                            'share_link_id': share_link_id,
                            'publication_id': publication_id,
                            'campaign_id': campaign_id or None,
                            'user_id': user_id,
                            'session_key': session_key or '',
                            'ip_address': ip_address or '',
                            'user_agent': user_agent or '',
                            'is_view': event_type == 'view',
                            'is_download': event_type == 'download',
                            'metadata': metadata or {},
                        }
                    )

            # Persist.
            try:
                with transaction.atomic():
                    if asset_events:
                        AssetEvent.objects.bulk_create(asset_events, batch_size=1000)
                    if user_logins:
                        UserSession.objects.bulk_create(user_logins, batch_size=1000)

                    # Apply logouts (best-effort updates).
                    for logout in user_logouts:
                        qs = UserSession.objects.filter(
                            user_id=logout['user_id'],
                            logout_timestamp__isnull=True
                        ).order_by('-login_timestamp')
                        if logout.get('session_key'):
                            qs = qs.filter(session_key=logout['session_key'])
                        session = qs.first()
                        if not session:
                            continue
                        now = logout['timestamp']
                        session.logout_timestamp = now
                        session.session_duration_seconds = int((now - session.login_timestamp).total_seconds())
                        session.save(update_fields=('logout_timestamp', 'session_duration_seconds'))

                    # Portal sessions: best-effort session-level aggregation.
                    for ev in portal_updates:
                        occurred_at = ev['occurred_at']
                        share_link_id = ev.get('share_link_id')
                        publication_id = ev.get('publication_id')
                        # Prefer session_key, fallback to ip_address, else "anon".
                        identity = (ev.get('session_key') or ev.get('ip_address') or 'anon').strip()

                        qs = PortalSession.objects.all()
                        if share_link_id:
                            qs = qs.filter(share_link_id=share_link_id)
                        if publication_id:
                            qs = qs.filter(publication_id=publication_id)

                        # Same-day grouping.
                        qs = qs.filter(started_at__date=occurred_at.date())
                        qs = qs.filter(session_key=identity) if ev.get('session_key') else qs.filter(ip_address=identity)

                        session = qs.order_by('-last_seen_at').first()
                        if not session:
                            session = PortalSession.objects.create(
                                share_link_id=share_link_id,
                                publication_id=publication_id,
                                campaign_id=ev.get('campaign_id'),
                                document_id=ev.get('document_id'),
                                user_id=ev.get('user_id'),
                                session_key=identity if ev.get('session_key') else '',
                                ip_address=identity if not ev.get('session_key') else '',
                                user_agent=ev.get('user_agent') or '',
                                started_at=occurred_at,
                                last_seen_at=occurred_at,
                                views=1 if ev.get('is_view') else 0,
                                downloads=1 if ev.get('is_download') else 0,
                                metadata=ev.get('metadata') or {},
                            )
                        else:
                            session.last_seen_at = occurred_at
                            if ev.get('is_view'):
                                session.views = int(session.views or 0) + 1
                            if ev.get('is_download'):
                                session.downloads = int(session.downloads or 0) + 1
                            # Keep latest user_agent if missing.
                            if not session.user_agent and ev.get('user_agent'):
                                session.user_agent = ev.get('user_agent')
                            session.save(update_fields=('last_seen_at', 'views', 'downloads', 'user_agent'))
            except Exception as exc:
                logger.error('Failed to persist analytics events batch: %s', exc)
                if once:
                    return
                continue

            # Post-processing: link SearchSession for downloads (best-effort).
            try:
                from django.contrib.auth import get_user_model
                from mayan.apps.analytics.services import link_download_to_latest_search_session

                User = get_user_model()
                download_events = [e for e in asset_events if e.event_type == AssetEvent.EVENT_TYPE_DOWNLOAD and e.user_id]
                if download_events:
                    user_ids = sorted({int(e.user_id) for e in download_events if e.user_id})
                    user_map = {u.pk: u for u in User.objects.filter(pk__in=user_ids)}
                    for ev in download_events:
                        user = user_map.get(ev.user_id)
                        if not user:
                            continue
                        try:
                            link_download_to_latest_search_session(user=user, download_event=ev, max_window_minutes=30)
                        except Exception:
                            continue
            except Exception:
                pass

            # Cache invalidation for affected assets.
            try:
                if download_document_ids:
                    for doc_id in sorted(set(download_document_ids)):
                        invalidate_asset_analytics_cache(document_id=doc_id)
            except Exception:
                pass

            # Real-time dashboard refresh (best-effort, aggregated per batch).
            try:
                notify_analytics_refresh(
                    reason='events_ingested',
                    dashboard='asset_bank',
                    payload={
                        'asset_events': len(asset_events),
                        'user_logins': len(user_logins),
                        'portal_events': len(portal_updates),
                        'download_assets': len(set(download_document_ids)),
                    }
                )
            except Exception:
                pass

            # Prometheus metrics (best-effort).
            try:
                analytics_events_processed_total.labels(kind='asset_event').inc(len(asset_events))
                analytics_events_processed_total.labels(kind='user_session').inc(len(user_logins))
                analytics_events_processed_total.labels(kind='portal_event').inc(len(portal_updates))
            except Exception:
                pass

            # Ack all processed entries.
            try:
                client.xack(stream, group, *[entry_id for entry_id, _fields in entries])
            except Exception:
                pass

            if once:
                return


