"""YouTube analytics provider (real API, best-effort).

Notes:
  - YouTube *Analytics* API generally requires OAuth2. For production, you'll
    want to implement OAuth flows / service account and store credentials.
  - This implementation uses the YouTube Data API (v3) with an API key to fetch
    basic per-video metrics (views/likes/comments). Watch time and geography are
    returned as None/empty unless you later add Analytics API support.
"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, Dict, Optional

from django.conf import settings
from django.utils import timezone

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleAuthRequest

from mayan.apps.documents.models import Document

from .base import BaseAnalyticsProvider

logger = logging.getLogger(__name__)


class YouTubeAnalyticsProvider(BaseAnalyticsProvider):
    provider_id = 'youtube'
    display_name = 'YouTube'
    channel = 'youtube'

    def get_authenticated_service(self):
        """Return an authenticated YouTube Analytics API service (OAuth2).

        Requires:
          - ANALYTICS_YOUTUBE_CLIENT_ID
          - ANALYTICS_YOUTUBE_CLIENT_SECRET
          - ANALYTICS_YOUTUBE_REFRESH_TOKEN
        """
        client_id = getattr(settings, 'ANALYTICS_YOUTUBE_CLIENT_ID', '') or ''
        client_secret = getattr(settings, 'ANALYTICS_YOUTUBE_CLIENT_SECRET', '') or ''
        refresh_token = getattr(settings, 'ANALYTICS_YOUTUBE_REFRESH_TOKEN', '') or ''

        if not (client_id and client_secret and refresh_token):
            return None

        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=client_id,
            client_secret=client_secret,
            scopes=['https://www.googleapis.com/auth/yt-analytics.readonly'],
        )

        try:
            creds.refresh(GoogleAuthRequest())
        except Exception as exc:
            logger.warning('YouTube OAuth refresh failed: %s', exc)
            return None

        try:
            return build('youtubeAnalytics', 'v2', credentials=creds, cache_discovery=False)
        except Exception as exc:
            logger.warning('YouTube Analytics service build failed: %s', exc)
            return None

    def _get_video_id(self, *, document: Document) -> str:
        video_id = ''
        try:
            extra = getattr(document, 'extra_data', None) or {}
            video_id = (extra.get('youtube_video_id') or extra.get('youtube_id') or '').strip()
        except Exception:
            video_id = ''
        return video_id

    def _fetch_metrics_data_api_v3(self, *, api_key: str, video_id: str) -> Dict[str, Any]:
        """Fallback method using YouTube Data API v3 (no watch_time/geography)."""
        youtube = build('youtube', 'v3', developerKey=api_key, cache_discovery=False)
        resp = youtube.videos().list(part='statistics,contentDetails', id=video_id).execute()

        items = (resp or {}).get('items') or []
        if not items:
            return {
                'views': 0,
                'clicks': 0,
                'conversions': 0,
                'bandwidth_bytes': None,
                'latency_ms': None,
                'external_id': video_id,
                'sync_status': 'error',
                'last_sync_error': 'Video not found in YouTube API response',
                'retry_count': 0,
                'metadata': {'provider': self.provider_id},
            }

        stats = items[0].get('statistics') or {}
        views = int(stats.get('viewCount') or 0)
        likes = int(stats.get('likeCount') or 0)
        comments = int(stats.get('commentCount') or 0)

        return {
            'views': views,
            'clicks': 0,
            'conversions': 0,
            'bandwidth_bytes': None,
            'latency_ms': None,
            'external_id': video_id,
            'sync_status': 'ok',
            'last_sync_error': '',
            'retry_count': 0,
            'metadata': {
                'provider': self.provider_id,
                'likes': likes,
                'comments': comments,
                'watch_time_minutes': None,
                'geography': {},
                'fetched_at': timezone.now().isoformat(),
                'fallback': 'data_api_v3',
            },
        }

    def _fetch_metrics_analytics_api(
        self,
        *,
        service,
        video_id: str,
        days: int = 7,
    ) -> Dict[str, Any]:
        end_date = (timezone.now().date() - timedelta(days=1))
        start_date = (end_date - timedelta(days=max(1, int(days))))

        ids = 'channel==MINE'
        channel_id = (getattr(settings, 'ANALYTICS_YOUTUBE_CHANNEL_ID', '') or '').strip()
        if channel_id:
            ids = f'channel=={channel_id}'

        base = service.reports().query(
            ids=ids,
            startDate=start_date.isoformat(),
            endDate=end_date.isoformat(),
            metrics='views,estimatedMinutesWatched',
            filters=f'video=={video_id}',
        ).execute()

        views = 0
        watch_minutes = 0
        try:
            rows = (base or {}).get('rows') or []
            if rows and len(rows[0]) >= 2:
                views = int(rows[0][0] or 0)
                watch_minutes = int(rows[0][1] or 0)
        except Exception:
            views = 0
            watch_minutes = 0

        geo = service.reports().query(
            ids=ids,
            startDate=start_date.isoformat(),
            endDate=end_date.isoformat(),
            metrics='views,estimatedMinutesWatched',
            dimensions='country',
            sort='-views',
            maxResults=5,
            filters=f'video=={video_id}',
        ).execute()

        geography = {}
        try:
            for row in (geo or {}).get('rows') or []:
                # row format: [country, views, estimatedMinutesWatched]
                country = str(row[0])
                geography[country] = {
                    'views': int(row[1] or 0) if len(row) > 1 else 0,
                    'estimated_minutes_watched': int(row[2] or 0) if len(row) > 2 else 0,
                }
        except Exception:
            geography = {}

        return {
            'views': views,
            'clicks': 0,
            'conversions': 0,
            'bandwidth_bytes': None,
            'latency_ms': None,
            'external_id': video_id,
            'sync_status': 'ok',
            'last_sync_error': '',
            'retry_count': 0,
            'metadata': {
                'provider': self.provider_id,
                'watch_time_minutes': watch_minutes,
                'geography': geography,
                'fetched_at': timezone.now().isoformat(),
                'source': 'youtube_analytics_api_v2',
                'window_days': int(days),
            },
        }

    def fetch_metrics(self, *, asset_id: int) -> Dict[str, Any]:
        document = Document.valid.filter(pk=int(asset_id)).only('pk', 'label').first()
        if not document:
            return {
                'views': 0,
                'clicks': 0,
                'conversions': 0,
                'bandwidth_bytes': None,
                'latency_ms': None,
                'external_id': '',
                'sync_status': 'error',
                'last_sync_error': 'Document not found',
                'retry_count': 0,
                'metadata': {'provider': self.provider_id},
            }

        video_id = self._get_video_id(document=document)
        if not video_id:
            return {
                'views': 0,
                'clicks': 0,
                'conversions': 0,
                'bandwidth_bytes': None,
                'latency_ms': None,
                'external_id': '',
                'sync_status': 'error',
                'last_sync_error': 'Missing youtube_video_id in document extra_data',
                'retry_count': 0,
                'metadata': {'provider': self.provider_id},
            }

        # Preferred: YouTube Analytics API v2 via OAuth2.
        service = self.get_authenticated_service()
        if service:
            try:
                return self._fetch_metrics_analytics_api(service=service, video_id=video_id, days=7)
            except Exception as exc:
                logger.warning('YouTube Analytics API failed, falling back to Data API v3: %s', exc)

        # Fallback: YouTube Data API v3 via API key (limited metrics).
        api_key = getattr(settings, 'ANALYTICS_YOUTUBE_API_KEY', '') or ''
        if not api_key:
            return {
                'views': 0,
                'clicks': 0,
                'conversions': 0,
                'bandwidth_bytes': None,
                'latency_ms': None,
                'external_id': video_id,
                'sync_status': 'error',
                'last_sync_error': 'OAuth2 not configured and ANALYTICS_YOUTUBE_API_KEY is not configured',
                'retry_count': 0,
                'metadata': {'provider': self.provider_id},
            }

        try:
            return self._fetch_metrics_data_api_v3(api_key=api_key, video_id=video_id)
        except Exception as exc:
            logger.exception('YouTube API call failed: %s', exc)
            return {
                'views': 0,
                'clicks': 0,
                'conversions': 0,
                'bandwidth_bytes': None,
                'latency_ms': None,
                'external_id': video_id,
                'sync_status': 'error',
                'last_sync_error': str(exc),
                'retry_count': 0,
                'metadata': {'provider': self.provider_id},
            }

    def push_event(self, *, event: Dict[str, Any]) -> Optional[str]:
        # Stub: no-op.
        return None

# End of file