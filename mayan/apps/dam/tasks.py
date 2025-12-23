import base64
import binascii
import logging
from typing import Dict, Any, List, Optional

import requests

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from mayan.apps.documents.models import Document, DocumentFile, DocumentType
from mayan.apps.dam import settings as dam_settings
from mayan.apps.dynamic_search.tasks import task_index_instance

from .models import DocumentAIAnalysis, DAMMetadataPreset
from .services import (
    YandexDiskClient, YandexDiskClientError, YandexDiskImporter
)
from .ai_providers import AIProviderRegistry

logger = logging.getLogger(__name__)


IMAGE_SIGNATURES = (
    b'\xff\xd8\xff',  # JPEG
    b'GIF87a',
    b'GIF89a',
    b'\x89PNG'
)


def _is_supported_image(data: bytes) -> bool:
    if not data:
        return False
    return any(data.startswith(signature) for signature in IMAGE_SIGNATURES)


def _shrink_image_bytes(image_data: bytes, max_width: Optional[int] = None) -> bytes:
    """
    Downscale raw image bytes to a JPEG preview to reduce payload size.
    
    Args:
        image_data: Raw image bytes to process
        max_width: Maximum width in pixels. If None, uses DAM_AI_IMAGE_MAX_WIDTH setting.
    
    Returns:
        Resized image bytes as JPEG, or None on error
    """
    # Получаем max_width из settings, если не указан явно
    if max_width is None:
        max_width = dam_settings.setting_ai_image_max_width.value or 1600
    
    try:
        from PIL import Image
        import io

        stream = io.BytesIO(image_data)
        image = Image.open(stream)

        if image.mode not in ('RGB', 'L'):
            image = image.convert('RGB')

        if image.width > max_width:
            aspect_ratio = image.height / image.width
            new_height = max(1, int(max_width * aspect_ratio))
            image = image.resize((max_width, new_height), Image.LANCZOS)

        output = io.BytesIO()
        image.save(output, format='JPEG', quality=90, optimize=True)
        data = output.getvalue()
        output.close()
        stream.close()
        return data
    except Exception as exc:
        logger.warning(f"⚠️ Could not shrink image bytes: {exc}")
        return None


def _flatten_setting_value(value, candidate_keys: List[str] = None):
    """
    Normalize smart setting values saved via YAML UI.

    Values entered through the interface can end up wrapped in dictionaries
    (for example: {'DAM_GIGACHAT_CREDENTIALS': '...'}). This helper extracts the
    actual payload and trims whitespace/newlines.
    """
    candidate_keys = candidate_keys or []

    if isinstance(value, dict):
        for key in candidate_keys:
            if key in value:
                value = value[key]
                break
        else:
            if len(value) == 1:
                value = next(iter(value.values()))

    if isinstance(value, (list, tuple)):
        value = "\n".join(str(item) for item in value)

    if isinstance(value, str):
        return value.strip()

    return value


def _coerce_bool(value, default=False):
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.strip().lower() in ('1', 'true', 'yes', 'on')

    return bool(value)


def _coerce_list(value) -> List[str]:
    if not value:
        return []

    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if str(item).strip()]

    if isinstance(value, str):
        parts = [item.strip() for item in value.replace('\n', ',').split(',')]
        return [item for item in parts if item]

    return [str(value).strip()]


def _looks_like_service_account_payload(value: str) -> bool:
    lowered = value.lower()
    return value.strip().startswith('{') or '-----begin private key-----' in lowered or 'service_account' in lowered


def _pick_gigachat_credentials(setting_value, env_value: str) -> str:
    primary = _flatten_setting_value(setting_value, candidate_keys=['DAM_GIGACHAT_CREDENTIALS', 'value'])
    candidates = [
        (primary, 'ui'),
        (env_value, 'env')
    ]

    for candidate, source in candidates:
        if not candidate:
            continue
        if not isinstance(candidate, str):
            candidate = str(candidate)
        candidate = candidate.strip()

        if not candidate:
            continue

        if _looks_like_service_account_payload(candidate):
            if source == 'ui':
                logger.warning(
                    "⚠️ Detected service account JSON pasted into DAM_GIGACHAT_CREDENTIALS. "
                    "Please provide base64(client_id:client_secret) as required by the official GigaChat SDK."
                )
            continue

        try:
            base64.b64decode(candidate, validate=True)
            return candidate
        except (ValueError, binascii.Error):
            if source == 'ui':
                logger.warning(
                    "⚠️ GigaChat credentials value is not valid base64. "
                    "It must be base64(client_id:client_secret) as issued by Sber."
                )
            continue

    return ''


def _update_analysis_progress(ai_analysis, progress: int, current_step: str):
    """Helper to update progress without triggering full save validation."""
    DocumentAIAnalysis.objects.filter(pk=ai_analysis.pk).update(
        progress=progress,
        current_step=current_step
    )
    logger.debug(f"📊 Progress: {progress}% - {current_step}")


