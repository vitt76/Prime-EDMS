import logging
import sys
import time

from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.apps import MayanAppConfig

from .backends.base import LockingBackend
from .literals import PURGE_LOCKS_COMMAND, TEST_LOCK_NAME
from .settings import setting_backend

logger = logging.getLogger(name=__name__)


class LockManagerApp(MayanAppConfig):
    has_tests = True
    name = 'mayan.apps.lock_manager'
    verbose_name = _('Lock manager')

    def ready(self):
        super().ready()

        # Skip lock backend initialization if backend is empty/disabled
        if not setting_backend.value or setting_backend.value.strip() == '':
            logger.info('Lock manager backend is disabled, skipping initialization')
            return

        if PURGE_LOCKS_COMMAND not in sys.argv:
            logger.debug('Starting lock backend connectivity test')
            # Don't test for locks during the `task_manager_purge_locks`
            # command as there may be some stuck locks which will block
            # the command.
            lock_instance = LockingBackend.get_backend()
            
            # Retry logic for Redis connectivity during container startup
            max_retries = 5
            retry_delay = 3  # seconds
            
            for attempt in range(max_retries):
                try:
                    lock = lock_instance.acquire_lock(
                        name=TEST_LOCK_NAME, timeout=30
                    )
                    lock.release()
                    logger.info('Lock backend connectivity test passed')
                    break
                except Exception as exception:
                    if attempt < max_retries - 1:
                        logger.warning(
                            'Lock backend test failed (attempt %d/%d): %s. Retrying in %ds...',
                            attempt + 1, max_retries, exception, retry_delay
                        )
                        time.sleep(retry_delay)
                    else:
                        logger.error(
                            'Lock backend initialization failed after %d attempts: %s',
                            max_retries, exception
                        )
                        # Don't raise - let the app start anyway
                        # Workers will retry connecting to Redis
                        logger.warning(
                            'Continuing without lock backend validation. '
                            'Workers will retry connecting to Redis.'
                        )
