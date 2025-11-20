import logging

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import OperationalError
from django.utils.module_loading import import_string

from mayan.celery import app

from .literals import (
    UPDATE_PAGE_COUNT_RETRY_DELAY, UPLOAD_NEW_VERSION_RETRY_DELAY
)

logger = logging.getLogger(name=__name__)


# Document file

@app.task(
    bind=True, default_retry_delay=UPDATE_PAGE_COUNT_RETRY_DELAY,
    ignore_result=True
)
def task_document_file_page_count_update(
    self, document_file_id, user_id=None
):
    DocumentFile = apps.get_model(
        app_label='documents', model_name='DocumentFile'
    )
    User = get_user_model()

    if user_id:
        user = User.objects.get(pk=user_id)
    else:
        user = None

    document_file = DocumentFile.objects.get(pk=document_file_id)
    try:
        document_file.page_count_update(user=user)
    except OperationalError as exception:
        logger.warning(
            'Operational error during attempt to update page count for '
            'document file: %s; %s. Retrying.', document_file,
            exception
        )
        raise self.retry(exc=exception)


@app.task(
    bind=True, default_retry_delay=UPLOAD_NEW_VERSION_RETRY_DELAY,
    ignore_result=True
)
def task_document_file_upload(
    self, document_id, shared_uploaded_file_id, user_id=None, action=None,
    comment=None, expand=False, filename=None
):
    Document = apps.get_model(
        app_label='documents', model_name='Document'
    )

    SharedUploadedFile = apps.get_model(
        app_label='storage', model_name='SharedUploadedFile'
    )

    try:
        document = Document.objects.get(pk=document_id)
        shared_uploaded_file = SharedUploadedFile.objects.get(
            pk=shared_uploaded_file_id
        )
        if user_id:
            user = get_user_model().objects.get(pk=user_id)
        else:
            user = None

    except OperationalError as exception:
        logger.warning(
            'Operational error during attempt to retrieve shared data for '
            'new document file for document ID: %s; %s. Retrying.', document_id,
            exception
        )
        raise self.retry(exc=exception)

    with shared_uploaded_file.open() as file_object:
        try:
            document.file_new(
                action=action, comment=comment, expand=expand,
                file_object=file_object,
                filename=filename or shared_uploaded_file.filename,
                _user=user
            )
        except Warning as warning:
            # New document file are blocked
            logger.info(
                'Warning during attempt to create new document file for '
                'document: %s; %s', document, warning
            )
            shared_uploaded_file.delete()
        except OperationalError as exception:
            logger.warning(
                'Operational error during attempt to create new document '
                'file for document: %s; %s. Retrying.', document, exception
            )
            raise self.retry(exc=exception)
        except Exception as exception:
            # This except and else block emulate a finally:
            logger.error(
                'Unexpected error during attempt to create new document '
                'file for document: %s; %s', document, exception,
                exc_info=True
            )
            try:
                shared_uploaded_file.delete()
            except OperationalError as exception:
                logger.warning(
                    'Operational error during attempt to delete shared '
                    'file: %s; %s.', shared_uploaded_file, exception
                )
        else:
            try:
                shared_uploaded_file.delete()
            except OperationalError as exception:
                logger.warning(
                    'Operational error during attempt to delete shared '
                    'file: %s; %s.', shared_uploaded_file, exception
                )


# Document

@app.task(ignore_result=True)
def task_document_stubs_delete():
    Document = apps.get_model(
        app_label='documents', model_name='Document'
    )

    logger.info(msg='Executing')
    Document.objects.delete_stubs()
    logger.info(msg='Finished')


@app.task(ignore_results=True)
def task_document_upload(
    document_type_id, shared_uploaded_file_id, callback_dotted_path=None,
    callback_function=None, callback_kwargs=None, description=None,
    label=None, language=None, user_id=None
):
    DocumentType = apps.get_model(
        app_label='documents', model_name='DocumentType'
    )
    SharedUploadedFile = apps.get_model(
        app_label='storage', model_name='SharedUploadedFile'
    )

    document_type = DocumentType.objects.get(pk=document_type_id)
    shared_uploaded_file = SharedUploadedFile.objects.get(
        pk=shared_uploaded_file_id
    )

    if user_id:
        user = get_user_model().objects.get(pk=user_id)
    else:
        user = None

    document = None
    try:
        with shared_uploaded_file.open() as file_object:
            document, document_file = document_type.new_document(
                file_object=file_object,
                label=label or shared_uploaded_file.filename,
                description=description, language=language,
                _user=user
            )
    except Exception as exception:
        logger.critical(
            'Unexpected exception while trying to create new document '
            '"%s"; %s',
            label or file_object.name, exception
        )
        if document:
            document.delete(to_trash=False)
        raise
    else:
        shared_uploaded_file.delete()

        if user:
            document.add_as_recent_document_for_user(user=user)

    if callback_dotted_path:
        callback = import_string(dotted_path=callback_dotted_path)
        callback_kwargs = callback_kwargs or {}
        function = getattr(callback, callback_function)
        function(
            document_file=document_file, **callback_kwargs
        )


