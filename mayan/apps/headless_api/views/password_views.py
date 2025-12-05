"""
Password management views for Headless API.

Provides REST endpoints for password-related operations that Mayan EDMS
doesn't expose through its standard API.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.hashers import check_password
from django.utils.translation import ugettext_lazy as _

import logging

logger = logging.getLogger(__name__)


class HeadlessPasswordChangeView(APIView):
    """
    REST API endpoint for changing user password.

    Mayan EDMS doesn't provide a REST API endpoint for password changes,
    only HTML forms. This view bridges that gap for SPA compatibility.

    Endpoint: POST /api/v4/headless/password/change/

    Expected JSON payload:
    {
        "current_password": "current_password_here",
        "new_password": "new_password_here",
        "new_password_confirm": "new_password_here"
    }

    Response:
    - 200: {"message": "Password changed successfully", "status": "success"}
    - 400: {"error": "Error message", "error_code": "ERROR_CODE"}
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handle password change request.

        Validates current password, checks new password requirements,
        and updates the user's password.
        """
        user = request.user
        data = request.data

        # Extract and validate input data
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        new_password_confirm = data.get('new_password_confirm')

        # Basic validation
        if not all([current_password, new_password, new_password_confirm]):
            return Response(
                {
                    'error': _('All fields are required'),
                    'error_code': 'MISSING_FIELDS'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify current password
        if not check_password(current_password, user.password):
            return Response(
                {
                    'error': _('Current password is incorrect'),
                    'error_code': 'INVALID_CURRENT_PASSWORD'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check password confirmation
        if new_password != new_password_confirm:
            return Response(
                {
                    'error': _('New passwords do not match'),
                    'error_code': 'PASSWORD_MISMATCH'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate new password complexity
        if len(new_password) < 8:
            return Response(
                {
                    'error': _('Password must be at least 8 characters long'),
                    'error_code': 'PASSWORD_TOO_SHORT'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_password.isdigit():
            return Response(
                {
                    'error': _('Password cannot be entirely numeric'),
                    'error_code': 'PASSWORD_NUMERIC_ONLY'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update password
        try:
            user.set_password(new_password)
            user.save()

            logger.info(f"Password changed for user: {user.username}")

            return Response(
                {
                    'message': _('Password changed successfully'),
                    'status': 'success'
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error changing password for user {user.username}: {str(e)}")
            return Response(
                {
                    'error': _('An error occurred while changing password'),
                    'error_code': 'INTERNAL_ERROR'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
