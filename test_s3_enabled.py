#!/usr/bin/env python3
"""
Test script for S3 enabled configuration
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings')
sys.path.insert(0, '/opt/mayan-edms/lib/python3.9/site-packages')
sys.path.insert(0, '/mnt/c/Users/vitt7/PycharmProjects/Prime-EDMS')

django.setup()

def test_s3_enabled():
    print("🧪 Testing S3 enabled configuration...")

    try:
        from mayan.apps.storage.settings import (
            setting_s3_enabled, setting_s3_endpoint_url, setting_s3_access_key,
            setting_s3_secret_key, setting_s3_bucket_name, setting_s3_region_name,
            setting_s3_verify
        )

        # Test the logic directly by mocking the setting value
        print(f"S3 Enabled (original): {setting_s3_enabled.value}")

        # Test with S3 disabled
        from mayan.apps.documents.storages import get_document_storage_backend, get_document_storage_kwargs
        backend_disabled = get_document_storage_backend()
        kwargs_disabled = get_document_storage_kwargs()
        print(f"Backend when disabled: {backend_disabled}")
        print(f"Disabled kwargs keys: {list(kwargs_disabled.keys())}")

        # Test the S3 configuration directly
        print("\n--- Testing S3 configuration ---")
        s3_config = {
            'endpoint_url': setting_s3_endpoint_url.value,
            'access_key': setting_s3_access_key.value,
            'secret_key': setting_s3_secret_key.value,
            'bucket_name': setting_s3_bucket_name.value,
            'region_name': setting_s3_region_name.value,
            'verify': setting_s3_verify.value,
        }
        print(f"S3 Config: {s3_config}")

        # Manually test what would happen if S3 was enabled
        if all(s3_config.values()):  # If all values are non-empty
            print("✅ All S3 config values are set")
            expected_s3_kwargs = {
                'access_key': s3_config['access_key'],
                'secret_key': s3_config['secret_key'],
                'bucket_name': s3_config['bucket_name'],
                'endpoint_url': s3_config['endpoint_url'],
                'region_name': s3_config['region_name'],
                'verify': s3_config['verify'],
                'default_acl': 'private',
                'file_overwrite': False,
            }
            print(f"Expected S3 kwargs: {expected_s3_kwargs}")
        else:
            print("⚠️ Some S3 config values are empty (expected for testing)")

        print("\n--- Testing S3 validation ---")
        from mayan.apps.storage.utils import validate_s3_connection
        success, message = validate_s3_connection(**s3_config)
        print(f"S3 validation result: {success}")
        print(f"Message: {message}")

    except Exception as e:
        print(f"❌ Error testing S3 enabled config: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_s3_enabled()
