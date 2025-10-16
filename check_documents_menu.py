#!/usr/bin/env python
"""
Скрипт для проверки регистрации меню в documents app
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings.development')
sys.path.insert(0, '/opt/mayan-edms/lib/python3.9/site-packages')
sys.path.insert(0, '/opt/mayan-edms')

django.setup()

print("=== CHECKING DOCUMENTS APP MENU REGISTRATION ===")

try:
    from django.conf import settings
    print(f"Distribution in INSTALLED_APPS: {'mayan.apps.distribution' in settings.INSTALLED_APPS}")
except Exception as e:
    print(f"❌ Failed to check INSTALLED_APPS: {e}")

try:
    from mayan.apps.documents.models import Document, DocumentFile
    print("✅ Document models imported successfully")
except Exception as e:
    print(f"❌ Failed to import Document models: {e}")

try:
    from mayan.apps.common.menus import menu_object
    print("✅ Menu object imported successfully")
except Exception as e:
    print(f"❌ Failed to import menu object: {e}")

# Проверяем, что ссылки зарегистрированы
try:
    print("=== CHECKING REGISTERED LINKS ===")
    # Получаем все зарегистрированные ссылки для Document
    document_links = menu_object.get_links(sources=(Document,))
    print(f"Links registered for Document: {len(document_links)}")
    for link in document_links:
        print(f"  - {link.text} ({link.url})")

    # Получаем все зарегистрированные ссылки для DocumentFile
    file_links = menu_object.get_links(sources=(DocumentFile,))
    print(f"Links registered for DocumentFile: {len(file_links)}")
    for link in file_links:
        print(f"  - {link.text} ({link.url})")

except Exception as e:
    print(f"❌ Failed to check registered links: {e}")
    import traceback
    traceback.print_exc()

print("=== DOCUMENTS MENU CHECK COMPLETE ===")
