from mayan.apps.common.tests.mixins import ObjectCopyTestMixin
from mayan.apps.documents.tests.mixins.document_mixins import DocumentTestMixin
from mayan.apps.testing.tests.base import BaseTestCase

from .mixins import SmartLinkTestMixin


class SmartLinkCopyTestCase(
    SmartLinkTestMixin, DocumentTestMixin, ObjectCopyTestMixin, BaseTestCase
):
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()
        self._create_test_smart_link()
        self._create_test_smart_link_condition()
        self._test_smart_link.document_types.add(self._test_document_type)
        self._test_object = self._test_smart_link
