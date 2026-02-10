"""
REST API views for Organizations app.

Provides endpoints for Organization CRUD, member management,
plan listing, and current organization retrieval.
"""

import logging

from rest_framework import status
from rest_framework.authentication import (
    SessionAuthentication, TokenAuthentication
)
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .audit import (
    log_org_event,
    EVENT_MEMBER_ADD, EVENT_MEMBER_REMOVE, EVENT_ORG_ACTIVATE,
    EVENT_ORG_ARCHIVE, EVENT_ORG_CREATE, EVENT_ORG_SUSPEND,
    EVENT_ORG_UPDATE,
)
from .models import (
    ORGANIZATION_STATUS_ACTIVE, ORGANIZATION_STATUS_ARCHIVED,
    ORGANIZATION_STATUS_SUSPENDED, ORGANIZATION_STATUS_TRIAL,
    Organization, Plan, UserOrganizationRole,
)
from .permission_classes import (
    IsTargetOrgAdminOrSuperAdmin, OrgScopedAPIMixin,
)
from .querysets import annotate_org_counts
from .serializers import (
    AddMemberSerializer,
    CurrentOrganizationSerializer,
    OrganizationListSerializer,
    OrganizationSerializer,
    PlanSerializer,
    RemoveMemberSerializer,
    UserOrganizationRoleSerializer,
)

# Default page size for list endpoints
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

logger = logging.getLogger(name=__name__)


class OrganizationListCreateView(APIView):
    """
    GET  — List all organizations (SuperAdmin only).
    POST — Create a new organization (SuperAdmin only).
    """
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, IsAdminUser)

    def get(self, request):
        organizations = annotate_org_counts(
            Organization.objects.select_related('owner')
        ).order_by('-created_at')

        # Simple page/page_size pagination
        try:
            page = max(int(request.query_params.get('page', 1)), 1)
        except (ValueError, TypeError):
            page = 1
        try:
            page_size = min(
                max(int(request.query_params.get(
                    'page_size', DEFAULT_PAGE_SIZE
                )), 1),
                MAX_PAGE_SIZE
            )
        except (ValueError, TypeError):
            page_size = DEFAULT_PAGE_SIZE

        total = organizations.count()
        start = (page - 1) * page_size
        end = start + page_size
        page_qs = organizations[start:end]

        serializer = OrganizationListSerializer(
            page_qs, many=True, context={'request': request}
        )
        return Response({
            'results': serializer.data,
            'count': total,
            'page': page,
            'page_size': page_size,
        })

    def post(self, request):
        serializer = OrganizationSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        organization = serializer.save()

        # Auto-create owner role for the requesting user
        UserOrganizationRole.objects.get_or_create(
            user=request.user,
            organization=organization,
            defaults={
                'role': UserOrganizationRole.ROLE_OWNER,
                'is_default': True,
            }
        )

        log_org_event(
            organization, EVENT_ORG_CREATE, user=request.user,
            details={'name': organization.name, 'slug': organization.slug}
        )

        return Response(
            OrganizationSerializer(
                organization, context={'request': request}
            ).data,
            status=status.HTTP_201_CREATED
        )


