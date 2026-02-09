"""
Tenant-aware managers and mixins for multi-tenancy data isolation.

Uses ContextVar for thread-safe tenant resolution in both sync and async
contexts. All tenant-aware models should use TenantAwareMixin as a base.

Architecture: Shared Database + Shared Schema + ForeignKey isolation.
See: docs/transformation-2025/TZ_Django_Tenant_Isolation.md
"""

import logging
from contextvars import ContextVar

from django.db import models
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(name=__name__)

# Thread-safe context variable for current organization.
# Set by TenantResolverMiddleware on each request.
_current_organization = ContextVar(
    'current_organization', default=None
)


def get_current_organization():
    """
    Get the current organization from the context variable.

    Returns:
        Organization instance or None if not set.
    """
    return _current_organization.get()


def set_current_organization(organization):
    """
    Set the current organization in the context variable.

    Args:
        organization: Organization instance or None to clear.

    Returns:
        Token that can be used to reset the context variable.
    """
    return _current_organization.set(organization)


def clear_current_organization(token=None):
    """
    Clear the current organization from the context variable.

    Args:
        token: Optional token from set_current_organization to reset to
               previous value.
    """
    if token is not None:
        _current_organization.reset(token)
    else:
        _current_organization.set(None)


class TenantAwareQuerySet(models.QuerySet):
    """
    QuerySet that automatically filters by current organization.

    Provides additional methods for explicit organization filtering.
    """

    def for_organization(self, organization):
        """
        Filter queryset for a specific organization.

        Args:
            organization: Organization instance to filter by.

        Returns:
            Filtered QuerySet.
        """
        return self.filter(organization=organization)

    def all_organizations(self):
        """
        Return queryset without tenant filtering.

        Use only for SuperAdmin operations or system-level queries.

        Returns:
            Unfiltered QuerySet.
        """
        # Return the base queryset from the unfiltered manager
        return self.model._default_manager.all()


class TenantAwareManager(models.Manager):
    """
    Manager that automatically filters QuerySet by the current Organization.

    Uses ContextVar for thread-safe organization resolution.
    When no organization is set in context, returns all records
    (for backward compatibility and standalone mode).

    Usage:
        class MyModel(TenantAwareMixin, models.Model):
            # Fields...
            pass

        # Automatic filtering (uses current organization from context)
        MyModel.objects.all()  # Returns only current org's records

        # Explicit filtering
        MyModel.objects.for_organization(org)

        # Unfiltered access (SuperAdmin)
        MyModel.objects_unfiltered.all()
    """

    def get_queryset(self):
        """
        Return QuerySet filtered by the current organization.

        If no organization is set in the context (standalone mode or
        system-level operations), returns all records.
        """
        queryset = TenantAwareQuerySet(self.model, using=self._db)
        organization = get_current_organization()

        if organization is not None:
            queryset = queryset.filter(organization=organization)

        return queryset

    def for_organization(self, organization):
        """
        Explicitly filter by a specific organization.

        Args:
            organization: Organization instance.

        Returns:
            Filtered QuerySet.
        """
        return self.get_queryset().filter(organization=organization)

    def all_organizations(self):
        """
        Return all records without tenant filtering.

        Bypasses automatic organization filtering.
        Use only for SuperAdmin operations.

        Returns:
            Unfiltered QuerySet.
        """
        return TenantAwareQuerySet(
            self.model, using=self._db
        )


# --- Hybrid managers for core Mayan models ---
# These combine TenantAwareManager filtering with the original manager
# functionality, so that monkey-patching Document.objects etc. preserves
# existing behaviour (delete_stubs, get_by_natural_key, trash filtering).


class TenantAwareDocumentManager(TenantAwareManager):
    """
    Hybrid manager for Document model.

    Combines TenantAwareManager (auto org filtering) with
    DocumentManager behaviour (delete_stubs, get_by_natural_key).
    """

    def delete_stubs(self):
        """Delete stale document stubs (copies DocumentManager logic)."""
        from datetime import timedelta

        from django.utils.timezone import now

        from mayan.apps.documents.settings import (
            setting_stub_expiration_interval
        )

        stale_stub_documents = self.filter(
            is_stub=True,
            datetime_created__lt=now() - timedelta(
                seconds=setting_stub_expiration_interval.value
            )
        )
        for stale_stub_document in stale_stub_documents:
            stale_stub_document.delete(to_trash=False)

    def get_by_natural_key(self, uuid):
        from django.utils.encoding import force_text

        return self.get(uuid=force_text(s=uuid))


class TenantAwareTrashCanManager(TenantAwareManager):
    """
    Hybrid manager for Document.trash.

    Returns only trashed documents, filtered by current organization.
    """

    def get_queryset(self):
        return super().get_queryset().filter(in_trash=True)


class TenantAwareValidDocumentManager(TenantAwareManager):
    """
    Hybrid manager for Document.valid.

    Returns only non-trashed documents, filtered by current organization.
    """

    def get_queryset(self):
        return super().get_queryset().filter(in_trash=False)


class TenantAwareMixin(models.Model):
    """
    Abstract model mixin for tenant-aware models.

    Adds:
    - ForeignKey to Organization with index
    - TenantAwareManager as default manager
    - Unfiltered manager for SuperAdmin access

    Usage:
        class Document(TenantAwareMixin, models.Model):
            label = models.CharField(max_length=255)
            # ... other fields

            class Meta(TenantAwareMixin.Meta):
                pass
    """

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_set',
        verbose_name=_('Organization'),
        help_text=_('Organization this record belongs to'),
        db_index=True,
        null=True,
        blank=True
    )

    # Tenant-filtered manager (default)
    objects = TenantAwareManager()

    # Unfiltered manager for SuperAdmin and system operations
    objects_unfiltered = models.Manager()

    class Meta:
        abstract = True
        indexes = [
            models.Index(
                fields=['organization'],
                name='%(app_label)s_%(class)s_org_idx'
            ),
        ]

    def save(self, *args, **kwargs):
        """
        Auto-populate organization from context if not set.
        """
        if self.organization_id is None:
            current_org = get_current_organization()
            if current_org is not None:
                self.organization = current_org

        super().save(*args, **kwargs)
