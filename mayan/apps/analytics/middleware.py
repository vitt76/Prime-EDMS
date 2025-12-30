"""Analytics middleware.

Contains lightweight feature usage tracking without impacting core requests.
"""

from django.utils.deprecation import MiddlewareMixin

from .services import track_feature_usage


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


