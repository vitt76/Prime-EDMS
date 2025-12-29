from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from mayan.apps.documents.models import Document, DocumentFile

from mayan.apps.analytics.models import AssetDailyMetrics, AssetEvent
from mayan.apps.analytics.permissions import permission_analytics_view_asset_bank
from mayan.apps.permissions import Permission


class AssetBankViewSet(viewsets.ViewSet):
    """Headless API: Asset Bank dashboard (Phase 1 / Level 1)."""

    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=('get',))
    def top_metrics(self, request):
        """GET /api/v4/headless/analytics/dashboard/assets/top-metrics/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_asset_bank,), user=request.user
        )
        total_assets = Document.valid.filter(in_trash=False).count()

        used_bytes = DocumentFile.valid.aggregate(
            total=Sum('size')
        )['total'] or 0

        # Phase 1: MAU and Search Success require Level 3/4 models; return 0 for now.
        return Response(
            data={
                'total_assets': total_assets,
                'storage_used_bytes': used_bytes,
                'mau': 0,
                'search_success_rate': 0,
                'avg_find_time_minutes': None,
                'notes': {
                    'mau': 'Phase 2: will be calculated from analytics user sessions.',
                    'search_success_rate': 'Phase 2: will be calculated from analytics search queries.',
                }
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=('get',))
    def asset_distribution(self, request):
        """GET /api/v4/headless/analytics/dashboard/assets/distribution/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_asset_bank,), user=request.user
        )
        # Build distribution by broad types: images/videos/documents/other.
        buckets = {
            'images': {'count': 0, 'size_bytes': 0},
            'videos': {'count': 0, 'size_bytes': 0},
            'documents': {'count': 0, 'size_bytes': 0},
            'other': {'count': 0, 'size_bytes': 0},
        }

        # Use latest file per document (best-effort): count by file mimetype.
        # Phase 1: approximate distribution using all valid files.
        for row in DocumentFile.valid.values('mimetype').annotate(
            count=Count('id'),
            size_bytes=Sum('size')
        ):
            mimetype = (row.get('mimetype') or '').lower()
            count = row.get('count') or 0
            size_bytes = row.get('size_bytes') or 0

            if mimetype.startswith('image/'):
                key = 'images'
            elif mimetype.startswith('video/'):
                key = 'videos'
            elif mimetype.startswith('audio/'):
                key = 'other'
            elif mimetype.startswith('application/') or mimetype.startswith('text/'):
                key = 'documents'
            else:
                key = 'other'

            buckets[key]['count'] += count
            buckets[key]['size_bytes'] += size_bytes

        return Response(
            data={
                'distribution': [
                    {'type': key, **value} for key, value in buckets.items()
                ]
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=('get',))
    def most_downloaded(self, request):
        """GET /api/v4/headless/analytics/dashboard/assets/most-downloaded/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_asset_bank,), user=request.user
        )
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        # Default window: last 30 days.
        if not date_from and not date_to:
            date_from = (timezone.now().date() - timedelta(days=30)).isoformat()
            date_to = timezone.now().date().isoformat()

        # Prefer aggregated table if present.
        metrics_qs = AssetDailyMetrics.objects.all()
        if date_from:
            metrics_qs = metrics_qs.filter(date__gte=date_from)
        if date_to:
            metrics_qs = metrics_qs.filter(date__lte=date_to)

        if metrics_qs.exists():
            rows = metrics_qs.values(
                'document_id',
                'document__label'
            ).annotate(
                downloads=Sum('downloads'),
                views=Sum('views'),
                shares=Sum('shares')
            ).order_by('-downloads')[:50]

            return Response(
                data={'results': list(rows), 'source': 'daily_metrics'},
                status=status.HTTP_200_OK
            )

        # Fallback: raw events.
        events_qs = AssetEvent.objects.filter(event_type=AssetEvent.EVENT_TYPE_DOWNLOAD)
        if date_from:
            events_qs = events_qs.filter(timestamp__date__gte=date_from)
        if date_to:
            events_qs = events_qs.filter(timestamp__date__lte=date_to)

        rows = events_qs.values('document_id').annotate(
            downloads=Count('id')
        ).order_by('-downloads')[:50]

        # Attach labels in bulk.
        document_ids = [row['document_id'] for row in rows]
        label_map = dict(
            Document.objects.filter(pk__in=document_ids).values_list('pk', 'label')
        )
        results = []
        for row in rows:
            results.append(
                {
                    'document_id': row['document_id'],
                    'document__label': label_map.get(row['document_id'], ''),
                    'downloads': row['downloads'],
                    'views': 0,
                    'shares': 0
                }
            )

        return Response(
            data={'results': results, 'source': 'raw_events'},
            status=status.HTTP_200_OK
        )


