"""
Authentication-related views for Headless API.

These endpoints provide SPA-friendly auth/user info that Mayan's core REST API
does not expose in a convenient way (e.g. is_staff / is_superuser on /users/current/).
"""

import logging

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

logger = logging.getLogger(name=__name__)


class HeadlessAuthMeView(APIView):
    """
    Return current authenticated user's identity, admin flags, and
    organization context.

    Endpoint:
        GET /api/v4/headless/auth/me/

    Response:
        {
            "user": { ... },
            "organization": {
                "id": "uuid", "name": "...", "slug": "...",
                "status": "active", "deployment_mode": "saas",
                "role": "admin", "branding_color": "#3B82F6", "logo": null
            },
            "organizations": [
                {"id": "...", "name": "...", "slug": "...", "role": "owner"}
            ]
        }
    """

    # IMPORTANT: Use token auth only to avoid mixing session cookies from another user.
    # SPA uses DRF token authentication; session auth can cause the "wrong" user to be
    # returned if a browser still has a valid Django session cookie.
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = []  # Disable throttling for critical auth endpoint

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
            groups = [
                {'id': g.pk, 'name': g.name}
                for g in user.groups.all().order_by('name')
            ]
        except Exception:
            groups = []

        # --- Organization context ---
        organization_data = None
        organizations_list = []

        try:
            from mayan.apps.organizations.models import UserOrganizationRole

            # Current organization (resolved by TenantResolverMiddleware)
            current_org = getattr(request, 'organization', None)

            # All organizations for the user
            user_roles = UserOrganizationRole.objects.filter(
                user=user,
                organization__is_active=True
            ).select_related('organization').order_by(
                '-is_default', '-role', 'organization__name'
            )

            for role_entry in user_roles:
                org = role_entry.organization
                org_item = {
                    'id': str(org.pk),
                    'name': org.name,
                    'slug': org.slug,
                    'status': org.status,
                    'deployment_mode': org.deployment_mode,
                    'role': role_entry.role,
                    'branding_color': org.branding_color,
                    'logo': org.logo.url if org.logo else None,
                    'is_default': role_entry.is_default,
                }
                organizations_list.append(org_item)

                # If this is the current org, use it for the primary field
                if current_org and str(org.pk) == str(current_org.pk):
                    organization_data = org_item

            # Fallback: if middleware resolved an org but user has no role
            # (e.g. standalone mode, superadmin)
            if organization_data is None and current_org is not None:
                organization_data = {
                    'id': str(current_org.pk),
                    'name': current_org.name,
                    'slug': current_org.slug,
                    'status': current_org.status,
                    'deployment_mode': current_org.deployment_mode,
                    'role': 'owner' if user.is_superuser else 'member',
                    'branding_color': current_org.branding_color,
                    'logo': current_org.logo.url if current_org.logo else None,
                    'is_default': True,
                }

        except Exception as exc:
            logger.warning(
                'Could not load organization context for user %s: %s',
                user.pk, exc
            )

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
                    'is_superuser': bool(
                        getattr(user, 'is_superuser', False)
                    ),
                    'groups': groups,
                    'permissions': user_permission_ids,
                    'can_access_admin_panel': (
                        bool(getattr(user, 'is_staff', False)) or
                        bool(getattr(user, 'is_superuser', False)) or
                        bool(user_permission_ids)
                    )
                },
                'organization': organization_data,
                'organizations': organizations_list,
            }
        )
