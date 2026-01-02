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
from typing import Any, Dict, Optional

from django.conf import settings
from django.utils import timezone

from googleapiclient.discovery import build

from mayan.apps.documents.models import Document

from .base import BaseAnalyticsProvider

logger = logging.getLogger(__name__)


class YouTubeAnalyticsProvider(BaseAnalyticsProvider):
    provider_id = 'youtube'
    display_name = 'YouTube'
    channel = 'youtube'

    def fetch_metrics(self, *, asset_id: int) -> Dict[str, Any]:
        api_key = getattr(settings, 'ANALYTICS_YOUTUBE_API_KEY', '') or ''
        if not api_key:
            return {
                'views': 0,
                'clicks': 0,
                'conversions': 0,
                'bandwidth_bytes': None,
                'latency_ms': None,
                'external_id': '',
                'sync_status': 'error',
                'last_sync_error': 'ANALYTICS_YOUTUBE_API_KEY is not configured',
                'retry_count': 0,
                'metadata': {'provider': self.provider_id, 'geography': {}, 'watch_time_minutes': None},
            }

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

        # Resolve video_id from Document extra_data or metadata types later.
        video_id = ''
        try:
            extra = getattr(document, 'extra_data', None) or {}
            video_id = (extra.get('youtube_video_id') or extra.get('youtube_id') or '').strip()
        except Exception:
            video_id = ''

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

        try:
            youtube = build('youtube', 'v3', developerKey=api_key, cache_discovery=False)
            resp = youtube.videos().list(
                part='statistics,contentDetails',
                id=video_id
            ).execute()
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

        # We map clicks/conversions as 0 here (requires downstream attribution).
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
            },
        }

    def push_event(self, *, event: Dict[str, Any]) -> Optional[str]:
        # Stub: no-op.
        return None

# End of file