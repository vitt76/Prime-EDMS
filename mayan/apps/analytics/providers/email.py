"""Email analytics provider (SendGrid/Mailchimp, Strategy pattern).

Scope:
  - fetch_metrics() pulls campaign-level stats (opens/clicks/etc.) and maps them
    into normalized metrics so they can be stored as DistributionEvent.
  - real-time click tracking is implemented via webhook endpoint:
    POST /api/v4/analytics/webhooks/email/click/
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from django.apps import apps as django_apps
from django.conf import settings
from django.utils import timezone

import requests

from mayan.apps.documents.models import Document

from .base import BaseAnalyticsProvider

logger = logging.getLogger(__name__)


class BaseEmailProvider:
    """Strategy interface for Email Service Providers (ESP)."""

    def fetch_campaign_metrics(self, *, campaign_id: str) -> Dict[str, Any]:
        raise NotImplementedError


class SendGridProvider(BaseEmailProvider):
    """SendGrid implementation (best-effort)."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_campaign_metrics(self, *, campaign_id: str) -> Dict[str, Any]:
        if not self.api_key:
            raise RuntimeError('ANALYTICS_SENDGRID_API_KEY is not configured')

        # Best-effort: endpoint availability depends on SendGrid plan/features.
        url = f'https://api.sendgrid.com/v3/marketing/stats/singlesends/{campaign_id}'
        headers = {'Authorization': f'Bearer {self.api_key}'}
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code >= 400:
            raise RuntimeError(f'SendGrid API error: {resp.status_code} {resp.text[:200]}')
        data = resp.json() or {}
        return {
            'opens': int(data.get('opens') or 0),
            'clicks': int(data.get('clicks') or 0),
            'bounces': int(data.get('bounces') or 0),
            'unsubscribes': int(data.get('unsubscribes') or 0),
            'raw': data,
        }


class MailchimpProvider(BaseEmailProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_campaign_metrics(self, *, campaign_id: str) -> Dict[str, Any]:
        if not self.api_key:
            raise RuntimeError('ANALYTICS_MAILCHIMP_API_KEY is not configured')
        # Mailchimp requires datacenter base URL (e.g. us5) which is embedded in the API key.
        raise RuntimeError('Mailchimp provider requires datacenter URL configuration')


class EmailAnalyticsProvider(BaseAnalyticsProvider):
    provider_id = 'email'
    display_name = 'Email'
    channel = 'email'

    def fetch_metrics(self, *, asset_id: int) -> Dict[str, Any]:
        provider_name = (getattr(settings, 'ANALYTICS_EMAIL_PROVIDER', 'sendgrid') or 'sendgrid').strip().lower()
        if provider_name == 'sendgrid':
            strategy: BaseEmailProvider = SendGridProvider(api_key=getattr(settings, 'ANALYTICS_SENDGRID_API_KEY', ''))
        elif provider_name == 'mailchimp':
            strategy = MailchimpProvider(api_key=getattr(settings, 'ANALYTICS_MAILCHIMP_API_KEY', ''))
        else:
            return {
                'views': 0,
                'clicks': 0,
                'conversions': 0,
                'bandwidth_bytes': None,
                'latency_ms': None,
                'external_id': '',
                'sync_status': 'error',
                'last_sync_error': f'Unsupported email provider: {provider_name}',
                'retry_count': 0,
                'metadata': {'provider': self.provider_id},
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

        campaign_id = ''
        try:
            extra = getattr(document, 'extra_data', None) or {}
            campaign_id = (extra.get('email_campaign_id') or extra.get('sendgrid_campaign_id') or '').strip()
        except Exception:
            campaign_id = ''

        if not campaign_id:
            try:
                DocumentMetadata = django_apps.get_model('metadata', 'DocumentMetadata')
                row = (
                    DocumentMetadata.objects.filter(document=document)
                    .select_related('metadata_type')
                    .filter(metadata_type__name__in=('email_campaign_id', 'sendgrid_campaign_id'))
                    .values_list('value', flat=True)
                    .first()
                )
                campaign_id = str(row or '').strip()
            except Exception:
                campaign_id = ''

        if not campaign_id:
            return {
                'views': 0,
                'clicks': 0,
                'conversions': 0,
                'bandwidth_bytes': None,
                'latency_ms': None,
                'external_id': '',
                'sync_status': 'error',
                'last_sync_error': 'Missing email_campaign_id in document extra_data/metadata',
                'retry_count': 0,
                'metadata': {'provider': self.provider_id},
            }

        try:
            metrics = strategy.fetch_campaign_metrics(campaign_id=campaign_id)
        except Exception as exc:
            logger.exception('Email provider fetch_campaign_metrics failed: %s', exc)
            return {
                'views': 0,
                'clicks': 0,
                'conversions': 0,
                'bandwidth_bytes': None,
                'latency_ms': None,
                'external_id': str(campaign_id),
                'sync_status': 'error',
                'last_sync_error': str(exc),
                'retry_count': 0,
                'metadata': {'provider': provider_name},
            }

        opens = int(metrics.get('opens') or 0)
        clicks = int(metrics.get('clicks') or 0)
        return {
            'views': opens,
            'clicks': clicks,
            'conversions': 0,
            'bandwidth_bytes': None,
            'latency_ms': None,
            'external_id': str(campaign_id),
            'sync_status': 'ok',
            'last_sync_error': '',
            'retry_count': 0,
            'metadata': {
                'provider': provider_name,
                'opens': opens,
                'clicks': clicks,
                'bounces': int(metrics.get('bounces') or 0),
                'unsubscribes': int(metrics.get('unsubscribes') or 0),
                'fetched_at': timezone.now().isoformat(),
            },
        }

    def push_event(self, *, event: Dict[str, Any]) -> Optional[str]:
        return None

# End of file