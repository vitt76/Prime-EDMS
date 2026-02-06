"""
Bulk Document Operations API Views.

Phase B1: API Gap Fill - Task 2.
Provides bulk operations for multiple documents at once.

Created: Phase B1 of TRANSFORMATION_PLAN.md
Author: Backend Adaptation Team
"""
import logging
from typing import Any, Dict

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models import Document
from mayan.apps.documents.permissions import (
    permission_document_edit, permission_document_trash, permission_document_view
)

logger = logging.getLogger(__name__)


# ==================== Swagger Serializers for Documentation ====================

class BulkActionParamsSerializer(serializers.Serializer):
    """Parameters for bulk actions."""
    tag_id = serializers.IntegerField(
        required=False, 
        help_text=_('Tag ID for tag/untag actions')
    )
    cabinet_id = serializers.IntegerField(
        required=False, 
        help_text=_('Cabinet ID for move action')
    )


class BulkOperationRequestSerializer(serializers.Serializer):
    """
    Request serializer for bulk document operations.
    Used for Swagger documentation.
    """
    action = serializers.ChoiceField(
        choices=['delete', 'tag', 'untag', 'move', 'restore'],
        help_text=_('Action to perform on documents')
    )
    ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        help_text=_('List of document IDs to process'),
        min_length=1,
        max_length=100
    )
    params = BulkActionParamsSerializer(
        required=False,
        help_text=_('Additional parameters for the action')
    )


class BulkOperationResultSerializer(serializers.Serializer):
    """Single result item in bulk operation response."""
    id = serializers.IntegerField(help_text=_('Document ID'))
    status = serializers.CharField(help_text=_('Operation status: success or error'))
    error = serializers.CharField(required=False, help_text=_('Error message if failed'))
    error_code = serializers.CharField(required=False, help_text=_('Error code if failed'))


class BulkOperationResponseSerializer(serializers.Serializer):
    """
    Response serializer for bulk document operations.
    Used for Swagger documentation.
    """
    success = serializers.BooleanField(help_text=_('Whether all operations succeeded'))
    processed = serializers.IntegerField(help_text=_('Number of successfully processed documents'))
    failed = serializers.IntegerField(help_text=_('Number of failed operations'))
    results = BulkOperationResultSerializer(many=True, help_text=_('Results for each document'))
    errors = BulkOperationResultSerializer(many=True, help_text=_('Failed operations details'))


class BulkDocumentActionSerializer:
    """
    Simple validator for bulk action payloads.
    
    Expected payload:
    {
        "action": "delete" | "tag" | "untag" | "move" | "restore",
        "ids": [1, 2, 3],
        "params": {
            "tag_id": 5,        // for tag/untag
            "cabinet_id": 10    // for move
        }
    }
    """
    ALLOWED_ACTIONS = {'delete', 'tag', 'untag', 'move', 'restore'}
    MAX_BULK_SIZE = 100
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.errors = {}
        self.validated_data = {}
    
    def is_valid(self) -> bool:
        """Validate the payload."""
        self.errors = {}
        
        # Validate action
        action = self.data.get('action')
        if not action:
            self.errors['action'] = _('Action is required')
        elif action not in self.ALLOWED_ACTIONS:
            self.errors['action'] = _(
                'Invalid action "%(action)s". Allowed: %(allowed)s'
            ) % {'action': action, 'allowed': ', '.join(self.ALLOWED_ACTIONS)}
        
        # Validate ids
        ids = self.data.get('ids')
        if not ids:
            self.errors['ids'] = _('Document IDs are required')
        elif not isinstance(ids, list):
            self.errors['ids'] = _('IDs must be a list')
        elif len(ids) == 0:
            self.errors['ids'] = _('At least one document ID is required')
        elif len(ids) > self.MAX_BULK_SIZE:
            self.errors['ids'] = _(
                'Too many documents. Maximum %(limit)d allowed, got %(count)d'
            ) % {'limit': self.MAX_BULK_SIZE, 'count': len(ids)}
        else:
            # Validate each ID is an integer
            invalid_ids = [i for i in ids if not isinstance(i, int) or i < 1]
            if invalid_ids:
                self.errors['ids'] = _('Invalid document IDs: %(ids)s') % {'ids': invalid_ids}
        
        # Validate params based on action
        params = self.data.get('params', {})
        if action in ('tag', 'untag') and not params.get('tag_id'):
            self.errors['params'] = _('tag_id is required for tag/untag actions')
        elif action == 'move' and not params.get('cabinet_id'):
            self.errors['params'] = _('cabinet_id is required for move action')
        
        if not self.errors:
            self.validated_data = {
                'action': action,
                'ids': ids,
                'params': params
            }
        
        return not bool(self.errors)


