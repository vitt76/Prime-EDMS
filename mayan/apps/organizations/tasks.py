"""
Celery task utilities for organization-aware (tenant-aware) task execution.

Celery tasks run outside the HTTP request cycle and therefore do not pass
through TenantResolverMiddleware. TenantAwareTask provides a base class
that extracts ``organization_id`` from task kwargs, resolves the
Organization, and sets the ContextVar so that TenantAwareManager
automatically filters querysets within the task body.

Usage::

    from mayan.apps.organizations.tasks import TenantAwareTask

    @shared_task(bind=True, base=TenantAwareTask, queue='tools')
    def my_task(self, document_id, **kwargs):
        # organization_id is already consumed by TenantAwareTask.__call__
        # ContextVar is set -- TenantAwareManager filters automatically
        doc = Document.objects.get(pk=document_id)
        ...

When scheduling a task, always pass ``organization_id``::

    my_task.delay(document_id=42, organization_id=str(org.pk))
"""

import logging

from celery import Task

from .managers import set_current_organization, clear_current_organization

logger = logging.getLogger(name=__name__)


class TenantAwareTask(Task):
    """
    Base Celery Task that sets organization context from task kwargs.

    The ``organization_id`` kwarg is popped from kwargs before the
    task body runs, so the task function does not need to handle it.
    """

    def __call__(self, *args, **kwargs):
        organization_id = kwargs.pop('organization_id', None)
        token = None

        if organization_id:
            try:
                from .models import Organization
                organization = Organization.objects.get(pk=organization_id)
                token = set_current_organization(organization)
                logger.debug(
                    'TenantAwareTask: set organization context to %s '
                    'for task %s',
                    organization.slug, self.name
                )
            except Exception as exc:
                logger.warning(
                    'TenantAwareTask: could not resolve organization %s '
                    'for task %s: %s',
                    organization_id, self.name, exc
                )

        try:
            return super().__call__(*args, **kwargs)
        finally:
            if token is not None:
                clear_current_organization(token)
                logger.debug(
                    'TenantAwareTask: cleared organization context '
                    'for task %s', self.name
                )
