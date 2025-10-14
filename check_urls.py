#!/usr/bin/env python3
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings')
sys.path.insert(0, '/opt/mayan-edms')
django.setup()

from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

# Проверяем различные варианты URL
url_patterns = [
    'converter_pipeline_extension:convert_with_id',
    'converter_pipeline_extension:convert_redirect',
    'converter_pipeline_extension:convert_media',
    'converter_pipeline_extension:setup_instructions',
]

print("Checking URL patterns:")
for pattern in url_patterns:
    try:
        url = reverse(pattern, kwargs={'document_file_id': 1} if 'with_id' in pattern else {})
        print(f"✓ {pattern}: {url}")
    except NoReverseMatch as e:
        print(f"✗ {pattern}: {e}")
    except Exception as e:
        print(f"✗ {pattern}: {e}")

# Проверяем все URL паттерны
from django.conf import settings
print(f"\nROOT_URLCONF: {settings.ROOT_URLCONF}")

# Импортируем URL конфиг
try:
    from mayan.urls import urlpatterns
    print(f"URL patterns count: {len(urlpatterns)}")
except Exception as e:
    print(f"Error importing URL patterns: {e}")
