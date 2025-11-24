"""
Document Indexing Coordinator

Unified coordinator for document indexing that eliminates duplication between
Dynamic Search and Document Indexing systems. Provides a single point of entry
for all document indexing operations.
"""
import logging
import time

from django.apps import apps
from django.db.models.signals import post_save

logger = logging.getLogger(name=__name__)


def is_transient_error(error):
    """
    Classify an error as transient (retryable) or non-transient (non-retryable).
    
    Transient errors are temporary conditions that might resolve on retry:
    - Lock errors (another process is holding a lock)
    - Database operational errors (connection issues, deadlocks)
    - Network errors (temporary connectivity issues)
    
    Non-transient errors are permanent conditions that won't resolve on retry:
    - DoesNotExist (object doesn't exist)
    - ValidationError (invalid data)
    - Permission errors (user doesn't have permission)
    - Trashed documents (document is in trash)
    
    Args:
        error: Exception instance or error string
    
    Returns:
        bool: True if error is transient (should retry), False otherwise
    """
    from django.core.exceptions import ValidationError
    from django.db import OperationalError
    from mayan.apps.lock_manager.exceptions import LockError
    
    # Handle string errors
    if isinstance(error, str):
        error_lower = error.lower()
        if any(keyword in error_lower for keyword in [
            'not found', 'does not exist', 'invalid', 'validation',
            'permission denied', 'forbidden', 'trashed', 'stub'
        ]):
            return False
        if any(keyword in error_lower for keyword in [
            'lock', 'timeout', 'connection', 'network', 'temporary'
        ]):
            return True
        return False
    
    # Handle exception instances
    if isinstance(error, Exception):
        # Non-transient errors
        if isinstance(error, (ValidationError,)):
            return False
        
        # Check for DoesNotExist
        if 'DoesNotExist' in type(error).__name__:
            return False
        
        # Transient errors
        if isinstance(error, (LockError, OperationalError)):
            return True
        
        # Check for database connection errors
        error_name = type(error).__name__
        if any(keyword in error_name for keyword in [
            'OperationalError', 'DatabaseError', 'ConnectionError',
            'TimeoutError', 'LockError'
        ]):
            return True
        
        # Check error message for transient indicators
        error_msg = str(error).lower()
        if any(keyword in error_msg for keyword in [
            'lock', 'timeout', 'connection', 'network', 'temporary',
            'deadlock', 'could not connect'
        ]):
            return True
    
    # Default: assume non-transient (don't retry unknown errors)
    return False


def is_coordinator_active():
    """
    Check if DocumentIndexCoordinator handlers are actually registered.
    
    This function checks if the coordinator's handlers are registered
    in Django signals, not just if the class exists. This provides
    a reliable way to determine if the coordinator is active.
    
    Returns:
        bool: True if coordinator handlers are registered, False otherwise
    """
    try:
        Document = apps.get_model(app_label='documents', model_name='Document')
        
        # Get all registered receivers for Document.post_save signal
        receivers = post_save._live_receivers(sender=Document)
        
        # Check if coordinator handler is registered
        for receiver in receivers:
            # Check by function name or dispatch_uid
            receiver_name = getattr(receiver, '__name__', '')
            if 'handler_coordinate_document_index' in receiver_name:
                return True
            
            # Also check by looking at the receiver's module path
            receiver_module = getattr(receiver, '__module__', '')
            if 'documents.handlers' in receiver_module and 'coordinate' in receiver_name:
                return True
        
        return False
    except Exception as e:
        logger.debug('Error checking coordinator status: %s', e)
        return False


