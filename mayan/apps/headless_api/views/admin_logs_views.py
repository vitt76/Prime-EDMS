"""Headless API views for admin logs.

This endpoint is intended for the admin panel only.
Regular users should use Notification Center (headless notifications) and should
NOT be exposed to the full events/activity stream.
"""

import logging

from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .activity_views import HeadlessActivityFeedView

logger = logging.getLogger(__name__)


class HeadlessAdminLogsView(HeadlessActivityFeedView):
    """GET `/api/v4/headless/admin/logs/`.

    Returns the full activity feed for administrators (including system events
    when requested via query param `system=1`).
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _is_admin_user(self, user) -> bool:
        """Return True if the user is an admin (Django Groups)."""

        try:
            group_names = set(user.groups.values_list('name', flat=True))
        except Exception:
            group_names = set()

        return (
            getattr(user, 'is_superuser', False)
            or getattr(user, 'is_staff', False)
            or ('admin' in {name.lower() for name in group_names})
        )

    def get(self, request):
        if not self._is_admin_user(request.user):
            return Response({'error': 'forbidden'}, status=status.HTTP_403_FORBIDDEN)

        # Force full feed for admin logs. All other query params (page/page_size,
        # important/system) are handled by the base implementation.
        try:
            # We can't mutate request.query_params (immutable), so we implement
            # a minimal wrapper that reuses the base view's internals.
            user = request.user

            page = int(request.query_params.get('page', 1))
            page_size = min(int(request.query_params.get('page_size', 20)), 100)

            actions = self._get_filtered_actions(user, filter_type='all')

            from django.core.paginator import EmptyPage, Paginator

            paginator = Paginator(actions, page_size)
            try:
                page_obj = paginator.page(page)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages or 1)

            prefetched_documents = self._prefetch_documents_for_actions(page_obj.object_list)
            results = [
                self._serialize_action(action, prefetched_documents=prefetched_documents)
                for action in page_obj.object_list
            ]

            return Response(
                {
                    'count': paginator.count,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': paginator.num_pages,
                    'results': results,
                }
            )
        except Exception as exc:
            logger.error(
                'Error getting admin logs for user %s: %s',
                getattr(request.user, 'username', None),
                str(exc),
                exc_info=True
            )
            return Response(
                {'error': 'internal_error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


