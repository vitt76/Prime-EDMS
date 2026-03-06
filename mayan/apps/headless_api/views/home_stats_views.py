"""
Home page statistics views for Headless API.

Provides tenant-safe home widgets backed by real organization data.
"""

from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mayan.apps.analytics.models import ApprovalWorkflowEvent
from mayan.apps.cabinets.models import CabinetUserShare
from mayan.apps.dam.models import DocumentAIAnalysis
from mayan.apps.document_comments.models import Comment
from mayan.apps.documents.models import Document
from mayan.apps.headless_api.views.notification_views import _get_unread_counters


def _get_request_organization(request):
    """Return organization from request or None if tenant context is missing."""
    return getattr(request, 'organization', None)


def _organization_required_response():
    return Response(
        {'error': 'Organization required'},
        status=status.HTTP_400_BAD_REQUEST
    )


class HeadlessHomeInboxStatsView(APIView):
    """
    Return inbox stats for the current user.

    Endpoint:
        GET /api/v4/headless/user/inbox-stats/
    """
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organization = _get_request_organization(request)
        if not organization:
            return _organization_required_response()

        counters = _get_unread_counters(request.user)
        unread = counters.get('unread_count', 0)

        now = timezone.now()
        recent_window_start = now - timedelta(days=7)

        comments_new = Comment.objects.filter(
            document__organization=organization,
            submit_date__gte=recent_window_start
        ).exclude(user=request.user).count()

        approvals_pending = ApprovalWorkflowEvent.objects.filter(
            document__organization=organization,
            status=ApprovalWorkflowEvent.STATUS_PENDING
        ).count()

        collections_shared = CabinetUserShare.objects.filter(
            organization=organization,
            user=request.user
        ).count()

        return Response({
            'unread_total': unread,
            'comments_new': comments_new,
            'approvals_pending': approvals_pending,
            'collections_shared': collections_shared,
            'mentions': None,
            'mentions_supported': False,
        })


class HeadlessHomeDocumentsStatsView(APIView):
    """
    Return basic document counts for the current user's organization.

    Endpoint:
        GET /api/v4/headless/documents/stats/
    """
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organization = _get_request_organization(request)
        if not organization:
            return _organization_required_response()

        now = timezone.now()
        start_7_days = now - timedelta(days=7)
        start_30_days = now - timedelta(days=30)

        # Base queryset scoped by organization
        qs = Document.valid.filter(organization=organization)

        total = qs.count()
        new_7days = qs.filter(datetime_created__gte=start_7_days).count()
        new_30days = qs.filter(datetime_created__gte=start_30_days).count()

        return Response({
            'total': total,
            'new_7days': new_7days,
            'new_30days': new_30days,
        })


class HeadlessHomeAIStatsView(APIView):
    """
    Return AI analysis status counts for the current user's organization.

    Endpoint:
        GET /api/v4/headless/documents/ai-stats/
    """
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organization = _get_request_organization(request)
        if not organization:
            return _organization_required_response()

        # We query DocumentAIAnalysis directly or through documents
        qs = DocumentAIAnalysis.objects.filter(
            organization=organization,
            document__in_trash=False
        )

        analyzed = qs.filter(analysis_status='completed').count()
        pending = qs.filter(analysis_status='pending').count()
        queued = qs.filter(analysis_status='queued').count()
        processing = qs.filter(analysis_status='processing').count()
        failed = qs.filter(analysis_status='failed').count()

        return Response({
            'analyzed': analyzed,
            'queued': queued + processing,
            'pending': pending,
            'failed': failed,
        })


class HeadlessHomeStorageStatsView(APIView):
    """
    Return basic storage metrics for the current user's organization.

    Endpoint:
        GET /api/v4/headless/organization/storage-stats/
    """
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organization = _get_request_organization(request)
        if not organization:
            return _organization_required_response()

        org = organization
        used_gb = org.get_storage_used_gb() if hasattr(org, 'get_storage_used_gb') else 0
        used_bytes = int(used_gb * 1024 * 1024 * 1024)

        limit_gb = org.storage_limit_gb if hasattr(org, 'storage_limit_gb') else 0
        limit_bytes = int(limit_gb * 1024 * 1024 * 1024) if limit_gb else None

        percentage = None
        if limit_bytes and limit_bytes > 0:
            percentage = round((used_bytes / limit_bytes) * 100, 1)

        return Response({
            'used_bytes': used_bytes,
            'limit_bytes': limit_bytes,
            'percentage': percentage,
            'is_unlimited': limit_bytes is None
        })

class HeadlessHomeDailyInsightsView(APIView):
    """
    Return daily AI insights (synchronous generation with caching).

    Endpoint:
        GET /api/v4/headless/user/daily-insights/
    """
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organization = _get_request_organization(request)
        if not organization:
            return _organization_required_response()

        org = organization
        now = timezone.now()
        start_7_days = now - timedelta(days=7)
        insights = []

        recent_documents = Document.valid.filter(
            organization=org,
            datetime_created__gte=start_7_days
        )

        # Recent assets without successful AI enrichment.
        untagged_count = recent_documents.filter(
            Q(ai_analysis__isnull=True) |
            Q(ai_analysis__analysis_status__in=['pending', 'queued', 'processing', 'failed']) |
            Q(ai_analysis__ai_tags__isnull=True)
        ).distinct().count()

        if untagged_count > 0:
            insights.append({
                'type': 'auto_tag_missing',
                'count': untagged_count,
                'cta_label': 'Запустить AI',
                'emoji': '🏷️',
                'message': f'{untagged_count} активов без тегов'
            })

        failed_ai_count = DocumentAIAnalysis.objects.filter(
            organization=org,
            document__in_trash=False,
            analysis_status='failed'
        ).count()

        if failed_ai_count > 0:
            insights.append({
                'type': 'ai_failed',
                'count': failed_ai_count,
                'cta_label': 'Проверить активы',
                'emoji': '⚠️',
                'message': f'{failed_ai_count} AI-анализов завершились ошибкой'
            })

        return Response(insights)
