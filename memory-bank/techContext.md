# Technical Context: Prime-EDMS

## Технологический стек

### Backend

#### Основной фреймворк
- **Django**: 3.2.14
- **Python**: 3.9 (базовый образ Mayan EDMS)
- **Mayan EDMS**: 4.3.1 (базовая платформа)

#### База данных и хранилище
- **PostgreSQL**: 12.10-alpine (основная БД)
- **Redis**: 6.2-alpine (кэширование, Celery results, блокировки)
- **S3 Storage**: Beget S3 (ru-1 регион) для хранения файлов
- **Локальное хранилище**: `/var/lib/mayan` для медиа-файлов

#### Очереди и задачи
- **RabbitMQ**: 3.10-management-alpine (Celery broker)
- **Celery**: 5.2.3 (асинхронная обработка задач)
- **Celery Beat**: 2.2.1 (периодические задачи)

#### Веб-серверы
- **Gunicorn**: 20.1.0 (WSGI сервер для основного приложения)
- **Daphne**: 3.0.2 (ASGI сервер для WebSocket уведомлений)

#### API и интеграции
- **Django REST Framework**: 3.13.1 (REST API)
- **drf-spectacular**: 0.27.2 (OpenAPI документация)
- **django-cors-headers**: 3.10.0 (CORS поддержка)

#### AI и обработка медиа
- **yandexgptlite**: (YandexGPT интеграция)
- **gigachat**: (GigaChat интеграция)
- **Pillow**: 9.2.0 (обработка изображений)
- **CairoSVG**: 2.5.2 (SVG рендеринг)
- **PyPDF2**: 1.28.4 (обработка PDF)
- **ffmpeg**: (обработка видео, установлен в Dockerfile)

#### Поиск и индексация
- **Whoosh**: 2.7.4 (полнотекстовый поиск)
- **Elasticsearch**: 7.17.1 (опциональный поисковый движок)
- **elasticsearch-dsl**: 7.4.0

#### Дополнительные библиотеки
- **channels**: 3.0.5 (WebSocket поддержка)
- **channels-redis**: 4.1.0 (Redis backend для channels)
- **django-redis**: 5.4.0 (Redis кэш backend)
- **django-prometheus**: 2.3.1 (метрики)
- **django-ratelimit**: 4.1.0 (ограничение запросов)
- **boto3/botocore**: (S3 интеграция)
- **django-storages**: (S3 storage backend)

### Frontend

#### Основной стек
- **Vue**: 3.x (SPA фреймворк)
- **TypeScript**: (типизация)
- **Vite**: 5.4.11 (сборщик и dev-сервер)
- **Pinia**: (state management)
- **Axios**: (HTTP клиент)

#### UI библиотеки
- **Tailwind CSS**: (utility-first CSS фреймворк)
- **Chart.js**: 4.5.1 (графики и визуализация)

### Инфраструктура

#### Контейнеризация
- **Docker**: (контейнеризация приложения)
- **Docker Compose**: (оркестрация сервисов)

#### Мониторинг и логирование
- **Sentry SDK**: 1.5.8 (отслеживание ошибок)
- **python-json-logger**: (структурированное логирование)

## Структура зависимостей

### requirements/base.txt
Содержит базовые зависимости Django и Mayan EDMS:
- Django 3.2.14
- Celery 5.2.3
- Pillow, CairoSVG, PyPDF2
- Django REST Framework
- И другие базовые библиотеки

### requirements/common.txt
Содержит только Django 3.2.14 (базовая зависимость)

### requirements.txt
Объединяет common.txt и base.txt

### Дополнительные зависимости в Dockerfile
- channels, channels-redis, daphne (WebSocket)
- django-redis, django-prometheus, django-ratelimit
- boto3, botocore, django-storages (S3)
- gigachat, yandexgptlite (AI провайдеры)
- drf-spectacular (API документация)

## Настройка окружения

### Переменные окружения (app.env)
- **База данных**: PostgreSQL настройки через `MAYAN_DATABASES`
- **Redis**: Настройки кэша, Celery results, блокировок
- **RabbitMQ**: Celery broker URL
- **S3 Storage**: Beget S3 credentials (hardcoded в docker-compose.yml)
- **AI провайдеры**: GigaChat и YandexGPT credentials через переменные окружения
- **Storage quota**: 500GB лимит через `MADDAM_STORAGE_TOTAL_BYTES`

### Docker Compose конфигурация

#### Сервисы:
1. **postgresql**: PostgreSQL 12.10-alpine
2. **redis**: Redis 6.2-alpine с паролем
3. **rabbitmq**: RabbitMQ 3.10-management-alpine
4. **app**: Основное приложение на Gunicorn (порт 8080)
5. **app_websocket**: WebSocket сервер на Daphne (порт 8001)

#### Volumes:
- `postgres_data`: Данные PostgreSQL
- `rabbitmq_data`: Данные RabbitMQ
- `redis_data`: Данные Redis
- `mayan_data`: Медиа-файлы приложения
- `mayan_renditions`: Сгенерированные превью

## Развертывание

### Поддерживаемые платформы
- **Windows + WSL2**: Ubuntu 22.04 в WSL2
- **Ubuntu нативно**: Ubuntu 20.04+ с systemd

### Скрипты установки
- `setup-wsl.sh`: Автоматическая установка для WSL2
- `ubuntu-setup.sh`: Установка для Ubuntu
- `start-mayan.sh`: Запуск в Linux/WSL2
- `start-mayan.ps1`: Запуск в Windows PowerShell

### Docker образы
- **Базовый образ**: `mayanedms/mayanedms:s4.3`
- **Кастомный Dockerfile**: `Dockerfile.app` с дополнительными зависимостями

## Ограничения и требования

### Версии Python
- Требуется Python 3.9 (совместимость с Mayan EDMS 4.3)

### Версии Django
- Django 3.2.14 (LTS версия, совместимая с Mayan EDMS)

### Системные зависимости
- FFmpeg для обработки видео
- Build tools для компиляции Python пакетов
- Python3-dev для разработки расширений

## Интеграции

### Внешние сервисы
- **Яндекс.Диск**: Импорт файлов через API
- **Beget S3**: Облачное хранилище файлов
- **YandexGPT**: AI анализ через Yandex API
- **GigaChat**: AI анализ через GigaChat API

### Внутренние модули
- **DAM app**: Расширение для управления цифровыми активами
- **Analytics app**: Аналитика использования активов
- **Headless API**: REST API для фронтенда
- **Image Editor**: Редактор изображений
- **Distribution**: Распределение контента
