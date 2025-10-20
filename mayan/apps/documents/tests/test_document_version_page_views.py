from django.contrib.contenttypes.models import ContentType

from mayan.apps.converter.layers import layer_saved_transformations
from mayan.apps.converter.permissions import (
    permission_transformation_delete, permission_transformation_edit
)
from mayan.apps.converter.tests.mixins import LayerTestMixin
from mayan.apps.documents.tests.literals import TEST_FILE_MULTI_PAGE_TIFF_FILENAME

from ..events import (
    event_document_version_page_created, event_document_version_page_deleted
)
from ..permissions import (
    permission_document_version_edit, permission_document_version_view
)

from .base import GenericDocumentViewTestCase
from .mixins.document_file_mixins import DocumentFileTestMixin
from .mixins.document_version_mixins import (
    DocumentVersionPageRemapViewTestMixin,
    DocumentVersionPageViewTestMixin,
    DocumentVersionTransformationTestMixin,
    DocumentVersionTransformationViewTestMixin
)


class DocumentVersionPageViewTestCase(
    DocumentVersionPageViewTestMixin, GenericDocumentViewTestCase
):
    def test_document_version_page_delete_no_permission(self):
        test_document_version_page_count = self._test_document_version.pages.count()

        self._clear_events()

        response = self._request_test_document_version_page_delete_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            self._test_document_version.pages.count(),
            test_document_version_page_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_page_delete_with_access(self):
        test_document_version_page_count = self._test_document_version.pages.count()

        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_edit
        )

        self._clear_events()

        response = self._request_test_document_version_page_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self._test_document_version.pages.count(),
            test_document_version_page_count - 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_document_version)
        self.assertEqual(
            events[0].verb, event_document_version_page_deleted.id
        )

    def test_trashed_document_version_page_delete_with_access(self):
        test_document_version_page_count = self._test_document_version.pages.count()

        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_edit
        )

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_document_version_page_delete_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            self._test_document_version.pages.count(),
            test_document_version_page_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_page_list_view_no_permission(self):
        self._clear_events()

        response = self._request_test_document_version_page_list_view()
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_page_list_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_view
        )

        self._clear_events()

        response = self._request_test_document_version_page_list_view()
        self.assertContains(
            response=response, status_code=200,
            text=str(self._test_document_version)
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_trashed_document_version_page_list_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_view
        )

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_document_version_page_list_view()
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_page_rotate_left_view_no_permission(self):
        self._clear_events()

        response = self._request_test_document_version_page_rotate_left_view()
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_page_rotate_left_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_view
        )

        self._clear_events()

        response = self._request_test_document_version_page_rotate_left_view()
        self.assertEqual(response.status_code, 302)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_trashed_document_version_page_rotate_left_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_view
        )

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_document_version_page_rotate_left_view()
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_page_rotate_right_view_no_permission(self):
        self._clear_events()

        response = self._request_test_document_version_page_rotate_right_view()
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_page_rotate_right_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_view
        )

        self._clear_events()

        response = self._request_test_document_version_page_rotate_right_view()
        self.assertEqual(response.status_code, 302)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_trashed_document_version_page_rotate_right_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_view
        )

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_document_version_page_rotate_right_view()
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_page_view_no_permission(self):
        self._clear_events()

        response = self._request_test_document_version_page_view(
            document_version_page=self._test_document_version.pages.first()
        )
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_page_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_view
        )

        self._clear_events()

        response = self._request_test_document_version_page_view(
            document_version_page=self._test_document_version.pages.first()
        )
        self.assertContains(
            response=response, status_code=200, text=str(
                self._test_document_version.pages.first()
            )
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_trashed_document_version_page_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_view
        )

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_document_version_page_view(
            document_version_page=self._test_document_version.pages.first()
        )
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_page_zoom_in_view_no_permission(self):
        self._clear_events()

        response = self._request_test_document_version_page_zoom_in_view()
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_page_zoom_in_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_view
        )

        self._clear_events()

        response = self._request_test_document_version_page_zoom_in_view()
        self.assertEqual(response.status_code, 302)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_trashed_document_version_page_zoom_in_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_view
        )

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_document_version_page_zoom_in_view()
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_page_zoom_out_view_no_permission(self):
        self._clear_events()

        response = self._request_test_document_version_page_zoom_out_view()
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_page_zoom_out_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_view
        )

        self._clear_events()

        response = self._request_test_document_version_page_zoom_out_view()
        self.assertEqual(response.status_code, 302)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_trashed_document_version_page_zoom_out_view_with_access(self):
        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_view
        )

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_document_version_page_zoom_out_view()
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)


