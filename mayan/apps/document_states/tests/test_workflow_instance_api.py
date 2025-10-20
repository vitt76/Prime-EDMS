import json

from rest_framework import status

from mayan.apps.documents.tests.mixins.document_mixins import DocumentTestMixin
from mayan.apps.rest_api.tests.base import BaseAPITestCase

from ..events import (
    event_workflow_instance_created, event_workflow_instance_transitioned
)
from ..permissions import (
    permission_workflow_instance_transition,
    permission_workflow_template_view, permission_workflow_tools
)

from .literals import TEST_WORKFLOW_INSTANCE_LOG_ENTRY_EXTRA_DATA
from .mixins.workflow_instance_mixins import (
    WorkflowInstanceAPIViewTestMixin,
    WorkflowInstanceLogEntryTransitrionListAPIViewTestMixin
)
from .mixins.workflow_template_mixins import WorkflowTemplateTestMixin


class WorkflowInstanceAPIViewTestCase(
    DocumentTestMixin, WorkflowInstanceAPIViewTestMixin,
    WorkflowTemplateTestMixin, BaseAPITestCase
):
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()
        self._create_test_workflow_template(add_test_document_type=True)
        self._create_test_workflow_template_state()
        self._create_test_workflow_template_state()
        self._create_test_workflow_template_transition()
        self._create_test_document_stub()

    def test_workflow_instance_detail_api_view_no_permission(self):
        self._clear_events()

        response = self._request_test_workflow_instance_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_detail_api_view_with_workflow_access(self):
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_template_view
        )

        self._clear_events()

        response = self._request_test_workflow_instance_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_detail_api_view_with_document_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_workflow_template_view
        )

        self._clear_events()

        response = self._request_test_workflow_instance_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_detail_api_view_with_full_access(self):
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_template_view
        )
        self.grant_access(
            obj=self._test_document,
            permission=permission_workflow_template_view
        )

        self._clear_events()

        response = self._request_test_workflow_instance_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['id'], self._test_document.workflows.first().pk
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_trashed_document_workflow_instance_detail_api_view_with_full_access(self):
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_template_view
        )
        self.grant_access(
            obj=self._test_document,
            permission=permission_workflow_template_view
        )

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_workflow_instance_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_list_api_view_no_permission(self):
        self._clear_events()

        response = self._request_test_workflow_instance_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_list_api_view_with_document_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_workflow_template_view
        )

        self._clear_events()

        response = self._request_test_workflow_instance_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_list_api_view_with_workflow_access(self):
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_template_view
        )

        self._clear_events()

        response = self._request_test_workflow_instance_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_list_api_view_with_full_access(self):
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_template_view
        )
        self.grant_access(
            obj=self._test_document,
            permission=permission_workflow_template_view
        )

        self._clear_events()

        response = self._request_test_workflow_instance_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['id'],
            self._test_document.workflows.first().pk
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_trashed_document_workflow_instance_list_api_view_with_full_access(self):
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_template_view
        )
        self.grant_access(
            obj=self._test_document,
            permission=permission_workflow_template_view
        )

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_workflow_instance_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_log_entries_create_api_view_no_permission(self):
        workflow_instance = self._test_document.workflows.first()

        self._clear_events()

        response = self._request_test_workflow_instance_log_entry_create_api_view(
            workflow_instance=workflow_instance
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(workflow_instance.log_entries.count(), 0)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_log_entries_create_api_view_with_document_access(self):
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_instance_transition
        )
        workflow_instance = self._test_document.workflows.first()

        self._clear_events()

        response = self._request_test_workflow_instance_log_entry_create_api_view(
            workflow_instance=workflow_instance
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(workflow_instance.log_entries.count(), 0)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_log_entries_create_api_view_with_transition_access(self):
        self.grant_access(
            obj=self._test_workflow_template_transition,
            permission=permission_workflow_instance_transition
        )
        workflow_instance = self._test_document.workflows.first()

        self._clear_events()

        response = self._request_test_workflow_instance_log_entry_create_api_view(
            workflow_instance=workflow_instance
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(workflow_instance.log_entries.count(), 0)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_log_entries_create_api_view_with_document_and_transition_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_workflow_instance_transition
        )
        self.grant_access(
            obj=self._test_workflow_template_transition,
            permission=permission_workflow_instance_transition
        )
        workflow_instance = self._test_document.workflows.first()

        self._clear_events()

        response = self._request_test_workflow_instance_log_entry_create_api_view(
            workflow_instance=workflow_instance
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(workflow_instance.log_entries.count(), 1)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, self._test_document)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(
            events[0].target, self._test_document.workflows.first()
        )
        self.assertEqual(
            events[0].verb, event_workflow_instance_transitioned.id
        )

    def test_trashed_document_workflow_instance_log_entries_create_api_view_with_document_and_transition_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_workflow_instance_transition
        )
        self.grant_access(
            obj=self._test_workflow_template_transition,
            permission=permission_workflow_instance_transition
        )
        workflow_instance = self._test_document.workflows.first()

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_workflow_instance_log_entry_create_api_view(
            workflow_instance=workflow_instance
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(workflow_instance.log_entries.count(), 0)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_log_entries_create_api_view_with_workflow_access(self):
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_instance_transition
        )
        workflow_instance = self._test_document.workflows.first()

        self._clear_events()

        response = self._request_test_workflow_instance_log_entry_create_api_view(
            workflow_instance=workflow_instance
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(workflow_instance.log_entries.count(), 0)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_log_entries_create_api_view_with_document_and_workflow_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_workflow_instance_transition
        )
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_instance_transition
        )
        workflow_instance = self._test_document.workflows.first()

        self._clear_events()

        response = self._request_test_workflow_instance_log_entry_create_api_view(
            workflow_instance=workflow_instance
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(workflow_instance.log_entries.count(), 1)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, self._test_document)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(
            events[0].target, self._test_document.workflows.first()
        )
        self.assertEqual(
            events[0].verb, event_workflow_instance_transitioned.id
        )

    def test_trashed_document_workflow_instance_log_entries_create_api_view_with_document_and_workflow_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_workflow_instance_transition
        )
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_instance_transition
        )
        workflow_instance = self._test_document.workflows.first()

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_workflow_instance_log_entry_create_api_view(
            workflow_instance=workflow_instance
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(workflow_instance.log_entries.count(), 0)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_log_entries_create_api_view_with_extra_data_document_and_workflow_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_workflow_instance_transition
        )
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_instance_transition
        )
        workflow_instance = self._test_document.workflows.first()

        self._clear_events()

        response = self._request_test_workflow_instance_log_entry_create_api_view(
            extra_data={
                'extra_data': TEST_WORKFLOW_INSTANCE_LOG_ENTRY_EXTRA_DATA
            }, workflow_instance=workflow_instance
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(workflow_instance.log_entries.count(), 1)
        workflow_instance.refresh_from_db()

        self.assertEqual(
            workflow_instance.get_context()['workflow_instance_context'],
            json.loads(s=TEST_WORKFLOW_INSTANCE_LOG_ENTRY_EXTRA_DATA)
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, self._test_document)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(
            events[0].target, self._test_document.workflows.first()
        )
        self.assertEqual(
            events[0].verb, event_workflow_instance_transitioned.id
        )

    def test_workflow_instance_log_entries_list_api_view_no_permission(self):
        self._create_test_workflow_template_instance_log_entry()

        self._clear_events()

        response = self._request_test_workflow_instance_log_entry_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_log_entries_list_api_view_with_document_access(self):
        self._create_test_workflow_template_instance_log_entry()

        self.grant_access(
            obj=self._test_document,
            permission=permission_workflow_template_view
        )

        self._clear_events()

        response = self._request_test_workflow_instance_log_entry_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['count'], 0
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_log_entries_list_api_view_with_workflow_access(self):
        self._create_test_workflow_template_instance_log_entry()

        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_template_view
        )

        self._clear_events()

        response = self._request_test_workflow_instance_log_entry_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_log_entries_list_api_view_with_full_access(self):
        self._create_test_workflow_template_instance_log_entry()

        self.grant_access(
            obj=self._test_document,
            permission=permission_workflow_template_view
        )
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_template_view
        )

        self._clear_events()

        response = self._request_test_workflow_instance_log_entry_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['count'], 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_trashed_document_workflow_instance_log_entries_list_api_view_with_full_access(self):
        self._create_test_workflow_template_instance_log_entry()

        self.grant_access(
            obj=self._test_document,
            permission=permission_workflow_template_view
        )
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_template_view
        )

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_workflow_instance_log_entry_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)


