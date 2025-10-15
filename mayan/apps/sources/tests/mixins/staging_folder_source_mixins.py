import json
from pathlib import Path
import shutil

from mayan.apps.documents.tests.literals import TEST_FILE_SMALL_PATH
from mayan.apps.storage.utils import fs_cleanup, mkdtemp

from ...source_backends.literals import SOURCE_UNCOMPRESS_CHOICE_NEVER
from ...source_backends.staging_folder_backends import SourceBackendStagingFolder

from ..literals import (
    TEST_STAGING_PREVIEW_HEIGHT, TEST_STAGING_PREVIEW_WIDTH
)

from .base_mixins import SourceTestMixin


class StagingFolderActionAPIViewTestMixin:
    def _request_test_staging_folder_file_delete_action_api_view(self):
        return self.post(
            viewname='rest_api:source-action', kwargs={
                'action_name': 'file_delete', 'source_id': self._test_source.pk
            }, data={
                'arguments': json.dumps(
                    obj={
                        'encoded_filename': self._test_staging_folder_file.encoded_filename
                    }
                )
            }
        )

    def _request_test_staging_folder_file_image_action_api_view(self):
        return self.get(
            viewname='rest_api:source-action', kwargs={
                'action_name': 'file_image', 'source_id': self._test_source.pk
            }, query={'encoded_filename': self._test_staging_folder_file.encoded_filename}
        )

    def _request_test_staging_folder_file_list_action_api_view(self):
        return self.get(
            viewname='rest_api:source-action', kwargs={
                'action_name': 'file_list', 'source_id': self._test_source.pk
            }
        )

    def _request_test_staging_folder_file_upload_action_api_view(self):
        return self.post(
            viewname='rest_api:source-action', kwargs={
                'action_name': 'file_upload', 'source_id': self._test_source.pk
            }, data={
                'arguments': json.dumps(
                    obj={
                        'document_type_id': self._test_document_type.pk,
                        'encoded_filename': self._test_staging_folder_file.encoded_filename
                    }
                )
            }
        )


class StagingFolderTestMixin(SourceTestMixin):
    _create_source_method = '_create_test_staging_folder'

    def setUp(self):
        self._temporary_folders = []
        super().setUp()
        self._test_staging_folder_files = []

    def tearDown(self):
        for temporary_folders in self._temporary_folders:
            fs_cleanup(filename=temporary_folders)

        super().tearDown()

    def _create_test_staging_folder(
        self, extra_data=None, add_subdirectory=False
    ):
        temporary_folder = mkdtemp()
        self._temporary_folders.append(temporary_folder)

        if add_subdirectory:
            self._temporary_subfolder = mkdtemp(dir=str(temporary_folder))
            self._temporary_folders.append(self._temporary_subfolder)

        backend_data = {
            'folder_path': temporary_folder,
            'preview_width': TEST_STAGING_PREVIEW_WIDTH,
            'preview_height': TEST_STAGING_PREVIEW_HEIGHT,
            'uncompress': SOURCE_UNCOMPRESS_CHOICE_NEVER
        }

        if extra_data:
            backend_data.update(extra_data)

        self._create_test_source(
            backend_path=SourceBackendStagingFolder.get_class_path(),
            backend_data=backend_data
        )

    def _copy_test_staging_folder_document(self, filename=None, to_subfolder=False):
        path = Path(self._test_source.get_backend_data()['folder_path'])

        if to_subfolder:
            path = Path(self._temporary_subfolder)

        shutil.copy(
            src=TEST_FILE_SMALL_PATH, dst=str(path / (filename or ''))
        )

        test_staging_folder_file_list = list(
            self._test_source.get_backend_instance().get_files()
        )
        if test_staging_folder_file_list:
            self._test_staging_folder_file = test_staging_folder_file_list[0]
            self._test_staging_folder_files.append(self._test_staging_folder_file)


class StagingFolderViewTestMixin:
    def _request_staging_folder_action_file_delete_view_via_get(self):
        return self.get(
            viewname='sources:source_action', kwargs={
                'source_id': self._test_source.pk,
                'action_name': 'file_delete'
            }, query={
                'encoded_filename': self._test_staging_folder_file.encoded_filename
            }
        )

    def _request_staging_folder_action_file_delete_view_via_post(self):
        return self.post(
            viewname='sources:source_action', kwargs={
                'source_id': self._test_source.pk,
                'action_name': 'file_delete'
            }, query={
                'encoded_filename': self._test_staging_folder_file.encoded_filename
            }
        )
