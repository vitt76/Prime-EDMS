import json
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from mayan.apps.analytics.models import DistributionEvent


class Command(BaseCommand):
    """Ingest distribution events from a JSON file (Release 3 foundation).

    File format:
      [
        {
          "channel": "website",
          "event_type": "published",
          "status": "ok",
          "document_id": 123,
          "campaign_id": "uuid-or-null",
          "occurred_at": "2025-12-30T12:00:00Z",
          "views": 10,
          "clicks": 2,
          "conversions": 0,
          "bandwidth_bytes": 123456,
          "latency_ms": 120,
          "metadata": { ... }
        }
      ]
    """

    help = 'Ingest distribution events from a JSON file into analytics_distribution_events.'

    def add_arguments(self, parser):
        parser.add_argument('--path', required=True, help='Path to JSON file with events.')

    def handle(self, *args, **options):
        path = options['path']

        with open(path, 'r', encoding='utf-8') as f:
            payload = json.load(f)

        if not isinstance(payload, list):
            raise ValueError('JSON payload must be a list of events.')

        created = 0
        for ev in payload:
            try:
                occurred_at = ev.get('occurred_at') or ev.get('timestamp')
                if occurred_at:
                    occurred_at_dt = timezone.datetime.fromisoformat(str(occurred_at).replace('Z', '+00:00'))
                else:
                    occurred_at_dt = timezone.now()

                DistributionEvent.objects.create(
                    channel=(ev.get('channel') or '').strip(),
                    event_type=ev.get('event_type') or DistributionEvent.EVENT_TYPE_SYNCED,
                    status=ev.get('status') or DistributionEvent.STATUS_OK,
                    sync_status=ev.get('sync_status') or '',
                    last_sync_error=ev.get('last_sync_error') or '',
                    retry_count=int(ev.get('retry_count') or 0),
                    document_id=ev.get('document_id') or None,
                    campaign_id=ev.get('campaign_id') or None,
                    views=ev.get('views'),
                    clicks=ev.get('clicks'),
                    conversions=ev.get('conversions'),
                    revenue_amount=ev.get('revenue_amount'),
                    currency=ev.get('currency') or '',
                    bandwidth_bytes=ev.get('bandwidth_bytes'),
                    latency_ms=ev.get('latency_ms'),
                    external_id=ev.get('external_id') or '',
                    occurred_at=occurred_at_dt,
                    metadata=ev.get('metadata') or {},
                )
                created += 1
            except Exception:
                continue

        self.stdout.write(self.style.SUCCESS(f'Ingested {created} distribution events from {path}.'))


