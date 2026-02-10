"""
Tenant resolver middleware for multi-tenancy support.

Determines the current Organization from the incoming request and sets it
in both request.organization and ContextVar for thread-safe access.

Resolution order:
1. Custom domain (dam.company.com -> Organization with DomainSettings)
2. Subdomain (org-slug.dam-brand.com -> Organization by slug)
3. Authorization token (extract org from user's default organization)
4. Standalone mode (use default Organization)

See: docs/transformation-2025/TZ_Django_Tenant_Isolation.md
"""

import logging
import os
import uuid as uuid_module

from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _

from .managers import set_current_organization, clear_current_organization

logger = logging.getLogger(name=__name__)

# Deployment mode from environment
DEPLOYMENT_MODE = os.environ.get('DEPLOYMENT_MODE', 'STANDALONE').upper()

# Base domain for subdomain resolution in SaaS mode
SAAS_BASE_DOMAIN = os.environ.get('SAAS_BASE_DOMAIN', 'dam-brand.com')

# Paths that should bypass tenant resolution (health checks, static, etc.)
TENANT_EXEMPT_PATHS = (
    '/health/',
    '/favicon.ico',
    '/static/',
    '/s/',
    '/__debug__/',
    '/api/v4/headless/organizations/',  # SuperAdmin org management endpoints
)


