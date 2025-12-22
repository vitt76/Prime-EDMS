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
    mayan_object_permissions = {'GET': (permission_publication_api_view,)}
    mayan_view_permissions = {'POST': (permission_publication_api_create,)}
    queryset = ShareLink.objects.all()
    serializer_class = ShareLinkSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = getattr(self.request, 'user', None)

        if not user or not user.is_authenticated:
            return queryset.none()

        # Filter to show only share links for publications owned by current user
        # Optimize queries with select_related
        return queryset.filter(
            rendition__publication_item__publication__owner=user
        ).select_related(
            'rendition__preset',
            'rendition__publication_item__publication__owner',
            'rendition__publication_item__document_file'
        ).order_by('-created')


class APIShareLinkDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    get: Return the details of a share link.
    put: Edit the properties of a share link.
    patch: Edit the properties of a share link.
    delete: Delete a share link.
    """
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
        # Optimize queries with select_related
        return queryset.filter(
            rendition__publication_item__publication__owner=user
        ).select_related(
            'rendition__preset',
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
    post: Generate all renditions for a publication.
    """
    mayan_object_permissions = {'POST': (permission_publication_api_edit,)}
    serializer_class = PublicationSerializer
    queryset = Publication.objects.all()

    def get_queryset(self):
        user = getattr(self.request, 'user', None)

        if not user or not user.is_authenticated:
            return Publication.objects.none()

        return Publication.objects.filter(owner=user)
