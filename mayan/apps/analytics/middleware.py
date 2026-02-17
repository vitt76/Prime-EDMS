"""Analytics middleware.

Contains lightweight feature usage tracking without impacting core requests.
"""

from django.utils.deprecation import MiddlewareMixin

from .services import track_feature_usage
from .tasks import track_asset_event_async


class AssetEventTrackingMiddleware(MiddlewareMixin):
    """Fire-and-forget tracking of document view/download via API (tenant-aware)."""

    TRACK_PREFIXES = (
        '/api/v4/documents/',
        '/api/v4/headless/documents/',
    )
    DOWNLOAD_SUBSTR = 'download'

    def process_response(self, request, response):
        if getattr(response, 'status_code', 500) >= 400:
            return response
        organization = getattr(request, 'organization', None)
        if not organization:
            return response
        path = (request.path or '').strip()
        if not path:
            return response

        event_type = None
        if self.DOWNLOAD_SUBSTR in path.lower():
            event_type = AssetEventTrackingMiddleware._event_download()
        else:
            for prefix in self.TRACK_PREFIXES:
                if path.startswith(prefix) and request.method == 'GET':
                    event_type = AssetEventTrackingMiddleware._event_view()
                    break
        if not event_type:
            return response

        document_id = None
        try:
            match = getattr(request, 'resolver_match', None)
            if match and getattr(match, 'kwargs', None):
                document_id = (
                    match.kwargs.get('document_id') or
                    match.kwargs.get('document_pk') or
                    match.kwargs.get('pk') or
                    match.kwargs.get('id')
                )
        except Exception:
            pass
        if document_id is not None:
            try:
                document_id = int(document_id)
            except (TypeError, ValueError):
                document_id = None
        if not document_id:
            return response

        search_session_id = (request.META.get('HTTP_X_SEARCH_SESSION_ID') or '').strip() or None
        if search_session_id and len(search_session_id) > 36:
            search_session_id = search_session_id[:36]

        try:
            track_asset_event_async.delay(
                organization_id=str(organization.pk),
                user_id=request.user.pk if getattr(request, 'user', None) and request.user.is_authenticated else None,
                document_id=document_id,
                event_type=event_type,
                ip_address=(request.META.get('REMOTE_ADDR') or '')[:45],
                user_agent=(request.META.get('HTTP_USER_AGENT') or '')[:500],
                referrer=(request.META.get('HTTP_REFERER') or '')[:500],
                metadata={},
                search_session_id=search_session_id,
            )
        except Exception:
            pass
        return response

    @staticmethod
    def _event_view():
        from .models import AssetEvent
        return AssetEvent.EVENT_TYPE_VIEW

    @staticmethod
    def _event_download():
        from .models import AssetEvent
        return AssetEvent.EVENT_TYPE_DOWNLOAD


class FeatureUsageMiddleware(MiddlewareMixin):
    """Track feature adoption using request paths (best-effort)."""

    PATH_PREFIX_TO_FEATURE = (
        ('/api/v4/headless/analytics/dashboard/assets/', 'analytics.asset_bank'),
        ('/api/v4/headless/analytics/dashboard/campaigns/', 'analytics.campaign_performance'),
        ('/api/v4/headless/analytics/dashboard/search/', 'analytics.search_analytics'),
        ('/api/v4/headless/analytics/dashboard/users/', 'analytics.user_activity'),
        ('/api/v4/headless/analytics/dashboard/approvals/', 'analytics.approvals'),
        ('/api/v4/headless/analytics/dashboard/roi/', 'analytics.roi'),
    )

    def process_response(self, request, response):
        try:
            path = request.path or ''
            user = getattr(request, 'user', None)
        except Exception:
            return response

        feature_name = None
        for prefix, mapped in self.PATH_PREFIX_TO_FEATURE:
            if path.startswith(prefix):
                feature_name = mapped
                break

        if feature_name:
            track_feature_usage(
                user=user,
                feature_name=feature_name,
                was_successful=int(getattr(response, 'status_code', 200)) < 400,
                metadata={'path': path}
            )

        return response


class QueryCountDebugMiddleware(MiddlewareMixin):
    """Log SQL query count for analytics endpoints (DEBUG-only).

    This middleware is intended for development troubleshooting to catch N+1
    queries and heavy endpoints. It is opt-in via development settings.
    """

    def __init__(self, get_response=None):
        super().__init__(get_response=get_response)
        import logging
        self._logger = logging.getLogger('mayan.apps.analytics.sql')

    def __call__(self, request):
        from django.conf import settings
        if not getattr(settings, 'DEBUG', False) or 'analytics' not in (request.path or ''):
            return self.get_response(request)

        try:
            from django.db import connection, reset_queries
            reset_queries()
            response = self.get_response(request)
            self._logger.debug('SQL queries=%d path=%s', len(connection.queries), request.path)
            return response
        except Exception:
            return self.get_response(request)

