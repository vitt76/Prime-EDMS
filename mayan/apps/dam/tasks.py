import logging
from typing import Dict, Any, List

from celery import shared_task
from django.conf import settings

from mayan.apps.documents.models import Document, DocumentFile

from .models import DocumentAIAnalysis, DAMMetadataPreset
from .ai_providers import AIProviderRegistry

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60, queue='documents')
def analyze_document_with_ai(self, document_id: int):
    """
    Analyze document with AI and update metadata.

    Args:
        document_id: ID of the document to analyze
    """
    try:
        # Get document and its latest file
        document = Document.objects.get(id=document_id)
        document_file = document.files.order_by('-timestamp').first()

        if not document_file:
            logger.error(f"No files found for document {document_id}")
            return

        # Get AI analysis record
        ai_analysis, created = DocumentAIAnalysis.objects.get_or_create(
            document=document,
            defaults={'analysis_status': 'processing'}
        )

        if not created and ai_analysis.analysis_status == 'completed':
            logger.info(f"AI analysis already completed for document {document_id}")
            return

        # Update status
        ai_analysis.analysis_status = 'processing'
        ai_analysis.save()

        # Get AI analysis results
        analysis_results = perform_ai_analysis(document_file)

        # Update AI analysis record
        ai_analysis.ai_description = analysis_results.get('description', '')
        ai_analysis.ai_tags = analysis_results.get('tags', [])
        ai_analysis.dominant_colors = analysis_results.get('colors', [])
        ai_analysis.alt_text = analysis_results.get('alt_text', '')
        # Extended fields (optional in provider response)
        ai_analysis.categories = analysis_results.get('categories', [])
        ai_analysis.language = analysis_results.get('language', '')
        ai_analysis.people = analysis_results.get('people', [])
        ai_analysis.locations = analysis_results.get('locations', [])
        ai_analysis.copyright_notice = analysis_results.get('copyright')
        ai_analysis.usage_rights = analysis_results.get('usage_rights')
        ai_analysis.rights_expiry = analysis_results.get('rights_expiry')
        ai_analysis.analysis_status = 'completed'
        ai_analysis.ai_provider = analysis_results.get('provider', 'unknown')
        ai_analysis.save()

        # Update document metadata if needed
        update_document_metadata_from_ai(document, analysis_results)

        logger.info(f"Successfully completed AI analysis for document {document_id}")

    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found")
    except Exception as exc:
        logger.error(f"AI analysis failed for document {document_id}: {exc}")

        # Update status on failure
        try:
            ai_analysis = DocumentAIAnalysis.objects.get(document_id=document_id)
            ai_analysis.analysis_status = 'failed'
            ai_analysis.save()
        except DocumentAIAnalysis.DoesNotExist:
            pass

        # Retry on failure
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        else:
            logger.error(f"Max retries exceeded for document {document_id}")


def get_document_image_data(document_file: DocumentFile) -> bytes:
    """
    Get document image data. For image files, read directly. For documents, use internal generation.

    Args:
        document_file: DocumentFile instance

    Returns:
        Image data as bytes
    """
    try:
        logger.info(f"Getting image data for document_file: {document_file}")

        # Check if this is an image file (JPEG, PNG, etc.)
        mimetype = document_file.mimetype or ''
        if mimetype.startswith('image/'):
            # For image files, we can try to read directly
            logger.info(f"Document is an image file ({mimetype}), trying direct read")
            try:
                with document_file.open() as file_obj:
                    image_data = file_obj.read()
                logger.info(f"Successfully read image data directly, size: {len(image_data)} bytes")
                return image_data
            except Exception as e:
                logger.warning(f"Direct read failed: {e}, falling back to page generation")

        # For non-image files or if direct read failed, use page-based approach
        first_page = document_file.pages.first()
        if not first_page:
            logger.error("No pages found in document file")
            return None

        logger.info(f"Using page-based image generation for page: {first_page} (ID: {first_page.pk})")

        # Use Mayan EDMS get_image method which handles caching internally
        from PIL import Image
        import io

        # Get the image using Mayan's method
        image = first_page.get_image()

        # Convert to bytes if it's a PIL Image
        if isinstance(image, Image.Image):
            # Resize if needed
            if image.width > 1600:
                # Calculate new height maintaining aspect ratio
                aspect_ratio = image.height / image.width
                new_height = int(1600 * aspect_ratio)
                image = image.resize((1600, new_height), Image.LANCZOS)

            # Convert to bytes
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=95)
            image_data = output.getvalue()
            output.close()
        else:
            # Assume it's already bytes
            image_data = image

        logger.info(f"Successfully got image data, size: {len(image_data)} bytes")
        return image_data

    except Exception as e:
        logger.error(f"Failed to get image data: {e}")
        import traceback
        traceback.print_exc()
        return None


