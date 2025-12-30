from datetime import timedelta

from django.conf import settings
from django.db.models import Avg, Count, Q, Sum
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from mayan.apps.documents.models import Document, DocumentFile

from mayan.apps.analytics.models import (
    AssetDailyMetrics, AssetEvent, Campaign, CampaignAsset, SearchDailyMetrics,
    ApprovalWorkflowEvent, AnalyticsAlert, CDNDailyCost, SearchQuery,
    CampaignDailyMetrics, CampaignEngagementEvent, FeatureUsage, SearchSession,
    DistributionEvent, UserDailyMetrics, UserSession
)
from mayan.apps.analytics.utils import track_asset_event
from mayan.apps.analytics.permissions import (
    permission_analytics_view_asset_bank, permission_analytics_view_campaign_performance,
    permission_analytics_view_search_analytics, permission_analytics_view_user_activity,
    permission_analytics_view_content_intelligence, permission_analytics_view_distribution
)
from mayan.apps.permissions import Permission
from mayan.apps.analytics.realtime import notify_analytics_refresh


class AssetBankViewSet(viewsets.ViewSet):
    """Headless API: Asset Bank dashboard (Phase 1 / Level 1)."""

    permission_classes = (IsAuthenticated,)

    @method_decorator(cache_page(600))
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
        successful_searches = search_qs.filter(
            Q(was_downloaded=True) | Q(was_clicked_result_document_id__isnull=False)
        ).count()
        search_success_rate = 0
        if total_searches:
            search_success_rate = round((successful_searches / total_searches) * 100, 2)

        # Avg Search-to-Find Time (minutes) based on aggregated UserDailyMetrics.
        avg_find_time_minutes = None
        try:
            avg_find_time_minutes = UserDailyMetrics.objects.filter(
                date__gte=last_30_days.date(),
                avg_search_to_find_minutes__isnull=False
            ).aggregate(avg=Avg('avg_search_to_find_minutes'))['avg']
            if avg_find_time_minutes is not None:
                avg_find_time_minutes = round(float(avg_find_time_minutes), 2)
        except Exception:
            avg_find_time_minutes = None

        # CDN cost per month (USD), based on daily rollups.
        cdn_cost_per_month = None
        try:
            cdn_cost_total = CDNDailyCost.objects.filter(
                date__gte=last_30_days.date()
            ).aggregate(total=Sum('cost_usd'))['total']
            if cdn_cost_total is not None:
                cdn_cost_per_month = float(cdn_cost_total)
        except Exception:
            cdn_cost_per_month = None

        return Response(
            data={
                'total_assets': total_assets,
                'storage_used_bytes': used_bytes,
                'mau': mau,
                'search_success_rate': search_success_rate,
                'avg_find_time_minutes': avg_find_time_minutes,
                'cdn_cost_per_month': cdn_cost_per_month,
            },
            status=status.HTTP_200_OK
        )

    @method_decorator(cache_page(600))
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

    @method_decorator(cache_page(600))
    @action(detail=False, methods=('get',))
    def most_downloaded(self, request):
        """GET /api/v4/headless/analytics/dashboard/assets/most-downloaded/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_asset_bank,), user=request.user
        )
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        asset_type = (request.query_params.get('asset_type') or '').strip().lower()
        department = (request.query_params.get('department') or '').strip()

        # Default window: last 30 days.
        if not date_from and not date_to:
            date_from = (timezone.now().date() - timedelta(days=30)).isoformat()
            date_to = timezone.now().date().isoformat()

        # Optional filter by broad asset type (best-effort).
        document_ids_by_type = None
        if asset_type in ('images', 'videos', 'documents', 'other'):
            qs = DocumentFile.valid.all()
            if asset_type == 'images':
                qs = qs.filter(mimetype__istartswith='image/')
            elif asset_type == 'videos':
                qs = qs.filter(mimetype__istartswith='video/')
            elif asset_type == 'documents':
                qs = qs.filter(Q(mimetype__istartswith='application/') | Q(mimetype__istartswith='text/'))
            elif asset_type == 'other':
                qs = qs.exclude(
                    Q(mimetype__istartswith='image/') |
                    Q(mimetype__istartswith='video/') |
                    Q(mimetype__istartswith='application/') |
                    Q(mimetype__istartswith='text/')
                )
            document_ids_by_type = qs.values_list('document_id', flat=True).distinct()

        # Prefer aggregated table if present.
        metrics_qs = AssetDailyMetrics.objects.all()
        if date_from:
            metrics_qs = metrics_qs.filter(date__gte=date_from)
        if date_to:
            metrics_qs = metrics_qs.filter(date__lte=date_to)
        if document_ids_by_type is not None:
            metrics_qs = metrics_qs.filter(document_id__in=document_ids_by_type)

        if metrics_qs.exists() and not department:
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
        if document_ids_by_type is not None:
            events_qs = events_qs.filter(document_id__in=document_ids_by_type)
        if department:
            events_qs = events_qs.filter(user_department=department)

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

    @method_decorator(cache_page(600))
    @action(detail=False, methods=('get',))
    def asset_detail(self, request):
        """GET /api/v4/headless/analytics/dashboard/assets/detail/?document_id=123"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_asset_bank,), user=request.user
        )
        document_id = int(request.query_params.get('document_id') or 0)
        days = int(request.query_params.get('days') or 30)
        if not document_id:
            return Response({'detail': 'document_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        date_from = timezone.now() - timedelta(days=days)

        document = Document.valid.filter(pk=document_id).first()
        if not document:
            return Response({'detail': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

        daily_series = list(
            AssetDailyMetrics.objects.filter(
                document_id=document_id,
                date__gte=date_from.date()
            ).order_by('date').values(
                'date', 'views', 'downloads', 'shares', 'performance_score',
                'cdn_bandwidth_gb', 'top_channel'
            )
        )

        channel_rows = list(
            AssetEvent.objects.filter(
                document_id=document_id,
                timestamp__gte=date_from
            ).values(
                'channel', 'event_type'
            ).annotate(
                count=Count('id'),
                bandwidth_bytes=Sum('bandwidth_bytes')
            ).order_by('-count')[:50]
        )

        # Best-effort: search queries that led to a download for this asset.
        session_ids = list(
            SearchSession.objects.filter(
                last_download_event__document_id=document_id,
                ended_at__gte=date_from
            ).values_list('pk', flat=True)[:5000]
        )
        search_referrers = list(
            SearchQuery.objects.filter(
                search_session_id__in=session_ids
            ).values('query_text').annotate(
                count=Count('id')
            ).order_by('-count')[:20]
        ) if session_ids else []

        return Response(
            data={
                'document': {'id': document.pk, 'label': document.label},
                'daily_series': daily_series,
                'channels': channel_rows,
                'search_referrers': search_referrers,
            },
            status=status.HTTP_200_OK
        )

    @method_decorator(cache_page(600))
    @action(detail=False, methods=('get',))
    def distribution_trend(self, request):
        """GET /api/v4/headless/analytics/dashboard/assets/distribution-trend/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_asset_bank,), user=request.user
        )

        today = timezone.now().date()

        def month_start(d):
            return d.replace(day=1)

        def add_months(d, months):
            year = d.year + (d.month - 1 + months) // 12
            month = (d.month - 1 + months) % 12 + 1
            return d.replace(year=year, month=month, day=1)

        def bucket_for_mimetype(mimetype: str) -> str:
            mimetype = (mimetype or '').lower()
            if mimetype.startswith('image/'):
                return 'images'
            if mimetype.startswith('video/'):
                return 'videos'
            if mimetype.startswith('application/') or mimetype.startswith('text/'):
                return 'documents'
            return 'other'

        start_month = add_months(month_start(today), -11)
        months = [add_months(start_month, i) for i in range(12)]

        baseline = {'images': 0, 'videos': 0, 'documents': 0, 'other': 0}
        for row in DocumentFile.valid.filter(timestamp__date__lt=start_month).values('mimetype').annotate(
            count=Count('id')
        ):
            baseline[bucket_for_mimetype(row.get('mimetype') or '')] += int(row.get('count') or 0)

        monthly_additions = {m.strftime('%Y-%m'): {'images': 0, 'videos': 0, 'documents': 0, 'other': 0} for m in months}
        for row in DocumentFile.valid.filter(timestamp__date__gte=start_month).annotate(
            month=TruncMonth('timestamp')
        ).values('month', 'mimetype').annotate(
            count=Count('id')
        ):
            month = row.get('month')
            if not month:
                continue
            key = month.date().strftime('%Y-%m')
            if key not in monthly_additions:
                continue
            monthly_additions[key][bucket_for_mimetype(row.get('mimetype') or '')] += int(row.get('count') or 0)

        cumulative = dict(baseline)
        trend = []
        for m in months:
            key = m.strftime('%Y-%m')
            additions = monthly_additions.get(key) or {}
            for bucket in cumulative.keys():
                cumulative[bucket] += int(additions.get(bucket) or 0)
            trend.append(
                {
                    'month': key,
                    'distribution': [
                        {'type': t, 'count': cumulative[t]} for t in ('images', 'videos', 'documents', 'other')
                    ]
                }
            )

        return Response(data={'trend': trend}, status=status.HTTP_200_OK)

    @method_decorator(cache_page(600))
    @action(detail=False, methods=('get',))
    def reuse_metrics(self, request):
        """GET /api/v4/headless/analytics/dashboard/assets/reuse-metrics/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_asset_bank,), user=request.user
        )
        today = timezone.now().date()

        def month_start(d):
            return d.replace(day=1)

        def add_months(d, months):
            # Pure python month arithmetic to avoid extra dependencies.
            year = d.year + (d.month - 1 + months) // 12
            month = (d.month - 1 + months) % 12 + 1
            return d.replace(year=year, month=month, day=1)

        months = []
        start = add_months(month_start(today), -11)
        for i in range(12):
            months.append(add_months(start, i))

        total_assets = Document.valid.filter(in_trash=False).count()
        production_cost_per_asset_usd = float(
            getattr(settings, 'ANALYTICS_PRODUCTION_COST_PER_ASSET_USD', 500.0)
        )
        target_rate = float(getattr(settings, 'ANALYTICS_TARGET_REUSE_RATE', 62.0))

        monthly_data = []
        for m_start in months:
            next_m = add_months(m_start, 1)
            m_end = next_m - timedelta(days=1)

            reused_assets = (
                CampaignAsset.objects.filter(added_at__date__lte=m_end)
                .values('document_id')
                .annotate(campaigns=Count('campaign_id', distinct=True))
                .filter(campaigns__gte=2)
                .count()
            )
            reuse_rate = 0.0
            if total_assets:
                reuse_rate = round((reused_assets / total_assets) * 100, 2)

            monthly_data.append(
                {
                    'month': m_start.strftime('%Y-%m'),
                    'reuse_rate': reuse_rate,
                    'reused_assets': reused_assets,
                    'total_assets': total_assets,
                }
            )

        current_rate = monthly_data[-1]['reuse_rate'] if monthly_data else 0.0
        current_reused_assets = monthly_data[-1]['reused_assets'] if monthly_data else 0
        estimated_savings_usd = round(current_reused_assets * production_cost_per_asset_usd, 2) if total_assets else 0.0

        return Response(
            data={
                'monthly_data': monthly_data,
                'current_rate': current_rate,
                'target_rate': target_rate,
                'estimated_savings_usd': estimated_savings_usd,
                'production_cost_per_asset_usd': production_cost_per_asset_usd,
            },
            status=status.HTTP_200_OK
        )

    @method_decorator(cache_page(600))
    @action(detail=False, methods=('get',))
    def storage_trends(self, request):
        """GET /api/v4/headless/analytics/dashboard/assets/storage-trends/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_asset_bank,), user=request.user
        )
        today = timezone.now().date()

        def month_start(d):
            return d.replace(day=1)

        def add_months(d, months):
            year = d.year + (d.month - 1 + months) // 12
            month = (d.month - 1 + months) % 12 + 1
            return d.replace(year=year, month=month, day=1)

        def bucket_for_mimetype(mimetype: str) -> str:
            mimetype = (mimetype or '').lower()
            if mimetype.startswith('image/'):
                return 'images'
            if mimetype.startswith('video/'):
                return 'videos'
            if mimetype.startswith('application/') or mimetype.startswith('text/'):
                return 'documents'
            return 'other'

        start_month = add_months(month_start(today), -11)
        months = [add_months(start_month, i) for i in range(12)]
        start_date = start_month

        baseline_bytes = DocumentFile.valid.filter(
            timestamp__date__lt=start_date
        ).aggregate(total=Sum('size'))['total'] or 0

        # Monthly added bytes by bucket.
        monthly_added = {m.strftime('%Y-%m'): {'images': 0, 'videos': 0, 'documents': 0, 'other': 0} for m in months}

        for row in (
            DocumentFile.valid.filter(timestamp__date__gte=start_date)
            .values('timestamp__year', 'timestamp__month', 'mimetype')
            .annotate(size_bytes=Sum('size'))
        ):
            year = row.get('timestamp__year')
            month = row.get('timestamp__month')
            if not year or not month:
                continue
            key = f'{year:04d}-{month:02d}'
            if key not in monthly_added:
                continue
            bucket = bucket_for_mimetype(row.get('mimetype') or '')
            monthly_added[key][bucket] += int(row.get('size_bytes') or 0)

        # Build cumulative historical totals.
        cumulative_total = int(baseline_bytes)
        cumulative_by_type = {'images': 0, 'videos': 0, 'documents': 0, 'other': 0}
        historical = []
        for m in months:
            key = m.strftime('%Y-%m')
            add_by_type = monthly_added[key]
            for t, v in add_by_type.items():
                cumulative_by_type[t] += int(v)
            cumulative_total += sum(int(v) for v in add_by_type.values())

            by_type_gb = {
                t: round((cumulative_by_type[t] / (1024 ** 3)), 3) for t in cumulative_by_type
            }
            historical.append(
                {
                    'month': key,
                    'total_gb': round((cumulative_total / (1024 ** 3)), 3),
                    'by_type': by_type_gb,
                }
            )

        # Simple linear regression forecast (6 months) on cumulative totals.
        def linear_forecast(values, months_ahead):
            n = len(values)
            if n < 2:
                return [values[-1] if values else 0.0 for _ in range(months_ahead)]
            x = list(range(n))
            y = values
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xx = sum(i * i for i in x)
            sum_xy = sum(i * y[i] for i in x)
            denom = (n * sum_xx - sum_x * sum_x)
            if denom == 0:
                return [y[-1] for _ in range(months_ahead)]
            slope = (n * sum_xy - sum_x * sum_y) / denom
            intercept = (sum_y - slope * sum_x) / n
            return [max(0.0, slope * (n + i) + intercept) for i in range(months_ahead)]

        total_series = [row['total_gb'] for row in historical]
        forecast_total_series = linear_forecast(values=total_series, months_ahead=6)

        # Forecast per type using per-type series.
        forecast_by_type_series = {}
        for t in ('images', 'videos', 'documents', 'other'):
            series = [row['by_type'][t] for row in historical]
            forecast_by_type_series[t] = linear_forecast(values=series, months_ahead=6)

        forecast = []
        for i in range(6):
            m = add_months(months[-1], i + 1)
            key = m.strftime('%Y-%m')
            by_type = {t: round(forecast_by_type_series[t][i], 3) for t in forecast_by_type_series}
            forecast.append(
                {
                    'month': key,
                    'total_gb': round(forecast_total_series[i], 3),
                    'by_type': by_type,
                }
            )

        storage_limit_gb = float(getattr(settings, 'ANALYTICS_STORAGE_LIMIT_GB', 1000.0))
        alert_threshold = float(getattr(settings, 'ANALYTICS_STORAGE_ALERT_THRESHOLD_GB', storage_limit_gb * 0.9))
        current_storage_gb = total_series[-1] if total_series else 0.0

        return Response(
            data={
                'historical': historical,
                'forecast': forecast,
                'current_storage_gb': current_storage_gb,
                'storage_limit_gb': storage_limit_gb,
                'alert_threshold': alert_threshold,
            },
            status=status.HTTP_200_OK
        )

    @method_decorator(cache_page(300))
    @action(detail=False, methods=('get',))
    def alerts(self, request):
        """GET /api/v4/headless/analytics/dashboard/assets/alerts/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_asset_bank,), user=request.user
        )
        limit = int(request.query_params.get('limit') or 50)
        qs = AnalyticsAlert.objects.filter(resolved_at__isnull=True).order_by('-created_at')[:limit]
        results = list(
            qs.values(
                'id', 'alert_type', 'severity', 'title', 'message',
                'document_id', 'campaign_id', 'created_at', 'metadata'
            )
        )
        return Response(data={'results': results}, status=status.HTTP_200_OK)


