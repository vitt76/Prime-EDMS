import logging

from django.http.request import HttpRequest
from django.utils.functional import cached_property

from .settings import setting_organization_installation_url

logger = logging.getLogger(name=__name__)


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
