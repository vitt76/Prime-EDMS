#!/usr/bin/env python3
"""
Simple check for DAM module loading
"""

import os
import sys

# Add Mayan paths
sys.path.insert(0, '/opt/mayan-edms')
sys.path.insert(0, '/opt/mayan-edms/lib/python3.9/site-packages')

# Configure Django minimal settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings')

import django
django.setup()

try:
    from mayan.apps.dam.apps import DAMApp
    print(f"✅ DAM module loaded successfully!")
    print(f"   App name: {DAMApp.name}")
    print(f"   Verbose name: {DAMApp.verbose_name}")
    print(f"   Has REST API: {DAMApp.has_rest_api}")
    print(f"   Has tests: {DAMApp.has_tests}")

    # Check AI providers
    try:
        from mayan.apps.dam.ai_providers.base import AIProviderRegistry
        providers = AIProviderRegistry.list_providers()
        print(f"   AI Providers registered: {len(providers)}")
        for provider_name in providers:
            print(f"     - {provider_name}")
    except Exception as e:
        print(f"   AI Providers check failed: {e}")
        # Try to import individual providers
        try:
            from mayan.apps.dam.ai_providers.gigachat import GigaChatProvider
            print("   ✅ GigaChat provider available")
        except Exception as e2:
            print(f"   ❌ GigaChat provider error: {e2}")

except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
