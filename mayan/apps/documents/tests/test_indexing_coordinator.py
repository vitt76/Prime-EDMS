"""
Tests for Document Indexing Coordinator.

Tests the unified coordination of document indexing between
Dynamic Search and Document Indexing systems.
"""
from unittest.mock import patch, MagicMock

from mayan.apps.testing.tests.base import BaseTestCase

from ..indexing_coordinator import DocumentIndexCoordinator
from ..validation import validate_document_for_indexing
from .base import GenericDocumentTestCase


class DocumentIndexCoordinatorTestCase(GenericDocumentTestCase):
    """Test cases for DocumentIndexCoordinator."""

    def test_index_document_coordination_with_chain(self):
        """Test that coordinator schedules chain for both search and hierarchy indexing."""
        self._upload_test_document()
        
        # Mock chain creation and execution
        mock_chain_result = MagicMock()
        mock_chain_result.id = 'test-chain-id'
        
        with patch('celery.chain') as mock_chain_class:
            mock_chain = MagicMock()
            mock_chain.link.return_value = mock_chain
            mock_chain.link_error.return_value = mock_chain
            mock_chain.apply_async.return_value = mock_chain_result
            mock_chain_class.return_value = mock_chain
            
            result = DocumentIndexCoordinator.index_document(
                document_id=self._test_document.pk,
                created=True
            )
            
            # Verify chain was created and scheduled
            self.assertTrue(result['search_indexed'])
            self.assertTrue(result['hierarchy_indexed'])
            self.assertEqual(result.get('chain_task_id'), 'test-chain-id')
            self.assertEqual(len(result.get('errors', [])), 0)
            
            # Verify chain was called with correct tasks
            mock_chain_class.assert_called_once()
            # Verify link and link_error were called for callback
            mock_chain.link.assert_called_once()
            mock_chain.link_error.assert_called_once()
            mock_chain.apply_async.assert_called_once_with(queue='indexing')

    def test_index_document_invalid_document(self):
        """Test that coordinator handles invalid documents gracefully."""
        # With new implementation, invalid documents are handled in validation task
        # Coordinator will schedule chain, but validation will skip indexing
        mock_chain_result = MagicMock()
        mock_chain_result.id = 'test-chain-id'
        
        with patch('celery.chain') as mock_chain_class:
            mock_chain = MagicMock()
            mock_chain.link.return_value = mock_chain
            mock_chain.link_error.return_value = mock_chain
            mock_chain.apply_async.return_value = mock_chain_result
            mock_chain_class.return_value = mock_chain
            
            result = DocumentIndexCoordinator.index_document(
                document_id=99999,  # Non-existent document
                created=False
            )
            
            # Chain should be scheduled (validation will handle invalid document)
            self.assertTrue(result.get('chain_task_id'))

    def test_deindex_document_coordination(self):
        """Test that coordinator schedules both search and hierarchy deindexing."""
        self._upload_test_document()
        
        with patch('mayan.apps.dynamic_search.tasks.task_deindex_instance.apply_async') as mock_search:
            with patch('mayan.apps.document_indexing.tasks.task_index_instance_document_remove.apply_async') as mock_hierarchy:
                result = DocumentIndexCoordinator.deindex_document(
                    document_id=self._test_document.pk
                )
                
                # Verify both tasks were scheduled
                self.assertTrue(result['search_deindexed'])
                self.assertTrue(result['hierarchy_deindexed'])
                self.assertEqual(len(result.get('errors', [])), 0)
                
                # Verify search deindexing was called
                mock_search.assert_called_once()
                call_kwargs = mock_search.call_args[1]
                self.assertEqual(call_kwargs['kwargs']['app_label'], 'documents')
                self.assertEqual(call_kwargs['kwargs']['model_name'], 'Document')
                self.assertEqual(call_kwargs['kwargs']['object_id'], self._test_document.pk)
                self.assertEqual(call_kwargs['queue'], 'indexing')
                
                # Verify hierarchy deindexing was called
                mock_hierarchy.assert_called_once()
                call_kwargs = mock_hierarchy.call_args[1]
                self.assertEqual(call_kwargs['kwargs']['document_id'], self._test_document.pk)
                self.assertEqual(call_kwargs['queue'], 'indexing')

    def test_index_document_batch(self):
        """Test batch indexing of multiple documents."""
        self._upload_test_document()
        document_2 = self._create_test_document()
        
        mock_chain_result = MagicMock()
        mock_chain_result.id = 'test-chain-id'
        
        with patch('celery.chain') as mock_chain_class:
            mock_chain = MagicMock()
            mock_chain.link.return_value = mock_chain
            mock_chain.link_error.return_value = mock_chain
            mock_chain.apply_async.return_value = mock_chain_result
            mock_chain_class.return_value = mock_chain
            
            result = DocumentIndexCoordinator.index_document_batch(
                document_ids=[self._test_document.pk, document_2.pk]
            )
            
            self.assertEqual(result['total'], 2)
            self.assertEqual(result['success_count'], 2)
            self.assertEqual(len(result.get('errors', [])), 0)

    def test_index_document_batch_empty_list(self):
        """Test batch indexing with empty list."""
        result = DocumentIndexCoordinator.index_document_batch(document_ids=[])
        
        self.assertEqual(result['total'], 0)
        self.assertEqual(result['success_count'], 0)
        self.assertEqual(len(result.get('errors', [])), 0)
    
    def test_index_document_batch_chunk_processing(self):
        """Test that batch processing uses iterative approach for large batches."""
        self._upload_test_document()
        # Create a batch larger than chunk size
        document_ids = [self._test_document.pk] * 2500  # Larger than default chunk_size=1000
        
        mock_chain_result = MagicMock()
        mock_chain_result.id = 'test-chain-id'
        
        with patch('celery.chain') as mock_chain_class:
            mock_chain = MagicMock()
            mock_chain.link.return_value = mock_chain
            mock_chain.link_error.return_value = mock_chain
            mock_chain.apply_async.return_value = mock_chain_result
            mock_chain_class.return_value = mock_chain
            
            result = DocumentIndexCoordinator.index_document_batch(
                document_ids=document_ids,
                chunk_size=1000
            )
            
            # Should process in chunks without recursion
            self.assertEqual(result['total'], 2500)
            self.assertEqual(result['success_count'], 2500)
    
    def test_index_document_permission_check(self):
        """Test that coordinator checks permissions when user is provided."""
        self._upload_test_document()
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        test_user = User.objects.create_user(
            username='test_user_no_access',
            password='testpass'
        )
        
        # User should not have access to document
        result = DocumentIndexCoordinator.index_document(
            document_id=self._test_document.pk,
            created=False,
            user=test_user
        )
        
        # Should return permission denied error
        self.assertFalse(result['search_indexed'])
        self.assertFalse(result['hierarchy_indexed'])
        self.assertEqual(result.get('error_type'), 'permission_denied')
    
    def test_validate_document_for_indexing(self):
        """Test unified validation function."""
        self._upload_test_document()
        
        # Valid document
        document = validate_document_for_indexing(self._test_document.pk)
        self.assertIsNotNone(document)
        self.assertEqual(document.pk, self._test_document.pk)
        
        # Invalid document (non-existent)
        document = validate_document_for_indexing(99999)
        self.assertIsNone(document)
    
    def test_validate_document_for_indexing_trashed(self):
        """Test that validation skips trashed documents."""
        self._upload_test_document()
        self._test_document.delete()
        
        document = validate_document_for_indexing(self._test_document.pk)
        self.assertIsNone(document)

    def test_index_document_chain_error_handling(self):
        """Test that coordinator handles chain errors gracefully and uses fallback."""
        self._upload_test_document()
        
        # Simulate chain scheduling failure
        with patch('celery.chain') as mock_chain_class:
            mock_chain = MagicMock()
            mock_chain.link.return_value = mock_chain
            mock_chain.link_error.return_value = mock_chain
            mock_chain.apply_async.side_effect = Exception('Chain error')
            mock_chain_class.return_value = mock_chain
            
            # Mock fallback tasks
            with patch('mayan.apps.documents.tasks.task_index_instance_safe.apply_async') as mock_fallback_search:
                with patch('mayan.apps.documents.tasks.task_index_instance_document_add_safe.apply_async') as mock_fallback_hierarchy:
                    result = DocumentIndexCoordinator.index_document(
                        document_id=self._test_document.pk,
                        created=False
                    )
                    
                    # Should have errors from chain failure
                    self.assertGreater(len(result.get('errors', [])), 0)
                    # Fallback should be called
                    mock_fallback_search.assert_called_once()
                    mock_fallback_hierarchy.assert_called_once()
    
    def test_index_document_callback_link_error(self):
        """Test that callback is linked for both success and error cases."""
        self._upload_test_document()
        
        mock_chain_result = MagicMock()
        mock_chain_result.id = 'test-chain-id'
        
        with patch('celery.chain') as mock_chain_class:
            mock_chain = MagicMock()
            mock_chain.link.return_value = mock_chain
            mock_chain.link_error.return_value = mock_chain
            mock_chain.apply_async.return_value = mock_chain_result
            mock_chain_class.return_value = mock_chain
            
            DocumentIndexCoordinator.index_document(
                document_id=self._test_document.pk,
                created=True
            )
            
            # Verify both link and link_error were called for callback
            self.assertEqual(mock_chain.link.call_count, 1)
            self.assertEqual(mock_chain.link_error.call_count, 1)

    def test_deindex_document_error_handling(self):
        """Test that coordinator handles deindexing errors gracefully."""
        self._upload_test_document()
        
        # Simulate error in search deindexing
        with patch('mayan.apps.dynamic_search.tasks.task_deindex_instance.apply_async', side_effect=Exception('Deindex error')):
            with patch('mayan.apps.document_indexing.tasks.task_index_instance_document_remove.apply_async'):
                result = DocumentIndexCoordinator.deindex_document(
                    document_id=self._test_document.pk
                )
                
                # Search deindexing should have failed
                self.assertFalse(result['search_deindexed'])
                # Hierarchy deindexing should still succeed
                self.assertTrue(result['hierarchy_deindexed'])
                # Should have errors
                self.assertGreater(len(result.get('errors', [])), 0)

