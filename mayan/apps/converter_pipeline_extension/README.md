# Converter Pipeline Extension

Расширение системы конвертации Mayan EDMS для поддержки профессиональных медиа-форматов.

## 🎯 Цель

Расширить возможности системы конвертации Mayan EDMS для автоматической генерации preview изображений из:

- **RAW изображений камер** (CR2, NEF, ARW, DNG, ORF, RAF, RW2, и др.)
- **Видео файлов** (MP4, AVI, MOV, MKV, WebM, FLV, WMV, и др.)
- **Профессиональных форматов** (PSD, CDR, XCF, PostScript)
- **Архивов** (RAR, 7z, ZIP, TAR, GZ, BZ2)

## 🏗️ Архитектура

### Откатываемое расширение
- **Не модифицирует** существующую систему Mayan EDMS
- **Полностью изолировано** в отдельном Django приложении
- **Легко отключаемо** через management команды
- **Миграции с rollback** для безопасного развертывания

### Микросервисная готовность
- Docker сервисы для каждого типа конвертеров
- API-first дизайн
- Асинхронная обработка через Celery
- Масштабируемость через Kubernetes

## 📦 Структура

```
converter_pipeline_extension/
├── __init__.py              # Конфигурация приложения
├── apps.py                  # MayanAppConfig
├── models.py                # Proxy модели и метаданные
├── signals.py               # Сигналы интеграции
├── utils.py                 # Утилиты и реестр форматов
├── backends/                # Конвертеры
│   ├── base.py             # Базовый класс
│   ├── raw_image.py        # RAW изображения
│   ├── video.py            # Видео файлы
│   └── archive.py          # Архивы
├── tasks.py                 # Celery задачи
├── management/             # Management команды
│   └── commands/
│       └── manage_converter_pipeline.py
├── migrations/             # Миграции БД
├── docker/                 # Docker сервисы
│   ├── raw/               # RAW конвертер
│   ├── video/             # Видео конвертер
│   ├── pro/               # Про форматы
│   └── archive/           # Архивы
├── tests/                  # Тесты
└── locale/                 # Переводы (26 языков)
```

## 🚀 Установка и настройка

### 1. Активация расширения

```bash
# Включить расширение
python manage.py manage_converter_pipeline enable

# Проверить статус
python manage.py manage_converter_pipeline status
```

### 2. Docker сервисы

```bash
# Запуск сервисов конвертеров
docker-compose -f docker-compose.extension.yml up -d

# Проверить статус
docker ps | grep converter
```

### 3. Настройка

```python
# settings.py или через админку
CONVERTER_PIPELINE = {
    'RAW_QUALITY': 90,
    'VIDEO_THUMBNAIL_SIZE': (320, 180),
    'MAX_FILE_SIZE_MB': 500,
    'CONVERSION_TIMEOUT': 300,
}
```

## 🎨 Использование

### Автоматическая конвертация

Расширение автоматически:
1. Определяет тип загружаемого файла
2. Выбирает подходящий конвертер
3. Создает preview через Celery
4. Сохраняет результат в Mayan

### Ручная конвертация

```python
from converter_pipeline_extension.tasks import task_convert_document_media

# Конвертировать документ
task_convert_document_media.delay(document_id)

# Создать миниатюры видео
from converter_pipeline_extension.tasks import task_convert_video_thumbnails
task_convert_video_thumbnails.delay(document_id)
```

### API

```python
# Проверить статус конвертации
document = Document.objects.get(pk=document_id)
status = document.conversion_metadata.conversion_status

# Получить поддерживаемые форматы
formats = document.supported_preview_formats
```

## 🔧 Управление

### Management команды

```bash
# Включить расширение
python manage.py manage_converter_pipeline enable

# Отключить расширение
python manage.py manage_converter_pipeline disable

# Показать статус
python manage.py manage_converter_pipeline status

# Очистить данные (ВНИМАНИЕ!)
python manage.py manage_converter_pipeline cleanup
```

