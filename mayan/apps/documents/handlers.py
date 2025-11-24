import logging

from django.apps import apps

logger = logging.getLogger(name=__name__)

from .literals import (
    DEFAULT_DOCUMENT_TYPE_LABEL, STORAGE_NAME_DOCUMENT_FILE_PAGE_IMAGE_CACHE,
    STORAGE_NAME_DOCUMENT_VERSION_PAGE_IMAGE_CACHE
)
from .settings import (
    setting_document_file_page_image_cache_maximum_size,
    setting_document_version_page_image_cache_maximum_size
)
from .signals import signal_post_initial_document_type


def handler_create_default_document_type(sender, **kwargs):
    DocumentType = apps.get_model(
        app_label='documents', model_name='DocumentType'
    )

    if not DocumentType.objects.count():
        document_type = DocumentType.objects.create(
            label=DEFAULT_DOCUMENT_TYPE_LABEL
        )
        signal_post_initial_document_type.send(
            sender=DocumentType, instance=document_type
        )


def handler_create_document_file_page_image_cache(sender, **kwargs):
    Cache = apps.get_model(app_label='file_caching', model_name='Cache')
    Cache.objects.update_or_create(
        defaults={
            'maximum_size': setting_document_file_page_image_cache_maximum_size.value,
        }, defined_storage_name=STORAGE_NAME_DOCUMENT_FILE_PAGE_IMAGE_CACHE,
    )


def handler_create_document_version_page_image_cache(sender, **kwargs):
    Cache = apps.get_model(app_label='file_caching', model_name='Cache')
    Cache.objects.update_or_create(
        defaults={
            'maximum_size': setting_document_version_page_image_cache_maximum_size.value,
        }, defined_storage_name=STORAGE_NAME_DOCUMENT_VERSION_PAGE_IMAGE_CACHE,
    )


# Document indexing coordination handlers

def handler_coordinate_document_index(sender, instance, created, **kwargs):
    """
    Unified handler for document indexing coordination.
    
    This handler replaces the separate handlers from Dynamic Search and
    Document Indexing, ensuring documents are indexed in both systems
    through a single coordinated process.
    """
    from .tasks import task_coordinate_document_index
    
    # Skip if document is a stub (no file uploaded yet)
    # Use safe check to avoid AttributeError if is_stub is not defined
    if getattr(instance, 'is_stub', False):
        return
    
    # Check if document is valid (not in trash, has files)
    # Use the valid manager to check
    try:
        Document = sender
        if not Document.valid.filter(pk=instance.pk).exists():
            return
    except Exception:
        # If check fails, proceed anyway (document might be newly created)
        pass
    
    # Check for duplicate indexing using distributed lock
    # This prevents multiple indexing tasks for the same document
    # Short-term lock (30 seconds) - only to prevent duplicate scheduling
    lock_name = 'indexing_document_{}'.format(instance.pk)
    lock = None
    try:
        from mayan.apps.lock_manager.backends.base import LockingBackend
        from mayan.apps.lock_manager.exceptions import LockError
        
        try:
            lock = LockingBackend.get_backend().acquire_lock(
                name=lock_name,
                timeout=30  # 30 seconds - short-term lock for scheduling only
            )
            logger.debug('Acquired short-term lock for document %s scheduling', instance.pk)
        except LockError:
            # Lock already held - another indexing task is in progress
            # Skip scheduling to avoid duplicate indexing
            logger.debug(
                'Document %s indexing already in progress (lock held), skipping',
                instance.pk
            )
            return
    except ImportError:
        # Lock manager not available, proceed without deduplication
        logger.warning('Lock manager not available, proceeding without deduplication')
        pass
    
    # Schedule coordinated indexing
    try:
        task_coordinate_document_index.apply_async(
            kwargs={
                'document_id': instance.pk,
                'created': created
            },
            queue='indexing'  # Use unified queue
        )
        logger.debug('Scheduled indexing coordination task for document %s', instance.pk)
    finally:
        # Always release lock after scheduling (success or failure)
        # Long-term lock will be held by coordinator until chain completes
        if lock:
            try:
                lock.release()
                logger.debug('Released short-term lock for document %s after scheduling', instance.pk)
            except Exception as e:
                logger.warning(
                    'Error releasing short-term lock for document %s: %s',
                    instance.pk, e
                )


def handler_coordinate_document_deindex(sender, instance, **kwargs):
    """
    Unified handler for document deindexing coordination.
    
    This handler ensures documents are removed from both Dynamic Search
    and Document Indexing systems through a single coordinated process.
    """
    from .tasks import task_coordinate_document_deindex
    
    # Schedule coordinated deindexing
    task_coordinate_document_deindex.apply_async(
        kwargs={'document_id': instance.pk},
        queue='indexing'  # Use unified queue
    )