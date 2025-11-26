from datetime import timedelta

from django.utils.translation import ugettext_lazy as _

from mayan.apps.task_manager.classes import CeleryQueue
from mayan.apps.task_manager.workers import worker_b, worker_c

from .literals import (
    CHECK_DELETE_PERIOD_INTERVAL, CHECK_TRASH_PERIOD_INTERVAL,
    DELETE_STALE_STUBS_INTERVAL, DEFAULT_INDEXING_PERIODIC_REINDEX_INTERVAL
)
from .settings import setting_indexing_periodic_reindex_interval

queue_documents_periodic = CeleryQueue(
    name='documents_periodic', label=_('Documents periodic'), transient=True,
    worker=worker_c
)
queue_uploads = CeleryQueue(
    name='uploads', label=_('Uploads'), worker=worker_c
)
queue_documents = CeleryQueue(
    name='documents', label=_('Documents'), worker=worker_b
)

queue_documents.add_task_type(
    dotted_path='mayan.apps.documents.tasks.task_trash_can_empty',
    label=_('Empty the trash can')
)
queue_documents.add_task_type(
    dotted_path='mayan.apps.documents.tasks.task_trashed_document_delete',
    label=_('Delete a document')
)
queue_documents.add_task_type(
    dotted_path='mayan.apps.documents.tasks.task_document_version_page_list_append',
    label=_('Append all document file pages to a document version')
)
queue_documents.add_task_type(
    dotted_path='mayan.apps.documents.tasks.task_document_version_page_list_reset',
    label=_('Reset the page list of a document version')
)
queue_documents.add_task_type(
    dotted_path='mayan.apps.documents.tasks.task_document_version_delete',
    label=_('Delete a document version')
)
queue_documents.add_task_type(
    dotted_path='mayan.apps.documents.tasks.task_document_version_export',
    label=_('Export a document version')
)
queue_documents.add_task_type(
    dotted_path='mayan.apps.documents.tasks.task_coordinate_document_index',
    label=_('Coordinate document indexing')
)
queue_documents.add_task_type(
    dotted_path='mayan.apps.documents.tasks.task_coordinate_document_deindex',
    label=_('Coordinate document deindexing')
)
queue_documents.add_task_type(
    dotted_path='mayan.apps.documents.tasks.task_coordinate_document_batch_index',
    label=_('Coordinate batch document indexing')
)
queue_documents.add_task_type(
    dotted_path='mayan.apps.documents.tasks.task_validate_document_for_indexing',
    label=_('Validate document for indexing')
)
queue_documents.add_task_type(
    dotted_path='mayan.apps.documents.tasks.task_index_instance_conditional',
    label=_('Conditional search indexing task')
)
queue_documents.add_task_type(
    dotted_path='mayan.apps.documents.tasks.task_index_instance_document_add_conditional',
    label=_('Conditional hierarchy indexing task')
)
queue_documents.add_task_type(
    dotted_path='mayan.apps.documents.tasks.task_release_indexing_lock',
    label=_('Release indexing lock')
)
queue_documents.add_task_type(
    dotted_path='mayan.apps.documents.tasks.task_index_instance_safe',
    label=_('Safe search indexing fallback')
)
queue_documents.add_task_type(
    dotted_path='mayan.apps.documents.tasks.task_index_instance_document_add_safe',
    label=_('Safe hierarchy indexing fallback')
)

queue_documents_periodic.add_task_type(
    dotted_path='mayan.apps.documents.tasks.task_document_type_document_trash_periods_check',
    label=_('Check document type trash periods'),
    name='task_document_type_document_trash_periods_check',
    schedule=timedelta(seconds=CHECK_TRASH_PERIOD_INTERVAL),
)
queue_documents_periodic.add_task_type(
    dotted_path='mayan.apps.documents.tasks.task_document_stubs_delete',
    label=_('Delete document stubs'),
    name='task_document_stubs_delete',
    schedule=timedelta(seconds=DELETE_STALE_STUBS_INTERVAL),
)
queue_documents_periodic.add_task_type(
    dotted_path='mayan.apps.documents.tasks.task_document_type_trashed_document_delete_periods_check',
    label=_('Check document type delete periods'),
    name='task_document_type_trashed_document_delete_periods_check',
    schedule=timedelta(
        seconds=CHECK_DELETE_PERIOD_INTERVAL
    )
)
queue_documents_periodic.add_task_type(
    dotted_path='mayan.apps.documents.tasks.task_periodic_reindex_documents',
    label=_('Periodic document reindexing'),
    name='task_periodic_reindex_documents',
    schedule=timedelta(seconds=setting_indexing_periodic_reindex_interval.value),
)
queue_documents_periodic.add_task_type(
    dotted_path='mayan.apps.documents.tasks.task_cleanup_stale_indexing_locks',
    label=_('Cleanup stale indexing locks'),
    name='task_cleanup_stale_indexing_locks',
    schedule=timedelta(seconds=300)
)

queue_uploads.add_task_type(
    dotted_path='mayan.apps.documents.tasks.task_document_file_page_count_update',
    label=_('Update document page count')
)
queue_uploads.add_task_type(
    dotted_path='mayan.apps.documents.tasks.task_document_file_upload',
    label=_('Upload new document file')
)
queue_uploads.add_task_type(
    dotted_path='mayan.apps.documents.tasks.task_document_upload',
    label=_('Upload new document')
)

# Document indexing coordination tasks
# These tasks are registered in the indexing queue (from document_indexing.queues)
# Registration happens in document_indexing/queues.py to avoid circular imports