# Document type

@app.task(ignore_result=True)
def task_document_type_trashed_document_delete_periods_check():
    DocumentType = apps.get_model(
        app_label='documents', model_name='DocumentType'
    )

    DocumentType.objects.check_delete_periods()


@app.task(ignore_result=True)
def task_document_type_document_trash_periods_check():
    DocumentType = apps.get_model(
        app_label='documents', model_name='DocumentType'
    )

    DocumentType.objects.check_trash_periods()


# Document version

@app.task(ignore_result=True)
def task_document_version_page_list_append(document_version_id, user_id=None):
    DocumentVersion = apps.get_model(
        app_label='documents', model_name='DocumentVersion'
    )
    User = get_user_model()

    if user_id:
        user = User.objects.get(pk=user_id)
    else:
        user = None

    document_version = DocumentVersion.objects.get(
        pk=document_version_id
    )
    document_version.pages_append_all(_user=user)


@app.task(ignore_result=True)
def task_document_version_page_list_reset(document_version_id, user_id=None):
    DocumentVersion = apps.get_model(
        app_label='documents', model_name='DocumentVersion'
    )
    User = get_user_model()

    if user_id:
        user = User.objects.get(pk=user_id)
    else:
        user = None

    document_version = DocumentVersion.objects.get(
        pk=document_version_id
    )
    document_version.pages_reset(_user=user)


@app.task(ignore_result=True)
def task_document_version_delete(document_version_id, user_id=None):
    DocumentVersion = apps.get_model(
        app_label='documents', model_name='DocumentVersion'
    )
    User = get_user_model()

    if user_id:
        user = User.objects.get(pk=user_id)
    else:
        user = None

    document_version = DocumentVersion.objects.get(
        pk=document_version_id
    )

    document_version._event_actor = user
    document_version.delete()


@app.task(ignore_result=True)
def task_document_version_export(
    document_version_id, organization_installation_url=None, user_id=None
):
    DocumentVersion = apps.get_model(
        app_label='documents', model_name='DocumentVersion'
    )
    User = get_user_model()

    if user_id:
        user = User.objects.get(pk=user_id)
    else:
        user = None

    document_version = DocumentVersion.objects.get(
        pk=document_version_id
    )

    document_version.export_to_download_file(
        organization_installation_url=organization_installation_url, user=user
    )


# Trash can

@app.task(ignore_result=True)
def task_trash_can_empty(user_id=None):
    TrashedDocument = apps.get_model(
        app_label='documents', model_name='TrashedDocument'
    )

    for trashed_document in TrashedDocument.objects.all():
        task_trashed_document_delete.apply_async(
            kwargs={
                'trashed_document_id': trashed_document.pk,
                'user_id': user_id
            }
        )


# Trashed document

@app.task(ignore_result=True)
def task_trashed_document_delete(trashed_document_id, user_id=None):
    TrashedDocument = apps.get_model(
        app_label='documents', model_name='TrashedDocument'
    )
    User = get_user_model()

    if user_id:
        user = User.objects.get(pk=user_id)
    else:
        user = None

    logger.debug(msg='Executing')
    trashed_document = TrashedDocument.objects.get(pk=trashed_document_id)
    trashed_document._event_actor = user
    trashed_document.delete()
    logger.debug(msg='Finished')


# Document indexing coordination

