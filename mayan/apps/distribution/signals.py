import logging

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from mayan.apps.documents.models import Document, DocumentFile

from .models import (
    CampaignPublication,
    DistributionCampaign,
    PublicationItem,
    ShareLink,
)

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
    if instance.organization_id:
        campaign_pubs = campaign_pubs.filter(
            publication__organization=instance.organization
        )

    pub_count = campaign_pubs.count()
    logger.info(
        '[Signal] Syncing metadata for campaign %s: found %s publications',
        instance.id,
        pub_count
    )

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

        ShareLink.objects_unfiltered.filter(
            rendition__publication_item__document_file=instance
        ).delete()
    except Exception as exc:
        logger.warning('cleanup_on_file_delete failed: %s', exc)


@receiver(pre_save, sender=Document, dispatch_uid='distribution_cleanup_document_trash', weak=False)
def handler_cleanup_on_document_trash(sender, instance, **kwargs):
    """
    При перемещении документа в корзину (soft delete): удаляем все публикационные элементы
    его файлов и связанные кампании/ссылки.

    Это срабатывает при изменении in_trash с False на True.
    """
    try:
        # Проверяем, был ли документ перемещен в корзину
        if not instance.in_trash:
            return

        # Проверяем, был ли документ уже в корзине до этого сохранения
        if instance.pk:
            try:
                old_instance = Document.objects.get(pk=instance.pk)
                if old_instance.in_trash:
                    # Документ уже был в корзине, ничего не делаем
                    return
            except Document.DoesNotExist:
                # Новый документ, пропускаем
                return

        # Документ перемещен в корзину - удаляем связанные элементы
        logger.info(
            '[Distribution] Document %s moved to trash, cleaning up campaign items',
            instance.pk
        )

        # Получаем файлы документа через менеджер, так как в pre_save
        # instance.files может быть недоступен
        file_ids = list(
            DocumentFile.objects.filter(
                document_id=instance.pk
            ).values_list('id', flat=True)
        )
        if not file_ids:
            logger.debug(
                '[Distribution] Document %s has no files, skipping cleanup',
                instance.pk
            )
            return

        items = PublicationItem.objects.filter(document_file_id__in=file_ids)
        pub_ids = list(items.values_list('publication_id', flat=True))
        items_count = items.count()
        items.delete()

        logger.info(
            '[Distribution] Deleted %s publication items for document %s',
            items_count,
            instance.pk
        )

        # Удаляем пустые публикации и связанные кампании
        empty_pubs = []
        for pub_id in pub_ids:
            if not PublicationItem.objects.filter(publication_id=pub_id).exists():
                empty_pubs.append(pub_id)

        if empty_pubs:
            campaign_pubs_count = CampaignPublication.objects.filter(
                publication_id__in=empty_pubs
            ).count()
            CampaignPublication.objects.filter(publication_id__in=empty_pubs).delete()

            from .models import Publication
            Publication.objects.filter(id__in=empty_pubs).delete()

            logger.info(
                '[Distribution] Deleted %s empty publications and %s campaign links',
                len(empty_pubs),
                campaign_pubs_count
            )

        # Удаляем связанные share links (objects_unfiltered: вне контекста org)
        share_links_count = ShareLink.objects_unfiltered.filter(
            rendition__publication_item__document_file_id__in=file_ids
        ).count()
        ShareLink.objects_unfiltered.filter(
            rendition__publication_item__document_file_id__in=file_ids
        ).delete()

        if share_links_count > 0:
            logger.info(
                '[Distribution] Deleted %s share links for document %s',
                share_links_count,
                instance.pk
            )

    except Exception as exc:
        logger.error('cleanup_on_document_trash failed: %s', exc, exc_info=True)


@receiver(post_delete, sender=Document, dispatch_uid='distribution_cleanup_document_delete', weak=False)
def handler_cleanup_on_document_delete(sender, instance, **kwargs):
    """
    При физическом удалении документа: удаляем все публикационные элементы его
    файлов и связанные кампании/ссылки.

    Это срабатывает только при полном удалении из БД (не при перемещении в корзину).
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

        ShareLink.objects_unfiltered.filter(
            rendition__publication_item__document_file_id__in=file_ids
        ).delete()
    except Exception as exc:
        logger.warning('cleanup_on_document_delete failed: %s', exc)
