#!/usr/bin/env python3
"""
Test DAM integration: AI providers, search fields, UI
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent / 'mayan'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings.production')
django.setup()

def test_gigachat_provider():
    """Test GigaChat structured response"""
    print("🧪 Testing GigaChat provider...")

    try:
        from mayan.apps.dam.ai_providers.gigachat import GigaChatProvider

        # Initialize provider with env vars
        provider = GigaChatProvider(
            credentials=os.environ.get('DAM_GIGACHAT_CREDENTIALS'),
            scope=os.environ.get('DAM_GIGACHAT_SCOPE', 'GIGACHAT_API_PERS'),
            verify_ssl_certs=os.environ.get('DAM_GIGACHAT_VERIFY_SSL_CERTS', 'False').lower() == 'true'
        )

        if not provider.is_available():
            print("❌ GigaChat provider not available (no credentials)")
            return False

        # Test structured request
        result = provider._make_request("Проанализируй изображение с людьми на природе")
        print(f"✅ GigaChat response: {result}")

        # Check structure
        required_fields = ['description', 'tags', 'categories', 'provider']
        for field in required_fields:
            if field not in result:
                print(f"❌ Missing field: {field}")
                return False

        print("✅ GigaChat provider test passed")
        return True

    except Exception as e:
        print(f"❌ GigaChat provider test failed: {e}")
        return False

def test_search_fields():
    """Test that AI fields are added to document search"""
    print("🧪 Testing search field extension...")

    try:
        from mayan.apps.documents.search import search_model_document

        # Manually extend search if not already done
        try:
            from mayan.apps.dam.search import extend_document_search
            extend_document_search()
        except Exception as e:
            print(f"Note: extend_document_search failed (may already be done): {e}")

        # Check if AI fields are present
        ai_fields = [
            'ai_analysis__ai_description',
            'ai_analysis__ai_tags',
            'ai_analysis__categories',
            'ai_analysis__people',
            'ai_analysis__locations'
        ]

        # Get field names - try different attributes
        search_field_names = []
        for field in search_model_document.search_fields:
            if hasattr(field, 'field_name'):
                search_field_names.append(field.field_name)
            elif hasattr(field, 'field'):
                search_field_names.append(field.field)
            else:
                search_field_names.append(str(field))

        print(f"Debug: Found {len(search_field_names)} search fields")

        missing_fields = []
        for field in ai_fields:
            if field not in search_field_names:
                missing_fields.append(field)

        if missing_fields:
            print(f"❌ Missing search fields: {missing_fields}")
            return False

        print(f"✅ Search fields added: {len(ai_fields)} AI fields found")
        return True

    except Exception as e:
        print(f"❌ Search field test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dam_models():
    """Test DAM models are accessible"""
    print("🧪 Testing DAM models...")

    try:
        from mayan.apps.dam.models import DocumentAIAnalysis

        # Check model fields
        fields = [f.name for f in DocumentAIAnalysis._meta.fields]
        required_fields = ['categories', 'language', 'people', 'locations', 'copyright_notice', 'usage_rights', 'rights_expiry']

        missing_fields = []
        for field in required_fields:
            if field not in fields:
                missing_fields.append(field)

        if missing_fields:
            print(f"❌ Missing model fields: {missing_fields}")
            return False

        print(f"✅ DAM model fields present: {len(required_fields)} new fields")
        return True

    except Exception as e:
        print(f"❌ DAM model test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting DAM integration tests...\n")

    tests = [
        test_dam_models,
        test_search_fields,
        test_gigachat_provider,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All DAM integration tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