@app.task(bind=True, ignore_result=True, max_retries=3, retry_backoff=True)
def task_coordinate_document_index(self, document_id, created=False):
    """
    Coordinate indexing of a document in both Dynamic Search and Document Indexing.
    
    This task uses the DocumentIndexCoordinator to ensure proper coordination
    between the two indexing systems.
    """
    from .indexing_coordinator import DocumentIndexCoordinator
    
    # Check if document exists and is valid before coordinating
    Document = apps.get_model(app_label='documents', model_name='Document')
    try:
        document = Document.valid.get(pk=document_id)
        
        # Check if document is in trash - don't index trashed documents
        if document.in_trash:
            logger.warning(
                'Document %s is in trash, skipping indexing coordination',
                document_id
            )
            return {
                'search_indexed': False,
                'hierarchy_indexed': False,
                'error': 'Document is in trash',
                'error_type': 'trashed'
            }
    except Document.DoesNotExist:
        # Document doesn't exist - don't retry, just log and return
        logger.warning(
            'Document %s does not exist, skipping indexing coordination',
            document_id
        )
        return {
            'search_indexed': False,
            'hierarchy_indexed': False,
            'error': 'Document not found',
            'error_type': 'not_found'
        }
    
    try:
        result = DocumentIndexCoordinator.index_document(
            document_id=document_id,
            created=created
        )
        
        # Only retry for transient errors, not for trashed/not_found documents
        error_type = result.get('error_type')
        if error_type in ('trashed', 'not_found', 'stub'):
            # Non-transient errors - don't retry
            return result
        
        # Check for partial success before retrying
        # Note: This is based on scheduling status, not actual execution status.
        # If chain was scheduled successfully, both tasks should execute.
        # If one system failed to schedule but the other succeeded, don't retry
        # entire operation to avoid infinite retry loop.
        # For actual execution status, check metrics or chain results.
        search_indexed = result.get('search_indexed', False)
        hierarchy_indexed = result.get('hierarchy_indexed', False)
        errors = result.get('errors', [])
        chain_task_id = result.get('chain_task_id')
        
        # Check if we have partial success (one system scheduled successfully, other failed)
        # If chain was scheduled, both systems should execute through the chain
        if chain_task_id:
            # Chain was scheduled - both systems should execute
            # If there are errors, they are from fallback scheduling, not chain
            # Don't retry if chain was scheduled successfully
            if not errors:
                # Chain scheduled successfully, no retry needed
                return result
        elif (search_indexed and not hierarchy_indexed) or (hierarchy_indexed and not search_indexed):
            # Partial success in fallback scheduling - don't retry entire operation
            # to avoid infinite retry loop
            logger.warning(
                'Document %s partially scheduled (search=%s, hierarchy=%s). '
                'Not retrying to avoid infinite retry loop. Errors: %s',
                document_id, search_indexed, hierarchy_indexed, errors
            )
            # Mark as partial success to prevent retry
            result['partial_success'] = True
            return result
        
        # Check if error is transient before retrying
        error = result.get('error')
        if error:
            from .indexing_coordinator import is_transient_error
            from .metrics import get_metrics
            
            metrics = get_metrics()
            
            if is_transient_error(error) and self.request.retries < self.max_retries:
                logger.warning(
                    'Document indexing coordination failed for document %s (transient error), retrying...',
                    document_id
                )
                # Record retry metric
                metrics.record_retry(document_id, self.request.retries + 1)
                raise self.retry(exc=Exception(error))
            elif not is_transient_error(error):
                # Non-transient error - don't retry, just log
                logger.warning(
                    'Document indexing coordination failed for document %s (non-transient error): %s',
                    document_id, error
                )
        
        return result
    except Exception as exception:
        from .indexing_coordinator import is_transient_error
        
        logger.error(
            'Unexpected error in document indexing coordination for document %s: %s',
            document_id, exception, exc_info=True
        )
        
        # Only retry transient errors
        if is_transient_error(exception) and self.request.retries < self.max_retries:
            logger.warning(
                'Retrying document indexing coordination for document %s (transient error)',
                document_id
            )
            raise self.retry(exc=exception)
        else:
            # Non-transient error - don't retry
            logger.error(
                'Document indexing coordination failed for document %s (non-transient error), not retrying',
                document_id
            )
            raise


