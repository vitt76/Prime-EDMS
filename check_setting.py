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

from mayan.apps.lock_manager.settings import setting_backend
print(f'setting_backend.value: {repr(setting_backend.value)}')

# Check environment variable
env_value = os.getenv('MAYAN_LOCK_MANAGER_BACKEND', 'NOT_SET')
print(f'ENV MAYAN_LOCK_MANAGER_BACKEND: {repr(env_value)}')
