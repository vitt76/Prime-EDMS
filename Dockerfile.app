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
    pip3 install reportlab --upgrade && \
    rm -rf /var/lib/apt/lists/*

# Копирование расширения
COPY mayan/apps/converter_pipeline_extension /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/converter_pipeline_extension

# Копирование измененных файлов Mayan EDMS
COPY mayan/apps/documents/links/document_file_links.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/links/document_file_links.py
COPY mayan/apps/documents/icons.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/icons.py
COPY mayan/apps/documents/apps.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/apps.py
COPY mayan/settings/base.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/settings/base.py

# Копирование файлов переводов
COPY mayan/apps/documents/locale /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/locale

# Компиляция переводов
RUN msgfmt /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/locale/ru/LC_MESSAGES/django.po -o /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/locale/ru/LC_MESSAGES/django.mo

