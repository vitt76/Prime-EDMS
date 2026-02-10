"""
Phase 3: Make organization FK required (NOT NULL) and add composite indexes.

ОБЪЕМ И ЛОГИКА (перенесены в целевые приложения, 2026-02-10):

После 0003_populate_default_organization все записи привязаны к default Organization.
Исходная логика (AlterField NOT NULL + AddIndex) сохранена в:

1) documents/migrations/0086_make_organization_required.py:
   - AlterField(document, organization) — убрать null=True, blank=True
   - AddIndex(document, ['organization', '-datetime_created'], name='idx_doc_org_created')

2) tags/migrations/0011_make_organization_required.py:
   - AlterField(tag, organization) — NOT NULL
   - AddIndex(tag, ['organization', 'label'], name='idx_tag_org_label')

3) cabinets/migrations/0008_make_organization_required.py:
   - AlterField(cabinet, organization) — NOT NULL
   - AddIndex(cabinet, ['organization', 'label'], name='idx_cabinet_org_label')

Цель: точка синхронизации — org 0004 выполняется после 0003 и всех *make_organization_required.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0003_populate_default_organization'),
        ('documents', '0086_make_organization_required'),
        ('tags', '0011_make_organization_required'),
        ('cabinets', '0008_make_organization_required'),
    ]

    operations = [
        # All operations moved to documents, tags, cabinets apps
    ]
