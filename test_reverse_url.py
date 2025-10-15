#!/usr/bin/env python3
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings')
import django
django.setup()

from django.urls import reverse

print("Testing reverse URL generation...")

# Test different namespace variations
namespaces_to_test = [
    'converter_pipeline_extension:convert_media',
    'converter-pipeline:convert_media',
    'converter_pipeline_extension:media-conversion',
    'converter-pipeline:media-conversion'
]

for namespace in namespaces_to_test:
    try:
        url = reverse(namespace, kwargs={'document_file_id': 1})
        print(f"✅ {namespace} -> {url}")
    except Exception as e:
        print(f"❌ {namespace} -> {e}")

# Check available URL names
from django.conf import settings
from django.urls import get_resolver

resolver = get_resolver()
print(f"\nAvailable URL names:")
converter_names = [name for name in resolver.reverse_dict.keys() if 'convert' in str(name).lower()]
for name in converter_names[:10]:  # Show first 10
    print(f"  - {name}")
