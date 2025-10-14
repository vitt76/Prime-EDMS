#!/usr/bin/env python3
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/opt/mayan-edms/lib/python3.9/site-packages')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings')
django.setup()

from django.conf import settings

print('INSTALLED_APPS with converter:')
for app in settings.INSTALLED_APPS:
    if 'converter' in app.lower():
        print(f'  {app}')

print('\nAll extra_apps from config:')
try:
    import yaml
    with open('/opt/mayan-edms/config.yml', 'r') as f:
        config = yaml.safe_load(f)
    print(f'  config.yml content: {config}')
except Exception as e:
    print(f'  Could not read config.yml: {e}')

try:
    from mayan.apps.common.settings import setting_extra_apps
    print(f'  setting_extra_apps.value: {setting_extra_apps.value}')
except Exception as e:
    print(f'  Could not get setting_extra_apps: {e}')

try:
    from django.conf import settings as django_settings
    print(f'  django_settings.COMMON_EXTRA_APPS: {getattr(django_settings, "COMMON_EXTRA_APPS", "NOT SET")}')
except Exception as e:
    print(f'  Could not get django COMMON_EXTRA_APPS: {e}')

# Check if our app is in INSTALLED_APPS
our_app = 'mayan.apps.converter_pipeline_extension'
if our_app in settings.INSTALLED_APPS:
    print(f'✅ Our app {our_app} is in INSTALLED_APPS')
else:
    print(f'❌ Our app {our_app} is NOT in INSTALLED_APPS')
