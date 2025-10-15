#!/usr/bin/env python3
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings')
import django
django.setup()

from django.urls import reverse, resolve
from mayan.apps.documents.links.document_file_links import link_document_file_convert

print("=== URL Generation Debug ===")

# Check if the view exists
try:
    url = reverse('converter-pipeline:convert_media', kwargs={'document_file_id': 1})
    print(f"✅ Reverse URL: {url}")
except Exception as e:
    print(f"❌ Reverse URL failed: {e}")

# Check URL resolution
try:
    match = resolve('/converter-pipeline/media-conversion/1/')
    print(f"✅ URL resolves to: {match.url_name} in {match.app_name}")
    print(f"   View function: {match.func}")
except Exception as e:
    print(f"❌ URL resolution failed: {e}")

# Check the link object
print(f"\nLink view: {link_document_file_convert.view}")
print(f"Link args: {link_document_file_convert.args}")

# Try to generate URL from link
try:
    # Create a mock object
    class MockFile:
        pk = 1

    from django.template import RequestContext
    from django.http import HttpRequest

    request = HttpRequest()
    context = RequestContext(request)
    context['resolved_object'] = MockFile()

    resolved_link = link_document_file_convert.resolve(context=context)
    print(f"✅ Link resolves to: {resolved_link.url}")
except Exception as e:
    print(f"❌ Link resolution failed: {e}")

print("\n=== Checking URL patterns ===")
from django.conf import settings
print(f"ROOT_URLCONF: {settings.ROOT_URLCONF}")

# Check if converter pipeline URLs are included
try:
    from mayan.urls import urlpatterns
    converter_urls = [url for url in urlpatterns if hasattr(url, 'pattern') and 'converter' in str(url.pattern)]
    print(f"Converter URL patterns found: {len(converter_urls)}")
    for url in converter_urls:
        print(f"  - {url}")
except Exception as e:
    print(f"Error checking URL patterns: {e}")
