#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, '/opt/mayan-edms/lib/python3.9/site-packages')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings')

from django.core import management

if __name__ == '__main__':
    management.execute_from_command_line(['manage.py', 'migrate', 'dam'])
