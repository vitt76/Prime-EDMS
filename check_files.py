#!/usr/bin/env python3
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings')
sys.path.insert(0, '/opt/mayan-edms')
django.setup()

from mayan.apps.documents.models import DocumentFile

print("Available document files:")
files = DocumentFile.objects.all()[:10]
for f in files:
    print(f"  ID: {f.pk}, File: {f.filename}, MIME: {f.mimetype}")
