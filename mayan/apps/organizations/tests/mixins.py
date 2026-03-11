import tempfile
from typing import Iterable, Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from mayan.apps.acls.models import AccessControlList
from mayan.apps.permissions.classes import Permission
from mayan.apps.permissions.models import Role

from ..models import Organization, UserOrganizationRole

User = get_user_model()


class SaaSTenantTestHarnessMixin:
    """Reusable SaaS tenant harness for backend API and task tests."""

    saas_base_domain = 'dam-brand.com'
    use_temporary_media_root = False

    def setUp(self):
        super().setUp()

        self._settings_override = self.settings(
            DEPLOYMENT_MODE='saas',
            SAAS_BASE_DOMAIN=self.saas_base_domain,
            CHANNEL_LAYERS={
                'default': {
                    'BACKEND': 'channels.layers.InMemoryChannelLayer'
                }
            }
        )
        self._settings_override.enable()
        self.addCleanup(self._settings_override.disable)

        self._media_root_dir = None
        self._media_root_override = None
        if self.use_temporary_media_root:
            self._media_root_dir = tempfile.TemporaryDirectory()
            self.addCleanup(self._media_root_dir.cleanup)
            self._media_root_override = self.settings(
                MEDIA_ROOT=self._media_root_dir.name
            )
            self._media_root_override.enable()
            self.addCleanup(self._media_root_override.disable)

    def create_organization(
        self,
        *,
        name: str,
        slug: str,
        email: Optional[str] = None
    ) -> Organization:
        return Organization.objects.create(
            name=name,
            slug=slug,
            email=email or f'{slug}@example.com',
            is_active=True,
            status='active',
            deployment_mode='saas',
        )

    def create_user(
        self,
        *,
        username: str,
        password: str = 'testpass123',
        email: Optional[str] = None,
        is_superuser: bool = False
    ):
        if is_superuser:
            return User.objects.create_superuser(
                username=username,
                password=password,
                email=email or f'{username}@example.com',
            )

        return User.objects.create_user(
            username=username,
            password=password,
            email=email or f'{username}@example.com',
        )

    def add_user_to_organization(
        self,
        *,
        user,
        organization: Organization,
        role: str = UserOrganizationRole.ROLE_OWNER,
        is_default: bool = False
    ) -> UserOrganizationRole:
        return UserOrganizationRole.objects.create(
            user=user,
            organization=organization,
            role=role,
            is_default=is_default,
        )

    def create_user_in_organization(
        self,
        *,
        username: str,
        organization: Organization,
        role: str = UserOrganizationRole.ROLE_OWNER,
        is_default: bool = True,
        is_superuser: bool = False
    ):
        user = self.create_user(
            username=username,
            is_superuser=is_superuser,
        )
        self.add_user_to_organization(
            user=user,
            organization=organization,
            role=role,
            is_default=is_default,
        )
        return user

    def organization_headers(self, organization: Organization):
        return {'HTTP_X_ORGANIZATION_ID': str(organization.pk)}

    def api_client_for(self, user):
        client = APIClient()
        token, _ = Token.objects.get_or_create(user=user)
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        return client

    def grant_permissions(
        self,
        *,
        user,
        permissions: Iterable,
        label: Optional[str] = None
    ) -> Role:
        role = Role.objects.create(
            label=label or f'Test Role {user.pk}'
        )
        for permission in permissions:
            role.grant(permission=permission)

        group = Group.objects.create(
            name=f'Test Group {user.pk} {role.pk}'
        )
        role.groups.add(group)
        group.user_set.add(user)
        Permission.invalidate_cache()
        return role

    def grant_access(self, *, obj, permission, role=None):
        acl_role = role or Role.objects.create(label=f'ACL Role {obj._meta.label} {obj.pk}')
        content_type = ContentType.objects.get_for_model(
            obj, for_concrete_model=False
        )
        acl = AccessControlList.objects.filter(
            content_type=content_type,
            object_id=obj.pk,
            role=acl_role,
        ).first()
        if acl is None:
            acl = AccessControlList(
                content_type=content_type,
                object_id=obj.pk,
                role=acl_role,
            )
            acl._event_ignore = True
            acl.save()
        acl.permissions.add(permission.stored_permission)
        Permission.invalidate_cache()
        return acl
