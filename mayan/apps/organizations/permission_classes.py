"""
Reusable DRF permission classes for organization-level access control.

These classes check the user's role in the current organization
(resolved by TenantResolverMiddleware and stored in request.organization).

Uses per-request caching via ``request._org_role_cache`` to avoid
redundant DB queries when multiple permission classes are applied.

Usage::

    class MyView(APIView):
        permission_classes = (IsAuthenticated, IsOrganizationMember)

For URL-scoped org endpoints (``/organizations/<organization_id>/...``),
use ``OrgScopedAPIMixin`` together with ``IsTargetOrgAdminOrSuperAdmin``::

    class MyOrgView(OrgScopedAPIMixin, APIView):
        permission_classes = (IsAuthenticated, IsTargetOrgAdminOrSuperAdmin)

        def get(self, request, organization_id):
            org = self.get_target_organization()
            ...
"""

import logging
import uuid as uuid_module

from rest_framework.permissions import BasePermission

from .models import UserOrganizationRole

logger = logging.getLogger(name=__name__)


def _get_user_role(request, organization):
    """
    Get user's role within the organization, cached per request.

    Returns the role string (owner, admin, member, viewer)
    or None if the user is not a member.

    The result is cached on ``request._org_role_cache`` so that
    multiple permission classes in the same request don't issue
    redundant queries.
    """
    if not hasattr(request, '_org_role_cache'):
        request._org_role_cache = {}

    cache_key = str(organization.pk)

    if cache_key not in request._org_role_cache:
        role = UserOrganizationRole.objects.filter(
            user=request.user,
            organization=organization
        ).values_list('role', flat=True).first()
        request._org_role_cache[cache_key] = role

    return request._org_role_cache[cache_key]


class IsOrganizationMember(BasePermission):
    """
    Allow access if the user is a member of request.organization
    (any role: owner, admin, member, viewer).
    """
    message = 'You must be a member of this organization.'

    def has_permission(self, request, view):
        organization = getattr(request, 'organization', None)
        if organization is None:
            return False

        if not request.user or not request.user.is_authenticated:
            return False

        # Superadmin always passes
        if request.user.is_staff or request.user.is_superuser:
            return True

        return _get_user_role(request, organization) is not None


class IsOrganizationAdmin(BasePermission):
    """
    Allow access if the user is an admin or owner of request.organization.
    """
    message = 'Organization admin or owner access required.'

    def has_permission(self, request, view):
        organization = getattr(request, 'organization', None)
        if organization is None:
            return False

        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_staff or request.user.is_superuser:
            return True

        role = _get_user_role(request, organization)
        return role in (
            UserOrganizationRole.ROLE_OWNER,
            UserOrganizationRole.ROLE_ADMIN
        )


class IsOrganizationOwner(BasePermission):
    """
    Allow access only to the owner of request.organization.
    """
    message = 'Organization owner access required.'

    def has_permission(self, request, view):
        organization = getattr(request, 'organization', None)
        if organization is None:
            return False

        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_staff or request.user.is_superuser:
            return True

        role = _get_user_role(request, organization)
        return role == UserOrganizationRole.ROLE_OWNER


class IsSuperAdminOrOrgAdmin(BasePermission):
    """
    Allow access if the user is a Django staff/superuser
    OR an admin/owner of request.organization.

    Useful for endpoints that should be accessible to both
    platform admins and organization admins.

    .. warning::
        This class checks ``request.organization`` (middleware-resolved).
        For URL-scoped endpoints use ``IsTargetOrgAdminOrSuperAdmin`` instead.
    """
    message = 'Super admin or organization admin access required.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_staff or request.user.is_superuser:
            return True

        organization = getattr(request, 'organization', None)
        if organization is None:
            return False

        role = _get_user_role(request, organization)
        return role in (
            UserOrganizationRole.ROLE_OWNER,
            UserOrganizationRole.ROLE_ADMIN
        )


# ---------------------------------------------------------------------------
# URL-scoped organization access (Sprint 4 Hotfix)
# ---------------------------------------------------------------------------

class OrgScopedAPIMixin:
    """
    Mixin for views that target a specific organization via URL kwarg.

    Extracts ``organization_id`` from URL kwargs, validates UUID format,
    and enforces tenant boundary:

    - **staff / superuser**: can access any organization
    - **non-staff**: ``organization_id`` MUST equal ``request.organization.pk``

    Provides :meth:`get_target_organization` for convenient, cached access
    to the resolved Organization instance (with annotations).

    Usage::

        class MyView(OrgScopedAPIMixin, APIView):
            permission_classes = (IsAuthenticated, IsTargetOrgAdminOrSuperAdmin)

            def get(self, request, organization_id):
                org = self.get_target_organization()
                ...
    """

    def get_target_organization_id(self):
        """Extract and UUID-validate organization_id from URL kwargs."""
        org_id = self.kwargs.get('organization_id')
        if not org_id:
            return None
        try:
            uuid_module.UUID(str(org_id))
        except (ValueError, TypeError):
            return None
        return org_id

    def get_target_organization(self):
        """
        Return the Organization identified by URL kwarg, with caching.

        The queryset is annotated with ``member_count`` via the shared
        helper :func:`~.querysets.annotate_org_counts` to avoid N+1
        in serializers.

        Raises ``Http404`` if the organization does not exist.
        """
        if hasattr(self, '_target_organization'):
            return self._target_organization

        from django.shortcuts import get_object_or_404

        from .models import Organization
        from .querysets import annotate_org_counts

        org_id = self.get_target_organization_id()
        qs = annotate_org_counts(
            Organization.objects.select_related(
                'owner'
            ).prefetch_related(
                'subscription__plan', 'domain_settings'
            )
        )
        org = get_object_or_404(qs, pk=org_id)
        self._target_organization = org
        return org


class IsTargetOrgAdminOrSuperAdmin(BasePermission):
    """
    Permission for URL-scoped organization endpoints.

    Enforces tenant boundary so that a non-staff user can only
    operate on the organization that matches ``request.organization``
    (resolved by middleware).

    - **staff / superuser**: allowed for any ``organization_id``
    - **non-staff org-admin/owner**: allowed only when
      ``organization_id == request.organization.pk``
    - everyone else: denied
    """
    message = 'Access denied: you are not authorized for this organization.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Platform admins can access any organization
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Extract target org_id from URL
        org_id = view.kwargs.get('organization_id')
        if not org_id:
            return False

        # Validate UUID format
        try:
            uuid_module.UUID(str(org_id))
        except (ValueError, TypeError):
            return False

        # Non-staff: target org MUST match request.organization
        request_org = getattr(request, 'organization', None)
        if request_org is None:
            return False

        if str(request_org.pk) != str(org_id):
            logger.warning(
                'Cross-org access attempt blocked: user=%s '
                'request_org=%s target_org=%s',
                request.user.pk, request_org.slug, org_id
            )
            return False

        # Verify the user is admin/owner of their own organization
        role = _get_user_role(request, request_org)
        return role in (
            UserOrganizationRole.ROLE_OWNER,
            UserOrganizationRole.ROLE_ADMIN
        )
