# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError

from mayan.apps.documents.models import DocumentType
from mayan.apps.documents.tests.literals import TEST_DOCUMENT_TYPE_2_LABEL
from mayan.apps.documents.tests.mixins.document_mixins import DocumentTestMixin
from mayan.apps.testing.tests.base import BaseTestCase

from ..models import DocumentMetadata

from .literals import (
    TEST_DEFAULT_VALUE, TEST_LOOKUP_TEMPLATE, TEST_LOOKUP_VALUE_INCORRECT,
    TEST_LOOKUP_VALUE_CORRECT
)
from .mixins import MetadataTypeTestMixin


class MetadataTypeTestCase(
    DocumentTestMixin, MetadataTypeTestMixin, BaseTestCase
):
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()

        self._create_test_document_stub()
        self._create_test_metadata_type(add_test_document_type=True)

    def test_add_new_metadata_type_on_document_type_change(self):
        """
        When switching document types, add the required metadata of the new
        document type, the value to the default of the metadata type.
        """
        self._test_metadata_type.default = TEST_DEFAULT_VALUE
        self._test_metadata_type.save()

        self._test_document_type_2 = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_2_LABEL
        )

        self._test_document_type_2.metadata.create(
            metadata_type=self._test_metadata_type, required=True
        )

        self._test_document.document_type_change(document_type=self._test_document_type_2)

        self.assertEqual(self._test_document.metadata.count(), 1)
        self.assertEqual(
            self._test_document.metadata.first().value, TEST_DEFAULT_VALUE
        )

    def test_default(self):
        self._test_metadata_type.default = TEST_DEFAULT_VALUE
        self._test_metadata_type.save()

        document_metadata = DocumentMetadata(
            document=self._test_document, metadata_type=self._test_metadata_type
        )

        document_metadata.full_clean()
        document_metadata.save()

        self.assertEqual(
            getattr(
                self._test_document.metadata_value_of,
                self._test_metadata_type.name
            ), TEST_DEFAULT_VALUE
        )

    def test_default_missing(self):
        document_metadata = DocumentMetadata(
            document=self._test_document, metadata_type=self._test_metadata_type
        )

        document_metadata.full_clean()
        document_metadata.save()

        self.assertEqual(
            getattr(
                self._test_document.metadata_value_of,
                self._test_metadata_type.name
            ), None
        )

    def test_delete_metadata_type_present_assigned_as_document_metadata(self):
        # GitLab issue #753
        document_metadata = DocumentMetadata(
            document=self._test_document, metadata_type=self._test_metadata_type,
            value=TEST_DEFAULT_VALUE
        )

        document_metadata.full_clean()
        document_metadata.save()

        # Must not raise an error
        self._test_metadata_type.delete()

    def test_delete_metadata_value_on_document_type_change(self):
        """
        Delete the old document metadata whose types are not present in the
        new document type
        """
        document_metadata = DocumentMetadata(
            document=self._test_document, metadata_type=self._test_metadata_type,
            value=TEST_DEFAULT_VALUE
        )

        document_metadata.full_clean()
        document_metadata.save()

        self._test_document_type_2 = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_2_LABEL
        )

        self._test_document.document_type_change(document_type=self._test_document_type_2)

        self.assertEqual(self._test_document.metadata.count(), 0)

    def test_duplicate_metadata_value_on_document_type_change(self):
        """
        Delete the old document metadata whose types are not present in the
        new document type
        """
        document_metadata = DocumentMetadata(
            document=self._test_document, metadata_type=self._test_metadata_type,
            value=TEST_DEFAULT_VALUE
        )

        document_metadata.full_clean()
        document_metadata.save()

        self._test_document_type_2 = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_2_LABEL
        )

        self._test_document_type_2.metadata.create(
            metadata_type=self._test_metadata_type, required=True
        )

        self._test_document.document_type_change(document_type=self._test_document_type_2)

        self.assertEqual(self._test_document.metadata.count(), 1)
        self.assertEqual(
            self._test_document.metadata.first().value, TEST_DEFAULT_VALUE
        )
        self.assertEqual(
            self._test_document.metadata.first().metadata_type, self._test_metadata_type
        )

    def test_lookup_empty_optional(self):
        """
        Checks for GitLab issue #250
        Empty optional lookup metadata trigger validation error
        """
        self._test_metadata_type.lookup = TEST_LOOKUP_TEMPLATE
        self._test_metadata_type.save()

        document_metadata = DocumentMetadata(
            document=self._test_document, metadata_type=self._test_metadata_type
        )

        document_metadata.full_clean()
        document_metadata.save()

    def test_lookup_unicode(self):
        # Should NOT return a ValidationError, otherwise test fails
        self._test_metadata_type.lookup = '测试1,测试2,test1,test2'
        self._test_metadata_type.save()
        self._test_metadata_type.validate_value(document_type=None, value='测试1')

    def test_lookup_non_unicode(self):
        # Should NOT return a ValidationError, otherwise test fails
        self._test_metadata_type.lookup = 'test1,test2'
        self._test_metadata_type.save()
        self._test_metadata_type.validate_value(document_type=None, value='test1')

    def test_lookup_with_correct_value(self):
        self._test_metadata_type.lookup = TEST_LOOKUP_TEMPLATE
        self._test_metadata_type.save()

        document_metadata = DocumentMetadata(
            document=self._test_document, metadata_type=self._test_metadata_type,
            value=TEST_LOOKUP_VALUE_CORRECT
        )

        document_metadata.full_clean()
        document_metadata.save()

        self.assertEqual(
            getattr(
                self._test_document.metadata_value_of,
                self._test_metadata_type.name
            ), TEST_LOOKUP_VALUE_CORRECT
        )

    def test_lookup_with_incorrect_value(self):
        self._test_metadata_type.lookup = TEST_LOOKUP_TEMPLATE
        self._test_metadata_type.save()

        document_metadata = DocumentMetadata(
            document=self._test_document, metadata_type=self._test_metadata_type,
            value=TEST_LOOKUP_VALUE_INCORRECT
        )

        with self.assertRaises(expected_exception=ValidationError):
            # Should return error
            document_metadata.full_clean()
            document_metadata.save()

    def test_preserve_metadata_value_on_document_type_change(self):
        """
        Preserve the document metadata that is present in the
        old and new document types
        """
        document_metadata = DocumentMetadata(
            document=self._test_document, metadata_type=self._test_metadata_type,
            value=TEST_DEFAULT_VALUE
        )

        document_metadata.full_clean()
        document_metadata.save()

        self._test_document_type_2 = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_2_LABEL
        )

        self._test_document_type_2.metadata.create(metadata_type=self._test_metadata_type)

        self._test_document.document_type_change(document_type=self._test_document_type_2)

        self.assertEqual(self._test_document.metadata.count(), 1)
        self.assertEqual(
            self._test_document.metadata.first().value, TEST_DEFAULT_VALUE
        )
        self.assertEqual(
            self._test_document.metadata.first().metadata_type, self._test_metadata_type
        )

    def test_required_metadata(self):
        self._test_document_type.metadata.all().delete()

        self.assertFalse(
            self._test_metadata_type.get_required_for(self._test_document_type)
        )

        self._test_document_type.metadata.create(
            metadata_type=self._test_metadata_type, required=False
        )

        self.assertFalse(
            self._test_metadata_type.get_required_for(self._test_document_type)
        )

        self._test_document_type.metadata.all().delete()

        self._test_document_type.metadata.create(
            metadata_type=self._test_metadata_type, required=True
        )

        self.assertTrue(
            self._test_metadata_type.get_required_for(self._test_document_type)
        )

    def test_method_get_absolute_url(self):
        self._create_test_metadata_type()

        self.assertTrue(self._test_metadata_type.get_absolute_url())
