from django.utils.translation import ugettext_lazy as _

from mayan.apps.documents.queues import queue_converter
from mayan.apps.documents.tasks import task_clear_images_cache
from mayan.apps.task_manager.classes import CeleryQueue
from mayan.apps.task_manager.workers import (
    worker_a, worker_b, worker_c, worker_d
)


queue_ocr = CeleryQueue(
    label=_('OCR'),
    name='ocr',
    worker=worker_d
)


queue_documents_periodic = CeleryQueue(
    label=_('Documents periodic'),
    name='documents_periodic',
    worker=worker_c
)


queue_checkouts_periodic = CeleryQueue(
    label=_('Checkouts periodic'),
    name='checkouts_periodic',
    worker=worker_c
)


queue_events = CeleryQueue(
    label=_('Events'),
    name='events',
    worker=worker_c
)


queue_statistics = CeleryQueue(
    label=_('Statistics'),
    name='statistics',
    worker=worker_c
)


queue_tools = CeleryQueue(
    label=_('Tools'),
    name='tools',
    worker=worker_d,
    transient=True
)


queue_search = CeleryQueue(
    label=_('Search'),
    name='search',
    worker=worker_b
)


queue_search_slow = CeleryQueue(
    label=_('Search slow'),
    name='search_slow',
    worker=worker_b
)


queue_sources = CeleryQueue(
    label=_('Sources'),
    name='sources',
    worker=worker_a
)


queue_sources_periodic = CeleryQueue(
    label=_('Sources periodic'),
    name='sources_periodic',
    worker=worker_c
)


queue_uploads = CeleryQueue(
    label=_('Uploads'),
    name='uploads',
    worker=worker_c
)


queue_documents = CeleryQueue(
    label=_('Documents'),
    name='documents',
    worker=worker_b
)


queue_document_states_medium = CeleryQueue(
    label=_('Document states medium'),
    name='document_states_medium',
    worker=worker_b
)


queue_duplicates = CeleryQueue(
    label=_('Duplicates'),
    name='duplicates',
    worker=worker_b
)


queue_file_caching = CeleryQueue(
    label=_('File caching'),
    name='file_caching',
    worker=worker_b
)


queue_file_metadata = CeleryQueue(
    label=_('File metadata'),
    name='file_metadata',
    worker=worker_b
)


queue_indexing = CeleryQueue(
    label=_('Indexing'),
    name='indexing',
    worker=worker_b
)


queue_metadata = CeleryQueue(
    label=_('Metadata'),
    name='metadata',
    worker=worker_b
)


queue_parsing = CeleryQueue(
    label=_('Parsing'),
    name='parsing',
    worker=worker_b
)


queue_signatures = CeleryQueue(
    label=_('Signatures'),
    name='signatures',
    worker=worker_b
)


queue_mailing = CeleryQueue(
    label=_('Mailing'),
    name='mailing',
    worker=worker_c
)


queue_storage_periodic = CeleryQueue(
    label=_('Storage periodic'),
    name='storage_periodic',
    worker=worker_d
)


queue_distribution = CeleryQueue(
    label=_('Distribution'),
    name='distribution',
    worker=worker_a
)


queue_converter.add_task_type(task_clear_images_cache)
