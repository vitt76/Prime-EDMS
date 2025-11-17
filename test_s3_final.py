#!/usr/bin/env python3
"""
Final test script for S3 integration
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings')
sys.path.insert(0, '/opt/mayan-edms/lib/python3.9/site-packages')
sys.path.insert(0, '/mnt/c/Users/vitt7/PycharmProjects/Prime-EDMS')

django.setup()

def test_storage_settings():
    print("🧪 Testing storage settings...")

    try:
        from mayan.apps.storage.settings import (
            setting_s3_enabled, setting_s3_endpoint_url, setting_s3_access_key,
            setting_s3_secret_key, setting_s3_bucket_name, setting_s3_region_name,
            setting_s3_verify
        )

        print(f"S3 Enabled: {setting_s3_enabled.value}")
        print(f"S3 Endpoint: {setting_s3_endpoint_url.value}")
        print(f"S3 Region: {setting_s3_region_name.value}")
        print(f"S3 Verify: {setting_s3_verify.value}")

        # Test storage backend functions
        from mayan.apps.documents.storages import get_document_storage_backend, get_document_storage_kwargs

        backend = get_document_storage_backend()
        kwargs = get_document_storage_kwargs()

        print(f"Storage Backend: {backend}")
        print(f"Storage Kwargs: {kwargs}")

        if setting_s3_enabled.value and backend == 'storages.backends.s3boto3.S3Boto3Storage':
            print("✅ S3 backend correctly configured")
        elif not setting_s3_enabled.value and 'filebasedstorage' in backend.lower():
            print("✅ FileSystem backend correctly configured")
        else:
            print("❌ Storage backend configuration issue")

    except Exception as e:
        print(f"❌ Error testing storage settings: {e}")
        import traceback
        traceback.print_exc()

def test_s3_validation():
    print("\n🧪 Testing S3 connection validation...")

    try:
        from mayan.apps.storage.utils import validate_s3_connection
        from mayan.apps.storage.settings import (
            setting_s3_endpoint_url, setting_s3_access_key,
            setting_s3_secret_key, setting_s3_bucket_name,
            setting_s3_region_name, setting_s3_verify
        )

        s3_config = {
            'endpoint_url': setting_s3_endpoint_url.value,
            'access_key': setting_s3_access_key.value,
            'secret_key': setting_s3_secret_key.value,
            'bucket_name': setting_s3_bucket_name.value,
            'region_name': setting_s3_region_name.value,
            'verify': setting_s3_verify.value,
        }

        success, message = validate_s3_connection(**s3_config)
        print(f"Validation Result: {success}")
        print(f"Message: {message}")

    except Exception as e:
        print(f"❌ Error testing S3 validation: {e}")
        import traceback
        traceback.print_exc()

def test_migration_command():
    print("\n🧪 Testing migration command...")

    try:
        from mayan.apps.storage.management.commands.migrate_to_s3 import Command
        cmd = Command()

        # Just check that command can be instantiated
        print("✅ Migration command can be instantiated")

        # Check help
        help_text = cmd.help
        print(f"Command help: {help_text}")

    except Exception as e:
        print(f"❌ Error testing migration command: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_storage_settings()
    test_s3_validation()
    test_migration_command()
