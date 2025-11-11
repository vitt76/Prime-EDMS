#!/usr/bin/env python3
import os
import django
from django.test import RequestFactory

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings.production')
django.setup()

print('🧪 Testing DAM API endpoints...')

# Test API views
try:
    from mayan.apps.dam.api_views import DAMDocumentDetailView

    # Create mock request
    factory = RequestFactory()
    request = factory.get('/api/dam/document-detail/?document_id=2')

    # Create view instance
    view = DAMDocumentDetailView()
    view.request = request

    # Test get_object
    obj = view.get_object()
    print(f'✅ API view get_object: {obj}')

    # Test retrieve
    response = view.retrieve(request)
    print(f'✅ API response status: {response.status_code}')
    if hasattr(response, 'data'):
        print(f'✅ Response data keys: {list(response.data.keys()) if isinstance(response.data, dict) else "not dict"}')

except Exception as e:
    print(f'❌ API test failed: {e}')
    import traceback
    traceback.print_exc()

print('✅ API test complete!')
