#!/usr/bin/env python3
"""
Check DAM initialization
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent / 'mayan'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings.production')
django.setup()

print("🔍 Checking DAM initialization...")

# Test app loading
try:
    from django.apps import apps
    dam_app = apps.get_app_config('dam')
    print(f"✅ DAM app loaded: {dam_app}")
    print(f"   Name: {dam_app.name}")
    print(f"   Verbose name: {dam_app.verbose_name}")
except Exception as e:
    print(f"❌ DAM app not loaded: {e}")
    sys.exit(1)

# Test search extension
print("\n🔍 Testing search extension...")
try:
    from mayan.apps.documents.search import search_model_document

    # Manually call extend function
    from mayan.apps.dam.search import extend_document_search
    extend_document_search()

    # Check fields
    field_names = []
    for field in search_model_document.search_fields:
        if hasattr(field, 'field'):
            field_names.append(field.field)
        else:
            field_names.append(str(field))

    ai_fields = [f for f in field_names if 'ai_analysis' in f]
    print(f"✅ Found {len(ai_fields)} AI search fields: {ai_fields[:3]}...")

except Exception as e:
    print(f"❌ Search extension failed: {e}")
    import traceback
    traceback.print_exc()

print("\n🎯 DAM initialization check complete!")
