"""
Task status endpoints for Headless API.

Provides endpoints for checking the status of asynchronous Celery tasks.
"""
import logging

from celery.result import AsyncResult
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class HeadlessTaskStatusView(APIView):
    """
    Get status of Celery task by task_id.
    
    GET /api/v4/headless/tasks/{task_id}/status/
    
    Returns JSON with task status, result (if SUCCESS), or error (if FAILURE).
    """
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, task_id: str):
        """
        Get task status from Celery Result Backend.
        
        Args:
            task_id: Celery task ID (UUID string)
        
        Returns:
            Response with task status and result/error information
        """
        try:
            result = AsyncResult(task_id)
            
            response_data = {
                'task_id': task_id,
                'status': result.state,
            }
            
            if result.state == 'PENDING':
                response_data['message'] = 'Task is waiting to be processed'
            elif result.state == 'STARTED':
                response_data['message'] = 'Task is being processed'
            elif result.state == 'SUCCESS':
                response_data['result'] = result.result
                response_data['message'] = 'Task completed successfully'
            elif result.state == 'FAILURE':
                # result.info содержит exception info при FAILURE
                error_info = result.info
                if isinstance(error_info, Exception):
                    response_data['error'] = str(error_info)
                elif isinstance(error_info, dict):
                    response_data['error'] = error_info.get('error', str(error_info))
                else:
                    response_data['error'] = str(error_info)
                response_data['message'] = 'Task failed'
            elif result.state == 'REVOKED':
                response_data['error'] = 'Task was revoked'
                response_data['message'] = 'Task was cancelled'
            else:
                response_data['message'] = f'Unknown status: {result.state}'
            
            return Response(response_data)
            
        except Exception as exc:
            logger.exception('Error getting task status for task_id %s: %s', task_id, exc)
            return Response(
                {
                    'error': 'invalid_task_id',
                    'detail': str(exc),
                    'task_id': task_id
                },
                status=status.HTTP_400_BAD_REQUEST
            )

