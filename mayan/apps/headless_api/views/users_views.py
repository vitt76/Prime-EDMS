"""
User management views for Headless API.

Why:
- Mayan core `/api/v4/users/` is subject to internal queryset rules and can
  hide staff/superusers like `admin`, which breaks SPA admin UI expectations.
- These endpoints provide a stable contract for the Vue admin panel.

Security:
- Token auth only.
- Requires Mayan user management permissions (user_view/user_edit/user_create/user_delete)
  or staff/superuser.
"""

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mayan.apps.user_management.permissions import (
    permission_user_create,
    permission_user_delete,
    permission_user_edit,
    permission_user_view,
)


def _user_has_permission(user, permission) -> bool:
    try:
        return permission.stored_permission.user_has_this(user=user)
    except Exception:
        return False


def _can_view_users(user) -> bool:
    return (
        bool(getattr(user, 'is_superuser', False)) or
        bool(getattr(user, 'is_staff', False)) or
        _user_has_permission(user=user, permission=permission_user_view)
    )


def _can_create_users(user) -> bool:
    return (
        bool(getattr(user, 'is_superuser', False)) or
        bool(getattr(user, 'is_staff', False)) or
        _user_has_permission(user=user, permission=permission_user_create)
    )


def _can_edit_users(user) -> bool:
    return (
        bool(getattr(user, 'is_superuser', False)) or
        bool(getattr(user, 'is_staff', False)) or
        _user_has_permission(user=user, permission=permission_user_edit)
    )


def _can_delete_users(user) -> bool:
    return (
        bool(getattr(user, 'is_superuser', False)) or
        bool(getattr(user, 'is_staff', False)) or
        _user_has_permission(user=user, permission=permission_user_delete)
    )


def _serialize_user(u):
    # Keep compatible with frontend `MayanUser` interface in adminService.ts.
    return {
        'id': u.pk,
        'username': getattr(u, 'username', '') or '',
        'email': getattr(u, 'email', '') or '',
        'first_name': getattr(u, 'first_name', '') or '',
        'last_name': getattr(u, 'last_name', '') or '',
        'is_active': bool(getattr(u, 'is_active', True)),
        'is_staff': bool(getattr(u, 'is_staff', False)),
        'is_superuser': bool(getattr(u, 'is_superuser', False)),
        'date_joined': getattr(u, 'date_joined', None).isoformat() if getattr(u, 'date_joined', None) else None,
        'last_login': getattr(u, 'last_login', None).isoformat() if getattr(u, 'last_login', None) else None,
        # SPA hydrates groups via /api/v4/groups/* endpoints.
        'groups': [],
    }


class HeadlessUsersListCreateView(APIView):
    """
    List and create users for the SPA admin UI.

    GET  /api/v4/headless/users/?page=&page_size=&search=&is_active=
    POST /api/v4/headless/users/
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _can_view_users(user=request.user):
            return Response({'error': 'access_denied'}, status=status.HTTP_403_FORBIDDEN)

        User = get_user_model()
        qs = User.objects.all().order_by('username')

        search = (request.query_params.get('search') or '').strip()
        if search:
            qs = qs.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        is_active_raw = request.query_params.get('is_active')
        if is_active_raw in ('True', 'False'):
            qs = qs.filter(is_active=(is_active_raw == 'True'))

        try:
            page = int(request.query_params.get('page', '1'))
        except Exception:
            page = 1
        try:
            page_size = int(request.query_params.get('page_size', '50'))
        except Exception:
            page_size = 50

        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 50
        if page_size > 500:
            page_size = 500

        count = qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        results = [_serialize_user(u) for u in qs[start:end]]

        return Response({'count': count, 'next': None, 'previous': None, 'results': results})

    def post(self, request):
        if not _can_create_users(user=request.user):
            return Response({'error': 'access_denied'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data or {}
        User = get_user_model()

        username = (data.get('username') or '').strip()
        if not username:
            return Response({'error': 'username_required'}, status=status.HTTP_400_BAD_REQUEST)

        user = User(
            username=username,
            email=(data.get('email') or '').strip(),
            first_name=(data.get('first_name') or '').strip(),
            last_name=(data.get('last_name') or '').strip(),
        )

        # Optional flags
        for key in ('is_active', 'is_staff', 'is_superuser'):
            if key in data:
                try:
                    setattr(user, key, bool(data.get(key)))
                except Exception:
                    pass

        password = data.get('password')
        if password:
            user.set_password(password)
        else:
            # Align with Mayan default behavior: allow unusable password.
            user.set_unusable_password()

        user.save()
        return Response(_serialize_user(user), status=status.HTTP_201_CREATED)


class HeadlessUsersDetailView(APIView):
    """
    Retrieve / update / delete a user.

    GET    /api/v4/headless/users/{id}/
    PATCH  /api/v4/headless/users/{id}/
    DELETE /api/v4/headless/users/{id}/
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, user_id: int):
        User = get_user_model()
        return User.objects.get(pk=user_id)

    def get(self, request, user_id: int):
        if not _can_view_users(user=request.user):
            return Response({'error': 'access_denied'}, status=status.HTTP_403_FORBIDDEN)
        user = self.get_object(user_id=user_id)
        return Response(_serialize_user(user))

    def patch(self, request, user_id: int):
        if not _can_edit_users(user=request.user):
            return Response({'error': 'access_denied'}, status=status.HTTP_403_FORBIDDEN)

        user = self.get_object(user_id=user_id)
        data = request.data or {}

        for field in ('username', 'email', 'first_name', 'last_name'):
            if field in data and data.get(field) is not None:
                setattr(user, field, (data.get(field) or '').strip())

        for field in ('is_active', 'is_staff', 'is_superuser'):
            if field in data:
                try:
                    setattr(user, field, bool(data.get(field)))
                except Exception:
                    pass

        if 'password' in data and data.get('password'):
            user.set_password(data.get('password'))

        user.save()
        return Response(_serialize_user(user))

    def delete(self, request, user_id: int):
        if not _can_delete_users(user=request.user):
            return Response({'error': 'access_denied'}, status=status.HTTP_403_FORBIDDEN)
        user = self.get_object(user_id=user_id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