class CampaignPerformanceViewSet(viewsets.ViewSet):
    """Headless API: Campaign Performance dashboard (Phase 2 / Level 2)."""

    permission_classes = (IsAuthenticated,)

    @method_decorator(cache_page(600))
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

    @action(detail=False, methods=('post',))
    def engagement(self, request, campaign_id: str = ''):
        """POST /api/v4/headless/analytics/campaigns/<campaign_id>/engagement/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_campaign_performance,), user=request.user
        )

        campaign = Campaign.objects.filter(pk=campaign_id).first()
        if not campaign:
            return Response(data={'detail': 'campaign not found'}, status=status.HTTP_404_NOT_FOUND)

        def parse_dt(value):
            if not value:
                return None
            text = str(value).strip()
            if text.endswith('Z'):
                text = text.replace('Z', '+00:00')
            try:
                dt = timezone.datetime.fromisoformat(text)
                if timezone.is_naive(dt):
                    dt = timezone.make_aware(dt)
                return dt
            except Exception:
                return None

        duration_seconds = int(request.data.get('duration_seconds') or 0)
        if duration_seconds <= 0:
            return Response(data={'detail': 'duration_seconds must be > 0'}, status=status.HTTP_400_BAD_REQUEST)

        session_start = parse_dt(request.data.get('session_start'))
        session_end = parse_dt(request.data.get('session_end'))
        if not session_end:
            session_end = timezone.now()
        if not session_start:
            session_start = session_end - timedelta(seconds=duration_seconds)

        # Safety: clamp duration to computed difference if provided.
        computed = int((session_end - session_start).total_seconds())
        if computed > 0:
            duration_seconds = computed

        event = CampaignEngagementEvent.objects.create(
            campaign=campaign,
            user=request.user,
            started_at=session_start,
            ended_at=session_end,
            duration_seconds=duration_seconds,
            metadata={'source': 'frontend', 'path': request.path},
        )

        return Response(
            data={'id': event.pk, 'duration_seconds': duration_seconds},
            status=status.HTTP_201_CREATED
        )

    @method_decorator(cache_page(600))
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

        # Baseline: previous campaign timeline for comparison (best-effort).
        previous_campaign = Campaign.objects.filter(
            updated_at__lt=campaign.updated_at
        ).order_by('-updated_at').first()
        baseline = None
        if previous_campaign:
            prev_doc_ids = list(
                CampaignAsset.objects.filter(campaign=previous_campaign).values_list('document_id', flat=True)
            )
            if prev_doc_ids:
                prev_events_qs = AssetEvent.objects.filter(
                    document_id__in=prev_doc_ids,
                    timestamp__date__gte=date_from
                )
                baseline_timeline = list(
                    prev_events_qs.values('timestamp__date').annotate(
                        views=Count('id', filter=Q(event_type=AssetEvent.EVENT_TYPE_VIEW)),
                        downloads=Count('id', filter=Q(event_type=AssetEvent.EVENT_TYPE_DOWNLOAD)),
                    ).order_by('timestamp__date')
                )
                baseline = {
                    'campaign': {'id': str(previous_campaign.id), 'label': previous_campaign.label},
                    'timeline': baseline_timeline,
                }

        avg_engagement_minutes = CampaignDailyMetrics.objects.filter(
            campaign=campaign,
            date__gte=date_from
        ).aggregate(avg=Avg('avg_engagement_minutes'))['avg']
        if avg_engagement_minutes is not None:
            avg_engagement_minutes = round(float(avg_engagement_minutes), 3)

        return Response(
            data={
                'campaign': {
                    'id': str(campaign.id),
                    'label': campaign.label,
                    'status': campaign.status,
                    'assets_count': len(document_ids),
                    'roi': campaign.get_roi(),
                    'avg_engagement_minutes': avg_engagement_minutes,
                    'cost_amount': campaign.cost_amount,
                    'revenue_amount': campaign.revenue_amount,
                    'currency': campaign.currency,
                    'updated_at': campaign.updated_at,
                },
                'timeline': timeline,
                'channels': channels,
                'baseline': baseline,
            },
            status=status.HTTP_200_OK
        )

    @method_decorator(cache_page(600))
    @action(detail=False, methods=('get',))
    def geography(self, request):
        """GET /api/v4/headless/analytics/dashboard/campaigns/geography/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_campaign_performance,), user=request.user
        )
        campaign_id = request.query_params.get('campaign_id')
        days = int(request.query_params.get('days') or 30)
        date_from_dt = timezone.now() - timedelta(days=days)

        campaign = None
        if campaign_id:
            campaign = Campaign.objects.filter(pk=campaign_id).first()
        if not campaign:
            campaign = Campaign.objects.order_by('-updated_at').first()

        if not campaign:
            return Response(data={'campaign': None, 'countries': []}, status=status.HTTP_200_OK)

        document_ids = list(
            CampaignAsset.objects.filter(campaign=campaign).values_list('document_id', flat=True)
        )
        if not document_ids:
            return Response(data={'campaign': {'id': str(campaign.id)}, 'countries': []}, status=status.HTTP_200_OK)

        user_ids = list(
            AssetEvent.objects.filter(
                document_id__in=document_ids,
                timestamp__gte=date_from_dt,
                user_id__isnull=False
            ).values_list('user_id', flat=True).distinct()
        )
        if not user_ids:
            return Response(data={'campaign': {'id': str(campaign.id)}, 'countries': []}, status=status.HTTP_200_OK)

        user_country_map = {}
        for row in UserSession.objects.filter(
            user_id__in=user_ids, login_timestamp__gte=date_from_dt
        ).exclude(geo_country='').order_by('-login_timestamp').values('user_id', 'geo_country'):
            user_id = row.get('user_id')
            if user_id in user_country_map:
                continue
            user_country_map[user_id] = row.get('geo_country') or ''

        counts = {}
        for country in user_country_map.values():
            if not country:
                continue
            counts[country] = counts.get(country, 0) + 1

        countries = [{'geo_country': k, 'mau': v} for k, v in counts.items()]
        countries.sort(key=lambda x: x['mau'], reverse=True)

        return Response(
            data={'campaign': {'id': str(campaign.id), 'label': campaign.label}, 'countries': countries},
            status=status.HTTP_200_OK
        )

    @method_decorator(cache_page(600))
    @action(detail=False, methods=('get',))
    def top_assets(self, request):
        """GET /api/v4/headless/analytics/dashboard/campaigns/top-assets/"""
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
            return Response(data={'results': [], 'campaign': None}, status=status.HTTP_200_OK)

        document_ids = list(
            CampaignAsset.objects.filter(campaign=campaign).values_list('document_id', flat=True)
        )
        if not document_ids:
            return Response(data={'results': [], 'campaign': {'id': str(campaign.id)}}, status=status.HTTP_200_OK)

        # Prefer daily metrics for speed; fallback to raw events if empty.
        metrics_qs = AssetDailyMetrics.objects.filter(
            document_id__in=document_ids, date__gte=date_from
        )

        rows = []
        if metrics_qs.exists():
            rows = list(
                metrics_qs.values('document_id', 'document__label').annotate(
                    downloads=Sum('downloads'),
                    views=Sum('views'),
                    shares=Sum('shares'),
                    bandwidth_gb=Sum('cdn_bandwidth_gb'),
                    engagement_score=Avg('performance_score'),
                ).order_by('-downloads')[:20]
            )
        else:
            events_qs = AssetEvent.objects.filter(
                document_id__in=document_ids,
                timestamp__date__gte=date_from
            )
            rows = list(
                events_qs.values('document_id').annotate(
                    downloads=Count('id', filter=Q(event_type=AssetEvent.EVENT_TYPE_DOWNLOAD)),
                    views=Count('id', filter=Q(event_type=AssetEvent.EVENT_TYPE_VIEW)),
                    shares=Count('id', filter=Q(event_type=AssetEvent.EVENT_TYPE_SHARE)),
                ).order_by('-downloads')[:20]
            )
            label_map = dict(
                Document.objects.filter(pk__in=[r['document_id'] for r in rows]).values_list('pk', 'label')
            )
            for r in rows:
                r['document__label'] = label_map.get(r['document_id'], '')
                r['bandwidth_gb'] = 0.0
                r['engagement_score'] = None

        # Sparkline (last 7 days) based on daily metrics downloads.
        spark_from = timezone.now().date() - timedelta(days=6)
        spark_dates = [spark_from + timedelta(days=i) for i in range(7)]
        spark_map = {doc_id: {d: 0 for d in spark_dates} for doc_id in [r['document_id'] for r in rows]}
        for r in AssetDailyMetrics.objects.filter(
            document_id__in=list(spark_map.keys()), date__gte=spark_from
        ).values('document_id', 'date').annotate(downloads=Sum('downloads')):
            doc_id = r['document_id']
            d = r['date']
            if doc_id in spark_map and d in spark_map[doc_id]:
                spark_map[doc_id][d] = int(r.get('downloads') or 0)

        results = []
        for r in rows:
            doc_id = r['document_id']
            sparkline = [spark_map.get(doc_id, {}).get(d, 0) for d in spark_dates]
            results.append(
                {
                    'document_id': doc_id,
                    'document__label': r.get('document__label') or '',
                    'downloads': int(r.get('downloads') or 0),
                    'views': int(r.get('views') or 0),
                    'shares': int(r.get('shares') or 0),
                    'bandwidth_gb': float(r.get('bandwidth_gb') or 0.0),
                    'engagement_score': r.get('engagement_score'),
                    'sparkline_data': sparkline,
                }
            )

        return Response(
            data={'campaign': {'id': str(campaign.id), 'label': campaign.label}, 'results': results},
            status=status.HTTP_200_OK
        )

    @method_decorator(cache_page(600))
    @action(detail=False, methods=('get',))
    def timeline(self, request):
        """GET /api/v4/headless/analytics/dashboard/campaigns/timeline/"""
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
            return Response(data={'campaign': None, 'milestones': [], 'velocity': {}}, status=status.HTTP_200_OK)

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

        peak = None
        for point in timeline:
            score = (point.get('downloads') or 0) + (point.get('views') or 0)
            if not peak or score > peak['score']:
                peak = {'date': point.get('timestamp__date'), 'score': score, 'views': point.get('views') or 0, 'downloads': point.get('downloads') or 0}

        created_date = campaign.created_at.date() if campaign.created_at else None
        launched_date = campaign.start_date or created_date
        completed_date = campaign.end_date

        milestones = []
        if created_date:
            milestones.append({'type': 'created', 'date': created_date.isoformat(), 'label': 'Campaign created'})
        if launched_date:
            milestones.append({'type': 'launched', 'date': launched_date.isoformat(), 'label': 'Campaign launched'})
        if peak and peak.get('date'):
            milestones.append(
                {
                    'type': 'peak',
                    'date': peak['date'].isoformat(),
                    'label': 'Peak performance',
                    'views': peak['views'],
                    'downloads': peak['downloads'],
                }
            )
        if completed_date:
            milestones.append({'type': 'completed', 'date': completed_date.isoformat(), 'label': 'Campaign completed'})

        velocity = {}
        if created_date and launched_date:
            velocity['days_to_launch'] = (launched_date - created_date).days
        if launched_date and peak and peak.get('date'):
            velocity['days_to_peak'] = (peak['date'] - launched_date).days
        if created_date and completed_date:
            velocity['days_to_completion'] = (completed_date - created_date).days

        return Response(
            data={
                'campaign': {'id': str(campaign.id), 'label': campaign.label, 'status': campaign.status},
                'milestones': milestones,
                'velocity': velocity,
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

    @action(detail=False, methods=('post',))
    def click(self, request):
        """POST /api/v4/headless/analytics/track/search/click/

        Records a search result click for CTR and Search Success metrics.
        """
        search_query_id = request.data.get('search_query_id')
        search_session_id = request.data.get('search_session_id')
        document_id = int(request.data.get('document_id') or 0)
        click_position = request.data.get('click_position')
        time_to_click_seconds = request.data.get('time_to_click_seconds')

        if not document_id:
            return Response({'detail': 'document_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        query = None
        if search_query_id:
            try:
                query = SearchQuery.objects.filter(pk=int(search_query_id)).first()
            except Exception:
                query = None

        if not query and search_session_id:
            try:
                query = (
                    SearchQuery.objects.filter(
                        user=request.user,
                        search_session_id=search_session_id
                    )
                    .order_by('-timestamp')
                    .first()
                )
            except Exception:
                query = None

        if query and query.user_id and query.user_id != request.user.pk:
            return Response({'detail': 'not allowed'}, status=status.HTTP_403_FORBIDDEN)

        if query:
            try:
                query.was_clicked_result_document_id = document_id
                query.click_position = int(click_position) if click_position is not None else None
                query.time_to_click_seconds = int(time_to_click_seconds) if time_to_click_seconds is not None else None
                query.save(update_fields=('was_clicked_result_document_id', 'click_position', 'time_to_click_seconds'))
            except Exception:
                pass

        # Count click as a view event for "success-by-action" and downstream analytics.
        try:
            document = Document.valid.filter(pk=document_id).first()
            if document:
                track_asset_event(
                    document=document,
                    event_type=AssetEvent.EVENT_TYPE_VIEW,
                    user=request.user,
                    channel='dam_search',
                    metadata={
                        'search_query_id': int(search_query_id) if search_query_id else None,
                        'search_session_id': str(search_session_id) if search_session_id else None,
                        'click_position': int(click_position) if click_position is not None else None,
                    }
                )
        except Exception:
            pass

        return Response({'status': 'ok'}, status=status.HTTP_200_OK)


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

        # Best-effort region per user (last known geo_country).
        user_region_map = {}
        for row in UserSession.objects.filter(
            login_timestamp__gte=date_from
        ).order_by('-login_timestamp').values('user_id', 'geo_country'):
            user_id = row.get('user_id')
            if user_id in user_region_map:
                continue
            user_region_map[user_id] = (row.get('geo_country') or '').strip() or '—'

        buckets = {}
        heatmap_buckets = {}
        for user_id in user_ids:
            user = user_map.get(user_id)
            department = ''
            if user:
                department = getattr(user, 'department', '') or ''

            buckets.setdefault(department or '—', set()).add(user_id)

            region = user_region_map.get(user_id, '—')
            key = (department or '—', region or '—')
            heatmap_buckets[key] = heatmap_buckets.get(key, 0) + 1

        results = []
        for department, ids in buckets.items():
            results.append({'department': department, 'mau': len(ids)})

        results.sort(key=lambda x: x['mau'], reverse=True)

        departments = sorted({d for d, _ in heatmap_buckets.keys()})
        regions = sorted({r for _, r in heatmap_buckets.keys()})
        heatmap_data = [
            {'department': d, 'region': r, 'mau': count}
            for (d, r), count in heatmap_buckets.items()
        ]

        geo_data = list(
            UserSession.objects.filter(login_timestamp__gte=date_from)
            .exclude(geo_country='')
            .values('geo_country')
            .annotate(mau=Count('user_id', distinct=True))
            .order_by('-mau')
        )

        return Response(
            data={
                'results': results,  # backwards-compatible
                'heatmap_data': heatmap_data,
                'departments': departments,
                'regions': regions,
                'geo_data': geo_data,
            },
            status=status.HTTP_200_OK
        )

    @method_decorator(cache_page(600))
    @action(detail=False, methods=('get',))
    def login_patterns(self, request):
        """GET /api/v4/headless/analytics/dashboard/users/login-patterns/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_user_activity,), user=request.user
        )
        days = int(request.query_params.get('days') or 30)
        date_from_dt = timezone.now() - timedelta(days=days)

        # DAU series (daily distinct users).
        dau_rows = list(
            UserSession.objects.filter(login_timestamp__gte=date_from_dt)
            .annotate(day=TruncDate('login_timestamp'))
            .values('day')
            .annotate(active_users=Count('user_id', distinct=True))
            .order_by('day')
        )
        dau_series = [
            {'date': row['day'].date().isoformat() if row.get('day') else None, 'active_users': row['active_users']}
            for row in dau_rows
        ]

        # Login frequency buckets (by distinct active days per user).
        distinct_days = (
            UserSession.objects.filter(login_timestamp__gte=date_from_dt)
            .annotate(day=TruncDate('login_timestamp'))
            .values('user_id', 'day')
            .distinct()
        )
        per_user_days = {}
        for row in distinct_days:
            user_id = row.get('user_id')
            per_user_days[user_id] = per_user_days.get(user_id, 0) + 1

        buckets = {'daily': 0, 'weekly': 0, 'monthly': 0, 'rare': 0}
        for days_active in per_user_days.values():
            if days_active >= 20:
                buckets['daily'] += 1
            elif days_active >= 8:
                buckets['weekly'] += 1
            elif days_active >= 2:
                buckets['monthly'] += 1
            else:
                buckets['rare'] += 1

        return Response(
            data={
                'window_days': days,
                'dau_series': dau_series,
                'frequency_buckets': buckets,
                'unique_users': len(per_user_days),
            },
            status=status.HTTP_200_OK
        )

    @method_decorator(cache_page(3600))
    @action(detail=False, methods=('get',))
    def cohorts(self, request):
        """GET /api/v4/headless/analytics/dashboard/users/cohorts/

        Cohorts by first-login week, retention measured by weekly activity.
        """
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_user_activity,), user=request.user
        )
        cohort_weeks = int(request.query_params.get('cohort_weeks') or 8)
        retention_weeks = int(request.query_params.get('retention_weeks') or 8)

        now = timezone.now()
        start = now - timedelta(weeks=cohort_weeks + retention_weeks + 1)

        sessions = list(
            UserSession.objects.filter(login_timestamp__gte=start)
            .values('user_id', 'login_timestamp')
        )
        if not sessions:
            return Response({'cohorts': []}, status=status.HTTP_200_OK)

        def week_start(dt):
            # ISO week start (Monday).
            d = dt.date()
            return d - timedelta(days=d.weekday())

        first_week = {}
        active_weeks = {}
        for row in sessions:
            user_id = row['user_id']
            ts = row['login_timestamp']
            w = week_start(ts)
            if user_id not in first_week or w < first_week[user_id]:
                first_week[user_id] = w
            active_weeks.setdefault(user_id, set()).add(w)

        # Build cohort map: cohort_week -> users
        cohort_map = {}
        for user_id, w0 in first_week.items():
            cohort_map.setdefault(w0, set()).add(user_id)

        cohort_rows = []
        for cohort_week in sorted(cohort_map.keys(), reverse=True)[:cohort_weeks]:
            users = cohort_map[cohort_week]
            cohort_size = len(users)
            if not cohort_size:
                continue
            retention = []
            for i in range(retention_weeks):
                target_week = cohort_week + timedelta(weeks=i)
                active = 0
                for user_id in users:
                    if target_week in active_weeks.get(user_id, set()):
                        active += 1
                retention.append(
                    {
                        'week_index': i,
                        'week_start': target_week.isoformat(),
                        'active_users': active,
                        'retention_rate': round((active / cohort_size) * 100, 2) if cohort_size else 0.0,
                    }
                )

            cohort_rows.append(
                {
                    'cohort_week_start': cohort_week.isoformat(),
                    'cohort_size': cohort_size,
                    'retention': retention,
                }
            )

        return Response({'cohorts': cohort_rows}, status=status.HTTP_200_OK)

    @method_decorator(cache_page(600))
    @action(detail=False, methods=('get',))
    def feature_adoption(self, request):
        """GET /api/v4/headless/analytics/dashboard/users/feature-adoption/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_user_activity,), user=request.user
        )
        days = int(request.query_params.get('days') or 30)
        date_from = timezone.now() - timedelta(days=days)

        rows = FeatureUsage.objects.filter(
            timestamp__gte=date_from
        ).values('feature_name').annotate(
            total=Count('id'),
            unique_users=Count('user_id', distinct=True)
        ).order_by('-total')[:100]

        return Response(data={'results': list(rows)}, status=status.HTTP_200_OK)


class ApprovalAnalyticsViewSet(viewsets.ViewSet):
    """Headless API: Approval workflow analytics (Phase 2 / Level 3)."""

    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=('get',))
    def summary(self, request):
        """GET /api/v4/headless/analytics/dashboard/approvals/summary/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_user_activity,), user=request.user
        )
        days = int(request.query_params.get('days') or 30)
        date_from = timezone.now() - timedelta(days=days)

        qs = ApprovalWorkflowEvent.objects.filter(submitted_at__gte=date_from)

        approved_qs = qs.filter(status=ApprovalWorkflowEvent.STATUS_APPROVED, approval_time_days__isnull=False)
        rejected_qs = qs.filter(status=ApprovalWorkflowEvent.STATUS_REJECTED)

        approval_cycle_time_days = approved_qs.aggregate(avg=Avg('approval_time_days'))['avg']
        if approval_cycle_time_days is not None:
            approval_cycle_time_days = round(float(approval_cycle_time_days), 3)

        total_approved = approved_qs.count()
        first_time_right = approved_qs.filter(attempt_number=1).count()
        first_time_right_rate = None
        if total_approved:
            first_time_right_rate = round((first_time_right / total_approved) * 100, 2)

        rejection_reasons = list(
            rejected_qs.exclude(rejection_reason='').values('rejection_reason').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
        )

        return Response(
            data={
                'approval_cycle_time_days': approval_cycle_time_days,
                'first_time_right_rate': first_time_right_rate,
                'total_approved': total_approved,
                'total_rejected': rejected_qs.count(),
                'rejection_reasons': rejection_reasons,
            },
            status=status.HTTP_200_OK
        )


class DistributionAnalyticsViewSet(viewsets.ViewSet):
    """Headless API: Distribution analytics (Release 3 foundation)."""

    permission_classes = (IsAuthenticated,)

    @method_decorator(cache_page(600))
    @action(detail=False, methods=('get',))
    def dashboard(self, request):
        """GET /api/v4/headless/analytics/dashboard/distribution/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_distribution,), user=request.user
        )
        days = int(request.query_params.get('days') or 7)
        date_from = timezone.now() - timedelta(days=days)

        qs = DistributionEvent.objects.filter(occurred_at__gte=date_from)

        # Matrix: last status per channel.
        channels = list(qs.values_list('channel', flat=True).distinct())
        matrix = []
        for channel in channels:
            last = qs.filter(channel=channel).order_by('-occurred_at').first()
            if not last:
                continue
            issues = qs.filter(channel=channel, status=DistributionEvent.STATUS_ERROR).count()
            matrix.append(
                {
                    'channel': channel,
                    'status': last.status,
                    'last_sync': last.occurred_at,
                    'events': qs.filter(channel=channel).count(),
                    'issues': issues,
                }
            )

        # Conversion success rate (converted events).
        conv_qs = qs.filter(event_type=DistributionEvent.EVENT_TYPE_CONVERTED)
        conv_rows = list(
            conv_qs.values('channel').annotate(
                total=Count('id'),
                ok=Count('id', filter=Q(status=DistributionEvent.STATUS_OK)),
                error=Count('id', filter=Q(status=DistributionEvent.STATUS_ERROR)),
            ).order_by('-total')
        )
        conversion = []
        for row in conv_rows:
            total = int(row.get('total') or 0)
            ok = int(row.get('ok') or 0)
            conversion.append(
                {
                    'channel': row['channel'],
                    'success_rate': round((ok / total) * 100, 2) if total else None,
                    'total': total,
                    'failed': int(row.get('error') or 0),
                }
            )

        # CDN performance (delivered events, aggregated).
        cdn_qs = qs.filter(event_type=DistributionEvent.EVENT_TYPE_DELIVERED)
        cdn_rows = list(
            cdn_qs.values('channel').annotate(
                bandwidth_bytes=Sum('bandwidth_bytes'),
                avg_latency_ms=Avg('latency_ms'),
                events=Count('id'),
            ).order_by('-bandwidth_bytes')
        )
        cdn_perf = []
        for row in cdn_rows:
            bw = int(row.get('bandwidth_bytes') or 0)
            cdn_perf.append(
                {
                    'channel': row['channel'],
                    'bandwidth_gb': round(float(bw) / (1024 ** 3), 3) if bw else 0.0,
                    'avg_latency_ms': int(row['avg_latency_ms']) if row.get('avg_latency_ms') is not None else None,
                    'events': int(row.get('events') or 0),
                }
            )

        return Response(
            data={
                'window_days': days,
                'matrix': matrix,
                'conversion_success': conversion,
                'cdn_performance': cdn_perf,
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=('post',))
    def ingest(self, request):
        """POST /api/v4/headless/analytics/ingest/distribution-events/

        Generic ingestion endpoint for Website/CMS + CDN vendors (Release 3).
        """
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_distribution,), user=request.user
        )
        channel = (request.data.get('channel') or '').strip()
        events = request.data.get('events') or []
        if not channel:
            return Response({'detail': 'channel is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(events, list) or not events:
            return Response({'detail': 'events must be a non-empty list'}, status=status.HTTP_400_BAD_REQUEST)

        created = 0
        for ev in events[:1000]:
            try:
                occurred_at = ev.get('occurred_at') or ev.get('timestamp')
                if occurred_at:
                    occurred_at_dt = timezone.datetime.fromisoformat(str(occurred_at).replace('Z', '+00:00'))
                else:
                    occurred_at_dt = timezone.now()

                DistributionEvent.objects.create(
                    channel=channel,
                    event_type=ev.get('event_type') or DistributionEvent.EVENT_TYPE_SYNCED,
                    status=ev.get('status') or DistributionEvent.STATUS_OK,
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

        try:
            notify_analytics_refresh(reason='distribution_ingest')
        except Exception:
            pass

        return Response({'created': created}, status=status.HTTP_200_OK)


class ContentIntelligenceViewSet(viewsets.ViewSet):
    """Headless API: Content Intelligence MVP (Release 3 foundation)."""

    permission_classes = (IsAuthenticated,)

    @method_decorator(cache_page(600))
    @action(detail=False, methods=('get',))
    def content_gaps(self, request):
        """GET /api/v4/headless/analytics/dashboard/content-intel/content-gaps/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_content_intelligence,), user=request.user
        )
        days = int(request.query_params.get('days') or 30)
        date_from = timezone.now() - timedelta(days=days)

        qs = SearchQuery.objects.filter(timestamp__gte=date_from, results_count=0)
        rows = list(
            qs.values('query_text').annotate(count=Count('id')).order_by('-count')[:50]
        )
        recommendations = []
        for row in rows[:20]:
            q = row['query_text']
            recommendations.append(
                {
                    'query': q,
                    'count': int(row.get('count') or 0),
                    'recommendation': 'Проверьте taxonomy/синонимы и добавьте релевантные теги/metadata. Если контента нет — поставить задачу на производство.',
                }
            )

        return Response(
            data={'window_days': days, 'top_null_queries': rows, 'recommendations': recommendations},
            status=status.HTTP_200_OK
        )

    @method_decorator(cache_page(600))
    @action(detail=False, methods=('get',))
    def metadata_compliance(self, request):
        """GET /api/v4/headless/analytics/dashboard/content-intel/compliance/metadata/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_content_intelligence,), user=request.user
        )
        limit = int(request.query_params.get('limit') or 50)
        rows = list(
            AnalyticsAlert.objects.filter(alert_type='metadata_incomplete')
            .order_by('-created_at')[:limit]
            .values('id', 'severity', 'title', 'message', 'document_id', 'created_at', 'metadata')
        )
        return Response({'results': rows}, status=status.HTTP_200_OK)
    @method_decorator(cache_page(600))
    @action(detail=False, methods=('get',))
    def timeseries(self, request):
        """GET /api/v4/headless/analytics/dashboard/approvals/timeseries/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_user_activity,), user=request.user
        )
        days = int(request.query_params.get('days') or 90)
        date_from = timezone.now() - timedelta(days=days)

        qs = ApprovalWorkflowEvent.objects.filter(submitted_at__gte=date_from)

        rows = list(
            qs.annotate(day=TruncDate('submitted_at')).values('day').annotate(
                submitted=Count('id'),
                approved=Count('id', filter=Q(status=ApprovalWorkflowEvent.STATUS_APPROVED)),
                rejected=Count('id', filter=Q(status=ApprovalWorkflowEvent.STATUS_REJECTED)),
                first_time_right=Count(
                    'id',
                    filter=Q(status=ApprovalWorkflowEvent.STATUS_APPROVED, attempt_number=1)
                ),
                avg_cycle=Avg('approval_time_days', filter=Q(approval_time_days__isnull=False)),
            ).order_by('day')
        )

        out = []
        for row in rows:
            approved = int(row.get('approved') or 0)
            ftr = int(row.get('first_time_right') or 0)
            ftr_rate = round((ftr / approved) * 100, 2) if approved else None
            avg_cycle = row.get('avg_cycle')
            if avg_cycle is not None:
                avg_cycle = round(float(avg_cycle), 3)
            out.append(
                {
                    'date': row['day'].date().isoformat() if row.get('day') else None,
                    'submitted': int(row.get('submitted') or 0),
                    'approved': approved,
                    'rejected': int(row.get('rejected') or 0),
                    'first_time_right_rate': ftr_rate,
                    'approval_cycle_time_days': avg_cycle,
                }
            )

        return Response({'results': out}, status=status.HTTP_200_OK)

    @method_decorator(cache_page(600))
    @action(detail=False, methods=('get',))
    def recommendations(self, request):
        """GET /api/v4/headless/analytics/dashboard/approvals/recommendations/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_user_activity,), user=request.user
        )
        days = int(request.query_params.get('days') or 30)
        date_from = timezone.now() - timedelta(days=days)

        qs = ApprovalWorkflowEvent.objects.filter(submitted_at__gte=date_from)
        approved_qs = qs.filter(status=ApprovalWorkflowEvent.STATUS_APPROVED, approval_time_days__isnull=False)
        rejected_qs = qs.filter(status=ApprovalWorkflowEvent.STATUS_REJECTED)

        avg_cycle = approved_qs.aggregate(avg=Avg('approval_time_days'))['avg']
        avg_cycle = round(float(avg_cycle), 3) if avg_cycle is not None else None

        total_approved = approved_qs.count()
        ftr = approved_qs.filter(attempt_number=1).count()
        ftr_rate = round((ftr / total_approved) * 100, 2) if total_approved else None

        top_reasons = list(
            rejected_qs.exclude(rejection_reason='').values('rejection_reason').annotate(
                count=Count('id')
            ).order_by('-count')[:5]
        )

        recs = []
        if avg_cycle is not None and avg_cycle > 2.5:
            recs.append(
                {
                    'type': 'cycle_time',
                    'severity': 'warning',
                    'title': 'Высокое среднее время согласования',
                    'message': f'Approval Cycle Time = {avg_cycle} дней. Рекомендуется добавить SLA по ролям, автоматизировать pre-checks и убрать ручные step-ы без ценности.',
                }
            )
        if ftr_rate is not None and ftr_rate < 70:
            recs.append(
                {
                    'type': 'first_time_right',
                    'severity': 'warning',
                    'title': 'Низкий First-Time-Right Approval Rate',
                    'message': f'FTR = {ftr_rate}%. Рекомендуется внедрить чеклист перед отправкой на согласование и шаблоны требований к ассетам (metadata, размеры, бренд).',
                }
            )

        for row in top_reasons:
            reason = row.get('rejection_reason') or ''
            count = int(row.get('count') or 0)
            msg = 'Добавьте гайдлайн/шаблон и автоматическую проверку перед отправкой.'
            low = reason.lower()
            if 'метад' in low or 'metadata' in low:
                msg = 'Включите обязательность полей metadata (schema), автозаполнение и подсказки. Добавьте alert “metadata completeness”.'
            elif 'логотип' in low or 'brand' in low:
                msg = 'Добавьте бренд-чеклист и (позже) CV compliance проверки; сейчас — минимум: metadata флаг “brand_reviewed”.'
            elif 'размер' in low or 'format' in low:
                msg = 'Добавьте пресеты каналов (target formats) и автоконвертацию; показывайте требования перед upload.'

            recs.append(
                {
                    'type': 'rejection_reason',
                    'severity': 'info',
                    'title': f'Топ причина отклонений: “{reason}”',
                    'message': f'{count} случаев за {days} дней. {msg}',
                    'metadata': {'reason': reason, 'count': count},
                }
            )

        return Response(
            data={
                'window_days': days,
                'approval_cycle_time_days': avg_cycle,
                'first_time_right_rate': ftr_rate,
                'top_rejection_reasons': top_reasons,
                'recommendations': recs,
            },
            status=status.HTTP_200_OK
        )


