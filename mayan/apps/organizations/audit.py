"""
Audit logging for multi-tenancy critical operations.

Provides structured logging for SIEM-compatible event tracking.
All organization-level events are logged through ``log_org_event()``.

Events logged:
- Organization lifecycle: create, update, suspend, archive, activate
- Membership: member_add, member_remove, role_change
- Subscription: plan_change, subscription_status_change
- Quota: quota_exceeded
"""

import logging

logger = logging.getLogger('organizations.audit')


# Event type constants
EVENT_ORG_CREATE = 'org.create'
EVENT_ORG_UPDATE = 'org.update'
EVENT_ORG_SUSPEND = 'org.suspend'
EVENT_ORG_ARCHIVE = 'org.archive'
EVENT_ORG_ACTIVATE = 'org.activate'

EVENT_MEMBER_ADD = 'member.add'
EVENT_MEMBER_REMOVE = 'member.remove'
EVENT_MEMBER_ROLE_CHANGE = 'member.role_change'

EVENT_PLAN_CHANGE = 'subscription.plan_change'
EVENT_SUBSCRIPTION_STATUS = 'subscription.status_change'

EVENT_QUOTA_EXCEEDED = 'quota.exceeded'


def log_org_event(organization, action, user=None, details=None):
    """
    Log an organization-level audit event.

    Uses structured logging so events can be parsed by SIEM tools
    (Elasticsearch, Splunk, Graylog).

    Args:
        organization: Organization instance.
        action: Event type string (use constants above).
        user: User who triggered the event (optional).
        details: Dict with additional context (optional).
    """
    extra = {
        'audit_event': True,
        'org_id': str(organization.pk) if organization else None,
        'org_slug': organization.slug if organization else None,
        'action': action,
        'user_id': user.pk if user else None,
        'username': user.username if user else None,
    }
    if details:
        extra['details'] = details

    logger.info(
        'AUDIT org=%s action=%s user=%s details=%s',
        extra.get('org_slug', 'N/A'),
        action,
        extra.get('username', 'system'),
        details or {},
        extra=extra
    )
