"""
SavedSearch model — tenant-aware saved search (Phase 5.3 Sprint 1 Backend).

Stores name, query string and filters (orientation, document_type, dates, tags, etc.)
for reuse in the headless API. Isolated by user and organization.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class SavedSearch(models.Model):
    """
    User-defined saved search: name, full-text query and filters.
    Tenant-scoped: user + organization.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_searches',
        verbose_name=_('User'),
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='saved_searches',
        verbose_name=_('Organization'),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_('Name'),
    )
    query = models.CharField(
        max_length=512,
        blank=True,
        default='',
        verbose_name=_('Query'),
        help_text=_('Full-text search query (q)'),
    )
    filters = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Filters'),
        help_text=_('Filters: orientation, document_type__label__in, tags__label__in, datetime_created__gte, etc.'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at'),
    )
    notification_enabled = models.BooleanField(
        default=False,
        verbose_name=_('Notification enabled'),
    )
    last_notified_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Last notified at'),
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Saved search')
        verbose_name_plural = _('Saved searches')

    def __str__(self):
        return f'{self.name} ({self.user_id})'
