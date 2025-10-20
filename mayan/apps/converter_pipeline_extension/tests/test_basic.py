"""
Basic tests for Converter Pipeline Extension
"""

from django.test import TestCase
from django.apps import apps

from ..models import ExtendedDocumentProxy, DocumentConversionMetadata
from ..utils import is_media_format_supported, get_supported_formats_for_document


class ConverterPipelineExtensionTestCase(TestCase):
    """Basic functionality tests"""

    def test_app_registration(self):
        """Test that the app is properly registered"""
        app_config = apps.get_app_config('converter_pipeline_extension')
        self.assertEqual(app_config.name, 'mayan.apps.converter_pipeline_extension')
        self.assertEqual(app_config.verbose_name, 'Converter Pipeline Extension')

    def test_proxy_model(self):
        """Test that proxy model works correctly"""
        # Create a mock document for testing
        Document = apps.get_model('documents', 'Document')

        # Test proxy model creation (would need actual document in real test)
        proxy_class = ExtendedDocumentProxy
        self.assertTrue(hasattr(proxy_class, 'media_conversion_status'))
        self.assertTrue(hasattr(proxy_class, 'supported_preview_formats'))

    def test_format_detection(self):
        """Test media format detection"""
        # Test supported formats
        self.assertTrue(is_media_format_supported('image/x-canon-cr2'))
        self.assertTrue(is_media_format_supported('video/mp4'))
        self.assertTrue(is_media_format_supported('application/x-rar'))

        # Test unsupported formats
        self.assertFalse(is_media_format_supported('application/pdf'))
        self.assertFalse(is_media_format_supported('text/plain'))
        self.assertFalse(is_media_format_supported('unknown/format'))

    def test_conversion_metadata_model(self):
        """Test DocumentConversionMetadata model"""
        # Test model fields
        metadata = DocumentConversionMetadata()
        self.assertEqual(metadata.conversion_status, 'not_started')
        self.assertFalse(metadata.preview_generated)

        # Test status methods
        metadata.mark_as_processing('test_converter')
        self.assertEqual(metadata.conversion_status, 'processing')
        self.assertEqual(metadata.converter_used, 'test_converter')

        metadata.mark_as_completed()
        self.assertEqual(metadata.conversion_status, 'completed')
        self.assertTrue(metadata.preview_generated)

    def test_utils_functions(self):
        """Test utility functions"""
        # Test format registry
        from ..utils import MEDIA_FORMAT_REGISTRY
        self.assertIsInstance(MEDIA_FORMAT_REGISTRY, dict)
        self.assertGreater(len(MEDIA_FORMAT_REGISTRY), 0)

        # Test category filtering
        from ..utils import get_formats_by_category
        raw_formats = get_formats_by_category('raw_image')
        self.assertIsInstance(raw_formats, dict)
        self.assertGreater(len(raw_formats), 0)

        video_formats = get_formats_by_category('video')
        self.assertIsInstance(video_formats, dict)
        self.assertGreater(len(video_formats), 0)

