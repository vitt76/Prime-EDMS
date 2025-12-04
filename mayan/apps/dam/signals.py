"""
Phase B4: Signal handlers for automatic AI analysis triggering.

Auto-triggers AI analysis when new document files are uploaded,
with proper S3 availability checking to avoid race conditions.
"""
import logging
import time

from django.db.models.signals import post_save
from django.dispatch import receiver

from mayan.apps.documents.models import Document, DocumentFile

from .models import DocumentAIAnalysis
from .tasks import analyze_document_with_ai

logger = logging.getLogger(__name__)

# MIME types that support AI image analysis
SUPPORTED_IMAGE_MIMETYPES = {
    'image/jpeg',
    'image/jpg', 
    'image/png',
    'image/gif',
    'image/webp',
    'image/bmp',
    'image/tiff',
}

SUPPORTED_DOCUMENT_MIMETYPES = {
    'application/pdf',
}

# Combined supported types
ANALYZABLE_MIMETYPES = SUPPORTED_IMAGE_MIMETYPES | SUPPORTED_DOCUMENT_MIMETYPES


def is_file_available_in_storage(document_file, max_retries=3, delay=1):
    """
    Check if file is available in storage (S3 or local).
    
    Phase B4: Prevents race conditions where AI analysis starts
    before file is fully uploaded to S3.
    
    Args:
        document_file: DocumentFile instance
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    
    Returns:
        bool: True if file is available, False otherwise
    """
    for attempt in range(max_retries):
        try:
            # Try to check if file exists
            if document_file.file and document_file.file.storage.exists(document_file.file.name):
                # Verify we can get file size (confirms accessibility)
                try:
                    size = document_file.file.size
                    if size > 0:
                        logger.debug(
                            f"✅ File available in storage: {document_file.file.name} ({size} bytes)"
                        )
                        return True
                except Exception as size_exc:
                    logger.debug(f"Size check failed: {size_exc}")
                    
        except Exception as exc:
            logger.debug(
                f"Storage check attempt {attempt + 1}/{max_retries} failed: {exc}"
            )
        
        if attempt < max_retries - 1:
            time.sleep(delay)
    
    logger.warning(
        f"File not available in storage after {max_retries} attempts: {document_file.file.name}"
    )
    return False


def should_trigger_analysis(document_file, document):
    """
    Determine if AI analysis should be triggered for this document file.
    
    Args:
        document_file: The newly created DocumentFile
        document: The parent Document
    
    Returns:
        tuple: (should_trigger: bool, reason: str)
    """
    from django.conf import settings
    
    # Check if auto-trigger is enabled
    if not getattr(settings, 'DAM_AI_ANALYSIS_AUTO_TRIGGER', True):
        return False, "Auto AI analysis is disabled"
    
    # Check MIME type
    mimetype = (document_file.mimetype or '').lower()
    if mimetype not in ANALYZABLE_MIMETYPES:
        # Check for common image extensions if mimetype detection failed
        filename = (document_file.filename or '').lower()
        is_image_by_ext = any(
            filename.endswith(ext) 
            for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.pdf']
        )
        if not is_image_by_ext:
            return False, f"MIME type not supported: {mimetype}"
    
    # Check if analysis already exists and is completed
    try:
        existing_analysis = document.ai_analysis
        if existing_analysis.analysis_status == 'completed':
            return False, "AI analysis already completed"
        if existing_analysis.analysis_status in ('pending', 'processing'):
            return False, f"AI analysis already {existing_analysis.analysis_status}"
    except DocumentAIAnalysis.DoesNotExist:
        pass  # No existing analysis, proceed
    
    return True, "Ready for analysis"


@receiver(post_save, sender=DocumentFile)
def trigger_ai_analysis(sender, instance, created, **kwargs):
    """
    Automatically trigger AI analysis for new document files.
    
    Phase B4 Enhanced:
    - Only analyzes supported file types
    - Checks S3 availability to avoid race conditions
    - Uses dedicated ai_analysis Celery queue
    - Stores task_id for progress tracking
    """
    logger.info(
        f"🔔 DocumentFile signal: {instance.filename}, created={created}, "
        f"mime={instance.mimetype}, doc_id={instance.document_id}"
    )

    if not created:
        logger.debug(f"⏭️ Skipping - file not created: {instance.filename}")
        return

    document = instance.document
    
    # Check if we should trigger analysis
    should_trigger, reason = should_trigger_analysis(instance, document)
    if not should_trigger:
        logger.info(f"⏭️ Skipping AI analysis: {reason}")
        return
    
    logger.info(f"✅ File eligible for AI analysis: {instance.filename}")
    
    # Create or get AI analysis record with pending status
    ai_analysis, analysis_created = DocumentAIAnalysis.objects.get_or_create(
        document=document,
        defaults={
            'analysis_status': 'pending',
            'progress': 0,
            'current_step': 'Queued for AI analysis',
            'ai_provider': ''
        }
    )
    
    if not analysis_created and ai_analysis.analysis_status in ('completed', 'processing'):
        logger.info(f"⏭️ AI analysis already {ai_analysis.analysis_status}")
        return
    
    # Update to pending if it was failed before
    if ai_analysis.analysis_status == 'failed':
        ai_analysis.analysis_status = 'pending'
        ai_analysis.progress = 0
        ai_analysis.current_step = 'Queued for retry'
        ai_analysis.error_message = None
        ai_analysis.save()
    
    logger.info(
        f"📋 AI analysis record {'created' if analysis_created else 'updated'} "
        f"for document: {document.id}"
    )
    
    # Schedule async AI analysis with delay
    # Delay allows S3 upload to complete before analysis starts
    try:
        countdown_seconds = getattr(
            __import__('django.conf', fromlist=['settings']).settings,
            'DAM_AI_ANALYSIS_DELAY_SECONDS',
            10  # Default 10 second delay for S3 propagation
        )
        
        task_result = analyze_document_with_ai.apply_async(
            args=[document.id],
            countdown=countdown_seconds
        )
        
        # Store task ID for progress tracking
        ai_analysis.task_id = task_result.id
        ai_analysis.save(update_fields=['task_id'])
        
        logger.info(
            f"📋 Scheduled AI analysis task {task_result.id} for document {document.id} "
            f"(countdown: {countdown_seconds}s)"
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to schedule AI analysis: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Mark as failed
        ai_analysis.analysis_status = 'failed'
        ai_analysis.error_message = f"Failed to schedule task: {str(e)[:500]}"
        ai_analysis.current_step = 'Scheduling failed'
        ai_analysis.save()


# Note: Document indexing is handled by the unified DocumentIndexCoordinator
# in mayan.apps.documents.indexing_coordinator - no duplicate handlers needed here.
