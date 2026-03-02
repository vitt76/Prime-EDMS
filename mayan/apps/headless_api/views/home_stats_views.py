"""
Home page statistics views for Headless API.

Provides endpoints for documents and AI stats scoped by tenant (organization).
"""

from datetime import timedelta
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mayan.apps.documents.models import Document
from mayan.apps.dam.models import DocumentAIAnalysis
from mayan.apps.headless_api.views.notification_views import _get_unread_counters


class HeadlessHomeInboxStatsView(APIView):
    """
    Return inbox stats for the current user.

    Endpoint:
        GET /api/v4/headless/user/inbox-stats/
    """
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        counters = _get_unread_counters(request.user)
        unread = counters.get('unread_count', 0)
        
        return Response({
            'unread_total': unread,
            'comments_new': 0,
            'approvals_pending': 0,
            'collections_shared': 0,
            'mentions': 0,
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
        if not hasattr(request, 'organization') or not request.organization:
            return Response(
                {'error': 'Organization required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        now = timezone.now()
        start_7_days = now - timedelta(days=7)
        start_30_days = now - timedelta(days=30)

        # Base queryset scoped by organization
        qs = Document.valid.filter(organization=request.organization)

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
        if not hasattr(request, 'organization') or not request.organization:
            return Response(
                {'error': 'Organization required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # We query DocumentAIAnalysis directly or through documents
        qs = DocumentAIAnalysis.objects.filter(organization=request.organization, document__in_trash=False)

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
        if not hasattr(request, 'organization') or not request.organization:
            return Response(
                {'error': 'Organization required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        org = request.organization
        used_bytes = org.get_storage_used_bytes() if hasattr(org, 'get_storage_used_bytes') else 0
        limit_gb = org.storage_limit_gb if hasattr(org, 'storage_limit_gb') else 0
        limit_bytes = limit_gb * 1024 * 1024 * 1024 if limit_gb else 0
        
        # Calculate percentage
        percentage = 0
        if limit_bytes > 0:
            percentage = round((used_bytes / limit_bytes) * 100, 1)

        return Response({
            'used_bytes': used_bytes,
            'limit_bytes': limit_bytes,
            'percentage': percentage
        })

class HeadlessHomeDailyInsightsView(APIView):
    """
    Return daily AI insights (synchronous generation with caching).

    Endpoint:
        GET /api/v4/headless/user/daily-insights/
    """
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Cache for 4 hours
    @method_decorator(cache_page(60 * 60 * 4))
    def get(self, request):
        if not hasattr(request, 'organization') or not request.organization:
            return Response(
                {'error': 'Organization required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        org = request.organization
        now = timezone.now()
        start_7_days = now - timedelta(days=7)
        insights = []

        # Insight 1: Untagged Assets (recently uploaded)
        # Assuming AI analysis missing or ai_tags empty
        untagged_count = Document.valid.filter(
            organization=org,
            datetime_created__gte=start_7_days
        ).exclude(
            ai_analysis__ai_tags__isnull=False
        ).count()

        if untagged_count > 0:
            insights.append({
                'type': 'auto_tag_missing',
                'count': untagged_count,
                'cta_label': 'Запустить AI',
                'emoji': '🏷️',
                'message': f'{untagged_count} активов без тегов'
            })

        # Future insights can be added here (e.g. duplicates, unused)

        return Response(insights)
    """
    Return AI analysis status counts for the current user's organization.

    Endpoint:
        GET /api/v4/headless/documents/ai-stats/
    """
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request, 'organization') or not request.organization:
            return Response(
                {'error': 'Organization required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # We query DocumentAIAnalysis directly or through documents
        qs = DocumentAIAnalysis.objects.filter(organization=request.organization, document__in_trash=False)

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