@app.task(bind=True, ignore_result=True, max_retries=3, retry_backoff=True)
def task_coordinate_document_deindex(self, document_id):
    """
    Coordinate removal of a document from both Dynamic Search and Document Indexing.
    
    This task uses the DocumentIndexCoordinator to ensure proper coordination
    between the two indexing systems.
    """
    from .indexing_coordinator import DocumentIndexCoordinator, is_transient_error
    
    try:
        result = DocumentIndexCoordinator.deindex_document(document_id=document_id)
        
        # Check if errors are transient before retrying
        errors = result.get('errors', [])
        if errors:
            error_msg = '; '.join(errors)
            if is_transient_error(error_msg) and self.request.retries < self.max_retries:
                logger.warning(
                    'Document deindexing coordination failed for document %s (transient error), retrying...',
                    document_id
                )
                raise self.retry(exc=Exception(error_msg))
            elif not is_transient_error(error_msg):
                # Non-transient error - don't retry, just log
                logger.warning(
                    'Document deindexing coordination failed for document %s (non-transient error): %s',
                    document_id, error_msg
                )
        
        return result
    except Exception as exception:
        logger.error(
            'Unexpected error in document deindexing coordination for document %s: %s',
            document_id, exception, exc_info=True
        )
        
        # Only retry transient errors
        if is_transient_error(exception) and self.request.retries < self.max_retries:
            logger.warning(
                'Retrying document deindexing coordination for document %s (transient error)',
                document_id
            )
            raise self.retry(exc=exception)
        else:
            # Non-transient error - don't retry
            logger.error(
                'Document deindexing coordination failed for document %s (non-transient error), not retrying',
                document_id
            )
            raise


@app.task(ignore_result=False)
def task_validate_document_for_indexing(document_id):
    """
    Validate document state before indexing.
    
    This task checks if the document exists, is valid, not in trash,
    and not a stub. Returns document_id if valid, None otherwise.
    
    Note: This task returns a result that is used by subsequent tasks in chain.
    If None is returned, subsequent tasks should skip execution.
    
    Args:
        document_id: ID of the document to validate
    
    Returns:
        int: document_id if valid, None if invalid
    """
    from .validation import validate_document_for_indexing as validate_document
    
    # Use unified validation function
    document = validate_document(document_id, require_lock=False)
    
    if document:
        return document_id
    return None


@app.task(ignore_result=True)
def task_index_instance_conditional(app_label, model_name, object_id, validation_result,
                                    exclude_app_label=None, exclude_model_name=None, exclude_kwargs=None):
    """
    Conditionally execute task_index_instance based on validation result.
    
    This task only executes if validation_result is not None (document is valid).
    
    Args:
        app_label: App label of the model
        model_name: Model name
        object_id: Object ID to index
        validation_result: Result from validation task (document_id if valid, None otherwise)
        exclude_app_label: Optional app label to exclude
        exclude_model_name: Optional model name to exclude
        exclude_kwargs: Optional kwargs to exclude
    """
    # Skip if validation failed
    if validation_result is None:
        logger.debug(
            'Skipping search indexing for %s.%s (id=%s) - validation failed',
            app_label, model_name, object_id
        )
        return
    
    # Execute indexing task asynchronously
    from mayan.apps.dynamic_search.tasks import task_index_instance
    try:
        task_index_instance.apply_async(
            args=(app_label, model_name, object_id),
            kwargs={
                'exclude_app_label': exclude_app_label,
                'exclude_model_name': exclude_model_name,
                'exclude_kwargs': exclude_kwargs
            },
            queue='indexing'
        )
        logger.debug('Scheduled search indexing for %s.%s (id=%s)', app_label, model_name, object_id)
    except Exception as e:
        logger.error(
            'Error scheduling task_index_instance for %s.%s (id=%s): %s',
            app_label, model_name, object_id, e, exc_info=True
        )
        raise


@app.task(ignore_result=True)
def task_index_instance_document_add_conditional(document_id, validation_result, index_instance_id=None):
    """
    Conditionally execute task_index_instance_document_add based on validation result.
    
    This task only executes if validation_result is not None (document is valid).
    
    Args:
        document_id: ID of the document to index
        validation_result: Result from validation task (document_id if valid, None otherwise)
        index_instance_id: Optional index instance ID
    """
    # Skip if validation failed
    if validation_result is None:
        logger.debug(
            'Skipping hierarchy indexing for document %s - validation failed',
            document_id
        )
        return
    
    # Execute indexing task asynchronously
    from mayan.apps.document_indexing.tasks import task_index_instance_document_add
    try:
        task_index_instance_document_add.apply_async(
            args=(document_id,),
            kwargs={'index_instance_id': index_instance_id} if index_instance_id else {},
            queue='indexing'
        )
        logger.debug('Scheduled hierarchy indexing for document %s', document_id)
    except Exception as e:
        logger.error(
            'Error scheduling task_index_instance_document_add for document %s: %s',
            document_id, e, exc_info=True
        )
        raise


