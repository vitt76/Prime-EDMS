"""
Configuration views for Headless API.

Provides REST endpoints for exposing Mayan EDMS configuration data
that frontend needs to build dynamic forms and interfaces.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from mayan.apps.documents.models import DocumentType
from mayan.apps.metadata.models import DocumentTypeMetadataType

import logging

logger = logging.getLogger(__name__)


class HeadlessDocumentTypeConfigView(APIView):
    """
    REST API endpoint for exposing document type configurations.

    Mayan EDMS provides basic document type info but doesn't expose
    the full configuration needed for dynamic form building (metadata,
    workflows, validation rules, etc.).

    Endpoints:
    - GET /api/v4/headless/config/document_types/ - List all types with basic info
    - GET /api/v4/headless/config/document_types/{id}/ - Detailed config for specific type

    Response Schema:
    {
        "id": int,
        "label": string,
        "description": string,
        "required_metadata": [...],
        "optional_metadata": [...],
        "workflows": [...],
        "retention_policy": {...},
        "capabilities": {...}
    }
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, document_type_id=None):
        """
        Handle GET requests for document type configurations.
        """
        if document_type_id:
            return self._get_single_config(document_type_id)
        else:
            return self._get_all_configs()

    def _get_single_config(self, document_type_id):
        """
        Get detailed configuration for a specific document type.
        """
        try:
            doc_type = DocumentType.objects.get(pk=document_type_id)
            config = self._build_full_config(doc_type)

            return Response(config)

        except ObjectDoesNotExist:
            return Response(
                {
                    'error': _('Document type not found'),
                    'error_code': 'NOT_FOUND'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting document type config {document_type_id}: {str(e)}")
            return Response(
                {
                    'error': _('Error retrieving document type configuration'),
                    'error_code': 'INTERNAL_ERROR'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_all_configs(self):
        """
        Get basic configuration for all document types.
        """
        try:
            doc_types = DocumentType.objects.all()
            configs = []

            for doc_type in doc_types:
                configs.append(self._build_basic_config(doc_type))

            return Response(configs)

        except Exception as e:
            logger.error(f"Error getting document types list: {str(e)}")
            return Response(
                {
                    'error': _('Error retrieving document types'),
                    'error_code': 'INTERNAL_ERROR'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _build_basic_config(self, doc_type):
        """
        Build basic configuration for document type list.
        """
        return {
            'id': doc_type.pk,
            'label': doc_type.label,
            'description': getattr(doc_type, 'description', ''),
            'url': f'/api/v4/headless/config/document_types/{doc_type.pk}/'
        }

    def _build_full_config(self, doc_type):
        """
        Build complete configuration for a document type.
        """
        # Get metadata relations
        metadata_relations = DocumentTypeMetadataType.objects.filter(
            document_type=doc_type
        ).select_related('metadata_type')

        required_metadata = []
        optional_metadata = []

        for relation in metadata_relations:
            meta_config = self._build_metadata_config(relation)
            if relation.required:
                required_metadata.append(meta_config)
            else:
                optional_metadata.append(meta_config)

        # Build workflows (simplified for now)
        workflows = []
        # TODO: Add workflow configuration when available

        # Build retention policy
        retention_policy = {
            'enabled': hasattr(doc_type, 'delete_time_period') and doc_type.delete_time_period is not None,
            'days': getattr(doc_type, 'delete_time_period', 0) or 0
        }

        # Build capabilities
        capabilities = {
            'ocr_enabled': getattr(doc_type, 'ocr', True),
            'ai_analysis_enabled': True,  # DAM-specific capability
            'preview_enabled': True
        }

        return {
            'id': doc_type.pk,
            'label': doc_type.label,
            'description': getattr(doc_type, 'description', ''),
            'required_metadata': required_metadata,
            'optional_metadata': optional_metadata,
            'workflows': workflows,
            'retention_policy': retention_policy,
            'capabilities': capabilities
        }

    def _build_metadata_config(self, relation):
        """
        Build configuration for a metadata field.
        """
        meta = relation.metadata_type

        # Determine field type based on Mayan metadata properties
        field_type = self._determine_field_type(meta)

        config = {
            'id': meta.pk,
            'name': meta.name,
            'label': meta.label,
            'type': field_type,
            'required': relation.required,
            'default_value': getattr(meta, 'default', None)
        }

        # Add validation if available
        if hasattr(meta, 'validation') and meta.validation:
            config['validation_regex'] = meta.validation

        # Add options for select fields
        if field_type == 'select' and hasattr(meta, 'lookup'):
            # TODO: Add lookup options when available
            config['options'] = []

        return config

    def _determine_field_type(self, meta):
        """
        Determine the frontend field type based on Mayan metadata properties.
        """
        # Check if it's a lookup (choice field)
        if hasattr(meta, 'lookup') and meta.lookup:
            return 'select'

        # Check validation pattern for hints
        validation = getattr(meta, 'validation', '')
        if 'email' in validation.lower():
            return 'email'
        elif 'url' in validation.lower():
            return 'url'
        elif 'date' in validation.lower():
            return 'date'

        # Default to text
        return 'text'
