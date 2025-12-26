"""Headless API views for Notification Center.

Implements `/api/v4/headless/notifications/*` endpoints as SPA-friendly REST APIs.
"""

import logging

from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from mayan.apps.events.models import Notification as EventNotification

from mayan.apps.notifications.models import NotificationPreference
from mayan.apps.notifications.serializers import (
    NotificationListSerializer, NotificationPreferenceSerializer, NotificationSerializer
)

logger = logging.getLogger(__name__)

_UNREAD_CACHE_TTL_SECONDS = 300


def _get_unread_cache_key(user_id: int) -> str:
    return f'notif_unread_count_v1_u{user_id}'


def _invalidate_unread_cache(user_id: int) -> None:
    try:
        cache.delete(_get_unread_cache_key(user_id=user_id))
    except Exception:
        # Cache is best-effort; never fail the request due to cache backend issues.
        pass


def _get_unread_counters(user) -> dict:
    """Return unread counters with Redis caching (Phase 7)."""

    if not getattr(user, 'is_authenticated', False):
        return {'unread_count': 0, 'has_urgent': False, 'urgent_count': 0}

    cache_key = _get_unread_cache_key(user_id=user.pk)
    try:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
    except Exception:
        cached = None

    if hasattr(EventNotification, 'state'):
        # Count both CREATED and SENT as unread:
        # - CREATED: just created, may still be pending the Celery delivery task
        # - SENT: delivered (email/WebSocket), still unread until READ
        # Enterprise note: `create_enhanced_notification()` has a fallback that marks
        # notifications as SENT synchronously if Celery is unavailable.
        unread_count = EventNotification.objects.filter(user=user, state__in=['CREATED', 'SENT']).count()
        urgent_count = EventNotification.objects.filter(user=user, state__in=['CREATED', 'SENT'], priority='URGENT').count()
    else:
        unread_count = EventNotification.objects.filter(user=user, read=False).count()
        urgent_count = 0

    payload = {'unread_count': unread_count, 'has_urgent': urgent_count > 0, 'urgent_count': urgent_count}

    try:
        cache.set(cache_key, payload, timeout=_UNREAD_CACHE_TTL_SECONDS)
    except Exception:
        pass

    return payload

class HeadlessNotificationsPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class HeadlessNotificationListView(APIView):
    """GET `/api/v4/headless/notifications/`."""

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """List notifications for the authenticated user.
        
        Returns all notifications (enhanced and legacy). Legacy notifications
        (without title) are handled via fallback in NotificationListSerializer.to_representation().
        """
        state = request.query_params.get('state', 'SENT')
        event_type = request.query_params.get('event_type') or request.query_params.get('filter_event')

        # Return all notifications - fallback for legacy notifications is in serializer
        queryset = EventNotification.objects.filter(user=request.user).select_related('action').order_by('-action__timestamp')

        # Extended schema: exclude DELETED by default.
        if hasattr(EventNotification, 'state'):
            queryset = queryset.exclude(state='DELETED')
            if state and state != 'ALL':
                # For 'SENT' state, include both CREATED and SENT so users see new
                # notifications even before Celery delivery task runs.
                if state == 'SENT':
                    queryset = queryset.filter(state__in=['CREATED', 'SENT'])
                else:
                    queryset = queryset.filter(state=state)
            if event_type:
                queryset = queryset.filter(event_type=event_type)
        else:
            # Legacy fallback: only support unread/read.
            if state == 'SENT':
                queryset = queryset.filter(read=False)
            elif state == 'READ':
                queryset = queryset.filter(read=True)

        paginator = HeadlessNotificationsPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)

        serializer = NotificationListSerializer(page, many=True, context={'request': request})
        response = paginator.get_paginated_response(serializer.data)

        counters = _get_unread_counters(user=request.user)
        response.data['unread_count'] = counters['unread_count']
        response.data['has_urgent'] = counters['has_urgent']
        return response


class HeadlessNotificationDetailView(APIView):
    """GET `/api/v4/headless/notifications/{id}/`."""

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, notification_id: int):
        try:
            notification = EventNotification.objects.select_related('action').get(
                pk=notification_id, user=request.user
            )
        except EventNotification.DoesNotExist:
            return Response({'error': 'not_found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = NotificationSerializer(notification, context={'request': request})
        return Response(serializer.data)

    def delete(self, request, notification_id: int):
        try:
            notification = EventNotification.objects.get(pk=notification_id, user=request.user)
        except EventNotification.DoesNotExist:
            return Response({'error': 'not_found'}, status=status.HTTP_404_NOT_FOUND)
        # Soft delete to keep audit trail.
        if hasattr(notification, 'soft_delete'):
            notification.soft_delete()
        else:
            notification.delete()
        _invalidate_unread_cache(user_id=request.user.pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class HeadlessNotificationReadView(APIView):
    """PATCH `/api/v4/headless/notifications/{id}/read/`."""

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, notification_id: int):
        try:
            notification = EventNotification.objects.get(pk=notification_id, user=request.user)
        except EventNotification.DoesNotExist:
            return Response({'error': 'not_found'}, status=status.HTTP_404_NOT_FOUND)
        notification.mark_as_read()
        _invalidate_unread_cache(user_id=request.user.pk)
        serializer = NotificationSerializer(notification, context={'request': request})
        return Response(serializer.data)


class HeadlessNotificationReadAllView(APIView):
    """POST `/api/v4/headless/notifications/read-all/`."""

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        filter_event_type = request.data.get('filter_event_type') or request.data.get('event_type')

        if not hasattr(EventNotification, 'state'):
            # Legacy fallback: mark all as read.
            queryset = EventNotification.objects.filter(user=request.user, read=False)
            marked_count = queryset.count()
            queryset.update(read=True)
            _invalidate_unread_cache(user_id=request.user.pk)
            return Response({'marked_count': marked_count, 'unread_count': 0})

        # Mark both CREATED and SENT as read (CREATED is pending, SENT is delivered)
        queryset = EventNotification.objects.filter(user=request.user, state__in=['CREATED', 'SENT'])
        if filter_event_type:
            queryset = queryset.filter(event_type=filter_event_type)

        marked_count = queryset.count()
        queryset.update(
            read=True,
            state='READ',
            read_at=timezone.now()
        )

        _invalidate_unread_cache(user_id=request.user.pk)
        counters = _get_unread_counters(user=request.user)
        return Response({'marked_count': marked_count, 'unread_count': counters['unread_count']})


class HeadlessNotificationUnreadCountView(APIView):
    """GET `/api/v4/headless/notifications/unread-count/`."""

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(_get_unread_counters(user=request.user))


class HeadlessNotificationPreferenceView(APIView):
    """GET/PATCH `/api/v4/headless/notifications/preferences/`."""

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pref, _created = NotificationPreference.objects.get_or_create(user=request.user)
        serializer = NotificationPreferenceSerializer(pref, context={'request': request})
        return Response(serializer.data)

    def patch(self, request):
        pref, _created = NotificationPreference.objects.get_or_create(user=request.user)
        serializer = NotificationPreferenceSerializer(pref, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