def perform_ai_analysis(document_file: DocumentFile) -> Dict[str, Any]:
    """
    Perform AI analysis using available providers.

    Args:
        document_file: DocumentFile instance to analyze

    Returns:
        Dict with analysis results
    """
    import os

    # Get file data - use direct file access (since we fixed volume mapping)
    logger.info(f"Starting AI analysis for document_file: {document_file} (mimetype: {document_file.mimetype})")

    try:
        # Use direct file access (should work now with proper volume mapping)
        logger.info("Reading file data directly...")
        with document_file.open() as file_obj:
            image_data = file_obj.read()
        logger.info(f"✅ Successfully read file data directly, size: {len(image_data)} bytes")
        logger.info(f"📍 File path: {document_file.file.path}")
        logger.info(f"📊 File exists at path: {os.path.exists(document_file.file.path)}")

        # Additional validation
        if len(image_data) < 100:
            logger.warning(f"⚠️ File is very small ({len(image_data)} bytes), might be corrupted")
        if not image_data.startswith((b'\xff\xd8\xff', b'GIF87a', b'GIF89a', b'\x89PNG')):
            logger.warning("⚠️ File does not start with known image header")

        # Log file signature for debugging
        import hashlib
        file_hash = hashlib.md5(image_data[:1000]).hexdigest()[:8]
        logger.info(f"🔒 File signature: {file_hash}")
        logger.info(f"📏 Expected size from DB: {document_file.size} bytes")

    except Exception as e:
        logger.error(f"❌ Could not read file data: {e}")
        raise Exception(f"Failed to read document file: {e}")

    # Validate image data
    logger.info(f"First 100 bytes (hex): {image_data[:100].hex()}")
    logger.info(f"First 100 bytes (repr): {repr(image_data[:100])}")

    # Check if this looks like valid image data
    if image_data.startswith(b'\xff\xd8\xff'):
        logger.info("✅ File appears to be valid JPEG (starts with JPEG SOI marker)")
    elif image_data.startswith((b'GIF87a', b'GIF89a')):
        logger.info("✅ File appears to be valid GIF")
    elif image_data.startswith(b'\x89PNG'):
        logger.info("✅ File appears to be valid PNG")
    else:
        logger.warning("⚠️ File does NOT appear to be valid image (missing known header)")

    mime_type = document_file.mimetype or 'application/octet-stream'

    # Try providers in order of proven availability (GigaChat first)
    providers_to_try = ['gigachat', 'openai', 'claude', 'gemini', 'yandexgpt']

    for provider_name in providers_to_try:
        try:
            print(f"🔄 Trying provider: {provider_name}")
            provider_class = AIProviderRegistry.get_provider_class(provider_name)
            provider_config = get_provider_config(provider_name)

            if not provider_config:
                print(f"❌ No config for provider {provider_name}")
                continue

            print(f"⚙️ Config for {provider_name}: {list(provider_config.keys())}")
            provider = provider_class(**provider_config)

            if not provider.is_available():
                print(f"❌ Provider {provider_name} is not available")
                continue

            # Perform analysis
            print(f"🤖 Analyzing document with {provider_name}")
            print(f"📊 Image data size: {len(image_data)}, mime_type: {mime_type}")

            results = provider.analyze_image(image_data, mime_type)

            # Add provider info
            results['provider'] = provider_name
            print(f"✅ Analysis successful with {provider_name}")

            return results

        except Exception as e:
            print(f"❌ AI analysis with {provider_name} failed: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            continue

    # Fallback if all providers fail
    logger.error("All AI providers failed, using fallback analysis")
    return get_fallback_analysis(mime_type)


def get_provider_config(provider_name: str) -> Dict[str, Any]:
    """
    Get configuration for AI provider from environment variables.

    Args:
        provider_name: Name of the provider

    Returns:
        Dict with provider configuration
    """
    import os

    config_mapping = {
        'openai': {
            'api_key': os.environ.get('DAM_OPENAI_API_KEY'),
            'model': os.environ.get('DAM_OPENAI_MODEL', 'gpt-4-vision-preview')
        },
        'yandexgpt': {
            'api_key': os.environ.get('DAM_YANDEXGPT_API_KEY'),
            'folder_id': os.environ.get('DAM_YANDEXGPT_FOLDER_ID'),
            'iam_token': os.environ.get('DAM_YANDEXGPT_IAM_TOKEN'),
            'service_account_key_id': os.environ.get('DAM_YANDEXGPT_KEY_ID'),
            'service_account_key_secret': os.environ.get('DAM_YANDEXGPT_PRIVATE_KEY')
        },
        'gigachat': {
            # Official library expects base64(client_id:client_secret) in credentials
            'credentials': os.environ.get('DAM_GIGACHAT_CREDENTIALS'),
            'scope': os.environ.get('DAM_GIGACHAT_SCOPE', 'GIGACHAT_API_PERS'),
            'verify_ssl_certs': os.environ.get('DAM_GIGACHAT_VERIFY_SSL_CERTS', 'False').lower() == 'true'
        },
        'claude': {
            'api_key': os.environ.get('DAM_CLAUDE_API_KEY')
        },
        'gemini': {
            'api_key': os.environ.get('DAM_GEMINI_API_KEY')
        }
    }

    config = config_mapping.get(provider_name, {})
    # Filter out None values
    return {k: v for k, v in config.items() if v is not None}


def get_fallback_analysis(mime_type: str) -> Dict[str, Any]:
    """
    Provide fallback analysis when AI providers are unavailable.

    Args:
        mime_type: MIME type of the file

    Returns:
        Basic analysis results
    """
    return {
        'description': f'Файл типа {mime_type}',
        'tags': get_basic_tags_for_mime_type(mime_type),
        'colors': [],
        'alt_text': f'Файл типа {mime_type}',
        'provider': 'fallback'
    }


def get_basic_tags_for_mime_type(mime_type: str) -> List[str]:
    """
    Generate basic tags based on MIME type.

    Args:
        mime_type: MIME type string

    Returns:
        List of basic tags
    """
    tags = ['файл']

    if mime_type.startswith('image/'):
        tags.extend(['изображение', 'графика'])
        if 'jpeg' in mime_type or 'jpg' in mime_type:
            tags.extend(['фото', 'JPEG'])
        elif 'png' in mime_type:
            tags.extend(['прозрачный', 'PNG'])
        elif 'gif' in mime_type:
            tags.extend(['анимация', 'GIF'])
    elif mime_type.startswith('video/'):
        tags.extend(['видео', 'мультимедиа'])
    elif mime_type.startswith('audio/'):
        tags.extend(['аудио', 'звук'])

    return tags


def update_document_metadata_from_ai(document: Document, analysis_results: Dict[str, Any]):
    """
    Update document metadata based on AI analysis results.

    Args:
        document: Document instance
        analysis_results: Results from AI analysis
    """
    try:
        # This is where we could integrate with Mayan's metadata system
        # For now, we'll just log the results
        logger.info(f"AI analysis results for document {document.id}: {analysis_results}")

        # TODO: Integrate with Mayan metadata system to automatically
        # create/update metadata entries based on AI results

    except Exception as e:
        logger.error(f"Failed to update document metadata: {e}")


@shared_task
def bulk_analyze_documents(document_ids: List[int]):
    """
    Bulk analyze multiple documents with AI.

    Args:
        document_ids: List of document IDs to analyze
    """
    for document_id in document_ids:
        analyze_document_with_ai.delay(document_id)

    logger.info(f"Scheduled AI analysis for {len(document_ids)} documents")
