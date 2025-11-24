from django.db import migrations


class Migration(migrations.Migration):
    """
    Создает составные индексы для частых комбинаций полей.
    Эти индексы ускоряют поиск по нескольким полям одновременно.
    
    Индексы:
    1. label + in_trash (WHERE in_trash = false) - для поиска по label среди активных документов
    2. document_type_id + in_trash (WHERE in_trash = false) - для фильтрации по типу документа
    """
    dependencies = [
        ('documents', '0082_document_description_gin_index'),
    ]

    operations = [
        # Составной индекс для частых комбинаций: label + in_trash
        # WHERE in_trash = false оптимизирует индекс для активных документов
        migrations.RunSQL(
            sql=(
                "CREATE INDEX IF NOT EXISTS documents_document_label_trash_idx "
                "ON documents_document (label, in_trash) "
                "WHERE in_trash = false;"
            ),
            reverse_sql="DROP INDEX IF EXISTS documents_document_label_trash_idx;"
        ),
        # Составной индекс для фильтрации по типу документа среди активных
        migrations.RunSQL(
            sql=(
                "CREATE INDEX IF NOT EXISTS documents_document_type_trash_idx "
                "ON documents_document (document_type_id, in_trash) "
                "WHERE in_trash = false;"
            ),
            reverse_sql="DROP INDEX IF EXISTS documents_document_type_trash_idx;"
        ),
    ]

