#!/usr/bin/env python3
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings')
import django
django.setup()

from mayan.apps.storage.settings import (
    setting_s3_enabled, setting_s3_endpoint_url, setting_s3_access_key,
    setting_s3_secret_key, setting_s3_bucket_name, setting_s3_region_name,
    setting_s3_use_ssl, setting_s3_verify
)

print("🔧 Финальная проверка настроек S3:")
print(f"✅ Включено: {setting_s3_enabled.value}")
print(f"🌐 Endpoint: {setting_s3_endpoint_url.value}")
print(f"📦 Bucket: {setting_s3_bucket_name.value}")
print(f"🔑 Access Key: {setting_s3_access_key.value[:10]}...")
print(f"🔒 Secret Key: {'заполнен' if setting_s3_secret_key.value else 'пустой'}")
print(f"📍 Region: {setting_s3_region_name.value}")
print(f"🔒 SSL: {setting_s3_use_ssl.value}")
print(f"🔒 Verify SSL: {setting_s3_verify.value}")

# Проверить storage backend
from mayan.apps.documents.storages import get_document_storage_backend
backend = get_document_storage_backend()
print(f"📦 Storage Backend: {backend}")

if 's3boto3' in backend.lower():
    print("✅ S3 storage backend активен!")
else:
    print("❌ Все еще используется локальное хранилище")

print("🎉 Готово к тестированию!")


