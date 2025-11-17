#!/usr/bin/env python3
"""
Test script for real S3 Beget connection
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings')
sys.path.insert(0, '/opt/mayan-edms/lib/python3.9/site-packages')
sys.path.insert(0, '/mnt/c/Users/vitt7/PycharmProjects/Prime-EDMS')

django.setup()

def test_real_s3_connection():
    print("🧪 Testing real S3 Beget connection...")

    # Real S3 credentials
    s3_config = {
        'endpoint_url': 'https://s3.ru1.storage.beget.cloud',
        'access_key': '2EILOPQ3JUAW797ZF3DL',
        'secret_key': 'RjLi6AD0OgofbJ2YbzMnHFCqudVwf9Tqw3kB9E7z',
        'bucket_name': 'cafdf4e9fa32-righteous-rimma',
        'region_name': 'ru-1',
        'verify': False
    }

    print(f"Testing connection to: {s3_config['endpoint_url']}")
    print(f"Bucket: {s3_config['bucket_name']}")
    print(f"Region: {s3_config['region_name']}")

    try:
        from mayan.apps.storage.utils import validate_s3_connection
        # Reload the module to get updated function
        import importlib
        import mayan.apps.storage.utils
        importlib.reload(mayan.apps.storage.utils)

        success, message = mayan.apps.storage.utils.validate_s3_connection(**s3_config)

        print(f"✅ Connection test result: {success}")
        print(f"Message: {message}")

        if success:
            print("🎉 S3 connection successful! Ready for migration.")
            return True
        else:
            print("❌ S3 connection failed. Check credentials and network.")
            return False

    except Exception as e:
        print(f"❌ Error testing S3 connection: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_real_s3_connection()
    sys.exit(0 if success else 1)
