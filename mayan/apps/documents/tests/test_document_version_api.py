from rest_framework import status

from mayan.apps.messaging.events import event_message_created
from mayan.apps.messaging.models import Message
from mayan.apps.rest_api.tests.base import (
    BaseAPITestCase, BaseAPITransactionTestCase
)
from mayan.apps.storage.events import event_download_file_created
from mayan.apps.storage.models import DownloadFile

from ..document_file_actions import (
    DocumentFileActionAppendNewPages, DocumentFileActionNothing
)
from ..events import (
    event_document_version_created, event_document_version_deleted,
    event_document_version_edited, event_document_version_exported,
    event_document_version_page_created, event_document_version_page_deleted
)
from ..permissions import (
    permission_document_version_create, permission_document_version_delete,
    permission_document_version_edit, permission_document_version_view,
    permission_document_version_export
)

from .mixins.document_mixins import DocumentTestMixin
from .mixins.document_file_mixins import DocumentFileTestMixin
from .mixins.document_version_mixins import (
    DocumentVersionModificationAPIViewTestMixin, DocumentVersionAPIViewTestMixin,
    DocumentVersionTestMixin
)


class DocumentVersionModificationAPIViewTestCase(
    DocumentFileTestMixin, DocumentTestMixin,
    DocumentVersionModificationAPIViewTestMixin, DocumentVersionTestMixin,
    BaseAPITestCase
):
    def test_document_version_action_page_append_api_view_no_permission(self):
        self._upload_test_document_file(
            action=DocumentFileActionNothing.backend_id
        )

        self._clear_events()

        response = self._request_test_document_version_action_page_append_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self._test_document_version.refresh_from_db()

        self.assertEqual(
            self._test_document_version.pages.count(),
            self._test_document_files[0].pages.count()
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_action_page_append_api_view_with_access(self):
        self._upload_test_document_file(
            action=DocumentFileActionNothing.backend_id
        )

        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_edit
        )

        self._clear_events()

        response = self._request_test_document_version_action_page_append_api_view()
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        self._test_document_version.refresh_from_db()

        self.assertEqual(
            self._test_document_version.pages.count(),
            self._test_document_files[0].pages.count() + self._test_document_files[1].pages.count()
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 3)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_document_version)
        self.assertEqual(
            events[0].verb, event_document_version_page_deleted.id
        )

        self.assertEqual(events[1].action_object, self._test_document_version)
        self.assertEqual(events[1].actor, self._test_case_user)
        self.assertEqual(
            events[1].target, self._test_document_version.pages[0]
        )
        self.assertEqual(
            events[1].verb, event_document_version_page_created.id
        )
        self.assertEqual(events[2].action_object, self._test_document_version)
        self.assertEqual(events[2].actor, self._test_case_user)
        self.assertEqual(
            events[2].target, self._test_document_version.pages[1]
        )
        self.assertEqual(
            events[2].verb, event_document_version_page_created.id
        )

    def test_trashed_document_version_action_page_append_api_view_with_access(self):
        self._upload_test_document_file(
            action=DocumentFileActionNothing.backend_id
        )

        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_edit
        )

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_document_version_action_page_append_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self._test_document_version.refresh_from_db()

        self.assertEqual(
            self._test_document_version.pages.count(),
            self._test_document_files[0].pages.count()
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_action_page_reset_api_view_no_permission(self):
        self._upload_test_document_file(
            action=DocumentFileActionAppendNewPages.backend_id
        )

        self._clear_events()

        response = self._request_test_document_version_action_page_reset_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self._test_document_version.refresh_from_db()

        self.assertEqual(
            self._test_document_version.pages.count(),
            self._test_document_files[0].pages.count() + self._test_document_files[1].pages.count()
        )

        self.assertEqual(
            self._test_document_version.pages.all()[0].content_object,
            self._test_document_file_pages[0]
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_action_page_reset_api_view_with_access(self):
        self._upload_test_document_file(
            action=DocumentFileActionAppendNewPages.backend_id
        )

        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_edit
        )

        self._clear_events()

        response = self._request_test_document_version_action_page_reset_api_view()
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        self._test_document_version.refresh_from_db()

        self.assertEqual(
            self._test_document_version.pages.count(),
            self._test_document_files[0].pages.count()
        )

        self.assertEqual(
            self._test_document_version.pages.all()[0].content_object,
            self._test_document_file_pages[1]
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 3)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_document_version)
        self.assertEqual(
            events[0].verb, event_document_version_page_deleted.id
        )

        self.assertEqual(events[1].action_object, None)
        self.assertEqual(events[1].actor, self._test_case_user)
        self.assertEqual(events[1].target, self._test_document_version)
        self.assertEqual(
            events[1].verb, event_document_version_page_deleted.id
        )

        self.assertEqual(events[2].action_object, self._test_document_version)
        self.assertEqual(events[2].actor, self._test_case_user)
        self.assertEqual(
            events[2].target, self._test_document_version.pages[0]
        )
        self.assertEqual(
            events[2].verb, event_document_version_page_created.id
        )

    def test_trashed_document_version_action_page_reset_api_view_with_access(self):
        self._upload_test_document_file(
            action=DocumentFileActionAppendNewPages.backend_id
        )

        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_edit
        )

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_document_version_action_page_reset_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self._test_document_version.refresh_from_db()

        self.assertEqual(
            self._test_document_version.pages.count(),
            self._test_document_files[0].pages.count() + self._test_document_files[1].pages.count()
        )

        self.assertEqual(
            self._test_document_version.pages.all()[0].content_object,
            self._test_document_file_pages[0]
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)


