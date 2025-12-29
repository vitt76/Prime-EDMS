"""Headless API views for Notification Center.

Implements `/api/v4/headless/notifications/*` endpoints as SPA-friendly REST APIs.
"""

import logging

from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models import Document
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.events.models import Notification as EventNotification

from mayan.apps.notifications.dam_taxonomy import (
    DAM_EVENT_TYPES_ALLOWLIST,
    EVENT_TYPE_TO_CATEGORY,
)
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
        # #region agent log
        import json as json_module
        import time as time_module
        logger.info('HeadlessNotificationListView.get() called for user=%s', request.user.id)
        try:
            with open('c:\\DAM\\Prime-EDMS\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json_module.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'D',
                    'location': 'headless_api/views/notification_views.py:88',
                    'message': 'API: HeadlessNotificationListView.get() called',
                    'data': {'user_id': request.user.id, 'username': request.user.username},
                    'timestamp': int(time_module.time() * 1000)
                }) + '\n')
                f.flush()  # Force write to disk
        except Exception as e:
            logger.exception('Failed to write debug log: %s', e)
        # #endregion
        state = request.query_params.get('state', 'SENT')
        event_type = request.query_params.get('event_type') or request.query_params.get('filter_event')
        category = request.query_params.get('category')
        scope = request.query_params.get('scope', 'dam')

        # Role resolution via Django Groups (Admin/Editor/Viewer).
        try:
            user_group_names = set(request.user.groups.values_list('name', flat=True))
        except Exception:
            user_group_names = set()
        is_admin = (
            getattr(request.user, 'is_superuser', False)
            or getattr(request.user, 'is_staff', False)
            or ('admin' in {name.lower() for name in user_group_names})
        )

        # #region agent log
        try:
            # Check user subscriptions and auto-subscribe if needed
            from mayan.apps.events.models import EventSubscription, StoredEventType
            user_subscriptions = EventSubscription.objects.filter(user=request.user)
            doc_event_types = StoredEventType.objects.filter(name__startswith='documents.')
            subscribed_doc_events = user_subscriptions.filter(stored_event_type__in=doc_event_types)
            
            # Auto-subscribe user to document events if not subscribed
            if subscribed_doc_events.count() == 0:
                document_event_types = [
                    'documents.document_file_created',
                    'documents.document_created',
                    'documents.document_edited',
                    'documents.document_version_created',
                ]
                for event_type_name in document_event_types:
                    try:
                        stored_event_type = StoredEventType.objects.get(name=event_type_name)
                        EventSubscription.objects.get_or_create(
                            user=request.user,
                            stored_event_type=stored_event_type
                        )
                        logger.info('Auto-subscribed user %s to event %s', request.user.username, event_type_name)
                    except StoredEventType.DoesNotExist:
                        logger.debug('Event type %s not found, skipping auto-subscription', event_type_name)
                    except Exception as e:
                        logger.warning('Failed to auto-subscribe user %s to event %s: %s', request.user.username, event_type_name, e)
                
                # Re-fetch subscriptions after auto-subscription
                user_subscriptions = EventSubscription.objects.filter(user=request.user)
                subscribed_doc_events = user_subscriptions.filter(stored_event_type__in=doc_event_types)
            
            with open('c:\\DAM\\Prime-EDMS\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json_module.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'F',
                    'location': 'headless_api/views/notification_views.py:88',
                    'message': 'API: checking user subscriptions',
                    'data': {'user_id': request.user.id, 'total_subscriptions': user_subscriptions.count(), 'document_event_subscriptions': subscribed_doc_events.count(), 'subscribed_event_names': list(subscribed_doc_events.values_list('stored_event_type__name', flat=True))},
                    'timestamp': int(time_module.time() * 1000)
                }) + '\n')
        except Exception as e:
            # Log exception for debugging
            try:
                with open('c:\\DAM\\Prime-EDMS\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                    f.write(json_module.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'F',
                        'location': 'headless_api/views/notification_views.py:88',
                        'message': 'API: exception checking subscriptions',
                        'data': {'error': str(e)},
                        'timestamp': int(time_module.time() * 1000)
                    }) + '\n')
            except Exception:
                pass
        # #endregion

        # #region agent log
        try:
            # Check all notifications in DB for this user
            all_notifications = EventNotification.objects.filter(user=request.user)
            notifications_with_title = all_notifications.exclude(title__isnull=True) if hasattr(EventNotification, 'title') else all_notifications.none()
            notifications_with_state = all_notifications.exclude(state__isnull=True) if hasattr(EventNotification, 'state') else all_notifications.none()
            with open('c:\\DAM\\Prime-EDMS\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json_module.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'D',
                    'location': 'headless_api/views/notification_views.py:134',
                    'message': 'API: checking all notifications in DB',
                    'data': {
                        'user_id': request.user.id,
                        'total_notifications_count': all_notifications.count(),
                        'notifications_with_title_count': notifications_with_title.count() if hasattr(EventNotification, 'title') else 0,
                        'notifications_with_state_count': notifications_with_state.count() if hasattr(EventNotification, 'state') else 0,
                        'recent_notification_ids': list(all_notifications[:5].values_list('id', flat=True))
                    },
                    'timestamp': int(time_module.time() * 1000)
                }) + '\n')
        except Exception as e:
            try:
                with open('c:\\DAM\\Prime-EDMS\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                    f.write(json_module.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'D',
                        'location': 'headless_api/views/notification_views.py:134',
                        'message': 'API: exception checking notifications',
                        'data': {'error': str(e)},
                        'timestamp': int(time_module.time() * 1000)
                    }) + '\n')
            except Exception:
                pass
        # #endregion

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
            # #region agent log
            # Log queryset state after filtering
            try:
                with open('c:\\DAM\\Prime-EDMS\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                    f.write(json_module.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'D',
                        'location': 'headless_api/views/notification_views.py:220',
                        'message': 'API: queryset after state filtering',
                        'data': {
                            'user_id': request.user.id,
                            'state_param': state,
                            'queryset_count': queryset.count(),
                            'has_state_attr': hasattr(EventNotification, 'state'),
                            'queryset_ids': list(queryset[:10].values_list('id', flat=True)),
                            'queryset_states': list(queryset[:10].values_list('state', flat=True)) if hasattr(EventNotification, 'state') else []
                        },
                        'timestamp': int(time_module.time() * 1000)
                    }) + '\n')
            except Exception:
                pass
            # #endregion
            if event_type:
                queryset = queryset.filter(event_type=event_type)
        else:
            # Legacy fallback: only support unread/read.
            if state == 'SENT':
                queryset = queryset.filter(read=False)
            elif state == 'READ':
                queryset = queryset.filter(read=True)

        # DAM scope filtering:
        # - Non-admin users see only curated DAM events.
        # - Admins can request scope=all to see everything in the Notification Center.
        if (not is_admin) or scope != 'all':
            queryset = queryset.filter(event_type__in=DAM_EVENT_TYPES_ALLOWLIST)

            if category:
                allowed_for_category = [
                    et for et, cat in EVENT_TYPE_TO_CATEGORY.items() if cat == category
                ]
                queryset = queryset.filter(event_type__in=allowed_for_category)

            # Object-level access control: do not leak notifications about documents
            # the user cannot view (even if subscribed globally).
            try:
                document_ct = ContentType.objects.get_for_model(Document)
                allowed_document_ids = AccessControlList.objects.restrict_queryset(
                    permission=permission_document_view,
                    queryset=Document.valid.all(),
                    user=request.user
                ).values_list('pk', flat=True)

                related_doc_q = (
                    Q(content_type=document_ct, object_id__in=allowed_document_ids) |
                    Q(action__target_content_type=document_ct, action__target_object_id__in=allowed_document_ids) |
                    Q(action__action_object_content_type=document_ct, action__action_object_object_id__in=allowed_document_ids)
                )
                queryset = queryset.filter(related_doc_q)
            except Exception:
                queryset = queryset.none()

        paginator = HeadlessNotificationsPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        # #region agent log
        import json as json_module
        import time as time_module
        try:
            with open('c:\\DAM\\Prime-EDMS\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json_module.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'D',
                    'location': 'headless_api/views/notification_views.py:120',
                    'message': 'API: queryset before pagination',
                    'data': {'user_id': request.user.id, 'queryset_count': queryset.count(), 'state_filter': state, 'has_state_attr': hasattr(EventNotification, 'state')},
                    'timestamp': int(time_module.time() * 1000)
                }) + '\n')
        except Exception:
            pass
        # #endregion

        serializer = NotificationListSerializer(page, many=True, context={'request': request})
        response = paginator.get_paginated_response(serializer.data)
        # #region agent log
        import json as json_module
        import time as time_module
        try:
            with open('c:\\DAM\\Prime-EDMS\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json_module.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'D',
                    'location': 'headless_api/views/notification_views.py:123',
                    'message': 'API: response data',
                    'data': {'user_id': request.user.id, 'results_count': len(response.data.get('results', [])), 'total_count': response.data.get('count', 0), 'first_result_id': response.data.get('results', [{}])[0].get('id') if response.data.get('results') else None},
                    'timestamp': int(time_module.time() * 1000)
                }) + '\n')
        except Exception:
            pass
        # #endregion

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


