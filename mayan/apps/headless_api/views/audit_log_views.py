"""Sprint 5.2: Audit log API — list and export AssetEvent for compliance."""

import csv
import io
import logging
from datetime import datetime

from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

# Max rows for export (avoid heavy load)
AUDIT_LOG_EXPORT_MAX_ROWS = 50000
AUDIT_LOG_EXPORT_MAX_DAYS = 365


def _can_view_audit_log(user) -> bool:
    """Allow staff, superuser, or users in group 'audit_viewer'."""
    if getattr(user, 'is_superuser', False) or getattr(user, 'is_staff', False):
        return True
    try:
        group_names = {name.lower() for name in user.groups.values_list('name', flat=True)}
    except Exception:
        group_names = set()
    return 'audit_viewer' in group_names


def _filter_audit_queryset(queryset, request):
    """Apply query params: user_id, date_from, date_to, action (event_type)."""
    user_id = request.query_params.get('user_id')
    if user_id:
        queryset = queryset.filter(user_id=user_id)
    date_from = request.query_params.get('date_from')
    if date_from:
        try:
            dt = timezone.make_aware(datetime.strptime(date_from[:10], '%Y-%m-%d'))
            queryset = queryset.filter(timestamp__gte=dt)
        except ValueError:
            pass
    date_to = request.query_params.get('date_to')
    if date_to:
        try:
            dt = timezone.make_aware(datetime.strptime(date_to[:10], '%Y-%m-%d'))
            # end of day
            dt = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            queryset = queryset.filter(timestamp__lte=dt)
        except ValueError:
            pass
    action = request.query_params.get('action') or request.query_params.get('event_type')
    if action:
        queryset = queryset.filter(event_type=action)
    return queryset


def _serialize_audit_event(event):
    """One audit log row as dict."""
    return {
        'id': event.pk,
        'timestamp': event.timestamp.isoformat() if event.timestamp else None,
        'user_id': event.user_id,
        'username': getattr(event.user, 'username', None) if event.user_id else None,
        'event_type': event.event_type,
        'document_id': event.document_id,
        'channel': event.channel or '',
        'metadata': event.metadata or {},
    }


class AuditLogListView(APIView):
    """GET /api/v4/headless/audit-logs/

    List audit log entries (AssetEvent) for the current organization.
    Query params: user_id, date_from, date_to, action (event_type), page, page_size.
    Permission: staff/superuser or group 'audit_viewer'.
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _can_view_audit_log(request.user):
            return Response({'error': 'forbidden'}, status=status.HTTP_403_FORBIDDEN)

        organization = getattr(request, 'organization', None)
        if not organization:
            return Response({'error': 'organization_required'}, status=status.HTTP_400_BAD_REQUEST)

        from mayan.apps.analytics.models import AssetEvent

        qs = AssetEvent.objects.filter(organization=organization).select_related(
            'user', 'document'
        ).order_by('-timestamp')
        qs = _filter_audit_queryset(qs, request)

        page = max(1, int(request.query_params.get('page', 1)))
        page_size = min(max(1, int(request.query_params.get('page_size', 20))), 100)

        from django.core.paginator import Paginator
        paginator = Paginator(qs, page_size)
        try:
            page_obj = paginator.page(page)
        except Exception:
            page_obj = paginator.page(1)

        results = [_serialize_audit_event(e) for e in page_obj.object_list]
        return Response({
            'count': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'results': results,
        })


class AuditLogExportView(APIView):
    """GET /api/v4/headless/audit-logs/export/?format=csv|json&date_from=&date_to=

    Export audit log for current organization. Limit rows and date range.
    Permission: staff/superuser or group 'audit_viewer'.
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _can_view_audit_log(request.user):
            return Response({'error': 'forbidden'}, status=status.HTTP_403_FORBIDDEN)

        organization = getattr(request, 'organization', None)
        if not organization:
            return Response({'error': 'organization_required'}, status=status.HTTP_400_BAD_REQUEST)

        fmt = (request.query_params.get('format') or 'json').lower()
        if fmt not in ('csv', 'json'):
            return Response({'error': 'format must be csv or json'}, status=status.HTTP_400_BAD_REQUEST)

        from mayan.apps.analytics.models import AssetEvent

        qs = AssetEvent.objects.filter(organization=organization).select_related(
            'user', 'document'
        ).order_by('-timestamp')
        qs = _filter_audit_queryset(qs, request)

        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        if date_from:
            try:
                dt = timezone.make_aware(datetime.strptime(date_from[:10], '%Y-%m-%d'))
                qs = qs.filter(timestamp__gte=dt)
            except ValueError:
                pass
        if date_to:
            try:
                dt = timezone.make_aware(datetime.strptime(date_to[:10], '%Y-%m-%d'))
                dt = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
                qs = qs.filter(timestamp__lte=dt)
            except ValueError:
                pass

        # Limit rows and optional max days
        qs = qs[:AUDIT_LOG_EXPORT_MAX_ROWS]
        rows = [_serialize_audit_event(e) for e in qs]

        if fmt == 'csv':
            buf = io.StringIO()
            if not rows:
                writer = csv.writer(buf)
                writer.writerow([
                    'id', 'timestamp', 'user_id', 'username', 'event_type',
                    'document_id', 'channel', 'ip_address', 'user_agent'
                ])
            else:
                writer = csv.DictWriter(
                    buf,
                    fieldnames=[
                        'id', 'timestamp', 'user_id', 'username', 'event_type',
                        'document_id', 'channel', 'ip_address', 'user_agent'
                    ],
                    extrasaction='ignore'
                )
                writer.writeheader()
                for r in rows:
                    meta = r.get('metadata') or {}
                    r['ip_address'] = meta.get('ip_address', '')
                    r['user_agent'] = meta.get('user_agent', '')
                    writer.writerow(r)
            return Response(
                buf.getvalue(),
                content_type='text/csv',
                headers={
                    'Content-Disposition': 'attachment; filename="audit-log.csv"'
                }
            )
        return Response({'count': len(rows), 'results': rows})


class DocumentActivityListView(APIView):
    """GET /api/v4/headless/documents/{document_id}/activity/

    List AssetEvent entries for a single document (current organization).
    Used by the Asset detail page "Activity" tab.
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, document_id):
        organization = getattr(request, 'organization', None)
        if not organization:
            return Response({'error': 'organization_required'}, status=status.HTTP_400_BAD_REQUEST)

        from mayan.apps.analytics.models import AssetEvent
        from mayan.apps.documents.models import Document
        from mayan.apps.acls.models import AccessControlList
        from mayan.apps.documents.permissions import permission_document_view

        try:
            doc_id = int(document_id)
        except (ValueError, TypeError):
            return Response({'error': 'invalid_document_id'}, status=status.HTTP_400_BAD_REQUEST)

        document = Document.objects.filter(pk=doc_id).first()
        if not document:
            return Response({'error': 'not_found'}, status=status.HTTP_404_NOT_FOUND)
        if getattr(document, 'organization_id', None) is not None and document.organization_id != organization.pk:
            return Response({'error': 'not_found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            AccessControlList.objects.check_access(
                obj=document, permissions=(permission_document_view,), user=request.user
            )
        except Exception:
            return Response({'error': 'forbidden'}, status=status.HTTP_403_FORBIDDEN)

        qs = AssetEvent.objects.filter(
            organization=organization, document_id=doc_id
        ).select_related('user').order_by('-timestamp')[:200]
        results = [_serialize_audit_event(e) for e in qs]
        return Response({'count': len(results), 'results': results})
