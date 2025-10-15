FROM mayanedms/mayanedms:s4.3

# Устанавливаем ffmpeg для конвертации видео
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы расширения
COPY ../../ /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/converter_pipeline_extension/


