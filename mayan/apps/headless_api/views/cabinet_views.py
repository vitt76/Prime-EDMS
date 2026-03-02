"""
Headless API views for Cabinet (collection) sharing within organization.

Sprint 3: Share cabinets with users in the same tenant (X-Organization-Id).
Endpoints:
- GET  /api/v4/headless/cabinets/org-members/ — list users in current org (for share modal)
- POST /api/v4/headless/cabinets/<id>/share-with-users/ — share with user_ids
- GET  /api/v4/headless/cabinets/shared-with-me/ — list cabinets shared with current user
"""

import logging
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from django.shortcuts import get_object_or_404

from mayan.apps.acls.models import AccessControlList
from django.core.exceptions import PermissionDenied as MayanPermissionDenied
from mayan.apps.cabinets.models import Cabinet, CabinetUserShare
from mayan.apps.cabinets.permissions import permission_cabinet_edit, permission_cabinet_view
from mayan.apps.cabinets.serializers import CabinetSerializer
from mayan.apps.organizations.models import UserOrganizationRole

logger = logging.getLogger(__name__)


class HeadlessCabinetOrgMembersView(APIView):
    """
    GET: List users in the current organization (for share modal).
    Requires X-Organization-Id. Returns minimal user info: id, username, full name.
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organization, err = _get_organization(request)
        if err is not None:
            return err

        members = UserOrganizationRole.objects.filter(
            organization=organization
        ).select_related('user').order_by('user__username')

        result = [
            {
                'id': m.user_id,
                'username': getattr(m.user, 'username', '') or '',
                'first_name': getattr(m.user, 'first_name', '') or '',
                'last_name': getattr(m.user, 'last_name', '') or '',
            }
            for m in members
        ]
        return Response(result)


def _get_organization(request):
    """Require X-Organization-Id for tenant isolation."""
    org = getattr(request, 'organization', None)
    if not org:
        return None, Response(
            {'detail': 'Organization context required (X-Organization-Id).'},
            status=status.HTTP_400_BAD_REQUEST
        )
    return org, None


def _cabinet_queryset_for_user(request, organization):
    """Cabinets in org that the user can view (ACL or CabinetUserShare)."""
    base_qs = Cabinet.objects.filter(organization=organization)
    # Cabinets user can access via ACL
    acl_allowed = AccessControlList.objects.restrict_queryset(
        permission=permission_cabinet_view,
        queryset=base_qs,
        user=request.user
    )
    # Cabinets shared with user via CabinetUserShare
    shared_ids = CabinetUserShare.objects.filter(
        user=request.user,
        organization=organization
    ).values_list('cabinet_id', flat=True)
    shared_qs = base_qs.filter(pk__in=shared_ids)
    # Union: distinct
    from django.db.models import Q
    return base_qs.filter(
        Q(pk__in=acl_allowed.values_list('pk', flat=True)) |
        Q(pk__in=shared_qs.values_list('pk', flat=True))
    ).distinct()


class HeadlessCabinetShareWithUsersView(APIView):
    """
    POST: Share a cabinet with users in the same organization.
    Body: { "user_ids": [1, 2, 3] }
    Requires X-Organization-Id. Caller must have permission_cabinet_edit on the cabinet.
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, cabinet_id):
        organization, err = _get_organization(request)
        if err is not None:
            return err

        cabinet = get_object_or_404(
            Cabinet.objects.filter(organization=organization),
            pk=cabinet_id
        )
        AccessControlList.objects.check_access(
            obj=cabinet,
            permissions=(permission_cabinet_edit,),
            user=request.user
        )

        user_ids = request.data.get('user_ids') or []
        if not isinstance(user_ids, list):
            return Response(
                {'detail': 'user_ids must be a list of integers.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from django.contrib.auth import get_user_model
        from mayan.apps.organizations.models import UserOrganizationRole
        User = get_user_model()

        org_member_ids = set(
            UserOrganizationRole.objects.filter(
                organization=organization
            ).values_list('user_id', flat=True)
        )

        created = []
        errors = []
        with transaction.atomic():
            for uid in user_ids:
                try:
                    uid = int(uid)
                except (TypeError, ValueError):
                    errors.append({'user_id': uid, 'error': 'Invalid id'})
                    continue
                if uid == request.user.pk:
                    continue
                if uid not in org_member_ids:
                    errors.append({'user_id': uid, 'error': 'User not in same organization'})
                    continue
                user = User.objects.filter(pk=uid).first()
                if not user:
                    errors.append({'user_id': uid, 'error': 'User not found'})
                    continue
                _, created_flag = CabinetUserShare.objects.get_or_create(
                    cabinet=cabinet,
                    user=user,
                    organization=organization,
                    defaults={'shared_by': request.user}
                )
                if created_flag:
                    created.append(uid)

        return Response({
            'cabinet_id': cabinet.pk,
            'shared_user_ids': created,
            'errors': errors if errors else None,
        }, status=status.HTTP_200_OK)


class HeadlessCabinetSharedWithMeListView(APIView):
    """
    GET: List cabinets shared with the current user (same organization).
    Requires X-Organization-Id.
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organization, err = _get_organization(request)
        if err is not None:
            return err

        shared = CabinetUserShare.objects.filter(
            user=request.user,
            organization=organization
        ).select_related('cabinet', 'shared_by').order_by('-created_at')

        cabinet_ids = list(shared.values_list('cabinet_id', flat=True))
        cabinets_qs = Cabinet.objects.filter(
            pk__in=cabinet_ids,
            organization=organization
        ).prefetch_related('documents')

        serializer = CabinetSerializer(
            cabinets_qs,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class HeadlessCabinetDetailView(APIView):
    """
    GET: Cabinet detail. Access allowed if user has permission_cabinet_view (ACL)
    or cabinet is in CabinetUserShare for this user.
    Requires X-Organization-Id.
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, cabinet_id):
        organization, err = _get_organization(request)
        if err is not None:
            return err

        cabinet = Cabinet.objects.filter(
            organization=organization,
            pk=cabinet_id
        ).first()
        if not cabinet:
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        has_acl = False
        try:
            AccessControlList.objects.check_access(
                obj=cabinet,
                permissions=(permission_cabinet_view,),
                user=request.user
            )
            has_acl = True
        except MayanPermissionDenied:
            pass
        has_share = CabinetUserShare.objects.filter(
            cabinet=cabinet,
            user=request.user,
            organization=organization
        ).exists()
        if not has_acl and not has_share:
            return Response(
                {'detail': 'You do not have permission to view this cabinet.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CabinetSerializer(cabinet, context={'request': request})
        return Response(serializer.data)
