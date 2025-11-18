"""
Celery queues for DAM module.
"""

from django.utils.translation import ugettext_lazy as _

# AI analysis queue
queue_ai_analysis = {
    'name': 'dam_ai_analysis',
    'label': _('DAM AI Analysis'),
    'worker': 'worker_d',  # Use existing worker
}

# Bulk operations queue
queue_bulk_operations = {
    'name': 'dam_bulk_operations',
    'label': _('DAM Bulk Operations'),
    'worker': 'worker_d',
}

# All queues
queues = [
    queue_ai_analysis,
    queue_bulk_operations,
]