### Откат изменений

```bash
# Отключить расширение
python manage.py manage_converter_pipeline disable

# Откатить миграции
python manage.py migrate converter_pipeline_extension zero

# Очистить данные
python manage.py manage_converter_pipeline cleanup

# Удалить приложение из INSTALLED_APPS
# Перезапустить сервер
```

## 📊 Поддерживаемые форматы

### RAW изображения (50+ форматов)
- Canon: CR2, CRW
- Nikon: NEF, NRW
- Sony: ARW, SRF
- Pentax: PEF
- Olympus: ORF
- Fuji: RAF
- Panasonic: RW2
- Adobe: DNG
- И многие другие...

### Видео (30+ форматов)
- MP4, AVI, MOV, MKV
- WebM, FLV, WMV, M4V
- 3GP, QuickTime
- И другие видео форматы

### Профессиональные форматы (20+)
- Adobe Photoshop (PSD)
- CorelDRAW (CDR)
- GIMP (XCF)
- PostScript, PDF
- И другие

### Архивы (10+ форматов)
- RAR, 7z, ZIP
- TAR, GZ, BZ2
- Извлечение изображений из архивов

## ⚙️ Настройки

### Глобальные настройки

```python
# settings.py
CONVERTER_PIPELINE = {
    # Качество конвертации
    'RAW_QUALITY': 90,
    'VIDEO_QUALITY': 85,

    # Размеры preview
    'RAW_MAX_SIZE': (1920, 1080),
    'VIDEO_THUMBNAIL_SIZE': (320, 180),

    # Ограничения
    'MAX_FILE_SIZE_MB': 500,
    'CONVERSION_TIMEOUT': 300,

    # Docker сервисы
    'DOCKER_NETWORK': 'mayan_default',
    'CONVERTER_SERVICES': {
        'raw': 'converter-raw:latest',
        'video': 'converter-video:latest',
        'archive': 'converter-archive:latest',
    }
}
```

### Настройки по типам документов

```python
# Через админку или API
document_type.media_conversion_policies = {
    'auto_convert': True,
    'preferred_format': 'JPEG',
    'quality': 'high',
    'max_resolution': '1920x1080'
}
```

## 🔒 Безопасность

- **Валидация входных данных** - проверка MIME типов и размеров
- **Изоляция через Docker** - конвертеры в отдельных контейнерах
- **Time limits** - ограничение времени выполнения
- **Resource limits** - ограничение использования CPU/памяти
- **Audit logging** - логирование всех операций конвертации

## 📈 Мониторинг

### Метрики
- Количество конвертаций по типам
- Время выполнения
- Успешность/неудачи
- Использование ресурсов

### Логи
```bash
# Логи конвертеров
docker logs converter-raw
docker logs converter-video

# Логи задач Celery
python manage.py celery inspect active
```

## 🧪 Тестирование

```bash
# Запуск тестов
python manage.py test converter_pipeline_extension

# С тестами производительности
python manage.py test converter_pipeline_extension --keepdb --parallel

# С покрытием
coverage run manage.py test converter_pipeline_extension
coverage report
```

## 📚 API Reference

### Models
- `DocumentConversionMetadata` - метаданные конвертации
- `ConversionFormatSupport` - поддерживаемые форматы
- `ExtendedDocumentProxy` - прокси модель документа

### Tasks
- `task_convert_document_media` - конвертация документа
- `task_convert_video_thumbnails` - миниатюры видео
- `task_batch_convert_documents` - пакетная конвертация

### Utils
- `is_media_format_supported()` - проверка поддержки формата
- `get_converter_for_mime_type()` - получение конвертера
- `validate_file_size()` - валидация размера файла

## 🤝 Contributing

1. Следовать архитектурным ограничениям (1.mdc)
2. Добавлять тесты для новых функций
3. Обновлять документацию
4. Использовать интернационализацию для текстов

## 📄 Лицензия

Расширение распространяется под той же лицензией, что и Mayan EDMS.



