import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from mayan.apps.documents.models import DocumentFile
from mayan.apps.documents.events import event_document_file_created

from .models import DocumentAIAnalysis
from .tasks import analyze_document_with_ai

logger = logging.getLogger(__name__)


@receiver(post_save, sender=DocumentFile)
def trigger_ai_analysis(sender, instance, created, **kwargs):
    """
    Automatically trigger AI analysis for new document files.

    Only analyzes image files to avoid unnecessary API calls.
    """
    if not created:
        return

    # Check if file is an image
    if not instance.mimetype or not instance.mimetype.startswith('image/'):
        logger.debug(f"Skipping AI analysis for non-image file: {instance.filename} ({instance.mimetype})")
        return

    # Check if AI analysis already exists
    if hasattr(instance.document, 'ai_analysis'):
        logger.debug(f"AI analysis already exists for document: {instance.document}")
        return

    # Create AI analysis record
    ai_analysis, created = DocumentAIAnalysis.objects.get_or_create(
        document=instance.document,
        defaults={
            'analysis_status': 'pending',
            'ai_provider': 'openai'  # Default provider
        }
    )

    if created:
        logger.info(f"Created AI analysis record for document: {instance.document}")

        # Trigger async AI analysis with delay to allow file processing
        analyze_document_with_ai.apply_async(
            args=[instance.document.id],
            countdown=30  # Wait 30 seconds for file processing
        )
        logger.info(f"Scheduled AI analysis for document: {instance.document}")
    else:
        logger.debug(f"AI analysis record already exists for document: {instance.document}")


@receiver(event_document_file_created)
def log_document_file_creation(sender, instance, **kwargs):
    """
    Log when document files are created for monitoring purposes.
    """
    logger.info(f"Document file created: {instance.filename} (ID: {instance.id})")
