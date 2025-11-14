import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from mayan.apps.documents.models import DocumentFile
# from mayan.apps.documents.events import event_document_file_created  # Not used

from .models import DocumentAIAnalysis
from .tasks import analyze_document_with_ai

logger = logging.getLogger(__name__)


@receiver(post_save, sender=DocumentFile)
def trigger_ai_analysis(sender, instance, created, **kwargs):
    """
    Automatically trigger AI analysis for new document files.

    Only analyzes image files to avoid unnecessary API calls.
    """
    logger.info(f"🔔 Signal triggered for document file: {instance.filename}, created: {created}")
    logger.info(f"📄 Document: {instance.document}, Document ID: {instance.document.id}")
    logger.info(f"🗂️  MIME type: {instance.mimetype}")

    if not created:
        logger.debug(f"⏭️ Skipping signal - file not created: {instance.filename}")
        return

    # Check if file is an image
    if not instance.mimetype or not instance.mimetype.startswith('image/'):
        logger.info(f"⏭️ Skipping AI analysis for non-image file: {instance.filename} ({instance.mimetype})")
        return

    # Check if AI analysis already exists and is completed
    if hasattr(instance.document, 'ai_analysis'):
        analysis = instance.document.ai_analysis
        logger.info(f"📊 Existing AI analysis status: {analysis.analysis_status}")
        if analysis.analysis_status == 'completed':
            logger.info(f"⏭️ AI analysis already completed for document: {instance.document}")
            return
        elif analysis.analysis_status == 'pending' or analysis.analysis_status == 'running':
            logger.info(f"⏭️ AI analysis already in progress for document: {instance.document}")
            return

    logger.info(f"🔄 Creating AI analysis record for document: {instance.document}")

    # Create AI analysis record
    ai_analysis, created = DocumentAIAnalysis.objects.get_or_create(
        document=instance.document,
        defaults={
            'analysis_status': 'pending',
            'ai_provider': ''  # Empty provider initially
        }
    )

    logger.info(f"📋 AI analysis record {'created' if created else 'already exists'} for document: {instance.document}")

    if created:
        logger.info(f"✅ Created AI analysis record for document: {instance.document}")

        # Trigger async AI analysis with delay to allow file processing
        try:
            task_result = analyze_document_with_ai.apply_async(
                args=[instance.document.id],
                countdown=5  # Reduced delay for testing
            )
            logger.info(f"📋 Scheduled AI analysis task {task_result.id} for document: {instance.document}")
        except Exception as e:
            logger.error(f"❌ Failed to schedule AI analysis: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    else:
        logger.info(f"⏭️ AI analysis record already exists for document: {instance.document}")


# Note: Mayan EDMS events are not Django signals, so we can't use @receiver decorator
# Instead, we'll use the Mayan event system if needed
# For now, we'll rely on the post_save signal above