class WorkflowInstanceLaunchAPIViewTestCase(
    DocumentTestMixin, WorkflowTemplateTestMixin, BaseAPITestCase
):
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()
        self._create_test_workflow_template(
            add_test_document_type=True, auto_launch=False
        )
        self._create_test_workflow_template_state()
        self._create_test_workflow_template_state()
        self._create_test_workflow_template_transition()
        self._create_test_document_stub()

    def _request_test_workflow_instance_launch_api_view(self):
        return self.post(
            viewname='rest_api:workflow-instance-launch', kwargs={
                'document_id': self._test_document.pk
            }, data={
                'workflow_template_id': self._test_workflow_template.pk
            }
        )

    def test_workflow_instance_api_view_no_permission(self):
        test_document_workflow_instance_count = self._test_document.workflows.count()

        self._clear_events()

        response = self._request_test_workflow_instance_launch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            self._test_document.workflows.count(),
            test_document_workflow_instance_count
        )
        self.assertNotEqual(
            list(
                self._test_document.workflows.values_list(
                    'workflow', flat=True
                )
            ), [self._test_workflow_template.pk]
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_api_view_with_document_access(self):
        self.grant_access(
            obj=self._test_document, permission=permission_workflow_tools
        )

        test_document_workflow_instance_count = self._test_document.workflows.count()

        self._clear_events()

        response = self._request_test_workflow_instance_launch_api_view()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            self._test_document.workflows.count(),
            test_document_workflow_instance_count
        )
        self.assertNotEqual(
            list(
                self._test_document.workflows.values_list(
                    'workflow', flat=True
                )
            ), [self._test_workflow_template.pk]
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_api_view_with_workflow_template_access(self):
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_tools
        )

        test_document_workflow_instance_count = self._test_document.workflows.count()

        self._clear_events()

        response = self._request_test_workflow_instance_launch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            self._test_document.workflows.count(),
            test_document_workflow_instance_count
        )
        self.assertNotEqual(
            list(
                self._test_document.workflows.values_list(
                    'workflow', flat=True
                )
            ), [self._test_workflow_template.pk]
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_api_view_with_full_access(self):
        self.grant_access(
            obj=self._test_document, permission=permission_workflow_tools
        )
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_tools
        )

        test_document_workflow_instance_count = self._test_document.workflows.count()

        self._clear_events()

        response = self._request_test_workflow_instance_launch_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            self._test_document.workflows.count(),
            test_document_workflow_instance_count + 1
        )
        self.assertEqual(
            list(
                self._test_document.workflows.values_list(
                    'workflow', flat=True
                )
            ), [self._test_workflow_template.pk]
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, self._test_document)
        self.assertEqual(
            events[0].actor, self._test_document.workflows.first()
        )
        self.assertEqual(
            events[0].target, self._test_document.workflows.first()
        )
        self.assertEqual(events[0].verb, event_workflow_instance_created.id)


