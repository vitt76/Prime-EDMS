from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework import status
import logging


logger = logging.getLogger(__name__)


def exception_handler(exc, context):
    """
    Custom exception handler that enriches DRF responses with error_code.
    """

    response = drf_exception_handler(exc, context)

    logger.exception(
        f'API Exception: {exc.__class__.__name__}',
        extra={
            'view': context.get('view'),
            'request': context.get('request'),
            'error': str(exc)
        }
    )

    if response is not None:
        if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            response.data = {
                'error': 'Rate limit exceeded',
                'error_code': 'RATE_LIMITED',
                'detail': response.data.get('detail', 'Too many requests'),
                'retry_after': response.get('Retry-After', 60)
            }
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            response.data = {
                'error': 'Permission denied',
                'error_code': 'PERMISSION_DENIED',
                'detail': response.data.get('detail', 'You do not have permission')
            }
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            response.data = {
                'error': 'Not found',
                'error_code': 'NOT_FOUND',
                'detail': response.data.get('detail', 'Resource not found')
            }
        elif response.status_code == status.HTTP_400_BAD_REQUEST:
            response.data = {
                'error': 'Invalid request',
                'error_code': 'VALIDATION_ERROR',
                'details': response.data
            }

    return response






