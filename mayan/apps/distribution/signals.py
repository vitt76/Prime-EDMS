import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import DistributionCampaign, CampaignPublication

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

