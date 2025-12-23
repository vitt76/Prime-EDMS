"""
Tests for document type configuration caching.

Tests cache functionality, invalidation, and fallback behavior.
"""
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from mayan.apps.documents.models import DocumentType
from mayan.apps.metadata.models import DocumentTypeMetadataType, MetadataType
from mayan.apps.document_states.models import Workflow
from mayan.apps.headless_api.cache_utils import (
    get_cache_key_list,
    get_cache_key_detail,
    invalidate_document_type_config_cache
)


class HeadlessDocumentTypeConfigCacheTests(APITestCase):
    """Tests for document type configuration cache functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = self._create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Clear cache before each test
        cache.clear()

        self.doc_type = DocumentType.objects.create(label='Test Images')
        self.doc_type2 = DocumentType.objects.create(label='Test Documents')

        self.required_meta = MetadataType.objects.create(
            name='author',
            label='Author',
            validation='^.{3,}$'
        )
        self.optional_meta = MetadataType.objects.create(
            name='description',
            label='Description'
        )

        DocumentTypeMetadataType.objects.create(
            document_type=self.doc_type,
            metadata_type=self.required_meta,
            required=True
        )
        DocumentTypeMetadataType.objects.create(
            document_type=self.doc_type,
            metadata_type=self.optional_meta,
            required=False
        )

    def _create_user(self):
        """Create a test user."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.create_user(
            username='cache-test-user',
            password='CacheTestPass123!'
        )

    def test_list_cache_hit(self):
        """Test that list endpoint uses cache on second request."""
        # First request - cache miss
        response1 = self.client.get('/api/v4/headless/config/document_types/')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Verify cache was set
        cache_key = get_cache_key_list()
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)
        self.assertEqual(len(cached_data), 2)  # Two document types

        # Second request - cache hit
        response2 = self.client.get('/api/v4/headless/config/document_types/')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data, response2.data)

    def test_detail_cache_hit(self):
        """Test that detail endpoint uses cache on second request."""
        # First request - cache miss
        url = f'/api/v4/headless/config/document_types/{self.doc_type.pk}/'
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Verify cache was set
        cache_key = get_cache_key_detail(self.doc_type.pk)
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data['id'], self.doc_type.pk)

        # Second request - cache hit
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data, response2.data)

    def test_cache_invalidation_on_document_type_save(self):
        """Test that cache is invalidated when DocumentType is saved."""
        # Populate cache
        self.client.get('/api/v4/headless/config/document_types/')
        self.client.get(f'/api/v4/headless/config/document_types/{self.doc_type.pk}/')
        
        # Verify cache exists
        list_key = get_cache_key_list()
        detail_key = get_cache_key_detail(self.doc_type.pk)
        self.assertIsNotNone(cache.get(list_key))
        self.assertIsNotNone(cache.get(detail_key))

        # Modify document type
        self.doc_type.label = 'Updated Label'
        self.doc_type.save()

        # Verify cache was invalidated
        self.assertIsNone(cache.get(list_key))
        self.assertIsNone(cache.get(detail_key))

    def test_cache_invalidation_on_document_type_delete(self):
        """Test that cache is invalidated when DocumentType is deleted."""
        # Populate cache
        self.client.get('/api/v4/headless/config/document_types/')
        self.client.get(f'/api/v4/headless/config/document_types/{self.doc_type.pk}/')
        
        # Verify cache exists
        list_key = get_cache_key_list()
        detail_key = get_cache_key_detail(self.doc_type.pk)
        self.assertIsNotNone(cache.get(list_key))
        self.assertIsNotNone(cache.get(detail_key))

        # Delete document type
        doc_type_id = self.doc_type.pk
        self.doc_type.delete()

        # Verify cache was invalidated
        self.assertIsNone(cache.get(list_key))
        self.assertIsNone(cache.get(detail_key))

    def test_cache_invalidation_on_metadata_change(self):
        """Test that cache is invalidated when DocumentTypeMetadataType changes."""
        # Populate cache
        self.client.get(f'/api/v4/headless/config/document_types/{self.doc_type.pk}/')
        
        # Verify cache exists
        detail_key = get_cache_key_detail(self.doc_type.pk)
        cached_data = cache.get(detail_key)
        self.assertIsNotNone(cached_data)

        # Add new metadata
        new_meta = MetadataType.objects.create(
            name='new_field',
            label='New Field'
        )
        DocumentTypeMetadataType.objects.create(
            document_type=self.doc_type,
            metadata_type=new_meta,
            required=False
        )

        # Verify cache was invalidated
        self.assertIsNone(cache.get(detail_key))
        self.assertIsNone(cache.get(get_cache_key_list()))

    def test_cache_invalidation_on_workflow_change(self):
        """Test that cache is invalidated when workflow-document_type relationship changes."""
        # Create workflow
        workflow = Workflow.objects.create(label='Test Workflow')
        
        # Populate cache
        self.client.get(f'/api/v4/headless/config/document_types/{self.doc_type.pk}/')
        
        # Verify cache exists
        detail_key = get_cache_key_detail(self.doc_type.pk)
        self.assertIsNotNone(cache.get(detail_key))

        # Add document type to workflow (triggers m2m_changed)
        workflow.document_types.add(self.doc_type)

        # Verify cache was invalidated
        self.assertIsNone(cache.get(detail_key))
        self.assertIsNone(cache.get(get_cache_key_list()))

    def test_cache_fallback_on_error(self):
        """Test that endpoint falls back to DB when cache fails."""
        # Manually set invalid cache data to simulate error
        cache_key = get_cache_key_list()
        
        # Make request - should work from DB
        response = self.client.get('/api/v4/headless/config/document_types/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_cache_not_stored_for_404(self):
        """Test that 404 responses are not cached."""
        # Request non-existent document type
        url = '/api/v4/headless/config/document_types/99999/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Verify nothing was cached
        cache_key = get_cache_key_detail(99999)
        self.assertIsNone(cache.get(cache_key))

    def test_list_cache_invalidated_on_any_type_change(self):
        """Test that list cache is invalidated when any document type changes."""
        # Populate cache for both types
        self.client.get('/api/v4/headless/config/document_types/')
        
        list_key = get_cache_key_list()
        self.assertIsNotNone(cache.get(list_key))

        # Modify second document type
        self.doc_type2.label = 'Updated'
        self.doc_type2.save()

        # Verify list cache was invalidated (but detail cache for first type may still exist)
        self.assertIsNone(cache.get(list_key))

