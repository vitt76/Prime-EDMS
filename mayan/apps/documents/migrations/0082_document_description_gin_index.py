from django.contrib.postgres.operations import BtreeGinExtension
from django.db import migrations


class Migration(migrations.Migration):
    """
    Создает GIN индекс с триграммами для поля description.
    Это значительно ускоряет поиск по текстовому полю description.
    
    GIN индекс с pg_trgm позволяет использовать полнотекстовый поиск
    для icontains запросов, что намного быстрее обычных индексов.
    """
    dependencies = [
        ('documents', '0081_documentfile_filename_index'),
    ]

    operations = [
        # Включаем расширение pg_trgm для триграммного поиска
        BtreeGinExtension(),
        # Создаем GIN индекс с триграммами для быстрого поиска по description
        migrations.RunSQL(
            sql=(
                "CREATE EXTENSION IF NOT EXISTS pg_trgm; "
                "CREATE INDEX IF NOT EXISTS documents_document_description_gin_idx "
                "ON documents_document USING gin (description gin_trgm_ops);"
            ),
            reverse_sql="DROP INDEX IF EXISTS documents_document_description_gin_idx;"
        ),
    ]

