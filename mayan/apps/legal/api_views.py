from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserConsentLog
from .serializers import UserConsentLogSerializer


def get_client_ip(request):
    """Extract client IP from request (X-Forwarded-For aware)."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR') or ''


def get_user_agent(request):
    """Extract User-Agent from request."""
    return request.META.get('HTTP_USER_AGENT', '')[:2000]


class ConsentLogAPIView(APIView):
    """
    Public (no auth) endpoint to log cookie/consent choice for audit.
    POST only; lightweight and fast.
    """
    permission_classes = (AllowAny,)
    serializer_class = UserConsentLogSerializer

    def post(self, request):
        serializer = UserConsentLogSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        ip = get_client_ip(request)
        user_agent = get_user_agent(request)

        UserConsentLog.objects.create(
            consent_type=serializer.validated_data['consent_type'],
            session_id=serializer.validated_data.get('session_id', '') or '',
            url_referer=serializer.validated_data.get('url_referer', '') or '',
            ip_address=ip or None,
            user_agent=user_agent,
        )
        return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)
