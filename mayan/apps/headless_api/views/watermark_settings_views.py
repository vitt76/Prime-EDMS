"""
Sprint 3.3: Organization watermark settings API.

GET /api/v4/headless/organization/watermark/  — current org watermark settings
PATCH /api/v4/headless/organization/watermark/ — update (admin/owner)
"""

from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class OrganizationWatermarkSettingsView(APIView):
    """
    GET: Return current organization's watermark settings.
    PATCH: Update current organization's watermark settings (enabled, text, position, opacity, etc.).
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organization = getattr(request, 'organization', None)
        if not organization:
            return Response(
                {'detail': 'Organization context required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        from mayan.apps.organizations.models import OrganizationWatermarkSettings
        ws, _ = OrganizationWatermarkSettings.objects.get_or_create(
            organization=organization,
            defaults={'enabled': False, 'text': '', 'position': 'bottom_right', 'opacity': 0.5}
        )
        return Response({
            'id': ws.id,
            'enabled': ws.enabled,
            'apply_on_download': getattr(ws, 'apply_on_download', False),
            'text': ws.text or '',
            'logo_url': ws.logo_url or '',
            'position': ws.position,
            'opacity': ws.opacity,
            'font_size': ws.font_size,
        })

    def patch(self, request):
        organization = getattr(request, 'organization', None)
        if not organization:
            return Response(
                {'detail': 'Organization context required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        from mayan.apps.organizations.models import OrganizationWatermarkSettings
        ws, _ = OrganizationWatermarkSettings.objects.get_or_create(
            organization=organization,
            defaults={'enabled': False, 'text': '', 'position': 'bottom_right', 'opacity': 0.5}
        )
        allowed = {'enabled', 'apply_on_download', 'text', 'logo_url', 'position', 'opacity', 'font_size'}
        for key in allowed:
            if key not in request.data:
                continue
            val = request.data[key]
            if key == 'apply_on_download':
                ws.apply_on_download = bool(val)
            elif key == 'opacity':
                if isinstance(val, (int, float)):
                    ws.opacity = max(0.0, min(1.0, float(val)))
            else:
                setattr(ws, key, val)
        ws.save()
        return Response({
            'id': ws.id,
            'enabled': ws.enabled,
            'apply_on_download': getattr(ws, 'apply_on_download', False),
            'text': ws.text or '',
            'logo_url': ws.logo_url or '',
            'position': ws.position,
            'opacity': ws.opacity,
            'font_size': ws.font_size,
        })
