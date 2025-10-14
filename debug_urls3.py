#!/usr/bin/env python3
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings')
sys.path.insert(0, '/opt/mayan-edms')
django.setup()

from django.conf import settings
from django.urls import resolve, Resolver404

# Проверяем все URL паттерны
from django.urls.resolvers import get_resolver

resolver = get_resolver()
print("Registered URL patterns containing 'converter-pipeline':")
for pattern in resolver.url_patterns:
    try:
        if hasattr(pattern, 'pattern') and 'converter-pipeline' in str(pattern.pattern):
            print(f"  Pattern: {pattern.pattern}")
            if hasattr(pattern, 'urlconf_name'):
                print(f"    Namespace: {pattern.urlconf_name}")
        elif hasattr(pattern, 'regex') and 'converter-pipeline' in str(pattern.regex):
            print(f"  Regex: {pattern.regex}")
    except:
        pass

# Проверяем конкретные URL
test_urls = [
    '/converter-pipeline/convert/1/',
    '/converter-pipeline/setup/',
]

print("\nTesting URL resolution:")
for url in test_urls:
    try:
        match = resolve(url)
        print(f"✓ {url} -> {match.view_name}")
    except Resolver404:
        print(f"✗ {url} -> Not found")
