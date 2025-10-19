from django.utils.translation import ugettext_lazy as _

from mayan.apps.task_manager.classes import CeleryQueue
from mayan.apps.task_manager.workers import worker_a

queue_distribution = CeleryQueue(
    label=_('Distribution'),
    name='distribution',
    transient=True,
    worker=worker_a
)

queue_distribution.add_task_type(
    dotted_path='mayan.apps.distribution.tasks.generate_rendition_task',
    label=_('Generate distribution rendition'),
    name='generate_rendition_task'
)

