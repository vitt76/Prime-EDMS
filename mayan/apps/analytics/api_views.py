"""API views for analytics (tenant-scoped dashboard and report generation)."""

import os
from datetime import timedelta

from django.db.models import Avg, Count
from django.http import Http404, HttpResponse
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mayan.apps.permissions.classes import Permission
from mayan.apps.documents.models import Document
from mayan.apps.organizations.models import Organization

from .dashboard_cache import (
    get_dashboard_cached, set_dashboard_cached,
)
from .literals import FEATURE_ADOPTION_NAMES
from .models import AssetEvent, AnalyticsReportTask, FeatureUsage, SearchSession
from .operational import get_operational_snapshot
from .permissions import permission_analytics_view_asset_bank
from .serializers import DashboardMetricsSerializer
from .tasks import generate_analytics_report


class AnalyticsDashboardViewSet(viewsets.ViewSet):
    """Single endpoint: tenant-scoped dashboard metrics (GET list = dashboard)."""

    permission_classes = (IsAuthenticated,)

    def list(self, request):
        """GET /api/v4/headless/analytics/dashboard/ — metrics for current organization."""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_asset_bank,), user=request.user
        )
        organization = getattr(request, 'organization', None)
        if not organization:
            return Response(
                {'detail': 'Organization context required (e.g. X-Organization-Id).'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            org = Organization.objects.get(pk=organization.pk)
        except Organization.DoesNotExist:
            return Response(
                {'detail': 'Organization not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        data = get_dashboard_cached(org.pk)
        if data is not None:
            return Response(data, status=status.HTTP_200_OK)

        total_documents = Document.valid.filter(
            organization=org, in_trash=False
        ).count()
        storage_used_gb = org.get_storage_used_gb()
        thirty_days_ago = timezone.now() - timedelta(days=30)
        active_users_30d = AssetEvent.objects.filter(
            organization=org,
            timestamp__gte=thirty_days_ago,
            user_id__isnull=False
        ).values('user_id').distinct().count()

        top_documents = list(
            AssetEvent.objects.filter(
                organization=org,
                event_type=AssetEvent.EVENT_TYPE_VIEW,
                timestamp__gte=thirty_days_ago
            ).values('document_id').annotate(
                view_count=Count('id')
            ).order_by('-view_count')[:5]
        )

        ai_count = org.get_ai_analyses_this_month()
        ai_usage = {
            'count_this_month': ai_count,
            'token_usage': getattr(org, 'ai_token_usage_this_month', None),
        }

        search_sessions_qs = SearchSession.objects.filter(
            organization=org,
            started_at__gte=thirty_days_ago,
            time_to_find_seconds__isnull=False
        )
        avg_stf = search_sessions_qs.aggregate(avg=Avg('time_to_find_seconds'))['avg']
        avg_search_to_find_seconds = int(avg_stf) if avg_stf is not None else None

        feature_adoption = []
        for feat_name in FEATURE_ADOPTION_NAMES:
            users_with_feature = FeatureUsage.objects.filter(
                organization=org,
                feature_name=feat_name,
                timestamp__gte=thirty_days_ago,
            ).values('user_id').distinct().count()
            rate = (users_with_feature / active_users_30d * 100) if active_users_30d else 0
            feature_adoption.append({
                'feature_name': feat_name,
                'users_count': users_with_feature,
                'adoption_rate_percent': round(rate, 2),
            })

        churn_count = 0
        churn_period_days = 30
        try:
            from django.apps import apps as django_apps
            events_org = AssetEvent.objects.filter(organization=org, user_id__isnull=False)
            active_user_ids = set(
                events_org.filter(timestamp__gte=thirty_days_ago)
                .values_list('user_id', flat=True)
                .distinct()
            )
            UserOrganizationRole = django_apps.get_model('organizations', 'UserOrganizationRole')
            org_member_ids = set(
                UserOrganizationRole.objects.filter(organization=org)
                .values_list('user_id', flat=True)
                .distinct()
            )
            churn_count = len(org_member_ids - active_user_ids)
        except Exception:
            pass

        data = {
            'organization': str(org.pk),
            'organization_name': org.name,
            'total_documents': total_documents,
            'storage_used_gb': storage_used_gb,
            'active_users_30d': active_users_30d,
            'top_documents': top_documents,
            'ai_usage': ai_usage,
            'avg_search_to_find_seconds': avg_search_to_find_seconds,
            'feature_adoption': feature_adoption,
            'churn_count': churn_count,
            'churn_period_days': churn_period_days,
        }
        set_dashboard_cached(org.pk, data)
        serializer = DashboardMetricsSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnalyticsReportGenerateViewSet(viewsets.ViewSet):
    """POST generate report (async); GET status by task id."""

    permission_classes = (IsAuthenticated,)

    def create(self, request):
        """POST /api/v4/headless/analytics/reports/generate/ — enqueue report generation."""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_asset_bank,), user=request.user
        )
        organization = getattr(request, 'organization', None)
        if not organization:
            return Response(
                {'detail': 'Organization context required (e.g. X-Organization-Id).'},
                status=status.HTTP_400_BAD_REQUEST
            )
        report_type = request.data.get('report_type') or AnalyticsReportTask.REPORT_TYPE_ASSET_USAGE
        date_range = request.data.get('date_range') or {}
        export_format = request.data.get('export_format') or 'json'

        report_task = AnalyticsReportTask.objects.create(
            organization=organization,
            user=request.user,
            report_type=report_type,
            parameters={'date_range': date_range, 'export_format': export_format},
            status=AnalyticsReportTask.STATUS_PENDING,
        )
        generate_analytics_report.delay(
            report_task.pk,
            organization_id=str(organization.pk),
        )
        return Response(
            {'task_id': report_task.pk, 'status': 'processing'},
            status=status.HTTP_202_ACCEPTED,
        )

    def retrieve(self, request, pk=None):
        """GET /api/v4/headless/analytics/reports/{id}/ — report task status."""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_asset_bank,), user=request.user
        )
        organization = getattr(request, 'organization', None)
        if not organization:
            return Response(
                {'detail': 'Organization context required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            task = AnalyticsReportTask.objects.get(pk=pk, organization=organization)
        except AnalyticsReportTask.DoesNotExist:
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response({
            'task_id': task.pk,
            'status': task.status,
            'file_path': task.file_path,
            'created_at': task.created_at,
            'completed_at': task.completed_at,
        })

    def download(self, request, pk=None):
        """GET /api/v4/headless/analytics/reports/{id}/download/ — serve report file."""
        Permission.check_user_permissions(
            permissions=(permission_analytics_view_asset_bank,), user=request.user
        )
        organization = getattr(request, 'organization', None)
        if not organization:
            return Response(
                {'detail': 'Organization context required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            task = AnalyticsReportTask.objects.get(pk=pk, organization=organization)
        except AnalyticsReportTask.DoesNotExist:
            raise Http404('Report not found')
        if task.status != AnalyticsReportTask.STATUS_COMPLETED or not task.file_path:
            return Response(
                {'detail': 'Report is not ready for download.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        path = task.file_path
        if not os.path.isabs(path):
            from django.conf import settings
            media_root = getattr(settings, 'MEDIA_ROOT', '') or ''
            path = os.path.join(media_root, path)
        if not os.path.isfile(path):
            return Response(
                {'detail': 'Report file not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        filename = os.path.basename(path) or f'report-{task.pk}.json'
        with open(path, 'rb') as fh:
            content = fh.read()
        response = HttpResponse(content, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class EmailClickWebhookView(APIView):
    """Webhook for external email tracking (e.g. Mailchimp click events)."""
    permission_classes = (AllowAny,)

    def post(self, request):
        return Response({'status': 'received'}, status=status.HTTP_200_OK)


class AnalyticsEventsExportView(APIView):
    """Export analytics events (filtered by date range, event type)."""
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(
            {'detail': 'Export not implemented'},
            status=status.HTTP_501_NOT_IMPLEMENTED
        )


class AnalyticsHealthCheckView(APIView):
    """Health check for analytics module."""
    permission_classes = (AllowAny,)

    def get(self, request):
        snapshot = get_operational_snapshot()

        has_recent_failure = bool(snapshot['tasks'].get('last_failure'))
        stale_reports = int(snapshot['reports'].get('stale_pending') or 0)
        stream_length = snapshot['stream'].get('length')
        broker_reachable = snapshot.get('broker', {}).get('reachable')
        worker_count = snapshot.get('broker', {}).get('worker_count')

        status_label = 'ok'
        http_status = status.HTTP_200_OK

        if has_recent_failure or stale_reports > 0 or broker_reachable is False:
            status_label = 'degraded'
            http_status = status.HTTP_200_OK

        if broker_reachable and worker_count == 0:
            status_label = 'degraded'

        if stream_length is None:
            status_label = 'unknown'

        return Response(
            {
                'status': status_label,
                'snapshot': snapshot,
            },
            status=http_status
        )
