"""
Signals for Headless API cache invalidation.

Handles automatic cache invalidation when document types, metadata, or workflows change.
"""
import logging
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver

from mayan.apps.documents.models import DocumentType
from mayan.apps.metadata.models import DocumentTypeMetadataType
from mayan.apps.document_states.models import Workflow

from .cache_utils import (
    invalidate_document_type_config_cache,
    invalidate_all_document_types_cache
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=DocumentType)
def invalidate_doc_type_cache_on_save(sender, instance, **kwargs):
    """Invalidate cache when DocumentType is saved."""
    invalidate_document_type_config_cache(document_type_id=instance.pk)


@receiver(post_delete, sender=DocumentType)
def invalidate_doc_type_cache_on_delete(sender, instance, **kwargs):
    """Invalidate cache when DocumentType is deleted."""
    invalidate_document_type_config_cache(document_type_id=instance.pk)


@receiver(post_save, sender=DocumentTypeMetadataType)
@receiver(post_delete, sender=DocumentTypeMetadataType)
def invalidate_doc_type_cache_on_metadata_change(sender, instance, **kwargs):
    """Invalidate cache when DocumentTypeMetadataType is saved or deleted."""
    invalidate_document_type_config_cache(document_type_id=instance.document_type.pk)


@receiver(m2m_changed, sender=Workflow.document_types.through)
def invalidate_doc_type_cache_on_workflow_change(sender, instance, action, pk_set, **kwargs):
    """
    Invalidate cache when workflow-document_type relationships change.
    
    This handles:
    - Adding document types to workflow (post_add)
    - Removing document types from workflow (pre_remove)
    - Clearing all document types from workflow (pre_clear, post_clear)
    
    Args:
        sender: The through model (Workflow.document_types.through)
        instance: Either Workflow or DocumentType instance
        action: The action being performed ('pre_add', 'post_add', 'pre_remove', 'post_remove', 'pre_clear', 'post_clear')
        pk_set: Set of primary keys being added/removed
    """
    if action in ('post_add', 'pre_remove', 'pre_clear', 'post_clear'):
        # When adding/removing document types to/from workflow
        # instance is the Workflow, pk_set contains DocumentType IDs
        if isinstance(instance, Workflow):
            if pk_set:
                # Invalidate specific document types
                for doc_type_id in pk_set:
                    invalidate_document_type_config_cache(document_type_id=doc_type_id)
            else:
                # Clear action - invalidate all document types (simplified approach)
                # We invalidate list cache, individual caches will expire via TTL
                invalidate_all_document_types_cache()
        # When adding/removing workflows to/from document type
        # instance is the DocumentType, pk_set contains Workflow IDs
        elif isinstance(instance, DocumentType):
            invalidate_document_type_config_cache(document_type_id=instance.pk)