class OrganizationDetailView(OrgScopedAPIMixin, APIView):
    """
    GET    — Retrieve organization details (admin/owner or superadmin).
    PUT    — Update organization.
    PATCH  — Partial update organization.
    DELETE — Archive organization (soft delete).

    Uses ``OrgScopedAPIMixin`` to enforce tenant boundary:
    non-staff users can only access their own organization.
    """
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, IsTargetOrgAdminOrSuperAdmin)

    def get(self, request, organization_id):
        organization = self.get_target_organization()
        serializer = OrganizationSerializer(
            organization, context={'request': request}
        )
        return Response(serializer.data)

    def put(self, request, organization_id):
        organization = self.get_target_organization()
        serializer = OrganizationSerializer(
            organization, data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        log_org_event(
            organization, EVENT_ORG_UPDATE, user=request.user,
            details={'fields': list(request.data.keys())}
        )
        return Response(serializer.data)

    def patch(self, request, organization_id):
        organization = self.get_target_organization()
        serializer = OrganizationSerializer(
            organization, data=request.data,
            partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        log_org_event(
            organization, EVENT_ORG_UPDATE, user=request.user,
            details={'fields': list(request.data.keys())}
        )
        return Response(serializer.data)

    def delete(self, request, organization_id):
        organization = self.get_target_organization()

        # Soft delete: archive the organization
        organization.status = 'archived'
        organization.is_active = False
        organization.save(update_fields=('status', 'is_active'))

        log_org_event(
            organization, EVENT_ORG_ARCHIVE, user=request.user
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


class OrganizationMembersView(OrgScopedAPIMixin, APIView):
    """
    GET    — List members of an organization (admin/owner or superadmin).
    POST   — Add a member to the organization.
    DELETE — Remove a member from the organization.

    Uses ``OrgScopedAPIMixin`` to enforce tenant boundary:
    non-staff users can only manage members of their own organization.
    """
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, IsTargetOrgAdminOrSuperAdmin)

    def get(self, request, organization_id):
        organization = self.get_target_organization()

        roles = UserOrganizationRole.objects.filter(
            organization=organization
        ).select_related('user').order_by('-role', 'joined_at')

        serializer = UserOrganizationRoleSerializer(
            roles, many=True, context={'request': request}
        )
        return Response(serializer.data)

    def post(self, request, organization_id):
        organization = self.get_target_organization()

        serializer = AddMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user_id']
        role = serializer.validated_data['role']

        # Check user quota
        from .quota import QuotaExceededException, check_user_quota
        try:
            check_user_quota(organization)
        except QuotaExceededException as exc:
            return Response(
                {
                    'detail': 'User limit exceeded for this organization.',
                    'quota_type': exc.quota_type,
                    'current': exc.current_value,
                    'limit': exc.limit_value,
                },
                status=status.HTTP_402_PAYMENT_REQUIRED
            )

        membership, created = UserOrganizationRole.objects.get_or_create(
            user=user,
            organization=organization,
            defaults={'role': role}
        )

        if not created:
            return Response(
                {'detail': 'User is already a member of this organization.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        log_org_event(
            organization, EVENT_MEMBER_ADD, user=request.user,
            details={
                'target_user_id': user.pk,
                'target_username': user.username,
                'role': role,
            }
        )

        return Response(
            UserOrganizationRoleSerializer(
                membership, context={'request': request}
            ).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, organization_id):
        organization = self.get_target_organization()

        serializer = RemoveMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data['user_id']

        try:
            membership = UserOrganizationRole.objects.get(
                user_id=user_id,
                organization=organization
            )
        except UserOrganizationRole.DoesNotExist:
            return Response(
                {'detail': 'User is not a member of this organization.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Prevent removing the last owner
        if membership.role == UserOrganizationRole.ROLE_OWNER:
            owner_count = UserOrganizationRole.objects.filter(
                organization=organization,
                role=UserOrganizationRole.ROLE_OWNER
            ).count()
            if owner_count <= 1:
                return Response(
                    {'detail': 'Cannot remove the last owner.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        membership.delete()

        log_org_event(
            organization, EVENT_MEMBER_REMOVE, user=request.user,
            details={'target_user_id': user_id}
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


class PlanListView(APIView):
    """
    GET — List all active, public plans.

    Public endpoint (no authentication required for viewing plans).
    """
    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        plans = Plan.objects.filter(
            is_active=True, is_public=True
        ).order_by('sort_order', 'price_monthly')

        serializer = PlanSerializer(
            plans, many=True, context={'request': request}
        )
        return Response(serializer.data)


class CurrentOrganizationView(APIView):
    """
    GET — Return the current organization (resolved from request).

    Uses the organization set by TenantResolverMiddleware.
    """
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        organization = getattr(request, 'organization', None)

        if organization is None:
            return Response(
                {'detail': 'No organization resolved for this request.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CurrentOrganizationSerializer(
            organization, context={'request': request}
        )
        return Response(serializer.data)


class OrganizationSuspendView(OrgScopedAPIMixin, APIView):
    """
    POST — Suspend an organization (SuperAdmin only).

    Sets ``status='suspended'`` and ``is_active=False``.
    Suspended organizations are blocked by TenantResolverMiddleware.
    Accepts optional ``reason`` field in the request body.

    ТЗ Section 4.5.3.
    """
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, IsAdminUser)

    def post(self, request, organization_id):
        organization = self.get_target_organization()

        if organization.status == ORGANIZATION_STATUS_SUSPENDED:
            return Response(
                {
                    'detail': 'Organization is already suspended.',
                    'organization_id': str(organization.pk),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if organization.status == ORGANIZATION_STATUS_ARCHIVED:
            return Response(
                {
                    'detail': 'Cannot suspend an archived organization.',
                    'organization_id': str(organization.pk),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        organization.status = ORGANIZATION_STATUS_SUSPENDED
        organization.is_active = False
        organization.save(update_fields=('status', 'is_active'))

        log_org_event(
            organization, EVENT_ORG_SUSPEND, user=request.user,
            details={
                'reason': request.data.get('reason', ''),
                'previous_status': organization.status,
            }
        )

        return Response({
            'success': True,
            'message': 'Organization suspended',
            'organization_id': str(organization.pk),
        })


class OrganizationActivateView(OrgScopedAPIMixin, APIView):
    """
    POST — Activate a suspended or trial organization (SuperAdmin only).

    Sets ``status='active'`` and ``is_active=True``.
    Only organizations in ``suspended`` or ``trial`` status can be activated.
    """
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, IsAdminUser)

    def post(self, request, organization_id):
        organization = self.get_target_organization()

        activatable_statuses = (
            ORGANIZATION_STATUS_SUSPENDED,
            ORGANIZATION_STATUS_TRIAL,
        )

        if organization.status not in activatable_statuses:
            return Response(
                {
                    'detail': (
                        'Only suspended or trial organizations can be '
                        'activated. Current status: %s' % organization.status
                    ),
                    'organization_id': str(organization.pk),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        previous_status = organization.status
        organization.status = ORGANIZATION_STATUS_ACTIVE
        organization.is_active = True
        organization.save(update_fields=('status', 'is_active'))

        log_org_event(
            organization, EVENT_ORG_ACTIVATE, user=request.user,
            details={'previous_status': previous_status}
        )

        return Response({
            'success': True,
            'message': 'Organization activated',
            'organization_id': str(organization.pk),
        })
