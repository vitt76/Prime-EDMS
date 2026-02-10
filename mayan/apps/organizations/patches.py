import logging

import django.db.models.deletion
from django.db import models
from django.http.request import HttpRequest
from django.utils.functional import cached_property

from .settings import setting_organization_installation_url

logger = logging.getLogger(name=__name__)


def patch_organization_fields():
    """
    Dynamically add ``organization`` ForeignKey to core Mayan models.

    The underlying DB columns already exist (migrations documents/0085-0086,
    tags/0010-0011, cabinets/0007-0008).  This function adds the matching
    Python-level field definitions so that Django ORM lookups like
    ``document__organization`` or ``DocumentFile.objects.filter(
    document__organization=org)`` work correctly.

    Must be called from ``OrganizationsApp.ready()`` **before** any code
    that uses these lookups.
    """
    from mayan.apps.documents.models import Document

    if not _has_concrete_field(Document, 'organization'):
        field = models.ForeignKey(
            'organizations.Organization',
            on_delete=django.db.models.deletion.CASCADE,
            related_name='documents',
            verbose_name='Organization',
            help_text='Organization this document belongs to',
            db_index=True,
        )
        field.contribute_to_class(Document, 'organization')
        logger.info('Patched Document with organization FK')

    try:
        from mayan.apps.tags.models import Tag

        if not _has_concrete_field(Tag, 'organization'):
            field = models.ForeignKey(
                'organizations.Organization',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='tags',
                verbose_name='Organization',
                help_text='Organization this tag belongs to',
                db_index=True,
            )
            field.contribute_to_class(Tag, 'organization')
            logger.info('Patched Tag with organization FK')
    except ImportError:
        logger.warning('Could not import Tag model for patching')

    try:
        from mayan.apps.cabinets.models import Cabinet

        if not _has_concrete_field(Cabinet, 'organization'):
            field = models.ForeignKey(
                'organizations.Organization',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='cabinets',
                verbose_name='Organization',
                help_text='Organization this cabinet belongs to',
                db_index=True,
            )
            field.contribute_to_class(Cabinet, 'organization')
            logger.info('Patched Cabinet with organization FK')
    except ImportError:
        logger.warning('Could not import Cabinet model for patching')


def _has_concrete_field(model, field_name):
    """Check if model already has a concrete field with the given name."""
    try:
        field = model._meta.get_field(field_name)
        return field.concrete
    except Exception:
        return False


def patch_HttpRequest():
    class MockClass:
        @cached_property
        def _patched_current_scheme_host(self):
            if setting_organization_installation_url.value:
                return setting_organization_installation_url.value
            else:
                return self._original_current_scheme_host

    _original_current_scheme_host = HttpRequest._current_scheme_host

    HttpRequest._current_scheme_host = MockClass._patched_current_scheme_host
    HttpRequest._original_current_scheme_host = _original_current_scheme_host


def patch_document_managers():
    """
    Replace Document model managers with tenant-aware hybrid versions.

    This monkey-patches Document.objects, Document.trash and Document.valid
    so that all QuerySets are automatically filtered by the current
    Organization from the ContextVar. The hybrid managers preserve the
    original manager functionality (delete_stubs, get_by_natural_key,
    trash/valid filtering).

    Must be called from OrganizationsApp.ready() AFTER all models are loaded.
    """
    from mayan.apps.documents.models import Document

    from .managers import (
        TenantAwareDocumentManager,
        TenantAwareTrashCanManager,
        TenantAwareValidDocumentManager
    )

    # Store originals for debugging / potential rollback
    Document._original_objects_manager = Document.objects
    Document._original_trash_manager = Document.trash
    Document._original_valid_manager = Document.valid

    # Create new manager instances and bind to model
    tenant_objects = TenantAwareDocumentManager()
    tenant_objects.auto_created = False
    tenant_objects.model = Document
    tenant_objects.name = 'objects'
    tenant_objects.creation_counter = Document.objects.creation_counter
    Document.objects = tenant_objects

    tenant_trash = TenantAwareTrashCanManager()
    tenant_trash.auto_created = False
    tenant_trash.model = Document
    tenant_trash.name = 'trash'
    tenant_trash.creation_counter = Document.trash.creation_counter
    Document.trash = tenant_trash

    tenant_valid = TenantAwareValidDocumentManager()
    tenant_valid.auto_created = False
    tenant_valid.model = Document
    tenant_valid.name = 'valid'
    tenant_valid.creation_counter = Document.valid.creation_counter
    Document.valid = tenant_valid

    logger.info(
        'Document managers patched with tenant-aware versions'
    )
