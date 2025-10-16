#!/usr/bin/env python
"""
Скрипт для проверки регистрации меню distribution
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings.development')
sys.path.insert(0, '/opt/mayan-edms/lib/python3.9/site-packages')
sys.path.insert(0, '/opt/mayan-edms')

django.setup()

print("=== CHECKING DISTRIBUTION MENU REGISTRATION ===")

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

try:
    from mayan.apps.distribution.links.distribution_links import (
        link_document_test, link_document_publish
    )
    print("✅ Distribution links imported successfully")
    print(f"Test link: {link_document_test}")
    print(f"Publish link: {link_document_publish}")
except Exception as e:
    print(f"❌ Failed to import distribution links: {e}")

print("=== MENU REGISTRATION CHECK COMPLETE ===")
