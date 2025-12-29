from django.conf import settings
from mayan.apps.rest_api import generics

from ..models import (
    Publication, PublicationItem, ShareLink, GeneratedRendition, AccessLog
)
from ..permissions import (
    permission_publication_api_create, permission_publication_api_view,
    permission_publication_api_edit, permission_publication_api_delete
)
from ..serializers import (
    PublicationSerializer, PublicationItemSerializer, ShareLinkSerializer,
    GeneratedRenditionSerializer, AccessLogSerializer
)
from ..throttles import DistributionThrottle


class APIPublicationListView(generics.ListCreateAPIView):
    """
    get: Return a list of publications.
    post: Create a new publication.
    """
    mayan_object_permissions = {'GET': (permission_publication_api_view,)}
    mayan_view_permissions = {'POST': (permission_publication_api_create,)}
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = getattr(self.request, 'user', None)

        if not user or not user.is_authenticated:
            return queryset.none()

        # Filter to show only publications owned by current user
        return queryset.filter(owner=user)

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
        }


class APIPublicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    get: Return the details of a publication.
    put: Edit the properties of a publication.
    patch: Edit the properties of a publication.
    delete: Delete a publication.
    """
    mayan_object_permissions = {
        'GET': (permission_publication_api_view,),
        'PUT': (permission_publication_api_edit,),
        'PATCH': (permission_publication_api_edit,),
        'DELETE': (permission_publication_api_delete,)
    }
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = getattr(self.request, 'user', None)

        if not user or not user.is_authenticated:
            return queryset.none()

        # Filter to show only publications owned by current user
        return queryset.filter(owner=user)

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
        }


class APIPublicationItemListView(generics.ListCreateAPIView):
    """
    get: Return a list of publication items.
    post: Create a new publication item.
    """
    mayan_object_permissions = {'GET': (permission_publication_api_view,)}
    mayan_view_permissions = {'POST': (permission_publication_api_edit,)}
    queryset = PublicationItem.objects.all()
    serializer_class = PublicationItemSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = getattr(self.request, 'user', None)

        if not user or not user.is_authenticated:
            return queryset.none()

        # Filter to show only items that belong to publications owned by current user
        return queryset.filter(publication__owner=user)


class APIPublicationItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    get: Return the details of a publication item.
    put: Edit the properties of a publication item.
    patch: Edit the properties of a publication item.
    delete: Delete a publication item.
    """
    mayan_object_permissions = {
        'GET': (permission_publication_api_view,),
        'PUT': (permission_publication_api_edit,),
        'PATCH': (permission_publication_api_edit,),
        'DELETE': (permission_publication_api_edit,)
    }
    queryset = PublicationItem.objects.all()
    serializer_class = PublicationItemSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = getattr(self.request, 'user', None)

        if not user or not user.is_authenticated:
            return queryset.none()

        # Filter to show only items that belong to publications owned by current user
        return queryset.filter(publication__owner=user)