class DocumentVersionPageRemapViewTestCase(
    DocumentVersionPageRemapViewTestMixin, DocumentFileTestMixin,
    GenericDocumentViewTestCase
):
    def setUp(self):
        super().setUp()
        self._upload_test_document_file()
        self._test_document_file_pages = []
        self.source_content_types = []
        self.source_object_ids = []

        for test_document_file in self._test_document.files.all():
            for test_document_file_page in test_document_file.pages.all():
                self._test_document_file_pages.append(test_document_file_page)
                self.source_content_types.append(
                    ContentType.objects.get_for_model(
                        model=test_document_file_page
                    )
                )
                self.source_object_ids.append(test_document_file_page.pk)

        self.single_page_remap_data = {
            'form-0-source_content_type': self.source_content_types[0].pk,
            'form-0-source_object_id': self.source_object_ids[0],
            'form-0-source_page_number': '1',
            'form-0-target_page_number': '1',
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '',
        }
        self.repeated_page_number_remap_data = {
            'form-0-source_content_type': self.source_content_types[0].pk,
            'form-0-source_object_id': self.source_object_ids[0],
            'form-0-source_page_number': '1',
            'form-0-target_page_number': '1',
            'form-1-source_content_type': self.source_content_types[1].pk,
            'form-1-source_object_id': self.source_object_ids[1],
            'form-1-source_page_number': '1',
            'form-1-target_page_number': '1',
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '',
        }

    def test_document_version_remap_view_no_permission(self):
        self._clear_events()

        response = self._request_test_document_version_page_list_remap_view(
            data=self.single_page_remap_data
        )
        self.assertEqual(response.status_code, 404)

        self._test_document_version.refresh_from_db()

        self.assertNotEqual(
            self._test_document_version.pages.first().content_object,
            self._test_document_file_pages[0]
        )
        self.assertEqual(
            self._test_document_version.pages.first().content_object,
            self._test_document_file_pages[1]
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_remap_view_with_access(self):
        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_edit
        )

        self._clear_events()

        response = self._request_test_document_version_page_list_remap_view(
            data=self.single_page_remap_data
        )
        self.assertEqual(response.status_code, 302)

        self._test_document_version.refresh_from_db()

        self.assertEqual(
            self._test_document_version.pages.first().content_object,
            self._test_document_file_pages[0]
        )
        self.assertNotEqual(
            self._test_document_version.pages.first().content_object,
            self._test_document_file_pages[1]
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 2)

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

    def test_trashed_document_version_remap_view_with_access(self):
        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_edit
        )

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_document_version_page_list_remap_view(
            data=self.single_page_remap_data
        )
        self.assertEqual(response.status_code, 404)

        self._test_document_version.refresh_from_db()

        self.assertNotEqual(
            self._test_document_version.pages.first().content_object,
            self._test_document_file_pages[0]
        )
        self.assertEqual(
            self._test_document_version.pages.first().content_object,
            self._test_document_file_pages[1]
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_remap_repeated_target_page_number_view_with_access(self):
        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_edit
        )

        self._clear_events()

        response = self._request_test_document_version_page_list_remap_view(
            data=self.repeated_page_number_remap_data
        )
        self.assertEqual(response.status_code, 200)

        self._test_document_version.refresh_from_db()

        self.assertNotEqual(
            self._test_document_version.pages.first().content_object,
            self._test_document_file_pages[0]
        )
        self.assertEqual(
            self._test_document_version.pages.first().content_object,
            self._test_document_file_pages[1]
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)


