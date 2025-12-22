"""
Views for creating share links with simplified workflow.
"""
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from mayan.apps.documents.models import DocumentFile
from mayan.apps.rest_api import generics

from ..models import Publication, PublicationItem, GeneratedRendition, ShareLink, RenditionPreset
from ..serializers.publication_serializers import ShareLinkSerializer

logger = logging.getLogger(name=__name__)


class ShareLinkCreateView(LoginRequiredMixin, TemplateView):
    """Template view for creating share links (UI)."""
    template_name = 'distribution/share_link_create.html'


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_share_link_simple(request):
    """
    Simplified endpoint to create a share link directly from document files.
    
    This endpoint automatically:
    1. Creates a publication (if needed)
    2. Adds document files to publication
    3. Generates renditions (if needed)
    4. Creates a share link
    
    Request body:
    {
        "document_file_ids": [1, 2, 3],
        "title": "My Share Link",  # Optional, defaults to "Share Link"
        "expires_at": "2025-12-31T23:59:59Z",  # Optional
        "max_downloads": 100,  # Optional
        "preset_id": 1  # Optional, uses first available preset if not provided
    }
    """
    document_file_ids = request.data.get('document_file_ids', [])
    title = request.data.get('title', 'Share Link')
    expires_at = request.data.get('expires_at')
    max_downloads = request.data.get('max_downloads')
    preset_id = request.data.get('preset_id')
    
    if not document_file_ids:
        return Response(
            {'detail': 'document_file_ids is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get document files
        document_files = DocumentFile.objects.filter(
            pk__in=document_file_ids
        )
        
        if document_files.count() != len(document_file_ids):
            return Response(
                {'detail': 'Some document files not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get or create a preset
        if preset_id:
            try:
                preset = RenditionPreset.objects.get(pk=preset_id)
            except RenditionPreset.DoesNotExist:
                return Response(
                    {'detail': f'Preset {preset_id} not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Use first available preset
            preset = RenditionPreset.objects.first()
            if not preset:
                return Response(
                    {'detail': 'No rendition presets available. Please create a preset first.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create publication
        publication = Publication.objects.create(
            owner=request.user,
            title=title,
            access_policy='public'
        )
        
        # Add document files to publication
        publication_items = []
        for doc_file in document_files:
            item, created = PublicationItem.objects.get_or_create(
                publication=publication,
                document_file=doc_file
            )
            publication_items.append(item)
        
        # Generate renditions for all items
        share_links = []
        for item in publication_items:
            # Get or create rendition
            rendition, created = GeneratedRendition.objects.get_or_create(
                publication_item=item,
                preset=preset,
                defaults={'status': 'pending'}
            )
            
            # Generate rendition if needed
            if created or rendition.status == 'pending':
                try:
                    preset.generate_rendition(item)
                    rendition.refresh_from_db()
                except Exception as e:
                    logger.error(f'Failed to generate rendition: {e}')
                    # Continue with other items
            
            # Create share link for this rendition
            share_link = ShareLink.objects.create(
                rendition=rendition,
                expires_at=expires_at,
                max_downloads=max_downloads
            )
            share_links.append(share_link)
        
        # Serialize the first share link (or return all if multiple)
        if len(share_links) == 1:
            serializer = ShareLinkSerializer(share_links[0], context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Return all share links
            serializer = ShareLinkSerializer(share_links, many=True, context={'request': request})
            return Response({
                'share_links': serializer.data,
                'publication_id': publication.id
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        logger.exception('Error creating share link')
        return Response(
            {'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
