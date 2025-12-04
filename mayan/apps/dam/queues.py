"""
Celery queues for DAM module.

Phase B4: Async & Webhooks - AI analysis tasks registered with 'tools' queue
which is processed by worker_d.
"""
from django.utils.translation import ugettext_lazy as _


def register_dam_tasks():
    """
    Register DAM tasks with existing queues.
    Called during app ready() to ensure task_manager is loaded.
    """
    try:
        # Import queue_tools from common app (where it's defined)
        from mayan.apps.common.queues import queue_tools
        
        # Register AI analysis task with tools queue
        queue_tools.add_task_type(
            dotted_path='mayan.apps.dam.tasks.analyze_document_with_ai',
            label=_('Analyze document with AI')
        )
        
        # Register bulk analysis task
        queue_tools.add_task_type(
            dotted_path='mayan.apps.dam.tasks.bulk_analyze_documents',
            label=_('Bulk analyze documents with AI')
        )
        
        # Register Yandex Disk import task
        queue_tools.add_task_type(
            dotted_path='mayan.apps.dam.tasks.import_yandex_disk',
            label=_('Import from Yandex Disk')
        )
        
        return True
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f'Could not register DAM tasks with tools queue: {e}')
        return False
