from django.db.models import Count, Sum
from django.utils.translation import ugettext_lazy as _

from mayan.apps.rest_api import serializers

from ..models import (
    CampaignPublication, DistributionCampaign, ShareLink, Publication
)
from .publication_serializers import PublicationSerializer


class CampaignPublicationSerializer(serializers.ModelSerializer):
    """
    Публикация внутри кампании (для детального просмотра кампании).
    """

    publication = PublicationSerializer(read_only=True)

    class Meta:
        model = CampaignPublication
        fields = (
            'id',
            'campaign',
            'platform_name',
            'sort_order',
            'metadata',
            'publication',
        )
        read_only_fields = fields


class CampaignPublicationCreateSerializer(serializers.ModelSerializer):
    """
    Создание связи публикации с кампанией.
    """

    publication_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CampaignPublication
        fields = (
            'id',
            'campaign',
            'publication_id',
            'platform_name',
            'sort_order',
            'metadata',
        )
        read_only_fields = ('id', 'campaign')

    def validate_publication_id(self, value):
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            raise serializers.ValidationError(_('Authentication required.'))

        try:
            publication = Publication.objects.get(id=value, owner=request.user)
        except Publication.DoesNotExist:
            raise serializers.ValidationError(_('Publication not found or access denied.'))
        return publication.id

    def create(self, validated_data):
        publication_id = validated_data.pop('publication_id')
        campaign = self.context.get('campaign')
        instance = CampaignPublication.objects.create(
            campaign=campaign,
            publication_id=publication_id,
            **validated_data
        )
        return instance


class DistributionCampaignSerializer(serializers.ModelSerializer):
    """
    Кампания для списка на /sharing.
    """

    owner_username = serializers.SerializerMethodField()
    publications_count = serializers.IntegerField(read_only=True)
    share_links_count = serializers.IntegerField(read_only=True)
    total_views = serializers.IntegerField(read_only=True)
    total_downloads = serializers.IntegerField(read_only=True)

    class Meta:
        model = DistributionCampaign
        fields = (
            'id',
            'title',
            'description',
            'state',
            'start_at',
            'end_at',
            'created',
            'modified',
            'owner_username',
            'publications_count',
            'share_links_count',
            'total_views',
            'total_downloads',
        )
        read_only_fields = (
            'id',
            'created',
            'modified',
            'owner_username',
            'publications_count',
            'share_links_count',
            'total_views',
            'total_downloads',
        )

    def get_owner_username(self, obj):
        owner = obj.owner
        if owner:
            return owner.get_username()
        return None

    def _strip_internal_fields(self, validated_data):
        """
        Remove internal fields that should not be passed to the model constructor.
        Mirrors pattern used in other distribution serializers.
        """
        validated_data.pop('_instance_extra_data', None)
        return validated_data

    def create(self, validated_data):
        validated_data = self._strip_internal_fields(validated_data)

        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data['owner'] = request.user

        # Явно создаем объект, чтобы гарантированно не передавать служебные поля
        return DistributionCampaign.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data = self._strip_internal_fields(validated_data)
        # Owner is controlled by backend
        validated_data.pop('owner', None)

        return super().update(instance, validated_data)


class DistributionCampaignDetailSerializer(DistributionCampaignSerializer):
    """
    Детальный сериализатор кампании с вложенными публикациями.
    """

    publications = CampaignPublicationSerializer(
        many=True,
        source='campaign_publications',
        read_only=True
    )

    class Meta(DistributionCampaignSerializer.Meta):
        fields = DistributionCampaignSerializer.Meta.fields + (
            'publications',
            'metadata',
        )
        read_only_fields = fields


