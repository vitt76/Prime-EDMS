import pytz

from django.conf import settings
from django.db import migrations, reset_queries


def code_document_version_page_create(apps, schema_editor):
    ContentType = apps.get_model(
        app_label='contenttypes', model_name='ContentType'
    )
    DocumentFilePage = apps.get_model(
        app_label='documents', model_name='DocumentFilePage'
    )
    DocumentVersion = apps.get_model(
        app_label='documents', model_name='DocumentVersion'
    )

    content_type = ContentType.objects.get_for_model(model=DocumentFilePage)
    content_type_id = content_type.id
    cursor_main = schema_editor.connection.create_cursor(name='document_file_to_version')
    cursor_document_version_page = schema_editor.connection.cursor()

    query = '''
    SELECT
        {documents_documentfile}.{document_id},
        {documents_documentfile}.{timestamp},
        {documents_documentfilepage}.{document_file_id},
        {documents_documentfilepage}.{id}
    FROM {documents_documentfilepage}
    INNER JOIN {documents_documentfile} ON (
        {documents_documentfilepage}.{document_file_id} = {documents_documentfile}.{id}
    ) ORDER BY {documents_documentfilepage}.{id} ASC
    '''.format(
        documents_documentfile=schema_editor.connection.ops.quote_name(
            name='documents_documentfile'
        ),
        document_id=schema_editor.connection.ops.quote_name(
            name='document_id'
        ),
        timestamp=schema_editor.connection.ops.quote_name(name='timestamp'),
        documents_documentfilepage=schema_editor.connection.ops.quote_name(
            name='documents_documentfilepage'
        ),
        document_file_id=schema_editor.connection.ops.quote_name(
            name='document_file_id'
        ),
        id=schema_editor.connection.ops.quote_name(name='id')
    )

    cursor_main.execute(query)

    class DummyDocumentVersion:
        def save(self):
            """Does not do anything."""

    document_file_id_last = None
    document_version = DummyDocumentVersion()

    document_version_page_insert_query = '''
        INSERT INTO {documents_documentversionpage} (
            {document_version_id},{content_type_id},{object_id},{page_number}
        ) VALUES {{}};
    '''.format(
        content_type_id=schema_editor.connection.ops.quote_name(
            name='content_type_id'
        ),
        document_version_id=schema_editor.connection.ops.quote_name(
            name='document_version_id'
        ),
        documents_documentversionpage=schema_editor.connection.ops.quote_name(
            name='documents_documentversionpage'
        ),
        object_id=schema_editor.connection.ops.quote_name(
            name='object_id'
        ),
        page_number=schema_editor.connection.ops.quote_name(
            name='page_number'
        )
    )

    document_version_page_values = []
    page_number = 1

    FETCH_SIZE = 100000

    time_zone = pytz.timezone(zone=settings.TIME_ZONE)

    while True:
        rows = cursor_main.fetchmany(FETCH_SIZE)

        if not rows:
            break

        for row in rows:
            document_id, timestamp, document_file_id, document_file_page_id = row
            timestamp = timestamp.astimezone(tz=time_zone)

            if document_file_id_last != document_file_id:
                document_version = DocumentVersion.objects.create(
                    document_id=document_id
                )
                document_version.timestamp = timestamp
                document_version.save()
                document_version_id = document_version.pk
                document_file_id_last = document_file_id
                if document_version_page_values:
                    final_query = document_version_page_insert_query.format(
                        ('(%s,%s,%s,%s),' * (page_number - 1))[:-1]
                    )

                    page_number = 1

                    cursor_document_version_page.execute(
                        final_query, document_version_page_values
                    )
                    reset_queries()

                document_version_page_values = []

            document_version_page_values += (
                document_version_id, content_type_id, document_file_page_id,
                page_number
            )

            page_number += 1

    if page_number > 1:
        final_query = document_version_page_insert_query.format(
            ('(%s,%s,%s,%s),' * (page_number - 1))[:-1]
        )
        cursor_document_version_page.execute(
            final_query, document_version_page_values
        )


def code_document_version_page_create_reverse(apps, schema_editor):
    DocumentVersion = apps.get_model(
        app_label='documents', model_name='DocumentVersion'
    )

    DocumentVersion.objects.using(
        alias=schema_editor.connection.alias
    ).all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('documents', '0062_auto_20200920_0614')
    ]

    operations = [
        migrations.RunPython(
            code=code_document_version_page_create,
            reverse_code=code_document_version_page_create_reverse
        )
    ]