class DocumentVersionTransformationViewTestCase(
    LayerTestMixin, DocumentVersionTransformationTestMixin,
    DocumentVersionTransformationViewTestMixin, GenericDocumentViewTestCase
):
    _test_document_filename = TEST_FILE_MULTI_PAGE_TIFF_FILENAME

    def setUp(self):
        super().setUp()
        self.assertTrue(
            expr=self._test_document_version.pages.count() > 1,
            msg='Test document must have more than one page'
        )

    def test_document_version_transformations_clear_view_no_permission(self):
        self._create_document_version_transformation()

        transformation_count = layer_saved_transformations.get_transformations_for(
            obj=self._test_document_version.pages.first()
        ).count()

        self._clear_events()

        response = self._request_test_document_version_transformations_clear_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            layer_saved_transformations.get_transformations_for(
                obj=self._test_document_version.pages.first()
            ).count(), transformation_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_transformations_clear_view_with_access(self):
        self._create_document_version_transformation()

        transformation_count = layer_saved_transformations.get_transformations_for(
            obj=self._test_document_version.pages.first()
        ).count()

        self.grant_access(
            obj=self._test_document_version,
            permission=permission_transformation_delete
        )

        self._clear_events()

        response = self._request_test_document_version_transformations_clear_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            layer_saved_transformations.get_transformations_for(
                obj=self._test_document_version.pages.first()
            ).count(), transformation_count - 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_trashed_document_version_transformations_clear_view_with_access(self):
        self._create_document_version_transformation()

        transformation_count = layer_saved_transformations.get_transformations_for(
            obj=self._test_document_version.pages.first()
        ).count()

        self.grant_access(
            obj=self._test_document_version,
            permission=permission_transformation_delete
        )

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_document_version_transformations_clear_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            layer_saved_transformations.get_transformations_for(
                obj=self._test_document_version.pages.first()
            ).count(), transformation_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_multiple_transformations_clear_view_no_permission(self):
        self._create_document_version_transformation()

        transformation_count = layer_saved_transformations.get_transformations_for(
            obj=self._test_document_version.pages.first()
        ).count()

        self._clear_events()

        response = self._request_test_document_version_multiple_transformations_clear_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            layer_saved_transformations.get_transformations_for(
                obj=self._test_document_version.pages.first()
            ).count(), transformation_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_multiple_transformations_clear_view_with_access(self):
        self._create_document_version_transformation()

        transformation_count = layer_saved_transformations.get_transformations_for(
            obj=self._test_document_version.pages.first()
        ).count()

        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_view
        )
        self.grant_access(
            obj=self._test_document_version,
            permission=permission_transformation_delete
        )

        self._clear_events()

        response = self._request_test_document_version_multiple_transformations_clear_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            layer_saved_transformations.get_transformations_for(
                obj=self._test_document_version.pages.first()
            ).count(), transformation_count - 1,
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_trashed_document_version_multiple_transformations_clear_view_with_access(self):
        self._create_document_version_transformation()

        transformation_count = layer_saved_transformations.get_transformations_for(
            obj=self._test_document_version.pages.first()
        ).count()

        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_view
        )
        self.grant_access(
            obj=self._test_document_version,
            permission=permission_transformation_delete
        )

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_document_version_multiple_transformations_clear_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            layer_saved_transformations.get_transformations_for(
                obj=self._test_document_version.pages.first()
            ).count(), transformation_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_transformations_clone_view_no_permission(self):
        self._create_document_version_transformation()

        page_first_transformation_count = layer_saved_transformations.get_transformations_for(
            obj=self._test_document_version.pages.first()
        ).count()
        page_last_transformation_count = layer_saved_transformations.get_transformations_for(
            obj=self._test_document_version.pages.last()
        ).count()

        self._clear_events()

        response = self._request_test_document_version_transformations_clone_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            layer_saved_transformations.get_transformations_for(
                obj=self._test_document_version.pages.first()
            ).count(), page_first_transformation_count
        )
        self.assertEqual(
            layer_saved_transformations.get_transformations_for(
                obj=self._test_document_version.pages.last()
            ).count(), page_last_transformation_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_transformations_clone_view_with_access(self):
        self._create_document_version_transformation()

        page_first_transformation_count = layer_saved_transformations.get_transformations_for(
            obj=self._test_document_version.pages.first()
        ).count()
        page_last_transformation_count = layer_saved_transformations.get_transformations_for(
            obj=self._test_document_version.pages.last()
        ).count()

        self.grant_access(
            obj=self._test_document_version,
            permission=permission_transformation_edit
        )

        self._clear_events()

        response = self._request_test_document_version_transformations_clone_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            layer_saved_transformations.get_transformations_for(
                obj=self._test_document_version.pages.first()
            ).count(), page_first_transformation_count
        )
        self.assertEqual(
            layer_saved_transformations.get_transformations_for(
                obj=self._test_document_version.pages.last()
            ).count(), page_last_transformation_count + 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_trashed_document_version_transformations_clone_view_with_access(self):
        self._create_document_version_transformation()

        page_first_transformation_count = layer_saved_transformations.get_transformations_for(
            obj=self._test_document_version.pages.first()
        ).count()
        page_last_transformation_count = layer_saved_transformations.get_transformations_for(
            obj=self._test_document_version.pages.last()
        ).count()

        self.grant_access(
            obj=self._test_document_version,
            permission=permission_transformation_edit
        )

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_document_version_transformations_clone_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            layer_saved_transformations.get_transformations_for(
                obj=self._test_document_version.pages.first()
            ).count(), page_first_transformation_count
        )
        self.assertEqual(
            layer_saved_transformations.get_transformations_for(
                obj=self._test_document_version.pages.last()
            ).count(), page_last_transformation_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)