class WorkflowInstanceLogEntryTransitrionListAPIViewTestCase(
    DocumentTestMixin, WorkflowInstanceAPIViewTestMixin,
    WorkflowInstanceLogEntryTransitrionListAPIViewTestMixin,
    WorkflowTemplateTestMixin, BaseAPITestCase
):
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()
        self._create_test_workflow_template(add_test_document_type=True)
        self._create_test_workflow_template_state()
        self._create_test_workflow_template_state()
        self._create_test_workflow_template_transition()
        self._create_test_document_stub()
        self._test_workflow_instance = self._test_document.workflows.first()

    def test_workflow_instance_log_entry_transition_list_api_view_no_permission(self):
        self._clear_events()

        response = self._request_test_workflow_instance_log_entry_transition_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_log_entry_transition_list_api_view_with_document_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_workflow_template_view
        )

        self._clear_events()

        response = self._request_test_workflow_instance_log_entry_transition_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_log_entry_transition_list_api_view_with_template_view_access(self):
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_template_view
        )

        self._clear_events()

        response = self._request_test_workflow_instance_log_entry_transition_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_log_entry_transition_list_api_view_with_document_and_template_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_workflow_template_view
        )
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_template_view
        )

        self._clear_events()

        response = self._request_test_workflow_instance_log_entry_transition_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_log_entry_transition_list_api_view_with_transition_access(self):
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_instance_transition
        )

        self._clear_events()

        response = self._request_test_workflow_instance_log_entry_transition_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_log_entry_transition_list_api_view_with_document_and_transition_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_workflow_template_view
        )
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_instance_transition
        )

        self._clear_events()

        response = self._request_test_workflow_instance_log_entry_transition_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_log_entry_transition_list_api_view_with_teamplate_and_transition_access(self):
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_template_view
        )
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_instance_transition
        )

        self._clear_events()

        response = self._request_test_workflow_instance_log_entry_transition_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_workflow_instance_log_entry_transition_list_api_view_with_full_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_workflow_template_view
        )
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_template_view
        )
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_instance_transition
        )

        self._clear_events()

        response = self._request_test_workflow_instance_log_entry_transition_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['results'][0]['id'],
            self._test_workflow_template_transition.pk
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_trashed_document_workflow_instance_log_entry_transition_list_api_view_with_full_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_workflow_template_view
        )
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_template_view
        )
        self.grant_access(
            obj=self._test_workflow_template,
            permission=permission_workflow_instance_transition
        )

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_workflow_instance_log_entry_transition_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)
