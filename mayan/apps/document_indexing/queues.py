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
except ImportError:
    # Documents app not available, skip registration
    pass

queue_tools.add_task_type(
    label=_('Rebuild index'),
    dotted_path='mayan.apps.document_indexing.tasks.task_index_template_rebuild'
)
