"""API views for analytics (tenant-scoped dashboard and report generation)."""

from datetime import timedelta

from django.db.models import Count
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from mayan.apps.acls.classes import Permission
from mayan.apps.documents.models import Document
from mayan.apps.organizations.models import Organization

from .models import AssetEvent, AnalyticsReportTask
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

        data = {
            'organization': str(org.pk),
            'organization_name': org.name,
            'total_documents': total_documents,
            'storage_used_gb': storage_used_gb,
            'active_users_30d': active_users_30d,
            'top_documents': top_documents,
            'ai_usage': ai_usage,
        }
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
