import uuid as uuid_module
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db import connection, models, transaction
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from mayan.apps.acls.models import AccessControlList
from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.events.classes import EventManagerMethodAfter, EventManagerSave
from mayan.apps.events.decorators import method_event

from .events import (
    event_cabinet_created, event_cabinet_edited, event_cabinet_document_added,
    event_cabinet_document_removed
)


class Cabinet(ExtraDataModelMixin, MPTTModel):
    """
    Model to store a hierarchical tree of document containers. Each container
    can store an unlimited number of documents using an M2M field. Only
    the top level container is can have an ACL. All child container's
    access is delegated to their corresponding root container.
    Tenant-scoped via organization FK (Phase 3 organizations integration).
    """
    parent = TreeForeignKey(
        blank=True, db_index=True, null=True, on_delete=models.CASCADE,
        related_name='children', to='self'
    )
    label = models.CharField(
        help_text=_('A short text used to identify the cabinet.'),
        max_length=128, verbose_name=_('Label')
    )
    organization = models.ForeignKey(
        help_text=_('Organization this cabinet belongs to'),
        on_delete=models.CASCADE, related_name='cabinets',
        to='organizations.Organization', verbose_name=_('Organization')
    )
    documents = models.ManyToManyField(
        blank=True, related_name='cabinets', to=Document,
        verbose_name=_('Documents')
    )

    class MPTTMeta:
        order_insertion_by = ('label',)

    class Meta:
        # unique_together: per-organization uniqueness of (parent, label)
        unique_together = ('organization', 'parent', 'label')
        verbose_name = _('Cabinet')
        verbose_name_plural = _('Cabinets')

    def __str__(self):
        return self.get_full_path()

    @method_event(
        action_object='self',
        event=event_cabinet_document_added,
        event_manager_class=EventManagerMethodAfter,
    )
    def document_add(self, document):
        self._event_target = document
        self.documents.add(document)

    @method_event(
        action_object='self',
        event=event_cabinet_document_removed,
        event_manager_class=EventManagerMethodAfter,
    )
    def document_remove(self, document):
        self._event_target = document
        self.documents.remove(document)

    def get_absolute_url(self):
        return reverse(
            viewname='cabinets:cabinet_view', kwargs={
                'cabinet_id': self.pk
            }
        )

    def get_documents(self, permission=None, user=None):
        """
        Provide a queryset of the documents in a cabinet. The queryset is
        filtered by access.
        """
        queryset = Document.valid.filter(pk__in=self.documents.all())

        if permission and user:
            queryset = AccessControlList.objects.restrict_queryset(
                permission=permission, queryset=queryset,
                user=user
            )

        return queryset

    def get_document_count(self, user):
        """
        Return numeric count of the total documents in a cabinet. The count
        is filtered by access.
        """
        return self.get_documents(
            permission=permission_document_view, user=user
        ).count()

    def get_full_path(self):
        """
        Returns a string that represents the path to the cabinet. The
        path string starts from the root cabinet.
        """
        result = []
        for node in self.get_ancestors(include_self=True):
            result.append(node.label)

        return ' / '.join(result)
    get_full_path.help_text = _(
        'The path to the cabinet including all ancestors.'
    )
    get_full_path.short_description = _('Full path')

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'event': event_cabinet_created,
            'target': 'self',
        },
        edited={
            'event': event_cabinet_edited,
            'target': 'self',
        }
    )
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    def validate_unique(self, exclude=None):
        """
        Explicit validation of uniqueness of organization+parent+label as the
        provided unique_together check in Meta is not working for all 100% cases
        when there is a FK in the unique_together tuple
        https://code.djangoproject.com/ticket/1751
        """
        with transaction.atomic():
            if connection.vendor == 'oracle':
                queryset = Cabinet.objects.filter(
                    organization=self.organization,
                    parent=self.parent,
                    label=self.label
                )
            else:
                queryset = Cabinet.objects.select_for_update().filter(
                    organization=self.organization,
                    parent=self.parent,
                    label=self.label
                )

            if queryset.exists():
                params = {
                    'model_name': _('Cabinet'),
                    'field_labels': _('Organization, Parent and Label')
                }
                raise ValidationError(
                    {
                        NON_FIELD_ERRORS: [
                            ValidationError(
                                message=_(
                                    '%(model_name)s with this %(field_labels)s already '
                                    'exists.'
                                ), code='unique_together', params=params,
                            )
                        ],
                    },
                )


class CabinetSearchResult(Cabinet):
    """
    Represent a cabinet's search result. This model is a proxy model from
    Cabinet and is used as an alias to map columns to it without having to
    map them to the base Cabinet model.
    """
    class Meta:
        proxy = True
        verbose_name = _('Cabinet')
        verbose_name_plural = _('Cabinets')


class DocumentCabinet(Cabinet):
    """
    Represent a document's cabinet. This Model is a proxy model from Cabinet
    and is used as an alias to map columns to it without having to map them
    to the base Cabinet model.
    """
    class Meta:
        proxy = True
        verbose_name = _('Document cabinet')
        verbose_name_plural = _('Document cabinets')


class CabinetShare(models.Model):
    """
    Public share link for a cabinet (collection). Allows read-only access
    to the cabinet's documents via a unique UUID, with optional expiry
    and password. Tenant-scoped via organization.
    """
    uuid = models.UUIDField(
        default=uuid_module.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        help_text=_('Unique public link identifier')
    )
    cabinet = models.ForeignKey(
        Cabinet,
        on_delete=models.CASCADE,
        related_name='shares',
        help_text=_('Cabinet (collection) this share exposes')
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='cabinet_shares',
        help_text=_('Organization (tenant) this share belongs to')
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('When this share link expires')
    )
    password_hash = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text=_('Hashed password for link protection')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_cabinet_shares',
        help_text=_('User who created this share')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Cabinet share')
        verbose_name_plural = _('Cabinet shares')
        indexes = [
            models.Index(
                fields=['organization', '-created_at'],
                name='idx_cabinet_share_org_created',
            ),
        ]

    def __str__(self):
        return f"{self.cabinet.label} → {self.uuid}"

    def set_password(self, raw_password):
        if raw_password:
            self.password_hash = make_password(raw_password)
        else:
            self.password_hash = None

    def check_password(self, raw_password):
        if not self.password_hash:
            return True
        return check_password(raw_password, self.password_hash)

    def is_expired(self):
        if not self.expires_at:
            return False
        from django.utils.timezone import now
        return now() >= self.expires_at