class BulkDocumentActionView(APIView):
    """
    Bulk Operations Endpoint for Documents.
    
    Endpoint: POST /api/v4/documents/bulk/
    
    Performs bulk operations on multiple documents at once.
    Supports: delete, tag, untag, move, restore actions.
    
    All operations are atomic - if any fails, the entire batch continues
    but failures are reported in the response.
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    
    @extend_schema(
        summary='Массовые операции над документами',
        description='Выполняет bulk-операции над документами: delete/tag/untag/move/restore.',
        request=BulkOperationRequestSerializer,
        responses={
            200: BulkOperationResponseSerializer,
            207: BulkOperationResponseSerializer,
            400: OpenApiResponse(
                response=inline_serializer(
                    name='BulkOperationValidationError',
                    fields={
                        'success': serializers.BooleanField(),
                        'error': serializers.CharField(),
                        'error_code': serializers.CharField(),
                        'details': serializers.DictField(),
                    }
                ),
                description='Ошибка валидации'
            ),
        },
        tags=['documents'],
    )
    def post(self, request, *args, **kwargs):
        """Handle bulk operation request."""
        # Validate payload
        serializer = BulkDocumentActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'error': 'Validation failed',
                    'error_code': 'VALIDATION_ERROR',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        action = serializer.validated_data['action']
        ids = serializer.validated_data['ids']
        params = serializer.validated_data['params']
        
        # Get action handler
        handler = self._get_action_handler(action)
        if not handler:
            return Response(
                {
                    'success': False,
                    'error': f'Unknown action: {action}',
                    'error_code': 'UNKNOWN_ACTION'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Execute bulk operation
        results = []
        errors = []
        processed = 0
        failed = 0
        
        # Use atomic transaction for consistency
        with transaction.atomic():
            for doc_id in ids:
                result = self._process_document(
                    doc_id=doc_id,
                    action=action,
                    handler=handler,
                    params=params,
                    user=request.user
                )
                
                if result['status'] == 'success':
                    processed += 1
                else:
                    failed += 1
                    errors.append(result)
                
                results.append(result)
        
        # Log the operation
        logger.info(
            'Bulk document operation completed',
            extra={
                'user_id': request.user.id,
                'action': action,
                'total_ids': len(ids),
                'processed': processed,
                'failed': failed
            }
        )
        
        return Response(
            {
                'success': failed == 0,
                'processed': processed,
                'failed': failed,
                'results': results,
                'errors': errors
            },
            status=status.HTTP_200_OK if failed == 0 else status.HTTP_207_MULTI_STATUS
        )
    
    def _get_action_handler(self, action: str):
        """Get handler method for action."""
        handlers = {
            'delete': self._action_delete,
            'tag': self._action_tag,
            'untag': self._action_untag,
            'move': self._action_move,
            'restore': self._action_restore
        }
        return handlers.get(action)
    
    def _process_document(
        self, 
        doc_id: int, 
        action: str, 
        handler, 
        params: Dict[str, Any],
        user
    ) -> Dict[str, Any]:
        """
        Process a single document in the bulk operation.
        
        Checks permissions and executes the action.
        """
        try:
            # Get document
            document = Document.objects.get(pk=doc_id)
            
            # Check base permission
            permission = self._get_required_permission(action)
            AccessControlList.objects.check_access(
                obj=document,
                permissions=(permission,),
                user=user
            )
            
            # Execute action
            handler(document=document, params=params, user=user)
            
            return {
                'id': doc_id,
                'status': 'success'
            }
            
        except Document.DoesNotExist:
            return {
                'id': doc_id,
                'status': 'error',
                'error': 'Document not found',
                'error_code': 'NOT_FOUND'
            }
        except PermissionDenied:
            return {
                'id': doc_id,
                'status': 'error',
                'error': 'Permission denied',
                'error_code': 'PERMISSION_DENIED'
            }
        except Exception as e:
            logger.exception(
                f'Error processing document {doc_id} for action {action}',
                extra={'doc_id': doc_id, 'action': action, 'error': str(e)}
            )
            return {
                'id': doc_id,
                'status': 'error',
                'error': str(e) if settings.DEBUG else 'Operation failed',
                'error_code': 'OPERATION_ERROR'
            }
    
    def _get_required_permission(self, action: str):
        """Get required permission for action."""
        permission_map = {
            'delete': permission_document_trash,
            'tag': permission_document_edit,
            'untag': permission_document_edit,
            'move': permission_document_edit,
            'restore': permission_document_trash
        }
        return permission_map.get(action, permission_document_view)
    
    # ==================== Action Handlers ====================
    
    def _action_delete(self, document: Document, params: Dict, user) -> None:
        """Move document to trash."""
        document._event_actor = user
        document.delete(to_trash=True, _user=user)
    
    def _action_tag(self, document: Document, params: Dict, user) -> None:
        """Attach tag to document."""
        from mayan.apps.tags.models import Tag
        
        tag_id = params.get('tag_id')
        tag = Tag.objects.get(pk=tag_id)
        tag.attach_to(document=document, _user=user)
    
    def _action_untag(self, document: Document, params: Dict, user) -> None:
        """Remove tag from document."""
        from mayan.apps.tags.models import Tag
        
        tag_id = params.get('tag_id')
        tag = Tag.objects.get(pk=tag_id)
        tag.remove_from(document=document, _user=user)
    
    def _action_move(self, document: Document, params: Dict, user) -> None:
        """Add document to cabinet."""
        from mayan.apps.cabinets.models import Cabinet
        
        cabinet_id = params.get('cabinet_id')
        cabinet = Cabinet.objects.get(pk=cabinet_id)
        cabinet.document_add(document=document, _user=user)
    
    def _action_restore(self, document: Document, params: Dict, user) -> None:
        """Restore document from trash."""
        if document.in_trash:
            document.in_trash = False
            document.trashed_date_time = None
            document._event_actor = user
            document.save(update_fields=('in_trash', 'trashed_date_time'))


class BulkTagActionView(APIView):
    """
    Specialized endpoint for bulk tag operations.
    
    Endpoint: POST /api/v4/documents/bulk/tags/
    
    Payload for attach:
    {
        "action": "attach",
        "document_ids": [1, 2, 3],
        "tag_ids": [5, 6]
    }
    
    Payload for remove:
    {
        "action": "remove",
        "document_ids": [1, 2, 3],
        "tag_ids": [5, 6]
    }
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    
    def post(self, request, *args, **kwargs):
        """Handle bulk tag operation."""
        action = request.data.get('action')
        document_ids = request.data.get('document_ids', [])
        tag_ids = request.data.get('tag_ids', [])
        
        # Validate
        if action not in ('attach', 'remove'):
            return Response(
                {
                    'success': False,
                    'error': 'Invalid action. Use "attach" or "remove"',
                    'error_code': 'INVALID_ACTION'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not document_ids or not tag_ids:
            return Response(
                {
                    'success': False,
                    'error': 'document_ids and tag_ids are required',
                    'error_code': 'MISSING_PARAMS'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from mayan.apps.tags.models import Tag
        
        # Get documents and tags
        documents = Document.objects.filter(pk__in=document_ids)
        tags = Tag.objects.filter(pk__in=tag_ids)
        
        processed = 0
        failed = 0
        errors = []
        
        with transaction.atomic():
            for document in documents:
                try:
                    # Check permission
                    AccessControlList.objects.check_access(
                        obj=document,
                        permissions=(permission_document_edit,),
                        user=request.user
                    )
                    
                    for tag in tags:
                        if action == 'attach':
                            tag.attach_to(document=document, _user=request.user)
                        else:
                            tag.remove_from(document=document, _user=request.user)
                    
                    processed += 1
                    
                except PermissionDenied:
                    failed += 1
                    errors.append({
                        'document_id': document.pk,
                        'error': 'Permission denied'
                    })
                except Exception as e:
                    failed += 1
                    errors.append({
                        'document_id': document.pk,
                        'error': str(e) if settings.DEBUG else 'Operation failed'
                    })
        
        return Response(
            {
                'success': failed == 0,
                'processed': processed,
                'failed': failed,
                'errors': errors
            },
            status=status.HTTP_200_OK if failed == 0 else status.HTTP_207_MULTI_STATUS
        )


class BulkCabinetActionView(APIView):
    """
    Specialized endpoint for bulk cabinet operations.
    
    Endpoint: POST /api/v4/documents/bulk/cabinets/
    
    Payload for add:
    {
        "action": "add",
        "document_ids": [1, 2, 3],
        "cabinet_id": 10
    }
    
    Payload for remove:
    {
        "action": "remove",
        "document_ids": [1, 2, 3],
        "cabinet_id": 10
    }
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    
    def post(self, request, *args, **kwargs):
        """Handle bulk cabinet operation."""
        action = request.data.get('action')
        document_ids = request.data.get('document_ids', [])
        cabinet_id = request.data.get('cabinet_id')
        
        # Validate
        if action not in ('add', 'remove'):
            return Response(
                {
                    'success': False,
                    'error': 'Invalid action. Use "add" or "remove"',
                    'error_code': 'INVALID_ACTION'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not document_ids or not cabinet_id:
            return Response(
                {
                    'success': False,
                    'error': 'document_ids and cabinet_id are required',
                    'error_code': 'MISSING_PARAMS'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from mayan.apps.cabinets.models import Cabinet
        
        try:
            cabinet = Cabinet.objects.get(pk=cabinet_id)
        except Cabinet.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'error': f'Cabinet {cabinet_id} not found',
                    'error_code': 'CABINET_NOT_FOUND'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        documents = Document.objects.filter(pk__in=document_ids)
        
        processed = 0
        failed = 0
        errors = []
        
        with transaction.atomic():
            for document in documents:
                try:
                    # Check permission
                    AccessControlList.objects.check_access(
                        obj=document,
                        permissions=(permission_document_edit,),
                        user=request.user
                    )
                    
                    if action == 'add':
                        cabinet.document_add(document=document, _user=request.user)
                    else:
                        cabinet.document_remove(document=document, _user=request.user)
                    
                    processed += 1
                    
                except PermissionDenied:
                    failed += 1
                    errors.append({
                        'document_id': document.pk,
                        'error': 'Permission denied'
                    })
                except Exception as e:
                    failed += 1
                    errors.append({
                        'document_id': document.pk,
                        'error': str(e) if settings.DEBUG else 'Operation failed'
                    })
        
        return Response(
            {
                'success': failed == 0,
                'processed': processed,
                'failed': failed,
                'errors': errors
            },
            status=status.HTTP_200_OK if failed == 0 else status.HTTP_207_MULTI_STATUS
        )

