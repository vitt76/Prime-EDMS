from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from .tasks import (
    task_index_instance_document_add, task_index_instance_document_remove,
    task_index_instance_node_delete_empty
)


def handler_create_default_document_index(sender, **kwargs):
    DocumentType = apps.get_model(
        app_label='documents', model_name='DocumentType'
    )
    IndexTemplate = apps.get_model(
        app_label='document_indexing', model_name='IndexTemplate'
    )

    index = IndexTemplate.objects.create(
        label=_('Creation date'), slug='creation_date'
    )
    for document_type in DocumentType.objects.all():
        index.document_types.add(document_type)

    root_template_node = index.index_template_root_node
    node = root_template_node.get_children().create(
        expression='{{ document.datetime_created|date:"Y" }}', index=index,
        parent=root_template_node
    )
    node.get_children().create(
        expression='{{ document.datetime_created|date:"m" }}',
        index=index, link_documents=True, parent=node
    )


def handler_delete_empty(sender, **kwargs):
    task_index_instance_node_delete_empty.apply_async()


def handler_event_trigger(sender, **kwargs):
    action = kwargs['instance']

    Document = apps.get_model(
        app_label='documents', model_name='Document'
    )
    IndexInstance = apps.get_model(
        app_label='document_indexing', model_name='IndexInstance'
    )

    if isinstance(action.target, Document):
        document = action.target
    elif isinstance(action.action_object, Document):
        document = action.action_object
    else:
        document = None

    if document:
        index_instance_queryset = IndexInstance.objects.filter(
            document_types=document.document_type,
            event_triggers__stored_event_type__name=kwargs['instance'].verb
        )

        for index_instance in index_instance_queryset:
            task_index_instance_document_add.apply_async(
                kwargs={
                    'document_id': document.pk,
                    'index_instance_id': index_instance.pk
                }
            )


def handler_index_document(sender, **kwargs):
    """
    Handler for document indexing in Document Indexing system.
    
    This handler checks if the DocumentIndexCoordinator is active.
    If the coordinator is active (handlers registered), this handler
    will be skipped to avoid duplicate indexing. This provides backward
    compatibility for cases where the coordinator is not available.
    """
    # Check if coordinator is actually active (handlers registered)
    try:
        from mayan.apps.documents.indexing_coordinator import is_coordinator_active
        if is_coordinator_active():
            # Coordinator is active, it will handle indexing
            return
    except ImportError:
        # Coordinator module not available, use legacy handler
        pass
    
    # Legacy behavior: only index on creation
    if kwargs.get('created', False):
        task_index_instance_document_add.apply_async(
            kwargs={'document_id': kwargs['instance'].pk}
        )


def handler_remove_document(sender, **kwargs):
    """
    Handler for document removal from Document Indexing system.
    
    This handler checks if the DocumentIndexCoordinator is active.
    If the coordinator is active (handlers registered), this handler
    will be skipped to avoid duplicate deindexing. This provides backward
    compatibility for cases where the coordinator is not available.
    """
    # Check if coordinator is actually active (handlers registered)
    try:
        from mayan.apps.documents.indexing_coordinator import is_coordinator_active
        if is_coordinator_active():
            # Coordinator is active, it will handle deindexing
            return
    except ImportError:
        # Coordinator module not available, use legacy handler
        pass
    
    # Legacy behavior
    task_index_instance_document_remove.apply_async(
        kwargs={
            'document_id': kwargs['instance'].pk
        }
    )
