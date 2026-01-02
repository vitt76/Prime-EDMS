"""Wildberries analytics provider (real API, best-effort).

This provider uses Wildberries Statistics API (seller) to fetch sales-like
metrics for assets mapped to WB SKU/NmID.

Mapping:
  - Expected in Document.extra_data['sku'] (string/int) or a metadata field
    (later can be implemented via DocumentMetadata lookup).
"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, Dict, Optional

from django.apps import apps as django_apps
from django.conf import settings
from django.utils import timezone

import requests

from mayan.apps.documents.models import Document

from .base import BaseAnalyticsProvider

logger = logging.getLogger(__name__)


class WildberriesAnalyticsProvider(BaseAnalyticsProvider):
    provider_id = 'wildberries'
    display_name = 'Wildberries'
    channel = 'wildberries'

    def fetch_metrics(self, *, asset_id: int) -> Dict[str, Any]:
        token = getattr(settings, 'ANALYTICS_WILDBERRIES_API_TOKEN', '') or ''
        if not token:
            return {
                'views': 0,
                'clicks': 0,
                'conversions': 0,
                'bandwidth_bytes': None,
                'latency_ms': None,
                'external_id': '',
                'sync_status': 'error',
                'last_sync_error': 'ANALYTICS_WILDBERRIES_API_TOKEN is not configured',
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

        sku = ''
        try:
            extra = getattr(document, 'extra_data', None) or {}
            sku = str(extra.get('sku') or extra.get('wb_sku') or extra.get('wb_nm_id') or '').strip()
        except Exception:
            sku = ''

        if not sku:
            # Best-effort metadata lookup (if metadata app installed).
            try:
                DocumentMetadata = django_apps.get_model('metadata', 'DocumentMetadata')
                row = (
                    DocumentMetadata.objects.filter(document=document)
                    .select_related('metadata_type')
                    .filter(metadata_type__name__in=('sku', 'wb_sku', 'wb_nm_id'))
                    .order_by('metadata_type__name')
                    .values_list('value', flat=True)
                    .first()
                )
                sku = str(row or '').strip()
            except Exception:
                sku = ''

        if not sku:
            return {
                'views': 0,
                'clicks': 0,
                'conversions': 0,
                'bandwidth_bytes': None,
                'latency_ms': None,
                'external_id': '',
                'sync_status': 'error',
                'last_sync_error': 'Missing sku in document extra_data/metadata',
                'retry_count': 0,
                'metadata': {'provider': self.provider_id},
            }

        # Wildberries Statistics API (seller) – sales endpoint.
        date_from = (timezone.now() - timedelta(days=7)).date().isoformat()
        url = 'https://statistics-api.wildberries.ru/api/v1/supplier/sales'
        headers = {'Authorization': token}
        params = {'dateFrom': date_from}

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=20)
            resp.raise_for_status()
            data = resp.json() or []
        except Exception as exc:
            logger.exception('Wildberries API call failed: %s', exc)
            return {
                'views': 0,
                'clicks': 0,
                'conversions': 0,
                'bandwidth_bytes': None,
                'latency_ms': None,
                'external_id': sku,
                'sync_status': 'error',
                'last_sync_error': str(exc),
                'retry_count': 0,
                'metadata': {'provider': self.provider_id},
            }

        # Aggregate rows for this SKU/NmID if present.
        orders = 0
        buyouts = 0
        revenue = 0.0
        matched = 0
        for row in data:
            row_sku = str(row.get('nmId') or row.get('supplierArticle') or '').strip()
            if not row_sku:
                continue
            if row_sku != sku:
                continue
            matched += 1
            orders += 1
            # isCancel / quantity? depends on API response; best-effort.
            if not row.get('isCancel'):
                buyouts += 1
            try:
                revenue += float(row.get('forPay') or 0.0)
            except Exception:
                pass

        conversion_rate = None
        if orders:
            conversion_rate = round((buyouts / orders) * 100, 2)

        return {
            'views': 0,
            'clicks': orders,
            'conversions': buyouts,
            'bandwidth_bytes': None,
            'latency_ms': None,
            'external_id': sku,
            'sync_status': 'ok',
            'last_sync_error': '',
            'retry_count': 0,
            'metadata': {
                'provider': self.provider_id,
                'orders': orders,
                'buyouts': buyouts,
                'conversion_rate': conversion_rate,
                'revenue_amount': round(revenue, 2),
                'matched_rows': matched,
                'date_from': date_from,
            },
        }

    def push_event(self, *, event: Dict[str, Any]) -> Optional[str]:
        return None


