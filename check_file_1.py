#!/usr/bin/env python3
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings')
sys.path.insert(0, '/opt/mayan-edms')
django.setup()

from mayan.apps.documents.models import DocumentFile

try:
    f = DocumentFile.objects.get(pk=1)
    print(f'File found: ID={f.pk}, Name={f.filename}, MIME={f.mimetype}')
except DocumentFile.DoesNotExist:
    print('File with ID=1 not found')
except Exception as e:
    print(f'Error: {e}')
