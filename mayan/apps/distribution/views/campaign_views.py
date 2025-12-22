from django.db.models import Count, Sum

from mayan.apps.rest_api import generics

from ..models import DistributionCampaign, CampaignPublication
from ..permissions import (
    permission_publication_api_view, permission_publication_api_create,
    permission_publication_api_edit, permission_publication_api_delete
)
from ..serializers import (
    CampaignPublicationSerializer, CampaignPublicationCreateSerializer,
    DistributionCampaignDetailSerializer, DistributionCampaignSerializer
)


class APIDistributionCampaignListView(generics.ListCreateAPIView):
    """
    get: Return a list of distribution campaigns for the current user.
    post: Create a new distribution campaign.
    """

    mayan_object_permissions = {'GET': (permission_publication_api_view,)}
    mayan_view_permissions = {'POST': (permission_publication_api_create,)}
    queryset = DistributionCampaign.objects.all()
    serializer_class = DistributionCampaignSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = getattr(self.request, 'user', None)

        if not user or not user.is_authenticated:
            return queryset.none()

        queryset = queryset.filter(owner=user)

        # Annotate basic aggregates for list view.
        queryset = queryset.annotate(
            publications_count=Count('campaign_publications', distinct=True),
            share_links_count=Count(
                'campaign_publications__publication__items__renditions__share_links',
                distinct=True
            ),
            total_views=Sum(
                'campaign_publications__publication__items__renditions__share_links__downloads_count'
            ),
            total_downloads=Sum(
                'campaign_publications__publication__items__renditions__share_links__downloads_count'
            ),
        )

        state = self.request.query_params.get('state')
        if state and state != 'all':
            queryset = queryset.filter(state=state)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
        }


class APIDistributionCampaignDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    get: Return the details of a distribution campaign.
    put: Edit the properties of a distribution campaign.
    patch: Edit the properties of a distribution campaign.
    delete: Delete a distribution campaign.
    """

    mayan_object_permissions = {
        'GET': (permission_publication_api_view,),
        'PUT': (permission_publication_api_edit,),
        'PATCH': (permission_publication_api_edit,),
        'DELETE': (permission_publication_api_delete,)
    }
    queryset = DistributionCampaign.objects.all()
    serializer_class = DistributionCampaignDetailSerializer
    lookup_url_kwarg = 'campaign_id'

    def get_queryset(self):
        queryset = super().get_queryset()
        user = getattr(self.request, 'user', None)

        if not user or not user.is_authenticated:
            return queryset.none()

        return queryset.filter(owner=user)

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
        }


class APICampaignPublicationListView(generics.ListCreateAPIView):
    """
    get: List publications attached to a campaign.
    post: Attach a publication to a campaign.
    """

    mayan_object_permissions = {'GET': (permission_publication_api_view,)}
    mayan_view_permissions = {'POST': (permission_publication_api_create,)}
    queryset = CampaignPublication.objects.all()
    serializer_class = CampaignPublicationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = getattr(self.request, 'user', None)

        if not user or not user.is_authenticated:
            return queryset.none()

        campaign_id = self.kwargs.get('campaign_id')
        return queryset.filter(
            campaign__id=campaign_id,
            campaign__owner=user
        ).select_related('campaign', 'publication')

    def get_serializer_class(self):
        if self.request.method.lower() == 'post':
            return CampaignPublicationCreateSerializer
        return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        campaign_id = self.kwargs.get('campaign_id')
        campaign = DistributionCampaign.objects.filter(
            id=campaign_id, owner=self.request.user
        ).first()
        context['campaign'] = campaign
        return context

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
        }


class APICampaignPublicationDetailView(generics.RetrieveDestroyAPIView):
    """
    delete: Remove publication from campaign.
    """

    mayan_object_permissions = {'DELETE': (permission_publication_api_delete,)}
    queryset = CampaignPublication.objects.all()
    serializer_class = CampaignPublicationSerializer
    lookup_url_kwarg = 'campaign_publication_id'

    def get_queryset(self):
        queryset = super().get_queryset()
        user = getattr(self.request, 'user', None)

        if not user or not user.is_authenticated:
            return queryset.none()

        campaign_id = self.kwargs.get('campaign_id')
        return queryset.filter(
            campaign__id=campaign_id,
            campaign__owner=user
        )

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
        }


