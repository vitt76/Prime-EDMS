from mayan.apps.documents.tests.mixins.document_mixins import DocumentTestMixin
from mayan.apps.testing.tests.base import BaseTestCase

from ..forms import DocumentMetadataForm

from .mixins import MetadataTypeTestMixin


class DocumentMetadataFormTestCase(
    DocumentTestMixin, MetadataTypeTestMixin, BaseTestCase
):
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()

        self._create_test_document_stub()
        self._create_test_metadata_type(
            add_test_document_type=True, required=True
        )

    def test_document_metadata_form_empty_required(self):
        form = DocumentMetadataForm(
            data={'update': True},
            initial={
                'document_type': self._test_document_type,
                'metadata_type': self._test_metadata_type
            }
        )

        # Trigger clean method.
        errors = form.errors

        self.assertEqual(
            errors['value'], [
                '"{}" is required for this document type.'.format(
                    self._test_metadata_type.label
                )
            ]
        )
        self.assertEqual(
            errors['metadata_type_id'], ['This field is required.']
        )

    def test_document_metadata_form_required_with_value_no_checkbox(self):
        form = DocumentMetadataForm(
            data={
                'update': False,
                'value': 'test value'
            },
            initial={
                'document_type': self._test_document_type,
                'metadata_type': self._test_metadata_type
            }
        )

        # Trigger clean method.
        errors = form.errors

        self.assertEqual(
            errors['value'], [
                '"{}" is required for this document type.'.format(
                    self._test_metadata_type.label
                )
            ]
        )
        self.assertEqual(
            errors['metadata_type_id'], ['This field is required.']
        )