class DocumentVersionAPIViewTestCase(
    DocumentVersionAPIViewTestMixin, DocumentTestMixin,
    DocumentVersionTestMixin, BaseAPITestCase
):
    def test_document_version_create_api_view_no_permission(self):
        document_version_count = self._test_document.versions.count()

        self._clear_events()

        response = self._request_test_document_version_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            self._test_document.versions.count(), document_version_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_create_api_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_create
        )

        document_version_count = self._test_document.versions.count()

        self._clear_events()

        response = self._request_test_document_version_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(
            self._test_document.versions.count(), document_version_count + 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)
        self.assertEqual(events[0].action_object, self._test_document)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_document_version)
        self.assertEqual(events[0].verb, event_document_version_created.id)

    def test_trashed_document_version_create_api_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_create
        )

        document_version_count = self._test_document.versions.count()

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_document_version_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            self._test_document.versions.count(), document_version_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_delete_api_view_no_permission(self):
        document_version_count = self._test_document.versions.count()

        self._clear_events()

        response = self._request_test_document_version_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            self._test_document.versions.count(), document_version_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_delete_api_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_delete
        )

        document_version_count = self._test_document.versions.count()

        self._clear_events()

        response = self._request_test_document_version_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(
            self._test_document.versions.count(), document_version_count - 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)
        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_document)
        self.assertEqual(events[0].verb, event_document_version_deleted.id)

    def test_trashed_document_version_delete_api_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_delete
        )

        document_version_count = self._test_document.versions.count()

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_document_version_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            self._test_document.versions.count(), document_version_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_detail_api_view_no_permission(self):
        self._clear_events()

        response = self._request_test_document_version_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_detail_api_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_view
        )

        self._clear_events()

        response = self._request_test_document_version_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.data['id'], self._test_document.version_active.id
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_trashed_document_version_detail_api_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_view
        )

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_document_version_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_edit_via_patch_api_view_no_permission(self):
        document_version_comment = self._test_document.version_active.comment

        self._clear_events()

        response = self._request_test_document_version_edit_via_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self._test_document.version_active.refresh_from_db()
        self.assertEqual(
            self._test_document.version_active.comment,
            document_version_comment
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_edit_via_patch_api_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_edit
        )

        document_version_comment = self._test_document.version_active.comment

        self._clear_events()

        response = self._request_test_document_version_edit_via_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self._test_document.version_active.refresh_from_db()
        self.assertNotEqual(
            self._test_document.version_active.comment,
            document_version_comment
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, self._test_document)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_document_version)
        self.assertEqual(events[0].verb, event_document_version_edited.id)

    def test_trashed_document_version_edit_via_patch_api_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_edit
        )

        document_version_comment = self._test_document.version_active.comment

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_document_version_edit_via_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self._test_document.version_active.refresh_from_db()
        self.assertEqual(
            self._test_document.version_active.comment,
            document_version_comment
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_edit_via_put_api_view_no_permission(self):
        document_version_comment = self._test_document.version_active.comment

        self._clear_events()

        response = self._request_test_document_version_edit_via_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self._test_document.version_active.refresh_from_db()
        self.assertEqual(
            self._test_document.version_active.comment,
            document_version_comment
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_edit_via_put_api_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_edit
        )

        document_version_comment = self._test_document.version_active.comment

        self._clear_events()

        response = self._request_test_document_version_edit_via_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self._test_document.version_active.refresh_from_db()
        self.assertNotEqual(
            self._test_document.version_active.comment,
            document_version_comment
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)
        self.assertEqual(events[0].action_object, self._test_document)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_document_version)
        self.assertEqual(events[0].verb, event_document_version_edited.id)

    def test_trashed_document_version_edit_via_put_api_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_edit
        )

        document_version_comment = self._test_document.version_active.comment

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_document_version_edit_via_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self._test_document.version_active.refresh_from_db()
        self.assertEqual(
            self._test_document.version_active.comment,
            document_version_comment
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_list_api_view_no_permission(self):
        self._clear_events()

        response = self._request_test_document_version_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_list_api_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_view
        )

        self._clear_events()

        response = self._request_test_document_version_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.data['results'][0]['id'],
            self._test_document.version_active.id
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_trashed_document_version_list_api_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_view
        )

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_document_version_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)


