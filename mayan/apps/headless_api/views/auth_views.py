"""
Authentication-related views for Headless API.

These endpoints provide SPA-friendly auth/user info that Mayan's core REST API
does not expose in a convenient way (e.g. is_staff / is_superuser on /users/current/).
"""

from django.utils.translation import ugettext_lazy as _
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mayan.apps.permissions.permissions import (
    permission_role_edit, permission_role_view
)
from mayan.apps.user_management.permissions import (
    permission_group_edit, permission_group_view, permission_user_edit,
    permission_user_view
)


class HeadlessAuthMeView(APIView):
    """
    Return current authenticated user's identity and admin flags.

    Endpoint:
        GET /api/v4/headless/auth/me/

    Response:
        {
            "user": {
                "id": int,
                "username": str,
                "email": str,
                "first_name": str,
                "last_name": str,
                "is_active": bool,
                "is_staff": bool,
                "is_superuser": bool,
                "groups": [{"id": int, "name": str}]
            }
        }
    """

    # IMPORTANT: Use token auth only to avoid mixing session cookies from another user.
    # SPA uses DRF token authentication; session auth can cause the "wrong" user to be
    # returned if a browser still has a valid Django session cookie.
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Determine SPA admin access using Mayan's permission system.
        # This avoids relying on group names, and works even when is_staff=False.
        admin_permissions = (
            permission_user_view,
            permission_user_edit,
            permission_group_view,
            permission_group_edit,
            permission_role_view,
            permission_role_edit,
        )
        user_permission_ids = []
        for perm in admin_permissions:
            try:
                if perm.stored_permission.user_has_this(user=user):
                    user_permission_ids.append(perm.pk)
            except Exception:
                continue

        groups = []
        try:
            groups = [{'id': g.pk, 'name': g.name} for g in user.groups.all().order_by('name')]
        except Exception:
            groups = []

        return Response(
            {
                'user': {
                    'id': user.pk,
                    'username': getattr(user, 'username', ''),
                    'email': getattr(user, 'email', ''),
                    'first_name': getattr(user, 'first_name', ''),
                    'last_name': getattr(user, 'last_name', ''),
                    'is_active': bool(getattr(user, 'is_active', True)),
                    'is_staff': bool(getattr(user, 'is_staff', False)),
                    'is_superuser': bool(getattr(user, 'is_superuser', False)),
                    'groups': groups,
                    'permissions': user_permission_ids,
                    'can_access_admin_panel': (
                        bool(getattr(user, 'is_staff', False)) or
                        bool(getattr(user, 'is_superuser', False)) or
                        bool(user_permission_ids)
                    )
                }
            }
        )