class TenantResolverMiddleware:
    """
    Middleware that resolves the current Organization (tenant) for each request.

    Sets:
    - request.organization: Organization instance or None
    - ContextVar: For thread-safe access in ORM managers

    Blocks access for suspended/archived organizations with HTTP 403.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip tenant resolution for exempt paths
        if self._is_exempt_path(request.path):
            request.organization = None
            token = set_current_organization(None)
            try:
                response = self.get_response(request)
            finally:
                clear_current_organization(token)
            return response

        # Resolve organization
        organization = self._resolve_organization(request)
        request.organization = organization

        # Check organization status
        if organization is not None:
            if not organization.is_active:
                return JsonResponse(
                    {
                        'error': str(_(
                            'Organization is not active'
                        )),
                        'error_code': 'ORGANIZATION_INACTIVE',
                        'organization_status': organization.status
                    },
                    status=403
                )

            if organization.status in ('suspended', 'archived'):
                return JsonResponse(
                    {
                        'error': str(_(
                            'Organization access is restricted'
                        )),
                        'error_code': 'ORGANIZATION_SUSPENDED',
                        'organization_status': organization.status
                    },
                    status=403
                )

        # Set context variable for TenantAwareManager
        token = set_current_organization(organization)

        try:
            response = self.get_response(request)
        finally:
            # Always clean up context variable
            clear_current_organization(token)

        return response

    def _is_exempt_path(self, path):
        """Check if the path should bypass tenant resolution."""
        for exempt_path in TENANT_EXEMPT_PATHS:
            if path.startswith(exempt_path):
                return True
        return False

    def _resolve_organization(self, request):
        """
        Resolve organization from the request.

        Resolution order:
        1. Custom domain lookup
        2. Subdomain extraction
        3. X-Organization-Id header (SPA org switching)
        4. User's default organization (from auth token)
        5. Default organization (standalone mode)

        Returns:
            Organization instance or None.
        """
        # Standalone mode: always return default organization
        if DEPLOYMENT_MODE == 'STANDALONE':
            return self._get_default_organization()

        # SaaS mode: try multiple resolution strategies
        host = request.get_host().split(':')[0]  # Remove port

        # 1. Try custom domain
        organization = self._resolve_by_custom_domain(host)
        if organization is not None:
            logger.debug(
                'Resolved organization by custom domain: %s -> %s',
                host, organization.slug
            )
            return organization

        # 2. Try subdomain
        organization = self._resolve_by_subdomain(host)
        if organization is not None:
            logger.debug(
                'Resolved organization by subdomain: %s -> %s',
                host, organization.slug
            )
            return organization

        # 3. Try X-Organization-Id header (SPA explicit org switching)
        organization = self._resolve_by_header(request)
        if organization is not None:
            logger.debug(
                'Resolved organization by X-Organization-Id header: %s',
                organization.slug
            )
            return organization

        # 4. Try from authenticated user's default organization
        if hasattr(request, 'user') and request.user.is_authenticated:
            organization = self._resolve_by_user(request.user)
            if organization is not None:
                logger.debug(
                    'Resolved organization by user: %s -> %s',
                    request.user.username, organization.slug
                )
                return organization

        # 5. Fallback to default organization
        logger.debug(
            'No organization resolved for host %s, using default', host
        )
        return self._get_default_organization()

    def _resolve_by_header(self, request):
        """
        Resolve organization from the X-Organization-Id HTTP header.

        This allows the SPA frontend to explicitly switch organizations
        by sending the header with each request. The user must be
        authenticated and a member of the target organization.

        Returns:
            Organization instance or None.
        """
        org_id = request.META.get('HTTP_X_ORGANIZATION_ID')
        if not org_id:
            return None

        # Validate UUID format to prevent injection or DoS
        try:
            uuid_module.UUID(str(org_id))
        except (ValueError, TypeError):
            logger.warning(
                'Invalid UUID format in X-Organization-Id header: %s',
                org_id
            )
            return None

        # User must be authenticated to use header-based switching
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            logger.debug(
                'X-Organization-Id header present but user not authenticated'
            )
            return None

        try:
            from .models import Organization, UserOrganizationRole

            organization = Organization.objects.filter(
                pk=org_id, is_active=True
            ).first()

            if organization is None:
                logger.warning(
                    'X-Organization-Id header references non-existent or '
                    'inactive organization: %s', org_id
                )
                return None

            # Superadmin can access any organization
            if request.user.is_staff or request.user.is_superuser:
                return organization

            # Regular users must be members
            is_member = UserOrganizationRole.objects.filter(
                user=request.user,
                organization=organization
            ).exists()

            if not is_member:
                logger.warning(
                    'User %s tried to access organization %s via header '
                    'but is not a member',
                    request.user.pk, org_id
                )
                return None

            return organization

        except Exception as exc:
            logger.warning(
                'Error resolving organization from X-Organization-Id '
                'header: %s', exc
            )
            return None

    def _resolve_by_custom_domain(self, host):
        """Resolve organization by custom domain from DomainSettings."""
        try:
            from .models import DomainSettings

            domain_settings = DomainSettings.objects.select_related(
                'organization'
            ).get(
                custom_domain=host,
                is_verified=True
            )
            return domain_settings.organization
        except DomainSettings.DoesNotExist:
            return None
        except Exception as exc:
            logger.warning(
                'Unexpected error resolving custom domain %s: %s', host, exc
            )
            return None

    def _resolve_by_subdomain(self, host):
        """
        Resolve organization by subdomain.

        Example: org-slug.dam-brand.com -> Organization(slug='org-slug')
        """
        base_domain = SAAS_BASE_DOMAIN

        if not host.endswith(base_domain):
            return None

        # Extract subdomain
        subdomain = host[:-len(base_domain)].rstrip('.')

        if not subdomain or subdomain == 'www' or subdomain == 'app':
            return None

        try:
            from .models import Organization

            return Organization.objects.get(
                slug=subdomain,
                is_active=True
            )
        except Organization.DoesNotExist:
            return None
        except Exception as exc:
            logger.warning(
                'Unexpected error resolving subdomain %s: %s', host, exc
            )
            return None

    def _resolve_by_user(self, user):
        """
        Resolve organization from user's default organization.

        Looks for the UserOrganizationRole with is_default=True.
        """
        try:
            from .models import UserOrganizationRole

            role = UserOrganizationRole.objects.select_related(
                'organization'
            ).filter(
                user=user,
                is_default=True,
                organization__is_active=True
            ).first()

            if role is not None:
                return role.organization

            # Fallback: get first organization for this user
            role = UserOrganizationRole.objects.select_related(
                'organization'
            ).filter(
                user=user,
                organization__is_active=True
            ).first()

            return role.organization if role else None
        except UserOrganizationRole.DoesNotExist:
            return None
        except Exception as exc:
            logger.warning(
                'Unexpected error resolving organization by user %s: %s',
                user.pk, exc
            )
            return None

    def _get_default_organization(self):
        """
        Get the default organization for standalone mode.

        Returns the organization with slug='default', creating it if needed.
        """
        try:
            from .models import Organization
            from .literals import (
                DEFAULT_ORGANIZATION_SLUG,
                DEFAULT_ORGANIZATION_NAME,
                DEFAULT_ORGANIZATION_EMAIL
            )

            organization, created = Organization.objects.get_or_create(
                slug=DEFAULT_ORGANIZATION_SLUG,
                defaults={
                    'name': DEFAULT_ORGANIZATION_NAME,
                    'email': DEFAULT_ORGANIZATION_EMAIL,
                    'is_active': True,
                    'status': 'active',
                    'deployment_mode': 'standalone',
                    'storage_limit_gb': None,  # Unlimited
                    'max_users': 999,
                    'max_ai_analyses_monthly': 999999,
                }
            )

            if created:
                logger.info(
                    'Created default organization: %s',
                    organization.name
                )

            return organization
        except Exception as exc:
            logger.warning(
                'Could not get/create default organization: %s', exc
            )
            return None