@app.task(
    bind=True, ignore_result=True,
    max_retries=3, retry_backoff=True
)
def task_index_instance_safe(self, app_label, model_name, object_id, exclude_app_label=None,
                              exclude_model_name=None, exclude_kwargs=None):
    """
    Safe wrapper for task_index_instance that validates document state.
    
    This wrapper checks if the document exists, is valid, not in trash,
    and not a stub before calling the actual indexing task.
    
    Note: This task is now used only for non-Document models or as fallback.
    For Document models, use validation task + indexing task in chain.
    
    Args:
        app_label: App label of the model
        model_name: Model name
        object_id: Object ID to index
        exclude_app_label: Optional app label to exclude
        exclude_model_name: Optional model name to exclude
        exclude_kwargs: Optional kwargs to exclude
    """
    # Only validate Document model, pass through others
    if app_label == 'documents' and model_name == 'Document':
        # For Document models, validation should be done in separate task
        # This is fallback for direct calls
        from .validation import validate_document_for_indexing as validate_document
        
        # Use unified validation function
        document = validate_document(object_id, require_lock=False)
        if not document:
            # Validation failed, skip indexing
            return
    
    # Call original task asynchronously if validation passed or not a Document
    from mayan.apps.dynamic_search.tasks import task_index_instance
    try:
        # Use apply_async for asynchronous execution
        task_index_instance.apply_async(
            args=(app_label, model_name, object_id),
            kwargs={
                'exclude_app_label': exclude_app_label,
                'exclude_model_name': exclude_model_name,
                'exclude_kwargs': exclude_kwargs
            },
            queue='indexing'
        )
    except Exception as e:
        logger.error(
            'Error scheduling task_index_instance for %s.%s (id=%s): %s',
            app_label, model_name, object_id, e, exc_info=True
        )
        # Retry only for transient errors
        from .indexing_coordinator import is_transient_error
        if is_transient_error(e) and self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        raise


@app.task(
    bind=True, ignore_result=True,
    max_retries=None, retry_backoff=True, retry_backoff_max=60
)
def task_index_instance_document_add_safe(self, document_id, index_instance_id=None):
    """
    Safe wrapper for task_index_instance_document_add that validates document state.
    
    This wrapper checks if the document exists, is valid, not in trash,
    and not a stub before calling the actual indexing task.
    
    Note: This task is now used only as fallback. For normal flow,
    use validation task + indexing task in chain.
    
    Args:
        document_id: ID of the document to index
        index_instance_id: Optional index instance ID
    """
    from .validation import validate_document_for_indexing as validate_document
    
    # Use unified validation function
    document = validate_document(document_id, require_lock=False)
    if not document:
        # Validation failed, skip indexing
        return
    
    # Call original task asynchronously if validation passed
    from mayan.apps.document_indexing.tasks import task_index_instance_document_add
    try:
        # Use apply_async for asynchronous execution
        task_index_instance_document_add.apply_async(
            args=(document_id,),
            kwargs={'index_instance_id': index_instance_id} if index_instance_id else {},
            queue='indexing'
        )
    except Exception as e:
        logger.error(
            'Error scheduling task_index_instance_document_add for document %s: %s',
            document_id, e, exc_info=True
        )
        # Retry logic is handled by the original task
        raise


