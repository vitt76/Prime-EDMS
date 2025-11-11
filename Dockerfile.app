FROM mayanedms/mayanedms:s4.3

# Установка системных зависимостей для расширения
RUN apt-get update && \
    apt-get install -y \
        ffmpeg \
        python3-pil \
        python3-reportlab \
        python3-pip \
        python3-dev \
        build-essential \
        gettext && \
    pip3 install reportlab cryptography PyJWT "gigachat<0.1.43" "pydantic<2.0" "typing-extensions<4.6" yandexgptlite --upgrade && \
    rm -rf /var/lib/apt/lists/*

# Копирование расширения (обновлено)
COPY mayan/apps/converter_pipeline_extension /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/converter_pipeline_extension
COPY mayan/apps/image_editor /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/image_editor

# Копирование измененных файлов Mayan EDMS
COPY mayan/apps/documents/links/document_file_links.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/links/document_file_links.py
COPY mayan/apps/documents/icons.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/icons.py
COPY mayan/apps/documents/apps.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/apps.py
COPY mayan/apps/distribution/models.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/distribution/models.py
COPY mayan/apps/distribution/serializers/publication_serializers.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/distribution/serializers/publication_serializers.py
COPY mayan/apps/distribution/ui_views.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/distribution/ui_views.py
COPY mayan/apps/distribution/urls/urls.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/distribution/urls/urls.py
COPY mayan/apps/distribution/templates /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/distribution/templates
COPY mayan/settings/base.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/settings/base.py

# Копирование файлов переводов
COPY mayan/apps/documents/locale /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/locale

# Компиляция переводов
RUN msgfmt /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/locale/ru/LC_MESSAGES/django.po -o /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/locale/ru/LC_MESSAGES/django.mo

# Build timestamp: 10/23/2025 15:16:12
