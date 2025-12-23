import logging

from django.db.models import Count, Sum
from django.utils.translation import ugettext_lazy as _

from mayan.apps.rest_api import serializers
from mayan.apps.documents.models import Document, DocumentFile

logger = logging.getLogger(name=__name__)

from ..models import (
    CampaignPublication, DistributionCampaign, Publication, PublicationItem,
    ShareLink
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
    assets_count = serializers.IntegerField(read_only=True)
    share_links_count = serializers.IntegerField(read_only=True)
    total_views = serializers.IntegerField(read_only=True)
    total_downloads = serializers.IntegerField(read_only=True)
    publication_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text=_('IDs of publications to attach to this campaign')
    )
    document_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text=_('Document IDs whose latest files will be included in this campaign')
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
            'assets_count',
            'share_links_count',
            'total_views',
            'total_downloads',
            'publication_ids',
            'document_ids',
        )
        read_only_fields = (
            'id',
            'created',
            'modified',
            'owner_username',
            'publications_count',
            'assets_count',
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
        document_ids = validated_data.pop('document_ids', [])
        validated_data = self._strip_internal_fields(validated_data)

        request = self.context.get('request')
        owner = None
        if request and request.user and request.user.is_authenticated:
            owner = request.user
            validated_data['owner'] = owner

        # Явно создаем объект, чтобы гарантированно не передавать служебные поля
        campaign = DistributionCampaign.objects.create(**validated_data)

        # Привязка по документам (создание публикации "под капотом")
        if document_ids and owner:
            self._sync_documents_for_campaign(
                campaign=campaign,
                owner=owner,
                document_ids=document_ids
            )
            # _sync_documents_for_campaign уже синхронизирует метаданные публикации
        # Либо привязка уже существующих публикаций
        elif publication_ids and owner:
            self._sync_publications_for_campaign(
                campaign=campaign,
                owner=owner,
                publication_ids=publication_ids
            )
            # Синхронизируем метаданные с уже существующей публикацией
            self._sync_publication_metadata(campaign=campaign, owner=owner)

        return campaign

    def update(self, instance, validated_data):
        logger.info(f'[CampaignSerializer.update] Called for campaign {instance.id}, validated_data keys: {list(validated_data.keys())}')
        publication_ids = validated_data.pop('publication_ids', None)
        document_ids = validated_data.pop('document_ids', None)
        validated_data = self._strip_internal_fields(validated_data)
        # Owner is controlled by backend
        validated_data.pop('owner', None)

        # Сохраняем старые значения для проверки изменений
        old_title = instance.title
        old_description = instance.description
        logger.info(f'[CampaignSerializer.update] Before update: title={old_title!r}, description={old_description!r}, validated_data={validated_data}')

        instance = super().update(instance, validated_data)
        
        # Обновляем из БД, чтобы получить актуальные значения
        instance.refresh_from_db()
        logger.info(f'[CampaignSerializer.update] After update: title={instance.title!r}, description={instance.description!r}')

        request = self.context.get('request')
        owner = getattr(request, 'user', None)

        # Всегда синхронизируем метаданные публикации с кампанией при обновлении
        # (если есть связанная публикация)
        if owner and owner.is_authenticated:
            logger.info(f'Syncing publication metadata for campaign {instance.id} (title={instance.title}, description={instance.description})')
            self._sync_publication_metadata(campaign=instance, owner=owner)

        # Если пришёл список документов — он имеет приоритет: создаём/синхронизируем
        # публикацию и её элементы "под капотом".
        if document_ids is not None and owner and owner.is_authenticated:
            self._sync_documents_for_campaign(
                campaign=instance,
                owner=owner,
                document_ids=document_ids
            )
        # Если пришёл список публикаций, синхронизируем связи через CampaignPublication.
        elif publication_ids is not None and owner and owner.is_authenticated:
            self._sync_publications_for_campaign(
                campaign=instance,
                owner=owner,
                publication_ids=publication_ids
            )

        return instance

    # ------------------------------------------------------------------
    # Helpers for publications & documents
    # ------------------------------------------------------------------

    def _sync_publication_metadata(self, campaign, owner):
        """
        Синхронизирует название и описание кампании с связанной публикацией.
        Обновляет только автоматически созданную публикацию (если она одна).
        """
        # Обновляем кампанию из БД, чтобы получить актуальные значения
        campaign.refresh_from_db()
        
        campaign_pubs = CampaignPublication.objects.filter(
            campaign=campaign,
            publication__owner=owner
        ).select_related('publication')

        pub_count = campaign_pubs.count()
        logger.info(f'Found {pub_count} publications for campaign {campaign.id} (owner={owner.username})')

        # Если у кампании есть только одна публикация этого владельца,
        # синхронизируем её метаданные с кампанией
        if pub_count == 1:
            publication = campaign_pubs.first().publication
            old_title = publication.title
            old_description = publication.description
            publication.title = campaign.title or _('Campaign publication')
            publication.description = campaign.description or ''
            publication.save(update_fields=['title', 'description'])
            logger.info(f'Updated publication {publication.id}: title "{old_title}" -> "{publication.title}", description "{old_description}" -> "{publication.description}"')
        elif pub_count > 1:
            logger.warning(f'Campaign {campaign.id} has {pub_count} publications, skipping metadata sync')
        else:
            logger.info(f'Campaign {campaign.id} has no publications, skipping metadata sync')

    def _sync_publications_for_campaign(self, campaign, owner, publication_ids):
        allowed_publications = set(
            Publication.objects.filter(id__in=publication_ids, owner=owner).values_list('id', flat=True)
        )
        # Удаляем связи, которых больше нет
        CampaignPublication.objects.filter(
            campaign=campaign
        ).exclude(publication_id__in=allowed_publications).delete()

        # Добавляем недостающие
        existing_ids = set(
            CampaignPublication.objects.filter(campaign=campaign).values_list('publication_id', flat=True)
        )
        for pub_id in allowed_publications:
            if pub_id not in existing_ids:
                CampaignPublication.objects.create(
                    campaign=campaign,
                    publication_id=pub_id
                )

    def _sync_documents_for_campaign(self, campaign, owner, document_ids):
        """
        Create or update a single Publication for this campaign and ensure its
        items correspond to the given document IDs (latest files).
        """
        # Ищем существующую публикацию кампании этого владельца
        campaign_pub = CampaignPublication.objects.filter(
            campaign=campaign,
            publication__owner=owner
        ).select_related('publication').first()

        if campaign_pub:
            publication = campaign_pub.publication
        else:
            publication = Publication.objects.create(
                owner=owner,
                title=campaign.title or _('Campaign publication'),
                description=campaign.description or ''
            )
            CampaignPublication.objects.create(
                campaign=campaign,
                publication=publication
            )

        # Получаем последние файлы документов
        documents = Document.objects.filter(id__in=document_ids)
        file_ids = []
        for doc in documents:
            doc_file = doc.files.order_by('-timestamp').first()
            if doc_file:
                file_ids.append(doc_file.id)

        # Синхронизируем PublicationItem
        existing_qs = PublicationItem.objects.filter(publication=publication)
        existing_file_ids = set(existing_qs.values_list('document_file_id', flat=True))

        # Удаляем лишние items
        existing_qs.exclude(document_file_id__in=file_ids).delete()

        # Добавляем недостающие
        for df_id in file_ids:
            if df_id not in existing_file_ids:
                PublicationItem.objects.create(
                    publication=publication,
                    document_file_id=df_id
                )

        # Синхронизируем метаданные публикации с кампанией
        publication.title = campaign.title or _('Campaign publication')
        publication.description = campaign.description or ''
        publication.save(update_fields=['title', 'description'])


class DistributionCampaignDetailSerializer(DistributionCampaignSerializer):
    """
    Детальный сериализатор кампании с вложенными публикациями.
    """

    publications = CampaignPublicationSerializer(
        many=True,
        source='campaign_publications',
        read_only=True
    )
    assets = serializers.SerializerMethodField()

    class Meta(DistributionCampaignSerializer.Meta):
        fields = DistributionCampaignSerializer.Meta.fields + (
            'publications',
            'assets',
            'metadata',
        )
        # В детальном сериализаторе оставляем возможность редактировать
        # основные поля кампании (title, description, state, даты),
        # read_only только вычисляемые/агрегированные поля.
        read_only_fields = DistributionCampaignSerializer.Meta.read_only_fields + (
            'publications',
            'assets',
            'metadata',
        )

    def get_assets(self, obj):
        """
        Возвращает список файлов (PublicationItem) в кампании с базовой
        информацией по документу и версии.
        """
        items = PublicationItem.objects.filter(
            publication__campaign_links__campaign=obj
        ).select_related('document_file__document')

        results = []
        for item in items:
            document_file = getattr(item, 'document_file', None)
            if not document_file:
                continue
            document = getattr(document_file, 'document', None)
            results.append({
                'id': item.pk,
                'document_id': document.pk if document else None,
                'document_label': document.label if document else None,
                'document_file_id': document_file.pk,
            })

        return results