class APIShareLinkListView(generics.ListCreateAPIView):
    """
    get: Return a list of share links.
    post: Create a new share link.
    """
    # Temporarily disabled throttle to debug 500 error
    # throttle_classes = [DistributionThrottle]
    mayan_object_permissions = {'GET': (permission_publication_api_view,)}
    mayan_view_permissions = {'POST': (permission_publication_api_create,)}
    queryset = ShareLink.objects.all()
    serializer_class = ShareLinkSerializer

    def get_queryset(self):
        import logging
        logger = logging.getLogger(__name__)
        
        queryset = super().get_queryset()
        user = getattr(self.request, 'user', None)

        if not user or not user.is_authenticated:
            return queryset.none()

        try:
            # Filter to show only share links for publications owned by current user
            # Use select_related and prefetch_related to optimize queries
            # Filter out any share links with missing relationships
            queryset = queryset.filter(
                rendition__isnull=False,
                rendition__publication_item__isnull=False,
                rendition__publication_item__publication__isnull=False,
                rendition__publication_item__publication__owner=user
            ).select_related(
                'rendition',
                'rendition__preset',
                'rendition__publication_item',
                'rendition__publication_item__publication',
                'rendition__publication_item__publication__owner',
                'rendition__publication_item__document_file'
            ).order_by('-created')
            
            return queryset
        except Exception as e:
            logger.exception('Error in APIShareLinkListView.get_queryset: %s', e)
            # Return empty queryset on error to prevent 500
            return queryset.none()
    
    def list(self, request, *args, **kwargs):
        import logging
        from rest_framework.response import Response
        from rest_framework import status
        
        logger = logging.getLogger(__name__)
        
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.exception('Error in APIShareLinkListView.list: %s', e)
            return Response(
                {
                    'error': 'Failed to retrieve share links',
                    'error_code': 'SERIALIZATION_ERROR',
                    'detail': str(e) if settings.DEBUG else 'An error occurred while retrieving share links'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class APIShareLinkDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    get: Return the details of a share link.
    put: Edit the properties of a share link.
    patch: Edit the properties of a share link.
    delete: Delete a share link.
    """
    # Temporarily disabled throttle to debug 500 error
    # throttle_classes = [DistributionThrottle]
    mayan_object_permissions = {
        'GET': (permission_publication_api_view,),
        'PUT': (permission_publication_api_edit,),
        'PATCH': (permission_publication_api_edit,),
        'DELETE': (permission_publication_api_delete,)
    }
    queryset = ShareLink.objects.all()
    serializer_class = ShareLinkSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = getattr(self.request, 'user', None)

        if not user or not user.is_authenticated:
            return queryset.none()

        # Filter to show only share links for publications owned by current user
        # Filter out any share links with missing relationships
        return queryset.filter(
            rendition__isnull=False,
            rendition__publication_item__isnull=False,
            rendition__publication_item__publication__isnull=False,
            rendition__publication_item__publication__owner=user
        ).select_related(
            'rendition',
            'rendition__preset',
            'rendition__publication_item',
            'rendition__publication_item__publication',
            'rendition__publication_item__publication__owner',
            'rendition__publication_item__document_file'
        )


class APIGeneratedRenditionListView(generics.ListAPIView):
    """
    get: Return a list of generated renditions.
    """
    mayan_object_permissions = {'GET': (permission_publication_api_view,)}
    queryset = GeneratedRendition.objects.all()
    serializer_class = GeneratedRenditionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = getattr(self.request, 'user', None)

        if not user or not user.is_authenticated:
            return queryset.none()

        # Filter to show only renditions for publications owned by current user
        return queryset.filter(publication_item__publication__owner=user)


class APIGeneratedRenditionDetailView(generics.RetrieveAPIView):
    """
    get: Return the details of a generated rendition.
    """
    mayan_object_permissions = {'GET': (permission_publication_api_view,)}
    queryset = GeneratedRendition.objects.all()
    serializer_class = GeneratedRenditionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = getattr(self.request, 'user', None)

        if not user or not user.is_authenticated:
            return queryset.none()

        # Filter to show only renditions for publications owned by current user
        return queryset.filter(publication_item__publication__owner=user)


class APIAccessLogListView(generics.ListAPIView):
    """
    get: Return a list of access logs.
    """
    mayan_object_permissions = {'GET': (permission_publication_api_view,)}
    queryset = AccessLog.objects.all()
    serializer_class = AccessLogSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = getattr(self.request, 'user', None)

        if not user or not user.is_authenticated:
            return queryset.none()

        # Filter to show only logs for share links of publications owned by current user
        return queryset.filter(share_link__rendition__publication_item__publication__owner=user)


class APIGenerateRenditionsView(generics.RetrieveAPIView):
    """
    get: Return publication details.
    post: Generate all renditions for a publication.
    """
    mayan_object_permissions = {
        'GET': (permission_publication_api_view,),
        'POST': (permission_publication_api_edit,)
    }
    serializer_class = PublicationSerializer
    queryset = Publication.objects.all()

    def get_queryset(self):
        user = getattr(self.request, 'user', None)

        if not user or not user.is_authenticated:
            return Publication.objects.none()

        return Publication.objects.filter(owner=user)
    
    def post(self, request, *args, **kwargs):
        """
        Generate renditions for all items in the publication.
        """
        publication = self.get_object()
        
        # Проверяем, есть ли у публикации пресеты
        if not publication.presets.exists():
            from ..models import RenditionPreset, Recipient
            
            # Ищем или создаем дефолтный пресет
            default_preset = RenditionPreset.objects.filter(
                resource_type='image',
                name__icontains='default'
            ).first()
            
            if not default_preset:
                default_recipient, _ = Recipient.objects.get_or_create(
                    email='system@mayan-edms.local',
                    defaults={
                        'name': 'System Default',
                        'organization': 'Mayan EDMS'
                    }
                )
                
                default_preset = RenditionPreset.objects.create(
                    resource_type='image',
                    format='jpeg',
                    name='Default JPEG',
                    description='Default preset for campaign publications',
                    quality=85,
                    width=1920,
                    height=None,
                    crop=False,
                    recipient=default_recipient
                )
            
            publication.presets.add(default_preset)
        
        # Генерируем рендишены для всех элементов
        try:
            items_count = publication.items.count()
            presets_count = publication.presets.count()
            publication.generate_all_renditions()
            
            from rest_framework.response import Response
            from rest_framework import status
            
            return Response({
                'status': 'success',
                'message': f'Rendition generation queued for {items_count} items with {presets_count} presets',
                'publication_id': publication.id,
                'items_count': items_count,
                'presets_count': presets_count
            }, status=status.HTTP_202_ACCEPTED)
        except Exception as exc:
            from rest_framework.response import Response
            from rest_framework import status
            import logging
            
            logger = logging.getLogger(__name__)
            logger.error(f'Failed to generate renditions for publication {publication.id}: {exc}', exc_info=True)
            
            return Response({
                'status': 'error',
                'message': f'Failed to generate renditions: {str(exc)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
