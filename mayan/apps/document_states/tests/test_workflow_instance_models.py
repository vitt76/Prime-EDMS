from mayan.apps.documents.events import (
    event_document_created, event_document_type_changed
)
from mayan.apps.documents.tests.base import GenericDocumentTestCase

from ..events import event_workflow_instance_created

from .mixins.workflow_template_mixins import WorkflowTemplateTestMixin


class WorkflowInstanceModelTestCase(
    WorkflowTemplateTestMixin, GenericDocumentTestCase
):
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()
        self._create_test_workflow_template(add_test_document_type=True)
        self._create_test_workflow_template_state()
        self._create_test_workflow_template_state()
        self._create_test_workflow_template_transition()

    def test_workflow_launch_on_document_type_change(self):
        self._create_test_document_type()

        self._create_test_document_stub()

        self._clear_events()

        self.assertEqual(self._test_document.workflows.count(), 0)

        self._test_document.document_type_change(
            document_type=self._test_document_types[0],
            _user=self._test_case_user
        )

        self.assertEqual(self._test_document.workflows.count(), 1)

        events = self._get_test_events()
        self.assertEqual(events.count(), 2)

        self.assertEqual(events[0].action_object, self._test_document)
        self.assertEqual(
            events[0].actor, self._test_document.workflows.first()
        )
        self.assertEqual(
            events[0].target, self._test_document.workflows.first()
        )
        self.assertEqual(events[0].verb, event_workflow_instance_created.id)

        self.assertEqual(
            events[1].action_object, self._test_document_types[0]
        )
        self.assertEqual(events[1].actor, self._test_case_user)
        self.assertEqual(events[1].target, self._test_document)
        self.assertEqual(events[1].verb, event_document_type_changed.id)

    def test_workflow_instance_method_get_absolute_url(self):
        self._create_test_document_stub()

        self._test_workflow_instance = self._test_document.workflows.first()

        self._test_workflow_instance.get_absolute_url()

    def test_workflow_template_auto_launch(self):
        self._test_workflow_template.auto_launch = True
        self._test_workflow_template.save()

        self._clear_events()

        self._create_test_document_stub()

        self.assertEqual(self._test_document.workflows.count(), 1)

        events = self._get_test_events()
        self.assertEqual(events.count(), 2)

        self.assertEqual(events[0].action_object, self._test_document)
        self.assertEqual(
            events[0].actor, self._test_document.workflows.first()
        )
        self.assertEqual(
            events[0].target, self._test_document.workflows.first()
        )
        self.assertEqual(events[0].verb, event_workflow_instance_created.id)

        self.assertEqual(
            events[1].action_object, self._test_document.document_type
        )
        self.assertEqual(events[1].actor, self._test_document)
        self.assertEqual(events[1].target, self._test_document)
        self.assertEqual(events[1].verb, event_document_created.id)

    def test_workflow_template_no_auto_launch(self):
        self._test_workflow_template.auto_launch = False
        self._test_workflow_template.save()

        self._clear_events()

        self._create_test_document_stub()

        self.assertEqual(self._test_document.workflows.count(), 0)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(
            events[0].action_object, self._test_document.document_type
        )
        self.assertEqual(events[0].actor, self._test_document)
        self.assertEqual(events[0].target, self._test_document)
        self.assertEqual(events[0].verb, event_document_created.id)

    def test_workflow_template_transition_no_condition(self):
        self._clear_events()

        self._create_test_document_stub()

        self._test_workflow_instance = self._test_document.workflows.first()
        self.assertEqual(
            self._test_workflow_instance.get_transition_choices().count(), 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 2)

        self.assertEqual(events[0].action_object, self._test_document)
        self.assertEqual(
            events[0].actor, self._test_document.workflows.first()
        )
        self.assertEqual(
            events[0].target, self._test_document.workflows.first()
        )
        self.assertEqual(events[0].verb, event_workflow_instance_created.id)

        self.assertEqual(
            events[1].action_object, self._test_document.document_type
        )
        self.assertEqual(events[1].actor, self._test_document)
        self.assertEqual(events[1].target, self._test_document)
        self.assertEqual(events[1].verb, event_document_created.id)

    def test_workflow_template_transition_false_condition(self):
        self._create_test_document_stub()

        self._test_workflow_instance = self._test_document.workflows.first()

        self._test_workflow_template_transition.condition = '{{ invalid_variable }}'
        self._test_workflow_template_transition.save()

        self.assertEqual(
            self._test_workflow_instance.get_transition_choices().count(), 0
        )

    def test_workflow_template_transition_true_condition(self):
        self._clear_events()

        self._create_test_document_stub()

        self._test_workflow_instance = self._test_document.workflows.first()

        self._test_workflow_template_transition.condition = '{{ workflow_instance }}'
        self._test_workflow_template_transition.save()

        self.assertEqual(
            self._test_workflow_instance.get_transition_choices().count(), 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 3)

        self.assertEqual(events[0].action_object, self._test_document)
        self.assertEqual(
            events[0].actor, self._test_document.workflows.first()
        )
        self.assertEqual(
            events[0].target, self._test_document.workflows.first()
        )
        self.assertEqual(events[0].verb, event_workflow_instance_created.id)