class ROIDashboardViewSet(viewsets.ViewSet):
    """Headless API: ROI dashboard (Phase 2 MVP)."""

    permission_classes = (IsAuthenticated,)

    @method_decorator(cache_page(3600))
    @action(detail=False, methods=('get',))
    def summary(self, request):
        """GET /api/v4/headless/analytics/dashboard/roi/summary/"""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_asset_bank,), user=request.user
        )

        # Inputs / assumptions (Phase 2: settings-driven).
        baseline_search_minutes = float(getattr(settings, 'ANALYTICS_ROI_BASELINE_SEARCH_MINUTES', 30.0))
        target_search_minutes = float(getattr(settings, 'ANALYTICS_ROI_TARGET_SEARCH_MINUTES', 5.0))
        searches_per_user_per_day = float(getattr(settings, 'ANALYTICS_ROI_SEARCHES_PER_USER_PER_DAY', 3.0))
        working_days = int(getattr(settings, 'ANALYTICS_ROI_WORKING_DAYS_PER_MONTH', 21))
        hourly_rate_usd = float(getattr(settings, 'ANALYTICS_ROI_HOURLY_RATE_USD', 65.0))

        projects_per_month = float(getattr(settings, 'ANALYTICS_ROI_PROJECTS_PER_MONTH', 45.0))
        baseline_reuse_rate = float(getattr(settings, 'ANALYTICS_TARGET_REUSE_RATE_BASELINE', 40.0))
        savings_per_project_usd = float(getattr(settings, 'ANALYTICS_ROI_SAVINGS_PER_PROJECT_USD', 500.0))

        compliance_savings_usd = float(getattr(settings, 'ANALYTICS_ROI_COMPLIANCE_SAVINGS_USD', 12000.0))
        storage_savings_usd = float(getattr(settings, 'ANALYTICS_ROI_STORAGE_SAVINGS_USD', 3000.0))
        dam_monthly_cost_usd = float(getattr(settings, 'ANALYTICS_ROI_DAM_MONTHLY_COST_USD', 16167.0))

        # Measured: MAU and reuse rate (best-effort).
        last_30_days = timezone.now() - timedelta(days=30)
        mau = UserSession.objects.filter(login_timestamp__gte=last_30_days).values('user_id').distinct().count()

        # Reuse rate current (best-effort): documents in >=2 campaigns / total assets.
        total_assets = Document.valid.filter(in_trash=False).count()
        reused_assets = (
            CampaignAsset.objects.values('document_id')
            .annotate(campaigns=Count('campaign_id', distinct=True))
            .filter(campaigns__gte=2)
            .count()
        )
        reuse_rate = round((reused_assets / total_assets) * 100, 2) if total_assets else 0.0

        # 1) Time savings
        time_saved_minutes = max(0.0, baseline_search_minutes - target_search_minutes)
        time_saved_hours = (time_saved_minutes / 60.0) * float(mau) * searches_per_user_per_day * float(working_days)
        time_savings_usd = round(time_saved_hours * hourly_rate_usd, 2)

        # 2) Asset reuse savings (incremental vs baseline)
        incremental_reuse = max(0.0, reuse_rate - baseline_reuse_rate) / 100.0
        reuse_savings_usd = round(projects_per_month * incremental_reuse * savings_per_project_usd, 2)

        # 3) Compliance and storage savings (assumptions)
        compliance_savings_usd = round(compliance_savings_usd, 2)
        storage_savings_usd = round(storage_savings_usd, 2)

        total_benefits_usd = round(time_savings_usd + reuse_savings_usd + compliance_savings_usd + storage_savings_usd, 2)
        roi_percent = None
        if dam_monthly_cost_usd:
            roi_percent = round(((total_benefits_usd - dam_monthly_cost_usd) / dam_monthly_cost_usd) * 100, 2)

        return Response(
            data={
                'assumptions': {
                    'baseline_search_minutes': baseline_search_minutes,
                    'target_search_minutes': target_search_minutes,
                    'searches_per_user_per_day': searches_per_user_per_day,
                    'working_days': working_days,
                    'hourly_rate_usd': hourly_rate_usd,
                    'projects_per_month': projects_per_month,
                    'baseline_reuse_rate': baseline_reuse_rate,
                    'savings_per_project_usd': savings_per_project_usd,
                    'dam_monthly_cost_usd': dam_monthly_cost_usd,
                },
                'measured': {
                    'mau': mau,
                    'reuse_rate': reuse_rate,
                },
                'breakdown': {
                    'time_savings_usd': time_savings_usd,
                    'reuse_savings_usd': reuse_savings_usd,
                    'compliance_savings_usd': compliance_savings_usd,
                    'storage_savings_usd': storage_savings_usd,
                },
                'total_benefits_usd': total_benefits_usd,
                'dam_monthly_cost_usd': dam_monthly_cost_usd,
                'roi_percent': roi_percent,
            },
            status=status.HTTP_200_OK
        )

