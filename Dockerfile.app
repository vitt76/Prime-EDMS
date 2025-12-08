FROM mayanedms/mayanedms:s4.3

# Установка системных зависимостей и Python-библиотек,
# необходимых для кастомных приложений.
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        ffmpeg \
        gettext \
        python3-dev \
        python3-pil \
        python3-pip \
        python3-reportlab && \
    /opt/mayan-edms/bin/pip install --upgrade \
        boto3 \
        botocore \
        cryptography \
        django-storages \
        gigachat \
        PyJWT \
        python-json-logger \
        reportlab \
        "pydantic<2.0" \
        "typing-extensions<4.6" \
        yandexgptlite && \
    rm -rf /var/lib/apt/lists/*

# Кастомные расширения
COPY mayan/apps/converter_pipeline_extension /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/converter_pipeline_extension
COPY mayan/apps/image_editor /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/image_editor

# Обновлённые модули Mayan EDMS
COPY mayan/apps/documents/links/document_file_links.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/links/document_file_links.py
COPY mayan/apps/documents/icons.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/icons.py
COPY mayan/apps/documents/apps.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/apps.py
COPY mayan/apps/documents/handlers.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/handlers.py
COPY mayan/apps/documents/tasks.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/tasks.py
COPY mayan/apps/documents/queues.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/queues.py
COPY mayan/apps/documents/literals.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/literals.py
COPY mayan/apps/documents/settings.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/settings.py
COPY mayan/apps/views/widgets.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/views/widgets.py
COPY mayan/apps/documents/forms /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/forms
COPY mayan/apps/documents/templates /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/templates
COPY mayan/apps/documents/views /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/views
COPY mayan/apps/documents/storages.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/storages.py
COPY mayan/apps/documents/search /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/search
COPY mayan/apps/documents/models/document_file_models.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/models/document_file_models.py
COPY mayan/apps/documents/migrations/0081_documentfile_filename_index.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/migrations/0081_documentfile_filename_index.py
COPY mayan/apps/documents/migrations/0082_document_description_gin_index.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/migrations/0082_document_description_gin_index.py
COPY mayan/apps/documents/migrations/0083_document_composite_indexes.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/migrations/0083_document_composite_indexes.py
COPY mayan/apps/document_indexing/queues.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/document_indexing/queues.py
COPY mayan/apps/dynamic_search /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/dynamic_search
COPY mayan/apps/dam /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/dam
COPY mayan/apps/headless_api /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/headless_api
COPY mayan/apps/autoadmin /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/autoadmin
COPY mayan/apps/storage /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/storage
COPY mayan/apps/smart_settings/classes.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/smart_settings/classes.py
COPY mayan/apps/lock_manager/apps.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/lock_manager/apps.py
COPY mayan/apps/task_manager/apps.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/task_manager/apps.py
COPY mayan/apps/distribution /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/distribution
COPY mayan/settings/base.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/settings/base.py

# Переводы
COPY mayan/apps/documents/locale /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/locale
RUN msgfmt /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/locale/ru/LC_MESSAGES/django.po \
        -o /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/locale/ru/LC_MESSAGES/django.mo
