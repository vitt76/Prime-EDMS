#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings.production')
django.setup()

from mayan.apps.dam.tasks import analyze_document_with_ai
from mayan.apps.documents.models import Document

# Get document
doc = Document.objects.get(id=2)
print(f"Starting AI analysis for document: {doc.label}")

# Start analysis
analyze_document_with_ai.delay(doc.id)
print("Analysis started!")
