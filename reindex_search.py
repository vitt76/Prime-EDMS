#!/usr/bin/env python3
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings')
import django
django.setup()

from mayan.apps.dynamic_search.tasks import task_reindex_backend

# Запустить полную переиндексацию
result = task_reindex_backend.apply_async()
print(f"Reindexing task started: {result.id}")
print("Wait a few minutes for reindexing to complete, then check search functionality.")