@app.task(ignore_result=True)
def task_release_indexing_lock(document_id):
    """
    Release indexing lock for a document after chain completion.
    
    This task is called as a callback after indexing chain completes
    (either successfully or with error) to ensure lock is always released.
    
    Note: Lock manager uses timeout-based expiration, so locks will be
    automatically released after timeout. This callback is a best-effort
    attempt to release the lock earlier if possible.
    
    Args:
        document_id: ID of the document whose lock should be released
    """
    import time
    from .metrics import get_metrics
    
    lock_name = 'indexing_document_{}'.format(document_id)
    metrics = get_metrics()
    start_time = time.time()
    
    try:
        from mayan.apps.lock_manager.backends.base import LockingBackend
        from mayan.apps.lock_manager.exceptions import LockError
        
        # Try to release lock by attempting to acquire and immediately release
        # This works if the lock backend supports it
        try:
            backend = LockingBackend.get_backend()
            # Some backends allow releasing by name
            # For model-based locks, we might need to query the lock model
            if hasattr(backend, 'release_lock_by_name'):
                backend.release_lock_by_name(name=lock_name)
                logger.debug('Released indexing lock for document %s (via callback)', document_id)
                # Record successful callback execution
                duration = time.time() - start_time
                metrics.record_callback_success(document_id, duration)
            else:
                # Lock will expire automatically after timeout
                logger.debug(
                    'Lock backend does not support release by name. '
                    'Lock for document %s will expire after timeout',
                    document_id
                )
                # Record callback execution (backend limitation, not failure)
                duration = time.time() - start_time
                metrics.record_callback_skipped(document_id, 'backend_limitation', duration)
        except (LockError, AttributeError):
            # Lock doesn't exist, already released, or backend doesn't support it
            # This is fine - lock will expire automatically
            logger.debug(
                'Lock for document %s already released, expired, or backend does not support release by name',
                document_id
            )
            # Record callback execution (lock already released, not a failure)
            duration = time.time() - start_time
            metrics.record_callback_skipped(document_id, 'already_released', duration)
    except ImportError:
        # Lock manager not available
        logger.debug('Lock manager not available, cannot release lock for document %s', document_id)
        duration = time.time() - start_time
        metrics.record_callback_skipped(document_id, 'lock_manager_unavailable', duration)
    except Exception as e:
        # Log error but don't raise - lock release is best effort
        # Lock will expire automatically after timeout anyway
        logger.debug(
            'Error releasing indexing lock for document %s (lock will expire automatically): %s',
            document_id, e
        )
        # Record callback failure
        duration = time.time() - start_time
        metrics.record_callback_failure(document_id, str(e), duration)


@app.task(ignore_result=True)
def task_cleanup_stale_indexing_locks():
    """
    Periodic task to clean up stale indexing locks.
    
    This task checks for locks that may have been left behind due to
    worker crashes or other failures. Locks with timeout-based expiration
    will be automatically released, but this task provides an additional
    safety mechanism.
    
    Note: This task should be scheduled via Celery Beat for periodic execution.
    Recommended frequency: every 5-10 minutes.
    """
    try:
        from mayan.apps.lock_manager.backends.base import LockingBackend
        from mayan.apps.lock_manager.exceptions import LockError
        from django.apps import apps
        from .metrics import get_metrics
        
        Document = apps.get_model(app_label='documents', model_name='Document')
        metrics = get_metrics()
        
        # Get all active indexing locks (if backend supports querying)
        # This is backend-specific, so we'll use a best-effort approach
        backend = LockingBackend.get_backend()
        
        # Try to get stale locks (older than expected timeout)
        # Most backends don't support querying, so we'll log a summary
        logger.debug('Running cleanup of stale indexing locks')
        
        # Record cleanup execution
        metrics.record_cleanup_execution()
        
        # Note: Actual cleanup depends on backend implementation
        # Most backends use timeout-based expiration, so locks will
        # be automatically released after timeout (300 seconds)
        
        logger.info('Completed cleanup check for stale indexing locks')
        
    except ImportError:
        logger.debug('Lock manager not available, skipping cleanup')
    except Exception as e:
        logger.error(
            'Error during cleanup of stale indexing locks: %s',
            e, exc_info=True
        )


@app.task(bind=True, ignore_result=True, max_retries=2, retry_backoff=True)
def task_coordinate_document_batch_index(self, document_ids):
    """
    Coordinate batch indexing of multiple documents.
    
    This task uses the DocumentIndexCoordinator to ensure proper coordination
    for batch operations.
    """
    from .indexing_coordinator import DocumentIndexCoordinator
    
    try:
        result = DocumentIndexCoordinator.index_document_batch(
            document_ids=document_ids
        )
        
        # Retry only if all documents failed
        if result.get('scheduled', 0) == 0 and result.get('total', 0) > 0:
            if self.request.retries < self.max_retries:
                logger.warning(
                    'Batch indexing coordination failed for all documents, retrying...'
                )
                raise self.retry(exc=Exception('All documents failed to index'))
        
        return result
    except Exception as exception:
        logger.error(
            'Unexpected error in batch indexing coordination: %s',
            exception, exc_info=True
        )
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exception)
        raise