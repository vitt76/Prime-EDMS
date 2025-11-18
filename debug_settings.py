#!/usr/bin/env python3
import os
import sys
import django

# Add Mayan to path
sys.path.insert(0, '/opt/mayan-edms/lib/python3.9/site-packages')

# Set environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings')

# Initialize Django
django.setup()

from mayan.apps.smart_settings.classes import Setting

# Get STORAGE_S3_ACCESS_KEY setting
setting = Setting.get('STORAGE_S3_ACCESS_KEY')
print(f'global_name: {setting.global_name}')
print(f'raw_value: {repr(setting.raw_value)}')
print(f'yaml: {repr(setting.yaml)}')
print(f'serialized_value: {repr(setting.serialized_value)}')
print(f'value: {repr(setting.value)}')
print(f'is_overridden: {setting.is_overridden()}')
print(f'environment_variable: {setting.environment_variable}')
