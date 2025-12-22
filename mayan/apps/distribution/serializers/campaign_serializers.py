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
    publication_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text=_('IDs of publications to attach to this campaign')
    )

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
            'publication_ids',
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
        publication_ids = validated_data.pop('publication_ids', [])
        validated_data = self._strip_internal_fields(validated_data)

        request = self.context.get('request')
        owner = None
        if request and request.user and request.user.is_authenticated:
            owner = request.user
            validated_data['owner'] = owner

        # Явно создаем объект, чтобы гарантированно не передавать служебные поля
        campaign = DistributionCampaign.objects.create(**validated_data)

        # Привязка публикаций, если переданы
        if publication_ids and owner:
            publications = Publication.objects.filter(id__in=publication_ids, owner=owner)
            existing_ids = set()
            for pub in publications:
                cp, _ = CampaignPublication.objects.get_or_create(
                    campaign=campaign,
                    publication=pub
                )
                existing_ids.add(pub.id)

        return campaign

    def update(self, instance, validated_data):
        publication_ids = validated_data.pop('publication_ids', None)
        validated_data = self._strip_internal_fields(validated_data)
        # Owner is controlled by backend
        validated_data.pop('owner', None)

        instance = super().update(instance, validated_data)

        # Если пришёл список публикаций, синхронизируем связи
        if publication_ids is not None:
            request = self.context.get('request')
            owner = getattr(request, 'user', None)
            if owner and owner.is_authenticated:
                allowed_publications = set(
                    Publication.objects.filter(id__in=publication_ids, owner=owner).values_list('id', flat=True)
                )
                # Удаляем связи, которых больше нет
                CampaignPublication.objects.filter(
                    campaign=instance
                ).exclude(publication_id__in=allowed_publications).delete()

                # Добавляем недостающие
                existing_ids = set(
                    CampaignPublication.objects.filter(campaign=instance).values_list('publication_id', flat=True)
                )
                for pub_id in allowed_publications:
                    if pub_id not in existing_ids:
                        CampaignPublication.objects.create(
                            campaign=instance,
                            publication_id=pub_id
                        )

        return instance


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