class DocumentVersionExportAPIViewTestCase(
    DocumentVersionAPIViewTestMixin, DocumentTestMixin,
    DocumentVersionTestMixin, BaseAPITransactionTestCase
):
    def test_document_version_export_api_view_via_get_no_permission(self):
        download_file_count = DownloadFile.objects.count()
        message_count = Message.objects.count()

        self._clear_events()

        response = self._request_test_document_version_export_api_view_via_get()
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

        self.assertEqual(
            DownloadFile.objects.count(), download_file_count
        )
        self.assertEqual(Message.objects.count(), message_count)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_export_api_view_via_get_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_export
        )
        download_file_count = DownloadFile.objects.count()
        message_count = Message.objects.count()

        self._clear_events()

        response = self._request_test_document_version_export_api_view_via_get()
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

        self.assertEqual(
            DownloadFile.objects.count(), download_file_count
        )
        self.assertEqual(Message.objects.count(), message_count)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_trashed_document_version_export_api_view_via_get_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_export
        )
        download_file_count = DownloadFile.objects.count()
        message_count = Message.objects.count()

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_document_version_export_api_view_via_get()
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

        self.assertEqual(
            DownloadFile.objects.count(), download_file_count
        )
        self.assertEqual(Message.objects.count(), message_count)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_export_api_view_via_post_no_permission(self):
        download_file_count = DownloadFile.objects.count()
        message_count = Message.objects.count()

        self._clear_events()

        response = self._request_test_document_version_export_api_view_via_post()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            DownloadFile.objects.count(), download_file_count
        )
        self.assertEqual(Message.objects.count(), message_count)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_export_api_view_via_post_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_export
        )
        download_file_count = DownloadFile.objects.count()
        message_count = Message.objects.count()

        self._clear_events()

        response = self._request_test_document_version_export_api_view_via_post()
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        self.assertEqual(
            DownloadFile.objects.count(), download_file_count + 1
        )
        self.assertEqual(Message.objects.count(), message_count + 1)

        test_download_file = DownloadFile.objects.first()
        test_message = Message.objects.first()

        events = self._get_test_events()
        self.assertEqual(events.count(), 3)

        self.assertEqual(events[0].action_object, self._test_document_version)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, test_download_file)
        self.assertEqual(events[0].verb, event_download_file_created.id)

        self.assertEqual(events[1].action_object, test_download_file)
        self.assertEqual(events[1].actor, self._test_case_user)
        self.assertEqual(events[1].target, self._test_document_version)
        self.assertEqual(events[1].verb, event_document_version_exported.id)

        self.assertEqual(events[2].action_object, None)
        self.assertEqual(events[2].actor, test_message)
        self.assertEqual(events[2].target, test_message)
        self.assertEqual(events[2].verb, event_message_created.id)

    def test_trashed_document_version_export_api_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_export
        )
        download_file_count = DownloadFile.objects.count()

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_document_version_export_api_view_via_post()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            DownloadFile.objects.count(), download_file_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)