class DocumentIndexCoordinator:
    """
    Coordinates document indexing between Dynamic Search and Document Indexing systems.
    
    This coordinator ensures that:
    - Documents are indexed in both systems without duplication
    - Tasks are executed in the correct order (Search -> Indexing)
    - Errors in one system don't affect the other
    - All operations are logged for debugging
    """
    
    @staticmethod
    def _check_access_permissions(document_id, user):
        """
        Check access permissions for document indexing.
        
        Args:
            document_id: ID of the document
            user: User to check permissions for
        
        Returns:
            dict with error info if permission denied, None if allowed
        """
        if not user:
            return None
        
        Document = apps.get_model(app_label='documents', model_name='Document')
        try:
            document = Document.objects.get(pk=document_id)
            
            from mayan.apps.acls.models import AccessControlList
            from mayan.apps.permissions import permission_document_view
            from django.core.exceptions import PermissionDenied
            
            try:
                AccessControlList.objects.check_access(
                    obj=document,
                    permissions=(permission_document_view,),
                    user=user
                )
            except PermissionDenied:
                logger.warning(
                    'User %s does not have permission to index document %s',
                    user, document_id
                )
                return {
                    'search_indexed': False,
                    'hierarchy_indexed': False,
                    'error': 'Permission denied',
                    'error_type': 'permission_denied'
                }
        except Document.DoesNotExist:
            # Document doesn't exist - validation task will handle this
            pass
        
        return None
    
    @staticmethod
    def _acquire_indexing_lock(document_id):
        """
        Acquire distributed lock for document indexing.
        
        Args:
            document_id: ID of the document
        
        Returns:
            Lock instance if acquired, None if not available or lock manager unavailable
        """
        lock_name = 'indexing_document_{}'.format(document_id)
        try:
            from mayan.apps.lock_manager.backends.base import LockingBackend
            from mayan.apps.lock_manager.exceptions import LockError
            from .settings import setting_indexing_lock_timeout
            
            try:
                lock = LockingBackend.get_backend().acquire_lock(
                    name=lock_name,
                    timeout=setting_indexing_lock_timeout.value
                )
                logger.debug('Acquired indexing lock for document %s', document_id)
                return lock
            except LockError:
                # Lock already held - another indexing task is in progress
                logger.debug(
                    'Document %s indexing already in progress (lock held), skipping',
                    document_id
                )
                return 'LOCKED'  # Special marker to indicate lock is held
        except ImportError:
            # Lock manager not available, proceed without lock
            logger.debug('Lock manager not available, proceeding without lock')
            return None
    
    @staticmethod
    def _create_indexing_chain(document_id):
        """
        Create Celery chain for document indexing.
        
        Args:
            document_id: ID of the document to index
        
        Returns:
            Celery chain instance
        """
        from celery import chain
        from .tasks import (
            task_validate_document_for_indexing,
            task_index_instance_conditional,
            task_index_instance_document_add_conditional,
            task_release_indexing_lock
        )
        
        # Chain: validate -> conditional search indexing -> validate -> conditional hierarchy indexing
        # Each validation step ensures document is still valid before indexing
        # Conditional tasks skip execution if validation returns None
        indexing_chain = chain(
            # First validation before search indexing
            task_validate_document_for_indexing.s(document_id),
            # Search indexing (only executes if validation returned document_id)
            task_index_instance_conditional.s(
                app_label='documents',
                model_name='Document',
                object_id=document_id,
                exclude_app_label=None,
                exclude_model_name=None,
                exclude_kwargs=None
            ),
            # Second validation before hierarchy indexing
            task_validate_document_for_indexing.s(document_id),
            # Hierarchy indexing (only executes if validation returned document_id)
            task_index_instance_document_add_conditional.s(
                document_id=document_id,
                index_instance_id=None
            )
        )
        
        # Add callback task to release lock after chain completes (success or error)
        # Use link() for success and link_error() for error to ensure callback always executes
        indexing_chain = indexing_chain.link(task_release_indexing_lock.s(document_id))
        indexing_chain = indexing_chain.link_error(task_release_indexing_lock.s(document_id))
        
        return indexing_chain
    
    @staticmethod
    def _schedule_fallback_indexing(document_id, result):
        """
        Schedule fallback indexing tasks if chain scheduling failed.
        
        Args:
            document_id: ID of the document
            result: Result dict to update with scheduling status
        """
        from .tasks import (
            task_index_instance_safe,
            task_index_instance_document_add_safe
        )
        from .settings import setting_indexing_fallback_countdown
        
        # Fallback: try to schedule tasks separately if chain fails
        try:
            task_index_instance_safe.apply_async(
                kwargs={
                    'app_label': 'documents',
                    'model_name': 'Document',
                    'object_id': document_id
                },
                queue='indexing'
            )
            result['search_indexed'] = True
            logger.debug('Scheduled search indexing (fallback) for document %s', document_id)
        except Exception as e:
            error_msg = f'Failed to schedule search indexing (fallback): {e}'
            result['errors'].append(error_msg)
            logger.error(
                'Error scheduling search indexing (fallback) for document %s: %s',
                document_id, e, exc_info=True
            )
        
        try:
            task_index_instance_document_add_safe.apply_async(
                kwargs={'document_id': document_id},
                queue='indexing',
                countdown=setting_indexing_fallback_countdown.value  # Configurable fallback delay
            )
            result['hierarchy_indexed'] = True
            logger.debug('Scheduled hierarchy indexing (fallback) for document %s', document_id)
        except Exception as e:
            error_msg = f'Failed to schedule hierarchy indexing (fallback): {e}'
            result['errors'].append(error_msg)
            logger.error(
                'Error scheduling hierarchy indexing (fallback) for document %s: %s',
                document_id, e, exc_info=True
            )
    
    @staticmethod
    def index_document(document_id, created=False, user=None):
        """
        Coordinate indexing of a document in both Dynamic Search and Document Indexing.
        
        Args:
            document_id: ID of the document to index
            created: Whether this is a new document (for logging purposes)
            user: Optional user for access control check. If provided, checks
                 permission_document_view before indexing. If None, skips
                 permission check (for system tasks).
        
        Returns:
            dict: Status of indexing operations
        """
        from .metrics import get_metrics
        
        Document = apps.get_model(app_label='documents', model_name='Document')
        metrics = get_metrics()
        start_time = time.time()
        
        try:
            # Check access permissions if user is provided
            permission_error = DocumentIndexCoordinator._check_access_permissions(document_id, user)
            if permission_error:
                return permission_error
            
            # No document existence check here - validation will be done in validation task
            # This prevents double validation and reduces DB load
            # If document doesn't exist, validation task will return None and chain will skip indexing
            
            # Check for duplicate indexing using distributed lock
            lock = DocumentIndexCoordinator._acquire_indexing_lock(document_id)
            if lock == 'LOCKED':
                return {
                    'search_indexed': False,
                    'hierarchy_indexed': False,
                    'error': 'Indexing already in progress'
                }
            
            result = {
                'search_indexed': False,
                'hierarchy_indexed': False,
                'errors': []
            }
            
            try:
                # Use Celery chain to ensure search indexing completes before hierarchy indexing
                # This guarantees the order of execution
                from celery.exceptions import BrokerConnectionError
                
                # Create indexing chain
                indexing_chain = DocumentIndexCoordinator._create_indexing_chain(document_id)
                
                # Execute chain asynchronously and check result
                try:
                    chain_result = indexing_chain.apply_async(queue='indexing')
                    
                    # Verify that chain was successfully scheduled
                    if chain_result and chain_result.id:
                        result['search_indexed'] = True
                        result['hierarchy_indexed'] = True
                        result['chain_task_id'] = chain_result.id
                        logger.debug(
                            'Scheduled indexing chain for document %s (created=%s, task_id=%s)',
                            document_id, created, chain_result.id
                        )
                    else:
                        raise Exception('Chain apply_async returned invalid result')
                except BrokerConnectionError as e:
                    # Celery broker is unavailable - critical error
                    error_msg = f'Celery broker unavailable: {e}'
                    result['errors'].append(error_msg)
                    logger.critical(
                        'Celery broker unavailable, cannot schedule indexing chain for document %s: %s',
                        document_id, e
                    )
                    raise
            except Exception as e:
                error_msg = f'Failed to schedule indexing chain: {e}'
                result['errors'].append(error_msg)
                logger.error(
                    'Error scheduling indexing chain for document %s: %s',
                    document_id, e, exc_info=True
                )
                
                # Fallback: try to schedule tasks separately if chain fails
                DocumentIndexCoordinator._schedule_fallback_indexing(document_id, result)
            finally:
                # DO NOT release lock here - it will be released by callback task
                # after chain completes. Lock must be held until tasks finish to prevent
                # race conditions. Only release if scheduling completely failed.
                if lock and result.get('errors') and not result.get('chain_task_id'):
                    # Scheduling failed completely - release lock to allow retry
                    try:
                        lock.release()
                        logger.debug('Released indexing lock for document %s (scheduling failed)', document_id)
                    except Exception as e:
                        logger.warning(
                            'Error releasing lock for document %s: %s',
                            document_id, e
                        )
                elif lock and result.get('chain_task_id'):
                    # Chain scheduled successfully - lock will be released by callback
                    logger.debug(
                        'Lock for document %s will be released by callback after chain completion',
                        document_id
                    )
            
            duration = time.time() - start_time
            
            if result['errors']:
                logger.warning(
                    'Document %s indexing completed with errors: %s',
                    document_id, result['errors']
                )
                # Record failure metrics
                error_type = result.get('error_type', 'unknown')
                metrics.record_index_failure(document_id, error_type, duration)
            else:
                logger.info(
                    'Document %s indexing scheduled successfully (created=%s)',
                    document_id, created
                )
                # Record success metrics
                metrics.record_index_success(document_id, duration)
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                'Unexpected error in document indexing coordinator for document %s: %s',
                document_id, e, exc_info=True
            )
            # Record failure metrics
            metrics.record_index_failure(document_id, 'exception', duration)
            return {
                'search_indexed': False,
                'hierarchy_indexed': False,
                'error': str(e),
                'error_type': 'exception'
            }
    
    @staticmethod
    def deindex_document(document_id):
        """
        Coordinate removal of a document from both Dynamic Search and Document Indexing.
        
        Args:
            document_id: ID of the document to remove from indexes
        
        Returns:
            dict: Status of deindexing operations
        """
        from .metrics import get_metrics
        
        metrics = get_metrics()
        start_time = time.time()
        
        result = {
            'search_deindexed': False,
            'hierarchy_deindexed': False,
            'errors': []
        }
        
        # Remove from Dynamic Search
        try:
            from mayan.apps.dynamic_search.tasks import task_deindex_instance
            
            task_deindex_instance.apply_async(
                kwargs={
                    'app_label': 'documents',
                    'model_name': 'Document',
                    'object_id': document_id
                },
                queue='indexing'  # Use unified queue
            )
            result['search_deindexed'] = True
            logger.debug('Scheduled search deindexing for document %s', document_id)
        except Exception as e:
            error_msg = f'Failed to schedule search deindexing: {e}'
            result['errors'].append(error_msg)
            logger.error(
                'Error scheduling search deindexing for document %s: %s',
                document_id, e, exc_info=True
            )
        
        # Remove from Document Indexing (hierarchical)
        try:
            from mayan.apps.document_indexing.tasks import task_index_instance_document_remove
            
            task_index_instance_document_remove.apply_async(
                kwargs={'document_id': document_id},
                queue='indexing'  # Use unified queue
            )
            result['hierarchy_deindexed'] = True
            logger.debug('Scheduled hierarchy deindexing for document %s', document_id)
        except Exception as e:
            error_msg = f'Failed to schedule hierarchy deindexing: {e}'
            result['errors'].append(error_msg)
            logger.error(
                'Error scheduling hierarchy deindexing for document %s: %s',
                document_id, e, exc_info=True
            )
        
        duration = time.time() - start_time
        
        if result['errors']:
            logger.warning(
                'Document %s deindexing completed with errors: %s',
                document_id, result['errors']
            )
            # Record failure metrics
            error_type = 'unknown'
            if result['errors']:
                error_msg = '; '.join(result['errors']).lower()
                if 'lock' in error_msg:
                    error_type = 'lock_error'
                elif 'connection' in error_msg or 'network' in error_msg:
                    error_type = 'connection_error'
            metrics.record_deindex_failure(document_id, error_type, duration)
        else:
            logger.info('Document %s deindexing scheduled successfully', document_id)
            # Record success metrics
            metrics.record_deindex_success(document_id, duration)
        
        return result
    
    @staticmethod
    def index_document_batch(document_ids, fail_fast=False, chunk_size=1000):
        """
        Coordinate batch indexing of multiple documents.
        
        Args:
            document_ids: List of document IDs to index
            fail_fast: If True, stop batch processing on first error.
                      Note: This stops only planning of new tasks; already
                      scheduled tasks will continue to execute.
            chunk_size: Process documents in chunks for very large batches.
                       If None, uses setting_indexing_batch_chunk_size.
                       Set to 0 to disable chunking.
        
        Returns:
            dict: Status of batch indexing operations with detailed statistics
        """
        from .settings import setting_indexing_batch_chunk_size, setting_indexing_batch_max_size
        
        if not document_ids:
            return {
                'total': 0,
                'success_count': 0,
                'failed_count': 0,
                'skipped_count': 0,
                'errors': [],
                'error_types': {}
            }
        
        # Check batch size limit
        if len(document_ids) > setting_indexing_batch_max_size.value:
            logger.warning(
                'Batch size %d exceeds maximum allowed size %d. '
                'Consider splitting into smaller batches.',
                len(document_ids), setting_indexing_batch_max_size.value
            )
        
        # Use default chunk size if not specified
        if chunk_size is None:
            chunk_size = setting_indexing_batch_chunk_size.value
        
        result = {
            'total': len(document_ids),
            'success_count': 0,
            'failed_count': 0,
            'skipped_count': 0,
            'errors': [],
            'error_types': {}
        }
        
        # Process in chunks for very large batches to avoid memory issues
        # Use fully iterative approach without recursion to avoid deep recursion and memory issues
        if chunk_size > 0 and len(document_ids) > chunk_size:
            logger.info(
                'Processing batch of %d documents in chunks of %d',
                len(document_ids), chunk_size
            )
            # Create chunks list using list comprehension (iterative, not recursive)
            chunks = [
                document_ids[i:i + chunk_size]
                for i in range(0, len(document_ids), chunk_size)
            ]
            
            # Process each chunk iteratively without recursion
            for chunk_idx, chunk_ids in enumerate(chunks):
                # Process each document in chunk directly without recursive call
                for document_id in chunk_ids:
                    try:
                        index_result = DocumentIndexCoordinator.index_document(
                            document_id=document_id,
                            created=False  # Batch operations are typically updates
                        )
                        
                        # Categorize result
                        error_type = index_result.get('error_type')
                        if error_type:
                            # Document was skipped (trashed, stub, not found, etc.)
                            result['skipped_count'] += 1
                            error_key = error_type
                            if error_key not in result['error_types']:
                                result['error_types'][error_key] = []
                            result['error_types'][error_key].append({
                                'document_id': document_id,
                                'error': index_result.get('error', 'Unknown error')
                            })
                        elif index_result.get('search_indexed') or index_result.get('hierarchy_indexed'):
                            # Successfully scheduled
                            result['success_count'] += 1
                        elif index_result.get('errors'):
                            # Failed with errors
                            result['failed_count'] += 1
                            for error in index_result.get('errors', []):
                                result['errors'].append({
                                    'document_id': document_id,
                                    'error': error
                                })
                            
                            # Group errors by type for better diagnostics
                            error_key = 'scheduling_error'
                            if error_key not in result['error_types']:
                                result['error_types'][error_key] = []
                            result['error_types'][error_key].append({
                                'document_id': document_id,
                                'error': '; '.join(index_result.get('errors', []))
                            })
                            
                            # Fail fast if requested
                            if fail_fast:
                                logger.warning(
                                    'Batch indexing stopped early due to fail_fast=True at document %s',
                                    document_id
                                )
                                break
                        else:
                            # Unknown state
                            result['failed_count'] += 1
                            result['errors'].append({
                                'document_id': document_id,
                                'error': 'Unknown indexing state'
                            })
                        
                    except Exception as e:
                        error_msg = f'Failed to index document {document_id}: {e}'
                        result['failed_count'] += 1
                        result['errors'].append({
                            'document_id': document_id,
                            'error': error_msg
                        })
                        
                        # Group by exception type
                        error_key = type(e).__name__
                        if error_key not in result['error_types']:
                            result['error_types'][error_key] = []
                        result['error_types'][error_key].append({
                            'document_id': document_id,
                            'error': str(e)
                        })
                        
                        logger.error(
                            'Error in batch indexing for document %s: %s',
                            document_id, e, exc_info=True
                        )
                        
                        # Fail fast if requested
                        if fail_fast:
                            logger.warning(
                                'Batch indexing stopped early due to fail_fast=True at document %s. '
                                'Note: Already scheduled tasks will continue to execute.',
                                document_id
                            )
                            break
                
                # Check fail_fast after processing chunk
                if fail_fast and result['failed_count'] > 0:
                    logger.warning(
                        'Batch indexing stopped early due to fail_fast=True at chunk %d (documents %d-%d)',
                        chunk_idx, chunk_idx * chunk_size, (chunk_idx + 1) * chunk_size
                    )
                    break
            
            logger.info(
                'Batch indexing completed: %d/%d successful, %d failed, %d skipped',
                result['success_count'], result['total'],
                result['failed_count'], result['skipped_count']
            )
            
            if result['error_types']:
                logger.debug(
                    'Batch indexing error breakdown: %s',
                    result['error_types']
                )
            
            return result
        
        # Process documents (either small batch or single chunk)
        for idx, document_id in enumerate(document_ids):
            try:
                index_result = DocumentIndexCoordinator.index_document(
                    document_id=document_id,
                    created=False  # Batch operations are typically updates
                )
                
                # Categorize result
                error_type = index_result.get('error_type')
                if error_type:
                    # Document was skipped (trashed, stub, not found, etc.)
                    result['skipped_count'] += 1
                    error_key = error_type
                    if error_key not in result['error_types']:
                        result['error_types'][error_key] = []
                    result['error_types'][error_key].append({
                        'document_id': document_id,
                        'error': index_result.get('error', 'Unknown error')
                    })
                elif index_result.get('search_indexed') or index_result.get('hierarchy_indexed'):
                    # Successfully scheduled
                    result['success_count'] += 1
                elif index_result.get('errors'):
                    # Failed with errors
                    result['failed_count'] += 1
                    for error in index_result.get('errors', []):
                        result['errors'].append({
                            'document_id': document_id,
                            'error': error
                        })
                    
                    # Group errors by type for better diagnostics
                    error_key = 'scheduling_error'
                    if error_key not in result['error_types']:
                        result['error_types'][error_key] = []
                    result['error_types'][error_key].append({
                        'document_id': document_id,
                        'error': '; '.join(index_result.get('errors', []))
                    })
                    
                    # Fail fast if requested
                    if fail_fast:
                        logger.warning(
                            'Batch indexing stopped early due to fail_fast=True at document %s',
                            document_id
                        )
                        break
                else:
                    # Unknown state
                    result['failed_count'] += 1
                    result['errors'].append({
                        'document_id': document_id,
                        'error': 'Unknown indexing state'
                    })
                    
            except Exception as e:
                error_msg = f'Failed to index document {document_id}: {e}'
                result['failed_count'] += 1
                result['errors'].append({
                    'document_id': document_id,
                    'error': error_msg
                })
                
                # Group by exception type
                error_key = type(e).__name__
                if error_key not in result['error_types']:
                    result['error_types'][error_key] = []
                result['error_types'][error_key].append({
                    'document_id': document_id,
                    'error': str(e)
                })
                
                logger.error(
                    'Error in batch indexing for document %s: %s',
                    document_id, e, exc_info=True
                )
                
                # Fail fast if requested
                # Note: fail_fast stops only planning of new tasks, already scheduled tasks continue
                if fail_fast:
                    logger.warning(
                        'Batch indexing stopped early due to fail_fast=True at document %s. '
                        'Note: Already scheduled tasks will continue to execute.',
                        document_id
                    )
                    break
        
        logger.info(
            'Batch indexing completed: %d/%d successful, %d failed, %d skipped',
            result['success_count'], result['total'],
            result['failed_count'], result['skipped_count']
        )
        
        if result['error_types']:
            logger.debug(
                'Batch indexing error breakdown: %s',
                result['error_types']
            )
        
        return result

