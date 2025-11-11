#!/usr/bin/env python3
"""
Test script for AI providers in DAM module.

Usage:
    python test_ai_providers.py [provider_name]

Examples:
    python test_ai_providers.py yandexgpt
    python test_ai_providers.py all
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings.production')

import django
django.setup()

from mayan.apps.dam.ai_providers import AIProviderRegistry
from mayan.apps.dam.tasks import get_provider_config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_yandexgpt_provider():
    """Test YandexGPT provider with a simple text request."""
    print("🤖 Testing YandexGPT provider...")

    try:
        # Register provider
        AIProviderRegistry.register('yandexgpt', 'mayan.apps.dam.ai_providers.yandex.YandexGPTProvider')

        config = get_provider_config('yandexgpt')
        print(f"📋 Config loaded: API_KEY={'***' if config.get('api_key') else 'MISSING'}, "
              f"SECRET={'***' if config.get('api_key_secret') else 'MISSING'}, "
              f"FOLDER_ID={config.get('folder_id', 'MISSING')}")

        if not config.get('api_key') or not config.get('folder_id'):
            print("❌ Missing required configuration for YandexGPT")
            return False

        # Create provider
        provider_class = AIProviderRegistry.get_provider_class('yandexgpt')
        provider = provider_class(**config)

        # Test availability
        if not provider.is_available():
            print("❌ Provider is not available")
            return False

        print("✅ Provider is available")

        # Test simple text generation
        print("📝 Testing text generation...")
        test_prompt = "Привет! Ты YandexGPT. Расскажи кратко о себе в 2-3 предложениях."

        response = provider._make_request(test_prompt, max_tokens=200)
        print(f"📄 Response: {response[:200]}...")

        print("✅ YandexGPT test passed!")
        return True

    except Exception as e:
        print(f"❌ YandexGPT test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_provider_availability():
    """Test availability of all configured providers."""
    print("🔍 Checking provider availability...")

    # Manually register providers for testing (in case apps.py didn't run)
    try:
        from mayan.apps.dam.ai_providers import yandex, gigachat, claude, gemini
        AIProviderRegistry.register('yandexgpt', 'mayan.apps.dam.ai_providers.yandex.YandexGPTProvider')
        AIProviderRegistry.register('gigachat', 'mayan.apps.dam.ai_providers.gigachat.GigaChatProvider')
        AIProviderRegistry.register('claude', 'mayan.apps.dam.ai_providers.claude.ClaudeProvider')
        AIProviderRegistry.register('gemini', 'mayan.apps.dam.ai_providers.gemini.GeminiProvider')
        print("   Providers registered successfully")
    except Exception as e:
        print(f"   Warning: Could not register providers: {e}")

    providers = ['yandexgpt', 'gigachat', 'openai', 'claude', 'gemini']

    for provider_name in providers:
        try:
            config = get_provider_config(provider_name)
            print(f"   {provider_name} config: {config}")  # Debug output

            # Check if config has required fields
            has_config = False
            if provider_name == 'openai' and config.get('api_key'):
                has_config = True
            elif provider_name == 'yandexgpt' and config.get('api_key') and config.get('folder_id'):
                has_config = True
            elif provider_name == 'gigachat' and config.get('client_id') and config.get('client_secret'):
                has_config = True
            elif provider_name in ['claude', 'gemini'] and config.get('api_key'):
                has_config = True

            print(f"   {provider_name} has_config: {has_config}")  # Debug output

            if has_config:
                provider_class = AIProviderRegistry.get_provider_class(provider_name)
                provider = provider_class(**config)

                available = provider.is_available()
                status = "✅ Available" if available else "❌ Not available"
                print(f"   {provider_name}: {status}")
            else:
                print(f"   {provider_name}: ⚠️  No configuration")

        except Exception as e:
            print(f"   {provider_name}: ❌ Error - {e}")
            import traceback
            traceback.print_exc()


def create_test_document():
    """Create a test document for AI analysis testing."""
    print("📄 Creating test document...")

    try:
        from mayan.apps.documents.models import Document, DocumentType
        from mayan.apps.documents.files.models import DocumentFile
        from django.core.files.base import ContentFile

        # Get or create document type
        doc_type, created = DocumentType.objects.get_or_create(
            name='Test Documents',
            defaults={'label': 'Test Documents'}
        )

        if created:
            print("📁 Created test document type")

        # Create test document
        document = Document.objects.create(
            document_type=doc_type,
            label='AI Test Document'
        )

        # Create test file content (simple text file)
        test_content = b"This is a test document for AI analysis.\nIt contains some sample text to test the AI capabilities."
        content_file = ContentFile(test_content, name='test_document.txt')

        # Create document file
        document_file = DocumentFile.objects.create(
            document=document,
            file=content_file
        )

        print(f"✅ Created test document: {document} (ID: {document.id})")
        print(f"✅ Created test file: {document_file} (ID: {document_file.id})")

        return document.id

    except Exception as e:
        print(f"❌ Failed to create test document: {e}")
        return None


def test_ai_analysis(document_id=None):
    """Test full AI analysis workflow."""
    print("🎨 Testing AI analysis workflow...")

    if not document_id:
        document_id = create_test_document()
        if not document_id:
            return False

    try:
        from mayan.apps.dam.tasks import analyze_document_with_ai

        print(f"🚀 Starting AI analysis for document {document_id}...")

        # Run analysis synchronously for testing
        result = analyze_document_with_ai(document_id)

        if result:
            print("✅ AI analysis completed successfully!")
            return True
        else:
            print("❌ AI analysis failed")
            return False

    except Exception as e:
        print(f"❌ AI analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("🚀 Starting AI Provider Tests for Prime-EDMS DAM module")
    print("=" * 60)

    provider_to_test = sys.argv[1] if len(sys.argv) > 1 else 'all'

    if provider_to_test == 'yandexgpt':
        test_yandexgpt_provider()
    elif provider_to_test == 'availability':
        test_provider_availability()
    elif provider_to_test == 'analysis':
        document_id = sys.argv[2] if len(sys.argv) > 2 else None
        test_ai_analysis(document_id)
    elif provider_to_test == 'all':
        print("📋 Running all tests...")

        # Test provider availability
        test_provider_availability()
        print()

        # Test YandexGPT specifically
        test_yandexgpt_provider()
        print()

        # Test full analysis workflow
        test_ai_analysis()
    else:
        print(f"❌ Unknown test: {provider_to_test}")
        print("Available tests: yandexgpt, availability, analysis, all")

    print("=" * 60)
    print("🏁 Tests completed!")


if __name__ == '__main__':
    main()
