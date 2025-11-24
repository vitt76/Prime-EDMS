"""
Document validation utilities for indexing operations.

Provides unified validation functions to avoid code duplication
across different components of the indexing system.
"""
import logging

from django.apps import apps

logger = logging.getLogger(name=__name__)


def validate_document_for_indexing(document_id, require_lock=False):
    """
    Validate document state before indexing.
    
    This function checks if the document exists, is valid (not in trash),
    and not a stub. This is the single source of truth for document
    validation in indexing operations.
    
    Args:
        document_id: ID of the document to validate
        require_lock: If True, use select_for_update (not recommended,
                     as lock is already held at coordinator level)
    
    Returns:
        Document instance if valid, None if invalid
    
    Note:
        Lock is already guaranteed at coordinator level, so require_lock
        should typically be False to avoid conflicts.
    """
    Document = apps.get_model(app_label='documents', model_name='Document')
    
    try:
        if require_lock:
            from django.db import transaction
            from django.db import OperationalError
            
            try:
                with transaction.atomic():
                    document = Document.valid.select_for_update(nowait=True).get(pk=document_id)
            except OperationalError:
                # Lock is held by another transaction
                logger.debug(
                    'Document %s is being processed by another task (lock held), skipping',
                    document_id
                )
                return None
        else:
            # Lock already guaranteed at coordinator level, no need for select_for_update
            document = Document.valid.get(pk=document_id)
        
        # Check if document is in trash
        if document.in_trash:
            logger.warning(
                'Document %s is in trash, skipping indexing',
                document_id
            )
            return None
        
        # Check if document is a stub
        if getattr(document, 'is_stub', False):
            logger.debug(
                'Document %s is a stub, skipping indexing',
                document_id
            )
            return None
        
        # Document is valid
        logger.debug('Document %s validated successfully for indexing', document_id)
        return document
        
    except Document.DoesNotExist:
        logger.warning(
            'Document %s does not exist or is not valid, skipping indexing',
            document_id
        )
        return None
    except Exception as e:
        logger.error(
            'Error validating document %s for indexing: %s',
            document_id, e, exc_info=True
        )
        # Don't retry validation errors - they are non-transient
        return None

