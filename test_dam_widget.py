#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the path
sys.path.insert(0, '/opt/mayan-edms/lib/python3.9/site-packages')
sys.path.insert(0, '/opt/mayan-edms')

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings')
django.setup()

from mayan.apps.documents.models import Document
from mayan.apps.dam.models import DocumentAIAnalysis

print("Testing DAM analysis for document 39...")

try:
    doc = Document.objects.get(pk=39)
    print(f"Document: {doc}")
    print(f"Document ID: {doc.id}")

    try:
        analysis = DocumentAIAnalysis.objects.get(document_id=39)
        print(f"Analysis found: {analysis}")
        print(f"Status: {analysis.analysis_status}")
        print(f"Provider: {analysis.ai_provider}")
        print(f"Description: {analysis.ai_description[:100] if analysis.ai_description else None}")
        print(f"Tags: {analysis.get_ai_tags_list()[:5] if hasattr(analysis, 'get_ai_tags_list') else None}")
        print(f"Categories: {analysis.categories}")
    except DocumentAIAnalysis.DoesNotExist:
        print("Analysis not found in database")
    except Exception as e:
        print(f"Error getting analysis: {e}")

except Document.DoesNotExist:
    print("Document 39 not found")
except Exception as e:
    print(f"Error: {e}")