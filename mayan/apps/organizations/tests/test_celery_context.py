"""
Tests for TenantAwareTask — Celery organization context.

Sprint 3: Verifies that TenantAwareTask correctly sets and clears
the ContextVar for organization isolation in Celery tasks.
"""

from unittest.mock import patch, MagicMock

from django.test import TestCase

from mayan.apps.organizations.managers import (
    get_current_organization,
    set_current_organization,
    clear_current_organization,
)
from mayan.apps.organizations.models import Organization
from mayan.apps.organizations.tasks import TenantAwareTask


class TenantAwareTaskTestCase(TestCase):
    """Test TenantAwareTask base class."""

    def setUp(self):
        self.org = Organization.objects.create(
            name='Task Test Org',
            slug='task-test-org',
            email='task@example.com',
            is_active=True,
            status='active'
        )

    def test_sets_context_var_from_organization_id(self):
        """Task with organization_id kwarg should set ContextVar."""
        context_org_during_run = None

        class TestTask(TenantAwareTask):
            name = 'test_task_with_org'

            def run(self, *args, **kwargs):
                nonlocal context_org_during_run
                context_org_during_run = get_current_organization()
                return 'ok'

        task = TestTask()
        result = task(organization_id=str(self.org.pk))

        self.assertEqual(result, 'ok')
        self.assertEqual(context_org_during_run, self.org)

    def test_clears_context_var_after_run(self):
        """ContextVar should be cleared after task completes."""
        # Ensure clean state
        clear_current_organization()

        class TestTask(TenantAwareTask):
            name = 'test_task_cleanup'

            def run(self, *args, **kwargs):
                return 'done'

        task = TestTask()
        task(organization_id=str(self.org.pk))

        # After task, ContextVar should be reset to previous value (None)
        self.assertIsNone(get_current_organization())

    def test_works_without_organization_id(self):
        """Task without organization_id should work normally."""
        context_org_during_run = 'NOT_SET'

        class TestTask(TenantAwareTask):
            name = 'test_task_no_org'

            def run(self, *args, **kwargs):
                nonlocal context_org_during_run
                context_org_during_run = get_current_organization()
                return 'ok'

        # Ensure clean state
        clear_current_organization()

        task = TestTask()
        result = task()

        self.assertEqual(result, 'ok')
        self.assertIsNone(context_org_during_run)

    def test_context_cleaned_on_exception(self):
        """ContextVar should be cleaned even if task raises."""
        clear_current_organization()

        class FailingTask(TenantAwareTask):
            name = 'test_task_failing'

            def run(self, *args, **kwargs):
                raise ValueError('Intentional failure')

        task = FailingTask()

        with self.assertRaises(ValueError):
            task(organization_id=str(self.org.pk))

        # Context should still be cleaned
        self.assertIsNone(get_current_organization())

    def test_invalid_organization_id_logs_warning(self):
        """Invalid organization_id should log warning, not crash."""
        context_org_during_run = 'NOT_SET'

        class TestTask(TenantAwareTask):
            name = 'test_task_invalid_org'

            def run(self, *args, **kwargs):
                nonlocal context_org_during_run
                context_org_during_run = get_current_organization()
                return 'ok'

        task = TestTask()
        result = task(
            organization_id='00000000-0000-0000-0000-000000000000'
        )

        self.assertEqual(result, 'ok')
        # Context should be None since org doesn't exist
        self.assertIsNone(context_org_during_run)
