from django.http import JsonResponse
from django.views import View
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .models import AutoAdminSingleton


class AutoAdminCredentialsAPIView(APIView):
    """
    Get auto-generated admin credentials for first-time setup.
    Only available when auto admin properties exist.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            autoadmin_properties = AutoAdminSingleton.objects.get()
            if autoadmin_properties.account and autoadmin_properties.password:
                return Response({
                    'username': autoadmin_properties.account.username,
                    'email': autoadmin_properties.account.email,
                    'password': autoadmin_properties.password,
                    'is_auto_generated': True
                })
        except AutoAdminSingleton.DoesNotExist:
            pass

        return Response({
            'message': 'No auto-generated credentials available',
            'is_auto_generated': False
        })


class AutoAdminCredentialsJSView(View):
    """
    Return auto-generated admin credentials as JavaScript object for injection.
    Used for frontend integration via JavaScript injection in login template.
    """

    def get(self, request):
        try:
            autoadmin_properties = AutoAdminSingleton.objects.get()
            if autoadmin_properties.account and autoadmin_properties.password:
                credentials = {
                    'username': autoadmin_properties.account.username,
                    'email': autoadmin_properties.account.email,
                    'password': autoadmin_properties.password,
                    'is_auto_generated': True
                }
            else:
                credentials = {
                    'is_auto_generated': False,
                    'message': 'No credentials available'
                }
        except AutoAdminSingleton.DoesNotExist:
            credentials = {
                'is_auto_generated': False,
                'message': 'No autoadmin setup'
            }

        # Return as JavaScript object
        js_content = f"""
// Auto-generated admin credentials for Prime-EDMS frontend integration
window.autoadminCredentials = {credentials};
"""
        return JsonResponse(credentials, safe=False)