@shared_task(bind=True, max_retries=3, default_retry_delay=60, queue='tools')
def analyze_document_with_ai(self, document_id: int):
    """
    Analyze document with AI and update metadata.
    
    Phase B4: Enhanced with progress tracking for frontend polling.

    Args:
        document_id: ID of the document to analyze
    """
    ai_analysis = None
    
    try:
        from django.conf import settings

        # Check if AI analysis is enabled
        if not getattr(settings, 'DAM_AI_ANALYSIS_ENABLED', True):
            logger.info(f"🚫 AI analysis is disabled, skipping document {document_id}")
            return

        logger.info(f"🚀 Starting AI analysis for document {document_id}")

        # Get document and its latest file
        document = Document.objects.get(id=document_id)
        document_file = document.files.order_by('-timestamp').first()

        logger.info(f"📄 Document: {document.label} (ID: {document_id})")
        
        if not document_file:
            logger.error(f"No files found for document {document_id}")
            return
        
        logger.info(f"📁 Document file: {document_file} (mimetype: {document_file.mimetype if document_file else 'N/A'})")

        # Check file size before processing (with type-specific limits)
        from .utils import get_max_file_size_for_mime_type, format_file_size
        
        if document_file.size:
            mime_type = document_file.mimetype or 'application/octet-stream'
            max_file_size = get_max_file_size_for_mime_type(mime_type)
            
            if document_file.size > max_file_size:
                file_size_str = format_file_size(document_file.size)
                max_size_str = format_file_size(max_file_size)
                error_msg = (
                    f'File size ({file_size_str}) exceeds maximum allowed size '
                    f'({max_size_str}) for {mime_type} files'
                )
                
                logger.warning(
                    f'File size check failed for document {document_id}: {error_msg}',
                    extra={
                        'document_id': document_id,
                        'file_size': document_file.size,
                        'max_size': max_file_size,
                        'mime_type': mime_type
                    }
                )
                
                # Get or create AI analysis record to update with error
                ai_analysis, created = DocumentAIAnalysis.objects.get_or_create(
                    document=document,
                    defaults={
                        'analysis_status': 'failed',
                        'task_id': self.request.id,
                        'progress': 0,
                        'current_step': f'File too large ({file_size_str} > {max_size_str})',
                        'error_message': error_msg
                    }
                )
                
                # Update status if record already existed
                if not created:
                    ai_analysis.analysis_status = 'failed'
                    ai_analysis.task_id = self.request.id
                    ai_analysis.current_step = f'File too large ({file_size_str} > {max_size_str})'
                    ai_analysis.error_message = error_msg
                    ai_analysis.save()
                
                return  # Exit early, don't process

        # Get AI analysis record
        ai_analysis, created = DocumentAIAnalysis.objects.get_or_create(
            document=document,
            defaults={
                'analysis_status': 'processing',
                'task_id': self.request.id,
                'progress': 0,
                'current_step': 'Initializing AI analysis'
            }
        )

        logger.info(f"🔍 AI Analysis record: created={created}, status={ai_analysis.analysis_status}")

        if not created and ai_analysis.analysis_status == 'completed':
            logger.info(f"AI analysis already completed for document {document_id}")
            return

        # Update status with task ID
        ai_analysis.analysis_status = 'processing'
        ai_analysis.task_id = self.request.id
        ai_analysis.progress = 5
        ai_analysis.current_step = 'Reading document file'
        ai_analysis.error_message = None
        ai_analysis.save()
        logger.info(f"✅ Set status to 'processing' for document {document_id}, task_id={self.request.id}")

        # Progress: 10% - File reading
        _update_analysis_progress(ai_analysis, 10, 'Reading document file from storage')

        # Get AI analysis results
        logger.info(f"🤖 Calling perform_ai_analysis for document {document_id}")
        
        # Progress: 20% - Starting AI analysis
        _update_analysis_progress(ai_analysis, 20, 'Preparing image for AI analysis')
        
        # Progress: 30% - Sending to AI provider
        _update_analysis_progress(ai_analysis, 30, 'Sending to AI provider')
        
        try:
            analysis_results = perform_ai_analysis(document_file)
            logger.info(f"✅ perform_ai_analysis completed for document {document_id}, provider={analysis_results.get('provider', 'unknown')}")
        except Exception as analysis_error:
            logger.error(f"❌ perform_ai_analysis failed for document {document_id}: {analysis_error}", exc_info=True)
            # Update status to failed immediately
            ai_analysis.analysis_status = 'failed'
            ai_analysis.error_message = str(analysis_error)[:1000]
            error_preview = str(analysis_error)[:70]  # Leave room for prefix
            ai_analysis.current_step = f'Failed: {error_preview}'[:100]  # Ensure max_length=100
            ai_analysis.save()
            raise  # Re-raise to trigger retry logic
        
        # Progress: 80% - Processing results
        _update_analysis_progress(ai_analysis, 80, 'Processing AI results')
        
        logger.info(f"✅ perform_ai_analysis returned: {analysis_results.get('provider', 'unknown')}")

        # Progress: 90% - Saving results
        _update_analysis_progress(ai_analysis, 90, 'Saving analysis results')
        
        # Refresh from database to get latest state
        ai_analysis.refresh_from_db()
        
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
        ai_analysis.analysis_completed = timezone.now()
        ai_analysis.ai_provider = analysis_results.get('provider', 'unknown')
        ai_analysis.progress = 100
        ai_analysis.current_step = 'Analysis complete'
        ai_analysis.error_message = None
        ai_analysis.save()

        # Progress: 100% - Complete, now reindexing
        logger.info(f"📊 Progress: 100% - Analysis complete, reindexing...")

        # Update document metadata if needed
        # Note: force_reanalyze can be passed via task kwargs in the future
        force_reanalyze = getattr(self, 'force_reanalyze', False)
        update_document_metadata_from_ai(document, analysis_results, force_reanalyze=force_reanalyze)
        reindex_document_assets(document=document)

        logger.info(f"Successfully completed AI analysis for document {document_id}")

    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found")
    except Exception as exc:
        logger.error(f"AI analysis failed for document {document_id}: {exc}")

        # Update status on failure with error message
        try:
            if ai_analysis is None:
                ai_analysis = DocumentAIAnalysis.objects.get(document_id=document_id)
            
            ai_analysis.analysis_status = 'failed'
            ai_analysis.error_message = str(exc)[:1000]  # Limit error message length
            ai_analysis.current_step = 'Analysis failed'
            ai_analysis.save()
        except DocumentAIAnalysis.DoesNotExist:
            pass

        # Retry on failure
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying AI analysis for document {document_id} (attempt {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=exc)
        else:
            logger.error(f"Max retries exceeded for document {document_id}")


@shared_task(bind=True, queue='tools')
def import_yandex_disk(self):
    """
    Trigger one-off import from Yandex Disk into Cabinets/Documents.
    """
    token = dam_settings.setting_yandex_disk_token.value
    if not token:
        logger.warning('Yandex Disk token is not configured, aborting import.')
        return

    document_type_id = dam_settings.setting_yandex_disk_document_type_id.value
    document_type = None
    if document_type_id:
        document_type = DocumentType.objects.filter(pk=document_type_id).first()
    if not document_type:
        document_type = DocumentType.objects.order_by('label').first()
    if not document_type:
        logger.error('No document type available for Yandex Disk import.')
        return

    base_path = dam_settings.setting_yandex_disk_base_path.value or 'disk:/'
    cabinet_root_label = dam_settings.setting_yandex_disk_cabinet_root_label.value or 'Yandex Disk'
    max_file_size = int(dam_settings.setting_yandex_disk_max_file_size.value or (20 * 1024 * 1024))
    file_limit = int(dam_settings.setting_yandex_disk_file_limit.value or 0)

    client = YandexDiskClient(token=token)
    importer = YandexDiskImporter(
        client=client,
        document_type=document_type,
        base_path=base_path,
        cabinet_root_label=cabinet_root_label,
        max_file_size=max_file_size,
        file_limit=file_limit
    )

    try:
        created = importer.run()
        logger.info('Yandex Disk import finished, documents created: %s', created)
    except YandexDiskClientError as exc:
        logger.error('Yandex Disk import failed: %s', exc)
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
    # Ensure AI providers are registered in Celery context
    from .ai_providers import AIProviderRegistry
    try:
        # Force re-registration in Celery context
        logger.info('🤖 Forcing AI provider registration in Celery context...')

        # Clear existing registrations
        if hasattr(AIProviderRegistry, '_providers'):
            AIProviderRegistry._providers = {}

        # Import and register all providers
        from .ai_providers.qwen_local import LocalQwenVisionProvider
        from .ai_providers.gigachat import GigaChatProvider
        from .ai_providers.openai import OpenAIProvider
        from .ai_providers.claude import ClaudeProvider
        from .ai_providers.gemini import GeminiProvider
        from .ai_providers.yandex import YandexGPTProvider
        from .ai_providers.kieai import KieAIProvider

        AIProviderRegistry.register('qwenlocal', 'mayan.apps.dam.ai_providers.qwen_local.LocalQwenVisionProvider')
        AIProviderRegistry.register('gigachat', 'mayan.apps.dam.ai_providers.gigachat.GigaChatProvider')
        AIProviderRegistry.register('openai', 'mayan.apps.dam.ai_providers.openai.OpenAIProvider')
        AIProviderRegistry.register('claude', 'mayan.apps.dam.ai_providers.claude.ClaudeProvider')
        AIProviderRegistry.register('gemini', 'mayan.apps.dam.ai_providers.gemini.GeminiProvider')
        AIProviderRegistry.register('yandexgpt', 'mayan.apps.dam.ai_providers.yandex.YandexGPTProvider')
        AIProviderRegistry.register('kieai', 'mayan.apps.dam.ai_providers.kieai.KieAIProvider')

        available_providers = list(AIProviderRegistry.get_available_providers())
        logger.info(f'🤖 AI providers registered in Celery context: {available_providers}')
    except Exception as e:
        logger.error(f'❌ Failed to register AI providers in Celery: {e}')
        import traceback
        logger.error(f'Traceback: {traceback.format_exc()}')

    # Get file data - use direct file access (since we fixed volume mapping)
    if not document_file:
        logger.error("document_file is None, cannot perform AI analysis")
        return get_fallback_analysis('application/octet-stream')
    
    # Get mime_type early to avoid errors
    mime_type = document_file.mimetype if document_file and hasattr(document_file, 'mimetype') else 'application/octet-stream'
    logger.info(f"Starting AI analysis for document_file: {document_file} (mimetype: {mime_type})")

    try:
        logger.info("Reading file data...")
        image_data = _read_document_file_bytes(document_file=document_file)
        if not image_data:
            logger.error("❌ Unable to read document file data from storage or S3.")
            return get_fallback_analysis(document_file.mimetype or 'application/octet-stream')
        logger.info(f"✅ Successfully read file data, size: {len(image_data)} bytes")
        storage_key = document_file.file.name
        logger.info(f"📍 Storage key: {storage_key}")

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

    # Validate basic properties of the file
    logger.info(f"First 100 bytes (hex): {image_data[:100].hex()}")
    logger.info(f"First 100 bytes (repr): {repr(image_data[:100])}")

    file_size_mb = len(image_data) / (1024 * 1024)
    logger.info(f"📏 File size: {file_size_mb:.2f} MB")

    # Downscale oversized assets to avoid overloading providers.
    max_size = getattr(dam_settings.setting_analysis_image_max_size, 'value', 10 * 1024 * 1024) or (10 * 1024 * 1024)
    if len(image_data) > max_size:
        logger.info(
            "⚠️ Image size %.2f MB exceeds limit %.2f MB; generating preview for AI analysis.",
            file_size_mb, max_size / (1024 * 1024)
        )
        optimized_data = None
        mimetype = document_file.mimetype or ''
        if mimetype.startswith('image/'):
            optimized_data = _shrink_image_bytes(image_data=image_data)
        if not optimized_data:
            optimized_data = get_document_image_data(document_file=document_file)
        if optimized_data and len(optimized_data) < len(image_data):
            image_data = optimized_data
            mime_type = 'image/jpeg'
            file_size_mb = len(image_data) / (1024 * 1024)
            logger.info("✅ Preview generated: %.2f MB, mime_type=%s", file_size_mb, mime_type)
        else:
            logger.warning("⚠️ Failed to optimize image size; continuing with original data.")

    if not _is_supported_image(image_data):
        logger.info("ℹ️ Source file is not a supported image, attempting conversion via document page preview.")
        converted_data = get_document_image_data(document_file=document_file)
        if converted_data:
            image_data = converted_data
            mime_type = 'image/jpeg'
            file_size_mb = len(image_data) / (1024 * 1024)
            logger.info("✅ Successfully rendered first page to JPEG for analysis (size %.2f MB).", file_size_mb)
        else:
            logger.error("❌ Could not render document to image, skipping AI analysis.")
            return get_fallback_analysis(document_file.mimetype or 'application/octet-stream')
    else:
        if image_data.startswith(b'\xff\xd8\xff'):
            logger.info("✅ File appears to be valid JPEG (starts with JPEG SOI marker)")
        elif image_data.startswith((b'GIF87a', b'GIF89a')):
            logger.info("✅ File appears to be valid GIF")
        elif image_data.startswith(b'\x89PNG'):
            logger.info("✅ File appears to be valid PNG")

    # Try providers in order of proven availability (GigaChat first)
    configured_providers = _coerce_list(dam_settings.setting_ai_providers_active.value)
    default_sequence = _coerce_list(dam_settings.setting_ai_provider_sequence.value)
    providers_to_try = configured_providers or default_sequence

    # Ensure локальная модель стоит первой, если она настроена
    qwen_config = get_provider_config('qwenlocal')
    if qwen_config:
        if 'qwenlocal' in providers_to_try:
            providers_to_try = ['qwenlocal'] + [
                provider for provider in providers_to_try if provider != 'qwenlocal'
            ]
        else:
            providers_to_try.insert(0, 'qwenlocal')

    # Skip GigaChat for больших файлов
    if 'gigachat' in providers_to_try and file_size_mb > 4:
        logger.warning(f"⚠️ File is too large ({file_size_mb:.2f} MB) for GigaChat API (limit: 4MB)")
        providers_to_try = [provider for provider in providers_to_try if provider != 'gigachat']

    for provider_name in providers_to_try:
        try:
            logger.info(f"🔄 Trying provider: {provider_name}")
            provider_class = AIProviderRegistry.get_provider_class(provider_name)
            provider_config = get_provider_config(provider_name)

            if not provider_config:
                logger.warning(f"❌ No config for provider {provider_name}")
                continue

            logger.info(f"⚙️ Config for {provider_name}: {list(provider_config.keys())}")
            provider = provider_class(**provider_config)

            if not provider.is_available():
                logger.warning(f"❌ Provider {provider_name} is not available")
                continue

            # Perform analysis
            logger.info(f"🤖 Analyzing document with {provider_name}")
            logger.info(f"📊 Image data size: {len(image_data)}, mime_type: {mime_type}")

            # Only use providers that support image description
            if provider.supports_image_description:
                results = provider.analyze_image(image_data, mime_type)
            else:
                # Skip providers that don't support image description
                logger.warning(f"⚠️ Provider {provider_name} doesn't support image description, skipping")
                continue

            # Add provider info
            results['provider'] = provider_name
            logger.info(f"✅ Analysis successful with {provider_name}")

            return results

        except Exception as e:
            logger.error(f"❌ AI analysis with {provider_name} failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

            # Add more detailed error info
            if hasattr(e, 'response'):
                logger.error(f"Response status: {getattr(e.response, 'status_code', 'unknown')}")
                logger.error(f"Response content: {getattr(e.response, 'text', 'unknown')[:500]}")

            continue

    # Fallback if all providers fail
    logger.error("All AI providers failed, using fallback analysis")
    return get_fallback_analysis(mime_type, image_data)


def get_provider_config(provider_name: str) -> Dict[str, Any]:
    """
    Get configuration for AI provider from environment variables.

    Args:
        provider_name: Name of the provider

    Returns:
        Dict with provider configuration
    """
    import os
    from mayan.apps.dam import settings as dam_settings

    if provider_name == 'gigachat':
        credentials_env = os.environ.get('DAM_GIGACHAT_CREDENTIALS')
        credentials = _pick_gigachat_credentials(dam_settings.setting_gigachat_credentials.value, credentials_env)
        if not credentials:
            return {}

        scope = _flatten_setting_value(dam_settings.setting_gigachat_scope.value) \
            or os.environ.get('DAM_GIGACHAT_SCOPE', 'GIGACHAT_API_PERS')

        verify_setting = dam_settings.setting_gigachat_verify_ssl.value
        verify = _coerce_bool(
            verify_setting if verify_setting not in (None, '') else os.environ.get('DAM_GIGACHAT_VERIFY_SSL_CERTS'),
            default=False
        )

        model = _flatten_setting_value(dam_settings.setting_gigachat_model.value) \
            or os.environ.get('DAM_GIGACHAT_MODEL', 'GigaChat')

        return {
            'credentials': credentials,
            'scope': (scope or 'GIGACHAT_API_PERS').strip(),
            'verify_ssl_certs': verify,
            'model': (model or 'GigaChat').strip()
        }

    if provider_name == 'qwenlocal':
        api_url = os.environ.get('DAM_QWENLOCAL_API_URL') or _flatten_setting_value(dam_settings.setting_qwenlocal_api_url.value)
        model = os.environ.get('DAM_QWENLOCAL_MODEL') or _flatten_setting_value(dam_settings.setting_qwenlocal_model.value)
        prompt = os.environ.get('DAM_QWENLOCAL_PROMPT') or _flatten_setting_value(dam_settings.setting_qwenlocal_prompt.value)
        timeout = os.environ.get('DAM_QWENLOCAL_TIMEOUT') or dam_settings.setting_qwenlocal_timeout.value or 120
        verify = _coerce_bool(dam_settings.setting_qwenlocal_verify_ssl.value, default=False)

        if not api_url or not model:
            return {}

        return {
            'api_url': api_url,
            'model': model,
            'prompt': prompt,
            'timeout': int(timeout),
            'verify_ssl': verify
        }

    if provider_name == 'kieai':
        api_key = os.environ.get('DAM_KIEAI_API_KEY') or _flatten_setting_value(dam_settings.setting_kieai_api_key.value)
        if not api_key:
            return {}

        base_url = os.environ.get('DAM_KIEAI_BASE_URL') or _flatten_setting_value(dam_settings.setting_kieai_base_url.value)
        upload_url = os.environ.get('DAM_KIEAI_UPLOAD_URL') or _flatten_setting_value(dam_settings.setting_kieai_upload_url.value)
        ocr_endpoint = os.environ.get('DAM_KIEAI_OCR_ENDPOINT') or _flatten_setting_value(dam_settings.setting_kieai_ocr_endpoint.value)
        status_endpoint = os.environ.get('DAM_KIEAI_STATUS_ENDPOINT') or _flatten_setting_value(dam_settings.setting_kieai_status_endpoint.value)
        default_language = os.environ.get('DAM_KIEAI_DEFAULT_LANGUAGE') or _flatten_setting_value(dam_settings.setting_kieai_default_language.value) or 'ru'
        upload_path = os.environ.get('DAM_KIEAI_UPLOAD_PATH') or _flatten_setting_value(dam_settings.setting_kieai_upload_path.value) or 'prime-edms/dam'
        timeout = dam_settings.setting_kieai_timeout.value or 45
        model = os.environ.get('DAM_KIEAI_MODEL') or 'flux-kontext-pro'
        default_prompt = os.environ.get('DAM_KIEAI_PROMPT') or 'Опиши содержимое изображения максимально подробно.'
        aspect_ratio = os.environ.get('DAM_KIEAI_ASPECT_RATIO') or '1:1'

        return {
            'api_key': api_key,
            'base_url': base_url or 'https://api.kie.ai/api/v1/flux/kontext',
            'upload_url': upload_url or 'https://kieai.redpandaai.co/api/file-stream-upload',
            'ocr_endpoint': ocr_endpoint or 'generate',
            'status_endpoint': status_endpoint or 'record-info',
            'default_language': default_language,
            'upload_path': upload_path,
            'timeout': int(timeout),
            'model': model,
            'default_prompt': default_prompt,
            'aspect_ratio': aspect_ratio
        }

    if provider_name == 'openai':
        api_key = os.environ.get('DAM_OPENAI_API_KEY')
        if not api_key:
            return {}
        model = os.environ.get('DAM_OPENAI_MODEL', 'gpt-4-vision-preview')
        return {
            'api_key': api_key,
            'model': model
        }

    if provider_name == 'claude':
        api_key = os.environ.get('DAM_CLAUDE_API_KEY')
        if not api_key:
            return {}
        model = os.environ.get('DAM_CLAUDE_MODEL', 'claude-3-sonnet-20240229')
        return {
            'api_key': api_key,
            'model': model
        }

    if provider_name == 'gemini':
        api_key = os.environ.get('DAM_GEMINI_API_KEY')
        if not api_key:
            return {}
        model = os.environ.get('DAM_GEMINI_MODEL', 'gemini-pro')
        return {
            'api_key': api_key,
            'model': model
        }

    if provider_name == 'yandexgpt':
        folder_id = os.environ.get('DAM_YANDEXGPT_FOLDER_ID')
        api_key = os.environ.get('DAM_YANDEXGPT_API_KEY')
        iam_token = os.environ.get('DAM_YANDEXGPT_IAM_TOKEN')
        if not folder_id or not (api_key or iam_token):
            return {}
        return {
            'api_key': api_key,
            'iam_token': iam_token,
            'folder_id': folder_id,
            'model': os.environ.get('DAM_YANDEXGPT_MODEL', 'yandexgpt-lite')
        }

    return {}


def _read_document_file_bytes(document_file: DocumentFile) -> bytes:
    """
    Try to read document bytes from the configured storage. If the underlying
    storage is remote (S3) and the file is not available locally, fall back
    to downloading via the storage URL.
    """
    try:
        with document_file.open() as file_obj:
            return file_obj.read()
    except FileNotFoundError as exc:
        logger.warning(
            "Document file %s missing locally (%s). Attempting S3 download via URL.",
            document_file.pk, exc
        )
        return _download_document_file_via_url(document_file=document_file)
    except Exception as exc:
        logger.error(f"Unexpected error reading document file {document_file.pk}: {exc}")
        return _download_document_file_via_url(document_file=document_file)


def _download_document_file_via_url(document_file: DocumentFile) -> bytes:
    """
    Download the document file using its storage URL (useful for S3-backed storage).
    """
    try:
        file_name = document_file.file.name
        storage_url = document_file.file.storage.url(file_name)
    except Exception as exc:
        logger.error(f"Unable to build storage URL for document file {document_file.pk}: {exc}")
        return None

    if not storage_url:
        logger.error(f"Storage URL for document file {document_file.pk} is empty.")
        return None

    logger.info(f"Downloading document file {document_file.pk} from {storage_url}")
    try:
        timeout = getattr(dam_settings.setting_kieai_timeout, 'value', 45) or 45
        response = requests.get(storage_url, timeout=int(timeout))
        response.raise_for_status()
        return response.content
    except requests.RequestException as exc:
        logger.error(f"Failed to download document file {document_file.pk} via URL: {exc}")
        return None


def get_fallback_analysis(mime_type: str, image_data: bytes = None) -> Dict[str, Any]:
    """
    Provide fallback analysis when AI providers are unavailable.
    This provides basic technical information, not content analysis.

    Args:
        mime_type: MIME type of the file
        image_data: Raw file data for additional analysis

    Returns:
        Basic technical analysis results
    """
    # Provide technical information about the file
    if mime_type.startswith('image/'):
        format_name = mime_type.split("/")[1].upper()
        description = f'Техническая информация: изображение в формате {format_name}'
        tags = ['изображение', 'графика', format_name.lower()]

        # Get technical metadata
        if image_data:
            try:
                from PIL import Image
                import io

                img = Image.open(io.BytesIO(image_data))
                width, height = img.size
                mode = img.mode
                file_size_kb = len(image_data) / 1024

                description = f'Техническая информация: изображение {format_name}, {width}×{height} пикселей, {file_size_kb:.1f} KB, режим {mode}'
                tags.extend([f'{width}x{height}', f'{file_size_kb:.0f}kb', f'режим_{mode}'])

                # Color mode tags
                if mode == 'RGB':
                    tags.append('цветное')
                elif mode == 'L':
                    tags.append('черно-белое')
                elif mode == 'RGBA':
                    tags.append('прозрачное')

            except Exception as e:
                logger.warning(f"Could not get technical info: {e}")
                description = f'Техническая информация: файл типа {mime_type}'

        alt_text = description
        categories = ['медиа', 'изображения']

    elif mime_type.startswith('video/'):
        format_name = mime_type.split("/")[1].upper()
        description = f'Техническая информация: видеофайл в формате {format_name}'
        alt_text = description
        tags = ['видео', 'мультимедиа', format_name.lower()]
        categories = ['мультимедиа', 'видео']
    elif mime_type.startswith('audio/'):
        format_name = mime_type.split("/")[1].upper()
        description = f'Техническая информация: аудиофайл в формате {format_name}'
        alt_text = description
        tags = ['аудио', 'мультимедиа', format_name.lower()]
        categories = ['мультимедиа', 'аудио']
    elif mime_type == 'application/pdf':
        description = 'Техническая информация: PDF документ'
        alt_text = 'PDF файл'
        tags = ['PDF', 'документ', 'текст']
        categories = ['документы', 'текст']
    else:
        description = f'Техническая информация: файл типа {mime_type}'
        alt_text = description
        tags = get_basic_tags_for_mime_type(mime_type)
        categories = ['файлы']

    return {
        'description': description,
        'tags': tags,
        'categories': categories,
        'language': '',
        'people': [],
        'locations': [],
        'copyright': '',
        'usage_rights': '',
        'colors': [],
        'alt_text': alt_text,
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


def update_document_metadata_from_ai(
    document: Document, 
    analysis_results: Dict[str, Any],
    force_reanalyze: bool = False
):
    """
    Update document metadata based on AI analysis results.
    
    Implements hybrid strategy:
    - Tags (ai_tags, people, locations, categories) -> Mayan Tag via tag.attach_to(document)
    - Text fields (ai_description, alt_text, copyright_notice) -> MetadataType via DocumentMetadata
    
    Principle: "Human > AI" - only overwrite if value is empty (except force_reanalyze).

    Args:
        document: Document instance
        analysis_results: Results from AI analysis
        force_reanalyze: If True, overwrite even non-empty values
    """
    try:
        from mayan.apps.tags.models import Tag
        from mayan.apps.metadata.models import MetadataType, DocumentMetadata
        from mayan.apps.metadata.api import save_metadata
        from django.core.exceptions import ObjectDoesNotExist
        from . import settings as dam_settings
        from .utils import get_or_create_tag
        
        # Get mapping configuration
        mapping_config = dam_settings.setting_ai_metadata_mapping.value or {}
        
        # Get DocumentAIAnalysis
        try:
            ai_analysis = document.ai_analysis
        except ObjectDoesNotExist:
            logger.warning(f"No AI analysis found for document {document.id}, skipping metadata update")
            return
        
        # Process tags (ai_tags, people, locations, categories) -> Mayan Tag
        if mapping_config.get('tags_to_mayan_tags', True):
            ai_tags = analysis_results.get('tags', [])
            if isinstance(ai_tags, list):
                for tag_label in ai_tags:
                    if tag_label:
                        try:
                            tag = get_or_create_tag(tag_label)
                            if tag:
                                tag.attach_to(document)
                                logger.debug(f"Attached tag '{tag_label}' to document {document.id}")
                        except Exception as e:
                            logger.warning(f"Failed to attach tag '{tag_label}': {e}")
        
        if mapping_config.get('people_to_tags', True):
            people = analysis_results.get('people', [])
            if isinstance(people, list):
                for person in people:
                    if person:
                        try:
                            tag = get_or_create_tag(str(person))
                            if tag:
                                tag.attach_to(document)
                                logger.debug(f"Attached person tag '{person}' to document {document.id}")
                        except Exception as e:
                            logger.warning(f"Failed to attach person tag '{person}': {e}")
        
        if mapping_config.get('locations_to_tags', True):
            locations = analysis_results.get('locations', [])
            if isinstance(locations, list):
                for location in locations:
                    if location:
                        try:
                            tag = get_or_create_tag(str(location))
                            if tag:
                                tag.attach_to(document)
                                logger.debug(f"Attached location tag '{location}' to document {document.id}")
                        except Exception as e:
                            logger.warning(f"Failed to attach location tag '{location}': {e}")
        
        if mapping_config.get('categories_to_tags', True):
            categories = analysis_results.get('categories', [])
            if isinstance(categories, list):
                for category in categories:
                    if category:
                        try:
                            tag = get_or_create_tag(str(category))
                            if tag:
                                tag.attach_to(document)
                                logger.debug(f"Attached category tag '{category}' to document {document.id}")
                        except Exception as e:
                            logger.warning(f"Failed to attach category tag '{category}': {e}")
        
        # Process metadata (description, alt_text, copyright_notice) -> MetadataType
        metadata_fields = {
            'description': 'ai_description',
            'alt_text': 'ai_alt_text',
            'copyright_notice': 'ai_copyright',
        }
        
        for field_key, metadata_type_name in metadata_fields.items():
            metadata_type_name_from_config = mapping_config.get(field_key)
            if metadata_type_name_from_config:
                metadata_type_name = metadata_type_name_from_config
            
            # Get value from analysis_results
            value = analysis_results.get(field_key, '')
            if not value and field_key == 'description':
                # Fallback to ai_description from DocumentAIAnalysis
                value = getattr(ai_analysis, 'ai_description', '') or ''
            elif not value and field_key == 'alt_text':
                # Fallback to alt_text from DocumentAIAnalysis
                value = getattr(ai_analysis, 'alt_text', '') or ''
            elif not value and field_key == 'copyright_notice':
                # Fallback to copyright_notice from DocumentAIAnalysis
                value = getattr(ai_analysis, 'copyright_notice', '') or ''
            
            if not value:
                continue  # Skip empty values
            
            # Find MetadataType by name
            try:
                metadata_type = MetadataType.objects.get(name=metadata_type_name)
            except MetadataType.DoesNotExist:
                logger.warning(
                    f"MetadataType '{metadata_type_name}' not found for field '{field_key}', "
                    f"skipping metadata update for document {document.id}"
                )
                continue
            
            # Check if DocumentMetadata exists
            try:
                document_metadata = DocumentMetadata.objects.get(
                    document=document,
                    metadata_type=metadata_type
                )
                # Check if we should overwrite (only if empty or force_reanalyze)
                if not force_reanalyze and document_metadata.value:
                    logger.debug(
                        f"Metadata '{metadata_type_name}' already has value for document {document.id}, "
                        f"skipping (Human > AI principle)"
                    )
                    continue
                
                # Update existing metadata
                document_metadata.value = str(value)[:255]  # DocumentMetadata.value max_length=255
                document_metadata.save()
                logger.info(
                    f"Updated metadata '{metadata_type_name}' for document {document.id}"
                )
            except DocumentMetadata.DoesNotExist:
                # Create new metadata
                try:
                    DocumentMetadata.objects.create(
                        document=document,
                        metadata_type=metadata_type,
                        value=str(value)[:255]  # DocumentMetadata.value max_length=255
                    )
                    logger.info(
                        f"Created metadata '{metadata_type_name}' for document {document.id}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to create metadata '{metadata_type_name}' for document {document.id}: {e}"
                    )
        
        logger.info(f"Successfully updated metadata for document {document.id}")

    except Exception as e:
        logger.error(f"Failed to update document metadata for document {document.id}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")


def reindex_document_assets(document: Document):
    """
    Запустить переиндексацию документа и связанных объектов,
    чтобы новые AI-данные сразу стали доступны в поиске.
    """
    try:
        task_index_instance.apply_async(
            kwargs={
                'app_label': 'documents',
                'model_name': 'document',
                'object_id': document.pk
            }
        )

        for document_file in document.files.only('pk'):
            task_index_instance.apply_async(
                kwargs={
                    'app_label': 'documents',
                    'model_name': 'documentfile',
                    'object_id': document_file.pk
                }
            )
    except Exception as exc:
        logger.warning('Failed to schedule search reindex for document %s: %s', document.pk, exc)


@shared_task(queue='tools')
def bulk_analyze_documents(
    document_ids: List[int],
    ai_service: Optional[str] = None,
    analysis_type: Optional[str] = None,
    user_id: Optional[int] = None,
    bulk_id: Optional[str] = None
):
    """
    Bulk analyze multiple documents with AI.

    Args:
        document_ids: List of document IDs to analyze
        ai_service: Optional preferred AI service
        analysis_type: Optional type of analysis
        user_id: Requesting user for auditing
        bulk_id: Traceable bulk request ID
    """
    logger.info(
        'Scheduling bulk AI analysis task',
        extra={
            'doc_count': len(document_ids),
            'ai_service': ai_service,
            'analysis_type': analysis_type,
            'user_id': user_id,
            'bulk_id': bulk_id
        }
    )

    for document_id in document_ids:
        analyze_document_with_ai.delay(document_id=document_id)
