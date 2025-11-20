from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.queues import queue_tools
from mayan.apps.task_manager.classes import CeleryQueue
from mayan.apps.task_manager.workers import worker_b

queue_indexing = CeleryQueue(
    label=_('Indexing'), name='indexing', worker=worker_b
)

queue_indexing.add_task_type(
    label=_('Delete empty index nodes'),
    dotted_path='mayan.apps.document_indexing.tasks.task_index_instance_node_delete_empty'
)
queue_indexing.add_task_type(
    label=_('Remove document'),
    dotted_path='mayan.apps.document_indexing.tasks.task_index_instance_document_remove'
)
queue_indexing.add_task_type(
    label=_('Index document'),
    dotted_path='mayan.apps.document_indexing.tasks.task_index_instance_document_add'
)

# Document indexing coordination tasks (from documents app)
# These tasks coordinate indexing between Dynamic Search and Document Indexing
try:
    # Try to import the tasks to verify they exist
    from mayan.apps.documents.tasks import (
        task_coordinate_document_index,
        task_coordinate_document_deindex,
        task_coordinate_document_batch_index
    )
    
    # Register tasks if import successful
    queue_indexing.add_task_type(
        label=_('Coordinate document indexing'),
        dotted_path='mayan.apps.documents.tasks.task_coordinate_document_index'
    )
    queue_indexing.add_task_type(
        label=_('Coordinate document deindexing'),
        dotted_path='mayan.apps.documents.tasks.task_coordinate_document_deindex'
    )
    queue_indexing.add_task_type(
        label=_('Coordinate batch document indexing'),
        dotted_path='mayan.apps.documents.tasks.task_coordinate_document_batch_index'
    )
    queue_indexing.add_task_type(
        label=_('Validate document for indexing'),
        dotted_path='mayan.apps.documents.tasks.task_validate_document_for_indexing'
    )
    queue_indexing.add_task_type(
        label=_('Conditional index instance'),
        dotted_path='mayan.apps.documents.tasks.task_index_instance_conditional'
    )
    queue_indexing.add_task_type(
        label=_('Conditional document add to index'),
        dotted_path='mayan.apps.documents.tasks.task_index_instance_document_add_conditional'
    )
    queue_indexing.add_task_type(
        label=_('Release indexing lock'),
        dotted_path='mayan.apps.documents.tasks.task_release_indexing_lock'
    )
    queue_indexing.add_task_type(
        label=_('Safe index instance'),
        dotted_path='mayan.apps.documents.tasks.task_index_instance_safe'
    )
    queue_indexing.add_task_type(
        label=_('Safe document add to index'),
        dotted_path='mayan.apps.documents.tasks.task_index_instance_document_add_safe'
    )
    queue_indexing.add_task_type(
        label=_('Cleanup stale indexing locks'),
        dotted_path='mayan.apps.documents.tasks.task_cleanup_stale_indexing_locks'
    )
except (ImportError, AttributeError) as e:
    # Documents app not available or tasks not found, skip registration
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f'Could not register document indexing coordination tasks: {e}')
    pass

queue_tools.add_task_type(
    label=_('Rebuild index'),
    dotted_path='mayan.apps.document_indexing.tasks.task_index_template_rebuild'
)
