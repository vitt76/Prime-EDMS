#!/usr/bin/env python3
"""
Test script for S3 connection validation
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings')
sys.path.insert(0, '/opt/mayan-edms/lib/python3.9/site-packages')
sys.path.insert(0, '/mnt/c/Users/vitt7/PycharmProjects/Prime-EDMS')

django.setup()

from mayan.apps.storage.utils import validate_s3_connection

def test_s3_validation():
    print("🧪 Testing S3 connection validation...")

    # Test with dummy credentials (should fail gracefully)
    test_config = {
        'endpoint_url': 'https://s3.beget.com',
        'access_key': 'test_key',
        'secret_key': 'test_secret',
        'bucket_name': 'test_bucket',
        'region_name': 'ru-1',
        'verify': False
    }

    success, message = validate_s3_connection(**test_config)
    print(f"Result: {success}")
    print(f"Message: {message}")

    if not success and "test_key" in message:
        print("✅ Function works correctly - rejected invalid credentials")
    else:
        print("❌ Function not working as expected")

if __name__ == '__main__':
    test_s3_validation()
