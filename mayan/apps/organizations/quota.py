"""
Quota enforcement utilities for multi-tenancy.

Provides functions and a signal handler to check storage, user, and AI
analysis quotas before allowing resource-consuming operations.

Integration points:
- ``pre_save`` signal on DocumentFile -> ``check_storage_quota()``
- ``analyze_document_with_ai()`` task -> ``check_ai_quota()``
- ``OrganizationMembersView.post()`` -> ``check_user_quota()``
"""

import logging

logger = logging.getLogger(name=__name__)


class QuotaExceededException(Exception):
    """
    Raised when an organization's resource quota has been exceeded.

    Attributes:
        quota_type: Type of quota exceeded (storage, users, ai_analyses).
        organization: The Organization instance.
        current_value: Current usage value.
        limit_value: Maximum allowed value.
        http_status: Suggested HTTP status code (402 or 429).
    """

    def __init__(
        self, quota_type, organization, current_value, limit_value,
        http_status=429
    ):
        self.quota_type = quota_type
        self.organization = organization
        self.current_value = current_value
        self.limit_value = limit_value
        self.http_status = http_status
        super().__init__(
            'Quota exceeded: {quota_type} ({current}/{limit}) '
            'for organization "{org}"'.format(
                quota_type=quota_type,
                current=current_value,
                limit=limit_value,
                org=organization.name
            )
        )


def check_storage_quota(organization):
    """
    Check if the organization's storage quota allows more uploads.

    Args:
        organization: Organization instance.

    Raises:
        QuotaExceededException: If storage limit is exceeded.
    """
    if organization is None:
        return

    if organization.storage_limit_gb is None:
        return  # Unlimited

    used_gb = organization.get_storage_used_gb()
    limit_gb = organization.storage_limit_gb

    if used_gb >= limit_gb:
        logger.warning(
            'Storage quota exceeded for organization %s: '
            '%.2f GB used of %d GB limit',
            organization.slug, used_gb, limit_gb
        )
        raise QuotaExceededException(
            quota_type='storage',
            organization=organization,
            current_value=used_gb,
            limit_value=limit_gb,
            http_status=402
        )


def check_user_quota(organization):
    """
    Check if the organization can add more users.

    Args:
        organization: Organization instance.

    Raises:
        QuotaExceededException: If user limit is exceeded.
    """
    if organization is None:
        return

    active_users = organization.get_active_users_count()
    max_users = organization.max_users

    if active_users >= max_users:
        logger.warning(
            'User quota exceeded for organization %s: '
            '%d users of %d limit',
            organization.slug, active_users, max_users
        )
        raise QuotaExceededException(
            quota_type='users',
            organization=organization,
            current_value=active_users,
            limit_value=max_users,
            http_status=402
        )


def check_ai_quota(organization):
    """
    Check if the organization can perform more AI analyses this month.

    Uses the cached ``Organization.get_ai_analyses_this_month()`` method
    to stay consistent with how ``check_storage_quota`` and
    ``check_user_quota`` use cached model methods.

    Args:
        organization: Organization instance.

    Raises:
        QuotaExceededException: If monthly AI analysis limit is exceeded.
    """
    if organization is None:
        return

    analyses_this_month = organization.get_ai_analyses_this_month()
    max_analyses = organization.max_ai_analyses_monthly

    if analyses_this_month >= max_analyses:
        logger.warning(
            'AI analysis quota exceeded for organization %s: '
            '%d analyses of %d monthly limit',
            organization.slug, analyses_this_month, max_analyses
        )
        raise QuotaExceededException(
            quota_type='ai_analyses',
            organization=organization,
            current_value=analyses_this_month,
            limit_value=max_analyses,
            http_status=429
        )


def on_document_file_pre_save(sender, instance, **kwargs):
    """
    Signal handler: check storage quota before saving a DocumentFile.

    Connected in OrganizationsApp.ready().
    """
    # Only check for new files (not updates to existing ones)
    if instance.pk:
        return

    try:
        document = instance.document
        organization = getattr(document, 'organization', None)
        if organization is not None:
            check_storage_quota(organization)
    except QuotaExceededException:
        raise
    except (AttributeError, ValueError, TypeError) as exc:
        logger.warning(
            'Error checking storage quota in pre_save signal: %s', exc
        )
    except Exception as exc:
        logger.error(
            'Unexpected error in storage quota pre_save signal: %s',
            exc, exc_info=True
        )
