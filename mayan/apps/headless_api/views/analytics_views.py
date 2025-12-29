from datetime import timedelta

from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from mayan.apps.documents.models import Document, DocumentFile

from mayan.apps.analytics.models import (
    AssetDailyMetrics, AssetEvent, Campaign, CampaignAsset, SearchDailyMetrics,
    SearchQuery, UserSession
)
from mayan.apps.analytics.permissions import (
    permission_analytics_view_asset_bank, permission_analytics_view_campaign_performance,
    permission_analytics_view_search_analytics, permission_analytics_view_user_activity
)
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

        last_30_days = timezone.now() - timedelta(days=30)
        mau = UserSession.objects.filter(
            login_timestamp__gte=last_30_days
        ).values('user_id').distinct().count()

        search_qs = SearchQuery.objects.filter(timestamp__gte=last_30_days)
        total_searches = search_qs.count()
        successful_searches = search_qs.filter(results_count__gt=0).count()
        search_success_rate = 0
        if total_searches:
            search_success_rate = round((successful_searches / total_searches) * 100, 2)

        return Response(
            data={
                'total_assets': total_assets,
                'storage_used_bytes': used_bytes,
                'mau': mau,
                'search_success_rate': search_success_rate,
                'avg_find_time_minutes': None,
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


class CampaignPerformanceViewSet(viewsets.ViewSet):
    """Headless API: Campaign Performance dashboard (Phase 2 / Level 2)."""

    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=('get',))
    def campaigns(self, request):
        """GET /api/v4/headless/analytics/campaigns/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_campaign_performance,), user=request.user
        )
        rows = Campaign.objects.order_by('-updated_at').values(
            'id', 'label', 'status', 'start_date', 'end_date', 'updated_at',
            'cost_amount', 'revenue_amount', 'currency'
        )[:200]
        return Response(data={'results': list(rows)}, status=status.HTTP_200_OK)

    @action(detail=False, methods=('post',))
    def create_campaign(self, request):
        """POST /api/v4/headless/analytics/campaigns/create/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_campaign_performance,), user=request.user
        )
        label = (request.data.get('label') or '').strip()
        if not label:
            return Response(
                data={'detail': 'label is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        campaign = Campaign.objects.create(
            label=label,
            description=(request.data.get('description') or '').strip(),
            status=request.data.get('status') or Campaign.STATUS_DRAFT,
            start_date=request.data.get('start_date') or None,
            end_date=request.data.get('end_date') or None,
            created_by=request.user,
            cost_amount=request.data.get('cost_amount') or None,
            revenue_amount=request.data.get('revenue_amount') or None,
            currency=request.data.get('currency') or 'RUB',
        )

        return Response(
            data={
                'id': str(campaign.id),
                'label': campaign.label,
                'status': campaign.status,
                'roi': campaign.get_roi(),
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=('post',))
    def add_assets(self, request):
        """POST /api/v4/headless/analytics/campaigns/add-assets/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_campaign_performance,), user=request.user
        )
        campaign_id = request.data.get('campaign_id')
        document_ids = request.data.get('document_ids') or []
        if not campaign_id or not document_ids:
            return Response(
                data={'detail': 'campaign_id and document_ids are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        campaign = Campaign.objects.filter(pk=campaign_id).first()
        if not campaign:
            return Response(data={'detail': 'campaign not found'}, status=status.HTTP_404_NOT_FOUND)

        created = 0
        for doc_id in document_ids:
            _, was_created = CampaignAsset.objects.get_or_create(
                campaign=campaign, document_id=doc_id
            )
            if was_created:
                created += 1

        return Response(
            data={'created': created},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=('post',))
    def update_financials(self, request):
        """POST /api/v4/headless/analytics/campaigns/update-financials/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_campaign_performance,), user=request.user
        )
        campaign_id = request.data.get('campaign_id')
        if not campaign_id:
            return Response(
                data={'detail': 'campaign_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        campaign = Campaign.objects.filter(pk=campaign_id).first()
        if not campaign:
            return Response(data={'detail': 'campaign not found'}, status=status.HTTP_404_NOT_FOUND)

        if 'cost_amount' in request.data:
            campaign.cost_amount = request.data.get('cost_amount') or None
        if 'revenue_amount' in request.data:
            campaign.revenue_amount = request.data.get('revenue_amount') or None
        if 'currency' in request.data:
            campaign.currency = request.data.get('currency') or campaign.currency

        campaign.save(update_fields=('cost_amount', 'revenue_amount', 'currency', 'updated_at'))

        return Response(
            data={
                'id': str(campaign.id),
                'roi': campaign.get_roi(),
                'cost_amount': campaign.cost_amount,
                'revenue_amount': campaign.revenue_amount,
                'currency': campaign.currency,
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=('get',))
    def dashboard(self, request):
        """GET /api/v4/headless/analytics/dashboard/campaigns/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_campaign_performance,), user=request.user
        )
        campaign_id = request.query_params.get('campaign_id')
        days = int(request.query_params.get('days') or 30)
        date_from = timezone.now().date() - timedelta(days=days)

        campaign = None
        if campaign_id:
            campaign = Campaign.objects.filter(pk=campaign_id).first()
        if not campaign:
            campaign = Campaign.objects.order_by('-updated_at').first()

        if not campaign:
            return Response(
                data={'campaign': None, 'timeline': [], 'channels': []},
                status=status.HTTP_200_OK
            )

        document_ids = list(
            CampaignAsset.objects.filter(campaign=campaign).values_list('document_id', flat=True)
        )

        events_qs = AssetEvent.objects.filter(
            document_id__in=document_ids,
            timestamp__date__gte=date_from
        )

        timeline = list(
            events_qs.values('timestamp__date').annotate(
                views=Count('id', filter=Q(event_type=AssetEvent.EVENT_TYPE_VIEW)),
                downloads=Count('id', filter=Q(event_type=AssetEvent.EVENT_TYPE_DOWNLOAD)),
            ).order_by('timestamp__date')
        )

        channels = list(
            events_qs.values('channel').annotate(
                views=Count('id', filter=Q(event_type=AssetEvent.EVENT_TYPE_VIEW)),
                downloads=Count('id', filter=Q(event_type=AssetEvent.EVENT_TYPE_DOWNLOAD)),
            ).order_by('-downloads')
        )

        return Response(
            data={
                'campaign': {
                    'id': str(campaign.id),
                    'label': campaign.label,
                    'status': campaign.status,
                    'assets_count': len(document_ids),
                    'roi': campaign.get_roi(),
                    'cost_amount': campaign.cost_amount,
                    'revenue_amount': campaign.revenue_amount,
                    'currency': campaign.currency,
                    'updated_at': campaign.updated_at,
                },
                'timeline': timeline,
                'channels': channels,
            },
            status=status.HTTP_200_OK
        )


class SearchAnalyticsViewSet(viewsets.ViewSet):
    """Headless API: Search Analytics (Phase 2 / Level 4)."""

    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=('get',))
    def top_queries(self, request):
        """GET /api/v4/headless/analytics/dashboard/search/top-queries/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_search_analytics,), user=request.user
        )
        days = int(request.query_params.get('days') or 30)
        date_from = timezone.now() - timedelta(days=days)
        qs = SearchQuery.objects.filter(timestamp__gte=date_from)
        rows = qs.values('query_text').annotate(
            count=Count('id')
        ).order_by('-count')[:50]
        return Response(data={'results': list(rows)}, status=status.HTTP_200_OK)

    @action(detail=False, methods=('get',))
    def null_searches(self, request):
        """GET /api/v4/headless/analytics/dashboard/search/null-searches/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_search_analytics,), user=request.user
        )
        days = int(request.query_params.get('days') or 30)
        date_from = timezone.now() - timedelta(days=days)
        qs = SearchQuery.objects.filter(timestamp__gte=date_from, results_count=0)
        rows = qs.values('query_text').annotate(
            count=Count('id')
        ).order_by('-count')[:50]
        return Response(data={'results': list(rows)}, status=status.HTTP_200_OK)

    @action(detail=False, methods=('get',))
    def daily(self, request):
        """GET /api/v4/headless/analytics/dashboard/search/daily/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_search_analytics,), user=request.user
        )
        days = int(request.query_params.get('days') or 30)
        date_from = timezone.now().date() - timedelta(days=days)
        rows = SearchDailyMetrics.objects.filter(
            date__gte=date_from
        ).order_by('date').values(
            'date', 'total_searches', 'successful_searches', 'null_searches',
            'ctr', 'avg_response_time_ms'
        )
        return Response(data={'results': list(rows)}, status=status.HTTP_200_OK)


class UserActivityViewSet(viewsets.ViewSet):
    """Headless API: User activity / adoption (Phase 2 / Level 3)."""

    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=('get',))
    def adoption_by_department(self, request):
        """GET /api/v4/headless/analytics/dashboard/users/adoption-heatmap/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_user_activity,), user=request.user
        )
        days = int(request.query_params.get('days') or 30)
        date_from = timezone.now() - timedelta(days=days)

        user_ids = list(
            UserSession.objects.filter(login_timestamp__gte=date_from).values_list(
                'user_id', flat=True
            ).distinct()
        )

        UserModel = UserSession._meta.get_field('user').remote_field.model
        user_map = {
            user.pk: user for user in UserModel.objects.filter(pk__in=user_ids)
        }

        buckets = {}
        for user_id in user_ids:
            user = user_map.get(user_id)
            department = ''
            if user:
                department = getattr(user, 'department', '') or ''

            buckets.setdefault(department or '—', set()).add(user_id)

        results = []
        for department, ids in buckets.items():
            results.append({'department': department, 'mau': len(ids)})

        results.sort(key=lambda x: x['mau'], reverse=True)
        return Response(data={'results': results}, status=status.HTTP_200_OK)

