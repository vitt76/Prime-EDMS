import logging

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class AIAnalysisThrottle(UserRateThrottle):
    """
    Throttle AI analysis endpoints for authenticated users.

    Limit the expensive operation aggressively to avoid abuse:
      * 10 analyses per minute
      * 50 analyses per hour
      * 500 analyses per day
    """

    scope = 'ai_analysis'

    def throttle_success(self):
        """
        Called when a request is allowed; log the event for monitoring.
        """
        result = super().throttle_success()

        logger = logging.getLogger('dam.throttle')
        history = getattr(self, 'history', None)
        remaining = 0
        if history is not None and self.num_requests is not None:
            remaining = max(self.num_requests - len(history), 0)

        logger.info(
            f'AI analysis request allowed for user {self.request.user.id}',
            extra={
                'user_id': getattr(self.request.user, 'id', None),
                'remaining': remaining
            }
        )

        return result


class AIAnalysisAnonThrottle(AnonRateThrottle):
    """Minimal throttle for anonymous users (AI endpoints should be locked)."""

    scope = 'ai_analysis_anon'

