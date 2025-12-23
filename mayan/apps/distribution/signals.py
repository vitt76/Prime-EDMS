import logging

from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import DistributionCampaign, CampaignPublication, PublicationItem, ShareLink
from mayan.apps.documents.models import Document, DocumentFile
import logging

logger = logging.getLogger(name=__name__)


@receiver(post_save, sender=DistributionCampaign)
def sync_campaign_publication_metadata(sender, instance, created, **kwargs):
    """
    Автоматически синхронизирует метаданные кампании с связанной публикацией
    при сохранении кампании (создании или обновлении).
    """
    # Пропускаем, если это создание новой кампании (синхронизация произойдет
    # через сериализатор при привязке документов/публикаций)
    if created:
        return
    
    # Находим связанные публикации этого владельца
    if not instance.owner:
        return
    
    campaign_pubs = CampaignPublication.objects.filter(
        campaign=instance,
        publication__owner=instance.owner
    ).select_related('publication')
    
    pub_count = campaign_pubs.count()
    logger.info(f'[Signal] Syncing metadata for campaign {instance.id}: found {pub_count} publications')
    
    # Если у кампании есть только одна публикация этого владельца,
    # синхронизируем её метаданные с кампанией
    if pub_count == 1:
        publication = campaign_pubs.first().publication
        old_title = publication.title
        old_description = publication.description
        
        publication.title = instance.title or 'Campaign publication'
        publication.description = instance.description or ''
        publication.save(update_fields=['title', 'description'])
        
        logger.info(
            f'[Signal] Updated publication {publication.id}: '
            f'title "{old_title}" -> "{publication.title}", '
            f'description "{old_description}" -> "{publication.description}"'
        )
    elif pub_count > 1:
        logger.debug(f'[Signal] Campaign {instance.id} has {pub_count} publications, skipping metadata sync')
    else:
        logger.debug(f'[Signal] Campaign {instance.id} has no publications, skipping metadata sync')


@receiver(post_delete, sender=DocumentFile, dispatch_uid='distribution_cleanup_file_delete', weak=False)
def handler_cleanup_on_file_delete(sender, instance, **kwargs):
    """
    При удалении файла: убираем PublicationItem, пустые Publication и связанные CampaignPublication, ShareLink.
    """
    try:
        items = PublicationItem.objects.filter(document_file=instance)
        pub_ids = list(items.values_list('publication_id', flat=True))
        items.delete()

        empty_pubs = []
        for pub_id in pub_ids:
            if not PublicationItem.objects.filter(publication_id=pub_id).exists():
                empty_pubs.append(pub_id)
        if empty_pubs:
            CampaignPublication.objects.filter(publication_id__in=empty_pubs).delete()
            from .models import Publication
            Publication.objects.filter(id__in=empty_pubs).delete()

        ShareLink.objects.filter(rendition__publication_item__document_file=instance).delete()
    except Exception as exc:
        logger.warning('cleanup_on_file_delete failed: %s', exc)


@receiver(post_delete, sender=Document, dispatch_uid='distribution_cleanup_document_delete', weak=False)
def handler_cleanup_on_document_delete(sender, instance, **kwargs):
    """
    При удалении документа: удаляем все публикационные элементы его файлов и связанные кампании/ссылки.
    """
    try:
        file_ids = list(instance.files.values_list('id', flat=True))
        if not file_ids:
            return
        items = PublicationItem.objects.filter(document_file_id__in=file_ids)
        pub_ids = list(items.values_list('publication_id', flat=True))
        items.delete()

        empty_pubs = []
        for pub_id in pub_ids:
            if not PublicationItem.objects.filter(publication_id=pub_id).exists():
                empty_pubs.append(pub_id)
        if empty_pubs:
            CampaignPublication.objects.filter(publication_id__in=empty_pubs).delete()
            from .models import Publication
            Publication.objects.filter(id__in=empty_pubs).delete()

        ShareLink.objects.filter(rendition__publication_item__document_file_id__in=file_ids).delete()
    except Exception as exc:
        logger.warning('cleanup_on_document_delete failed: %s', exc)

