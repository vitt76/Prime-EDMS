"""
Phase 1: Add nullable organization FK to core models.

ОБЪЕМ И ЛОГИКА (перенесены в целевые приложения, 2026-02-10):

Django AddField/AlterField НЕ принимают параметр app_label — cross-app миграции
должны содержать операции в приложении-владельце модели. Исходная логика сохранена
в следующих файлах:

1) documents/migrations/0085_add_organization.py:
   - AddField(document, organization) — nullable FK на organizations.Organization
   - blank=True, null=True, db_index=True, related_name='documents'

2) tags/migrations/0010_add_organization.py:
   - AddField(tag, organization) — nullable FK на organizations.Organization
   - AlterField(tag, label) — снятие unique=True (label → db_index=True)
   - AlterUniqueTogether(tag, [('organization', 'label')])

3) cabinets/migrations/0007_add_organization.py:
   - AddField(cabinet, organization) — nullable FK на organizations.Organization
   - AlterUniqueTogether(cabinet, [('organization', 'parent', 'label')])

Цель этой миграции: точка синхронизации зависимостей — гарантирует порядок:
org 0001 → documents 0085, tags 0010, cabinets 0007 → org 0002.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
        ('documents', '0085_add_organization'),
        ('tags', '0010_add_organization'),
        ('cabinets', '0007_add_organization'),
    ]

    operations = [
        # All operations moved to documents, tags, cabinets apps
    ]
