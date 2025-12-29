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
    1. Checks if files are already in user's publications (uses existing if found)
    2. Creates a publication only if files are not in any publication
    3. Adds document files to publication (if new publication)
    4. Generates renditions (if needed)
    5. Creates a share link
    
    Request body:
    {
        "document_file_ids": [1, 2, 3],  # Required: document file IDs (active versions)
        "title": "My Share Link",  # Optional, defaults to "Share Link"
        "expires_at": "2025-12-31T23:59:59Z",  # Optional
        "max_downloads": 100,  # Optional
        "preset_id": 1  # Optional, uses first available preset if not provided
    }
    """
    document_file_ids = request.data.get('document_file_ids', [])
    publication_id = request.data.get('publication_id')  # Use existing publication if provided
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
        
        # If publication_id is provided, use it (files are already in this publication)
        publication = None
        if publication_id:
            try:
                publication = Publication.objects.get(pk=publication_id, owner=request.user)
                logger.info(f'Using provided publication {publication.id} for share link creation')
            except Publication.DoesNotExist:
                return Response(
                    {'detail': f'Publication {publication_id} not found or access denied'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Check if files are already in user's publications
            # Find existing PublicationItems for these files in user's publications
            existing_items = PublicationItem.objects.filter(
                document_file__in=document_files,
                publication__owner=request.user
            ).select_related('publication', 'document_file')
            
            # Group items by publication
            items_by_publication = {}
            for item in existing_items:
                pub_id = item.publication.id
                if pub_id not in items_by_publication:
                    items_by_publication[pub_id] = []
                items_by_publication[pub_id].append(item)
            
            # Find files that are already in publications
            existing_file_ids = set(item.document_file.id for item in existing_items)
            new_file_ids = [fid for fid in document_file_ids if fid not in existing_file_ids]
            
            # Use existing publication if all files are in the same publication
            # Otherwise, create new publication for new files
            if existing_items.exists() and len(items_by_publication) == 1:
                # All files are in the same publication - use it
                publication = existing_items.first().publication
                logger.info(f'Using existing publication {publication.id} for share link creation')
            else:
                # Create new publication for new files or if files are in different publications
                if new_file_ids:
                    publication = Publication.objects.create(
                        owner=request.user,
                        title=title,
                        access_policy='public'
                    )
                    logger.info(f'Created new publication {publication.id} for share link creation')
                elif existing_items.exists():
                    # Files are in different publications - use the first one
                    publication = existing_items.first().publication
                    logger.info(f'Using first existing publication {publication.id} (files in multiple publications)')
        
        if not publication:
            return Response(
                {'detail': 'Could not determine or create publication'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create PublicationItems for all files in the publication
        publication_items = []
        
        for doc_file in document_files:
            # Get or create PublicationItem for this file in the publication
            item, created = PublicationItem.objects.get_or_create(
                publication=publication,
                document_file=doc_file
            )
            publication_items.append(item)
        
        # If no items found, something went wrong
        if not publication_items:
            return Response(
                {'detail': 'No publication items found or created'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate renditions and create share links for all items
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

            # Analytics (Level 1): track share link creation as a "share" event.
            try:
                from mayan.apps.analytics.models import AssetEvent
                from mayan.apps.analytics.utils import track_asset_event

                document = item.document_file.document
                user = request.user if request.user.is_authenticated else None
                track_asset_event(
                    document=document,
                    event_type=AssetEvent.EVENT_TYPE_SHARE,
                    user=user,
                    channel='public_link',
                    metadata={
                        'share_link_id': share_link.pk,
                        'rendition_id': rendition.pk,
                        'publication_id': publication.pk,
                        'document_file_id': item.document_file_id,
                        'preset': getattr(preset, 'name', ''),
                    }
                )
            except Exception:
                # Best-effort only; never fail share link creation due to analytics.
                pass
        
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
