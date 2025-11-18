#!/usr/bin/env python3
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings')
import django
django.setup()

from mayan.apps.documents.storages import get_document_storage_backend
backend = get_document_storage_backend()
print(f"Storage Backend: {backend}")

if "s3" in backend.lower():
    print("✅ Файлы сохраняются в S3")
else:
    print("📁 Файлы сохраняются локально")


