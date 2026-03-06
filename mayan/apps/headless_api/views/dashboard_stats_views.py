"""
Dashboard statistics views for Headless API.

Provides a SPA-friendly endpoint to compute simple time-based metrics (counts and growth)
without requiring the frontend to guess filter parameters for the core REST API.
"""

import os
from datetime import timedelta

from django.db.models import BigIntegerField, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mayan.apps.documents.models import Document
from mayan.apps.documents.models.document_file_models import DocumentFile
from mayan.apps.organizations.models import UserOrganizationRole


class HeadlessDashboardStatsView(APIView):
    """
    Return aggregated dashboard metrics for admin UI.

    Endpoint:
        GET /api/v4/headless/dashboard/stats/

    Notes:
    - Uses the last 30 days vs previous 30 days windows.
    - Restricts access to staff/superusers.
    - Counts use Document.objects.all() to include all documents (including trashed) for admin overview.
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not (getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False)):
            return Response(
                {'error': 'access_denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        organization = getattr(request, 'organization', None)
        if not organization:
            return Response(
                {'error': 'organization_required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        now = timezone.now()
        window = timedelta(days=30)
        start_current = now - window
        start_prev = now - (window * 2)

        # Documents
        documents_qs = Document.valid.filter(organization=organization)
        documents_total = documents_qs.count()
        documents_last_30 = documents_qs.filter(datetime_created__gte=start_current).count()
        documents_prev_30 = documents_qs.filter(
            datetime_created__gte=start_prev,
            datetime_created__lt=start_current
        ).count()

        documents_growth_percent = None
        documents_growth_label = '0%'
        if documents_prev_30 == 0:
            if documents_last_30 > 0:
                documents_growth_label = '+∞%'
        else:
            documents_growth_percent = ((documents_last_30 - documents_prev_30) / documents_prev_30) * 100.0
            sign = '+' if documents_growth_percent >= 0 else ''
            documents_growth_label = f'{sign}{documents_growth_percent:.0f}%'

        # Users
        users_total = organization.members.count()
        users_active_total = organization.members.filter(is_active=True).count()
        user_roles_qs = UserOrganizationRole.objects.filter(organization=organization)
        users_last_30 = user_roles_qs.filter(joined_at__gte=start_current).count()
        users_prev_30 = user_roles_qs.filter(
            joined_at__gte=start_prev,
            joined_at__lt=start_current
        ).count()

        users_growth_percent = None
        users_growth_label = '0%'
        if users_prev_30 == 0:
            if users_last_30 > 0:
                users_growth_label = '+∞%'
        else:
            users_growth_percent = ((users_last_30 - users_prev_30) / users_prev_30) * 100.0
            sign = '+' if users_growth_percent >= 0 else ''
            users_growth_label = f'{sign}{users_growth_percent:.0f}%'

        # Storage (bytes)
        storage_used_bytes = DocumentFile.valid.filter(
            document__organization=organization
        ).aggregate(
            total=Coalesce(Sum('size', output_field=BigIntegerField()), 0)
        )['total'] or 0

        unknown_size_files_count = DocumentFile.valid.filter(
            document__organization=organization,
            size__isnull=True
        ).count()

        storage_total_bytes = 0
        limit_gb = getattr(organization, 'storage_limit_gb', None)
        if limit_gb:
            storage_total_bytes = int(limit_gb * 1024 * 1024 * 1024)
        else:
            raw_total = os.environ.get('MADDAM_STORAGE_TOTAL_BYTES', '')
            try:
                if raw_total:
                    storage_total_bytes = int(raw_total)
            except Exception:
                storage_total_bytes = 0

        return Response(
            {
                'generated_at': now.isoformat(),
                'window_days': 30,
                'documents': {
                    'total': documents_total,
                    'last_30_days': documents_last_30,
                    'prev_30_days': documents_prev_30,
                    'growth_percent': documents_growth_percent,
                    'growth_label': documents_growth_label,
                },
                'users': {
                    'total': users_total,
                    'active_total': users_active_total,
                    'last_30_days': users_last_30,
                    'prev_30_days': users_prev_30,
                    'growth_percent': users_growth_percent,
                    'growth_label': users_growth_label,
                },
                'storage': {
                    'used_bytes': storage_used_bytes,
                    'total_bytes': storage_total_bytes,
                    'unknown_size_files': unknown_size_files_count,
                },
            }
        )


