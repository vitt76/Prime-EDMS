#!/usr/bin/env python3
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings')
import django
django.setup()

from django.utils.translation import activate
from mayan.apps.documents.links.document_file_links import link_document_file_convert

print("Testing translation...")

# Test with English
activate('en')
print(f"English: {link_document_file_convert.text}")

# Test with Russian
activate('ru')
print(f"Russian: {link_document_file_convert.text}")

print("✅ Translation test completed!")
