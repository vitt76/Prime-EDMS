#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings.production')
django.setup()

print('🔍 Checking DAM status...')

# Check documents
from mayan.apps.documents.models import Document
doc_count = Document.objects.count()
print(f'📄 Documents: {doc_count}')

if doc_count > 0:
    doc = Document.objects.first()
    print(f'📄 First document: ID {doc.id} - {doc.label}')

    # Check DAM analysis
    from mayan.apps.dam.models import DocumentAIAnalysis
    analysis = DocumentAIAnalysis.objects.filter(document=doc).first()
    if analysis:
        print(f'🤖 AI Analysis: {analysis.analysis_status} by {analysis.ai_provider}')
    else:
        print('🤖 No AI analysis for this document')

# Check URLs
from django.urls import reverse
try:
    dashboard_url = reverse('dam:dashboard')
    print(f'🔗 DAM Dashboard URL: {dashboard_url}')
except Exception as e:
    print(f'❌ Dashboard URL error: {e}')

try:
    analyses_url = reverse('dam:ai_analysis_list')
    print(f'🔗 AI Analyses URL: {analyses_url}')
except Exception as e:
    print(f'❌ Analyses URL error: {e}')

print('✅ Check complete!')