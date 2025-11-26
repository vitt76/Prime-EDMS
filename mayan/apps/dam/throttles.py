import logging
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

logger = logging.getLogger('mayan.apps.dam.throttle')


class AIAnalysisThrottle(UserRateThrottle):
    """
    Strict throttling for AI analysis endpoints.

    Rate limits:
    - 10 requests per minute (aggressive protection)
    - 50 requests per hour
    - 500 requests per day

    Logs all throttle events for monitoring and security audit.
    """
    scope = 'ai_analysis'

    def get_cache_key(self, request, view):
        """
        Custom cache key that includes user ID for per-user throttling.
        """
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            ident = user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }

    def throttle_success(self):
        """
        Called when request is allowed. Log successful throttle check.
        """
        result = super().throttle_success()

        # Log successful throttle (for monitoring usage patterns)
        request = getattr(self, 'request', None)
        if request:
            user = getattr(request, 'user', None)
            user_id = user.pk if user and user.is_authenticated else None

            remaining = self.get_remaining_time()
            if remaining is not None:
                logger.info(
                    'Throttle success',
                    extra={
                        'user_id': user_id,
                        'event': 'throttle_success',
                        'scope': self.scope,
                        'remaining_requests': remaining,
                        'path': request.path,
                        'method': request.method
                    }
                )

        return result

    def throttle_failure(self):
        """
        Called when request is throttled. Log the rejection.
        """
        result = super().throttle_failure()

        # Log throttle rejection (security event)
        request = getattr(self, 'request', None)
        if request:
            user = getattr(request, 'user', None)
            user_id = user.pk if user and user.is_authenticated else None

            logger.warning(
                'Throttle limit exceeded',
                extra={
                    'user_id': user_id,
                    'event': 'throttle_limit_exceeded',
                    'scope': self.scope,
                    'path': request.path,
                    'method': request.method,
                    'remaining': 0
                }
            )

        return result


class AIAnalysisAnonThrottle(AnonRateThrottle):
    """
    Very restrictive throttling for anonymous users on AI endpoints.

    Rate limit: 1 request per hour (almost blocked)
    """
    scope = 'ai_analysis_anon'

    def throttle_failure(self):
        """
        Log anonymous throttle rejections.
        """
        result = super().throttle_failure()

        request = getattr(self, 'request', None)
        if request:
            logger.warning(
                'Anonymous throttle limit exceeded',
                extra={
                    'user_id': None,
                    'event': 'anon_throttle_limit_exceeded',
                    'scope': self.scope,
                    'path': request.path,
                    'method': request.method,
                    'ip': self.get_ident(request)
                }
            )

        return result