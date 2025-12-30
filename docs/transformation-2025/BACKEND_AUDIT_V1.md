# BACKEND_AUDIT_V1.md

**Дата аудита:** 2025-12-09  
**Версия:** 2.0  
**Последнее обновление:** 2025-12-23 (добавлены модули analytics и notifications: модели, API endpoints, Celery tasks, сигналы, интеграция с headless_api)  
**Статус:** Полный технический аудит бэкенда

---

## 1. Обзор Архитектуры Бэкенда

### 1.1. Версии и Стек

| Компонент | Версия | Источник |
|-----------|--------|----------|
| **Mayan EDMS** | 4.3 (s4.3) | Базовый образ `mayanedms/mayanedms:s4.3` |
| **Python** | 3.9 | Базовый образ Mayan |
| **Django** | 3.2.14 | Установлен в requirements |
| **Django REST Framework** | (встроен в Mayan) | Стандартная версия Mayan 4.3 |
| **Celery** | (встроен в Mayan) | Для асинхронных задач |
| **PostgreSQL** | 12.10-alpine | Docker-контейнер |
| **Redis** | 6.2-alpine | Docker-контейнер (кеш, Celery results, locks) |
| **RabbitMQ** | (через docker-compose) | Celery broker |

### 1.2. Разделение INSTALLED_APPS

#### Vendor Core (Mayan EDMS)
Все приложения из базового Mayan EDMS 4.3, включая:
- `mayan.apps.documents` — управление документами
- `mayan.apps.metadata` — метаданные
- `mayan.apps.ocr` — OCR
- `mayan.apps.acls` — Access Control Lists
- `mayan.apps.rest_api` — REST API
- `mayan.apps.authentication` — аутентификация
- `mayan.apps.permissions` — система прав
- `mayan.apps.document_states` — workflow
- `mayan.apps.tags` — теги
- `mayan.apps.cabinets` — папки/кабинеты
- И другие стандартные приложения Mayan...

#### Custom Apps (Кастомные расширения)

**Способ установки:**
- **Явно в INSTALLED_APPS** (`mayan/settings/base.py`): устанавливаются при старте Django
- **Через `ready()` метод** (`apps.py`): устанавливаются динамически при инициализации приложения

**Список кастомных приложений:**

1. **`mayan.apps.headless_api`** — BFF-адаптер для SPA
   - **Способ установки:** Явно в INSTALLED_APPS (строка 101)
   - **Назначение:** Предоставляет SPA-friendly REST endpoints

2. **`mayan.apps.dam`** — Digital Asset Management (AI-анализ, метаданные)
   - **Способ установки:** Через `ready()` метод (`apps.py:46-47`)
   - **Назначение:** AI-анализ документов, извлечение метаданных
   - **Особенность:** Автоматически добавляется в INSTALLED_APPS при инициализации

3. **`mayan.apps.distribution`** — Распространение контента (публикации, share links)
   - **Способ установки:** Через `ready()` метод (`apps.py:34-35`)
   - **Назначение:** Управление публикациями, share links, rendition'ами
   - **Особенность:** Автоматически добавляется в INSTALLED_APPS при инициализации

4. **`mayan.apps.converter_pipeline_extension`** — Расширение конвертера (RAW, DNG)
   - **Способ установки:** Через `ready()` метод (`apps.py:27-28`)
   - **Назначение:** Расширенная система конвертеров для RAW/DNG файлов
   - **Особенность:** Автоматически добавляется в INSTALLED_APPS при инициализации

5. **`mayan.apps.storage`** — Кастомные storage backends (S3, Яндекс.Диск)
   - **Способ установки:** Явно в INSTALLED_APPS (строка 103)
   - **Назначение:** Кастомные storage backends для файлов

6. **`mayan.apps.user_management`** — Расширенное управление пользователями
   - **Способ установки:** Явно в INSTALLED_APPS (строка 79)
   - **Назначение:** Расширенное управление пользователями и группами

7. **`mayan.apps.autoadmin`** — Автоматическая администрирование
   - **Способ установки:** Явно в INSTALLED_APPS (строка 82)
   - **Назначение:** Автоматическая настройка администратора

8. **`mayan.apps.image_editor`** — Редактор изображений (server-side)
   - **Способ установки:** Не установлен в INSTALLED_APPS, используется через интеграцию с `headless_api`
   - **Назначение:** Server-side редактор изображений
   - **Особенность:** Функционал экспонируется через `headless_api` endpoints (`/api/v4/headless/image-editor/...`)

9. **`mayan.apps.analytics`** — Корпоративная аналитика (Asset Bank, Campaign Performance, Search Analytics)
   - **Способ установки:** Явно в INSTALLED_APPS (строка 107)
   - **Назначение:** Сбор и агрегация аналитических данных (события активов, кампании, поисковые сессии, workflow-аналитика, CDN-метрики)
   - **Особенность:** Интегрируется через `headless_api` endpoints (`/api/v4/headless/analytics/...`), имеет middleware для отслеживания использования функций

10. **`mayan.apps.notifications`** — Центр уведомлений (Notification Center)
    - **Способ установки:** Явно в INSTALLED_APPS (строка 106)
    - **Назначение:** Расширенная система уведомлений с шаблонами, настройками пользователей, email-рассылкой и WebSocket-доставкой
    - **Особенность:** Интегрируется через `headless_api` endpoints (`/api/v4/headless/notifications/...`), расширяет стандартную систему уведомлений Mayan

### 1.3. Конфигурация Инфраструктуры

#### Celery
- **Broker:** RabbitMQ (`amqp://mayan:mayanrabbitpass@rabbitmq:5672/mayan`)
- **Result Backend:** Redis (`redis://:mayanredispassword@redis:6379/1`)
- **Lock Manager:** Redis (`redis://:mayanredispassword@redis:6379/2`)
- **Queues:**
  - `tools` — AI-анализ (`mayan.apps.dam.tasks.analyze_document_with_ai`)
  - `converter` — Конвертация файлов (`mayan.apps.distribution.tasks.generate_rendition_task`, `mayan.apps.headless_api.tasks.process_editor_version_task`)
  - `distribution` — Распространение (transient queue)
  - `documents` — Агрегация аналитики (`mayan.apps.analytics.tasks.aggregate_daily_metrics`, `aggregate_search_daily_metrics`, `aggregate_user_daily_metrics`, `calculate_cdn_daily_costs`, `generate_analytics_alerts`, `cleanup_old_events`, `aggregate_campaign_engagement_daily_metrics`)
  - `notifications` — Доставка уведомлений (`mayan.apps.notifications.tasks.send_notification_async`, `send_notification_email`, `send_websocket_notification`, `cleanup_old_notifications`)

#### База Данных
- **Engine:** `django.db.backends.postgresql`
- **Database:** `mayan` (по умолчанию)
- **Host:** `postgresql` (Docker service)
- **User:** `mayan`
- **Password:** `mayandbpass` (по умолчанию, через env)

#### Кеширование
- **Backend:** `django_redis.cache.RedisCache` (Redis через django-redis)
- **Location:** `redis://:{password}@{host}:{port}/{db}` (DB 0 для cache, настраивается через env: `MAYAN_REDIS_HOST`, `MAYAN_REDIS_PORT`, `MAYAN_REDIS_PASSWORD`, `MAYAN_REDIS_DB_CACHE`)
- **Timeout:** 300 секунд
- **KEY_PREFIX:** `mayan_v4` (для версионирования ключей)
- **Connection Pool:** Enterprise настройки (max_connections=100, retry_on_timeout, socket timeouts)
- **Разделение баз данных:** DB 0 (Cache), DB 1 (Celery Result Backend), DB 2 (Lock Manager)

### 1.4. Механизм Аутентификации

**Активные методы:**
1. **Token Authentication** (`rest_framework.authentication.TokenAuthentication`)
   - DRF Token-based auth
   - Endpoint: `POST /api/v4/auth/token/obtain/`
   - Токен передается в заголовке: `Authorization: Token <token>`

2. **Session Authentication** (`rest_framework.authentication.SessionAuthentication`)
   - Django sessions
   - Используется для браузерных запросов

**Не используется:**
- OAuth2 (не настроен)
- JWT (не установлен)
- Knox (не установлен)

**Middleware:**
- `stronghold.middleware.LoginRequiredMiddleware` — защита URL (требует аутентификации для всех путей, кроме исключений)

---

## 2. Карта Кастомных Модулей (Custom Apps Map)

### 2.1. `mayan.apps.headless_api` — BFF Adapter

**Назначение:** Предоставляет SPA-friendly REST endpoints для функционала, не экспонируемого стандартным Mayan API.

**Архитектурный паттерн:** Sidecar App — не модифицирует core Mayan, добавляет новые endpoints.

#### Ключевые Модели
**Нет собственных моделей** — использует модели из core Mayan (`Document`, `User`, `Action`, `DocumentType`).

#### API Эндпоинты

| URL | Метод | View | Описание |
|-----|-------|------|----------|
| `/api/v4/headless/ping/` | GET | Lambda | Health check |
| `/api/v4/headless/auth/me/` | GET | `HeadlessAuthMeView` | Расширенная информация о текущем пользователе |
| `/api/v4/headless/password/change/` | POST | `HeadlessPasswordChangeView` | Смена пароля |
| `/api/v4/headless/profile/` | GET | `HeadlessProfileView` | Профиль пользователя |
| `/api/v4/headless/config/document_types/` | GET | `HeadlessDocumentTypeConfigView` | Список типов документов |
| `/api/v4/headless/config/document_types/{id}/` | GET | `HeadlessDocumentTypeConfigView` | Детальная конфигурация типа |
| `/api/v4/headless/activity/feed/` | GET | `HeadlessActivityFeedView` | Персонализированная лента активности |
| `/api/v4/headless/dashboard/activity/` | GET | `DashboardActivityView` | Активность для дашборда |
| `/api/v4/headless/dashboard/stats/` | GET | `HeadlessDashboardStatsView` | Статистика дашборда |
| `/api/v4/headless/favorites/` | GET | `HeadlessFavoriteListView` | Список избранного |
| `/api/v4/headless/favorites/{id}/toggle/` | POST | `HeadlessFavoriteToggleView` | Переключение избранного |
| `/api/v4/headless/documents/my_uploads/` | GET | `HeadlessMyUploadsView` | Мои загрузки |
| `/api/v4/headless/documents/{id}/versions/new_from_edit/` | POST | `HeadlessEditView` | Создание версии из отредактированного изображения (асинхронно, возвращает 202 Accepted + task_id) |
| `/api/v4/headless/documents/{id}/convert/` | POST | `HeadlessDocumentConvertView` | Конвертация документа |
| `/api/v4/headless/tasks/{task_id}/status/` | GET | `HeadlessTaskStatusView` | Статус асинхронной задачи (поллинг) |
| `/api/v4/headless/users/` | GET, POST | `HeadlessUsersListCreateView` | Список/создание пользователей |
| `/api/v4/headless/users/{id}/` | GET, PATCH, DELETE | `HeadlessUsersDetailView` | Детали пользователя |
| `/api/v4/headless/storage/s3/config/` | GET | `HeadlessS3ConfigView` | Конфигурация S3 |
| `/api/v4/headless/storage/s3/stats/` | GET | `HeadlessS3StatsView` | Статистика S3 |
| `/api/v4/headless/image-editor/sessions/` | POST | `HeadlessImageEditorSessionCreateView` | Создание сессии редактора |
| `/api/v4/headless/image-editor/sessions/{id}/` | GET, PATCH | `HeadlessImageEditorSessionDetailView` | Детали сессии |
| `/api/v4/headless/image-editor/sessions/{id}/preview/` | GET | `HeadlessImageEditorPreviewView` | Превью отредактированного изображения |
| `/api/v4/headless/image-editor/sessions/{id}/commit/` | POST | `HeadlessImageEditorCommitView` | Коммит изменений |
| `/api/v4/headless/image-editor/watermarks/` | GET | `HeadlessImageEditorWatermarkListView` | Список водяных знаков |

#### Фоновые Задачи

**Celery tasks:**

##### `process_editor_version_task` (`tasks.py:47`)
- **Queue:** `converter`
- **Retries:** 3 (max_retries=3, default_retry_delay=60)
- **Триггер:** 
  - API endpoint `/api/v4/headless/documents/{id}/versions/new_from_edit/` (`HeadlessEditView`)
  - API endpoint `/api/v4/headless/image-editor/sessions/{id}/commit/` (`HeadlessImageEditorCommitView`)
- **Логика:**
  1. Получение временного файла из `SharedUploadedFile` по `shared_uploaded_file_id`
  2. Получение документа по `document_id`
  3. Конвертация изображения (если указан `target_format`) через Pillow
  4. Создание новой версии документа через `document.file_new()` с указанным `action_id`
  5. Автоматический запуск постобработки (OCR, AI-анализ) через сигналы Mayan EDMS
  6. Очистка временного файла из `SharedUploadedFile`
  7. Возврат результата с `document_id`, `file_id`, `version_id`
- **Особенности:**
  - Использует `SharedUploadedFile` для временного хранения файлов перед обработкой
  - Поддерживает retry при операционных ошибках БД (`OperationalError`)
  - Автоматическая очистка временных файлов при ошибках
  - TTFB < 200ms независимо от размера файла (асинхронная обработка)

#### Использование Core Mayan
- **Модели:** `Document`, `User`, `Action`, `DocumentType`, `DocumentTypeMetadataType`
- **ACL:** `AccessControlList.objects.restrict_queryset()`, `AccessControlList.objects.check_access()`
- **Permissions:** `permission_document_view`, `permission_document_version_create`
- **Оптимизации:** `select_related()`, `prefetch_related()` используются в views

**Примеры ACL-проверок:**
```python
# version_views.py:54
queryset = AccessControlList.objects.restrict_queryset(
    permission=permission_document_version_create,
    queryset=Document.valid.all(),
    user=request.user
)
```

---

### 2.2. `mayan.apps.dam` — Digital Asset Management

**Назначение:** AI-анализ документов, извлечение метаданных, управление DAM-специфичными данными.

#### Ключевые Модели

##### `DocumentAIAnalysis` (`models.py:8`)
**Связь:** `OneToOneField(Document, related_name='ai_analysis')`

**Поля:**
- `document` — связь с Document (OneToOne)
- `copyright_notice` — TextField (авторские права)
- `usage_rights` — TextField (права использования)
- `rights_expiry` — DateField (истечение прав)
- `categories` — JSONField (категории)
- `language` — CharField (язык, BCP-47)
- `people` — JSONField (обнаруженные люди)
- `locations` — JSONField (обнаруженные локации)
- `ai_description` — TextField (AI-описание)
- `ai_tags` — JSONField (AI-теги)
- `dominant_colors` — JSONField (доминирующие цвета)
- `alt_text` — CharField (alt-текст для accessibility)
- `ai_provider` — CharField (провайдер AI)
- `analysis_status` — CharField (pending/processing/completed/failed)
- `current_step` — CharField (текущий шаг обработки)
- `progress` — PositiveSmallIntegerField (0-100)
- `error_message` — TextField (ошибка)
- `task_id` — CharField (Celery task ID)
- `created`, `updated`, `analysis_completed` — DateTimeField

##### `DAMMetadataPreset` (`models.py:185`)
**Поля:**
- `name` — CharField (уникальное имя)
- `description` — TextField
- `ai_providers` — JSONField (список провайдеров)
- `extract_description`, `extract_tags`, `extract_colors`, `extract_alt_text` — BooleanField
- `supported_mime_types` — JSONField
- `is_enabled` — BooleanField
- `created` — DateTimeField

##### `YandexDiskImportRecord` (миграция 0003)
**Поля:**
- `document` — ForeignKey(Document)
- `yandex_disk_path` — CharField
- `imported_at` — DateTimeField

#### API Эндпоинты

| URL | Метод | View | Описание |
|-----|-------|------|----------|
| `/api/v4/dam/ai-analysis/` | GET, POST | `DocumentAIAnalysisViewSet` | Список/создание AI-анализа |
| `/api/v4/dam/ai-analysis/{id}/` | GET, PATCH, DELETE | `DocumentAIAnalysisViewSet` | Детали AI-анализа |
| `/api/v4/dam/ai-analysis/analyze/` | POST | `DocumentAIAnalysisViewSet.analyze` | Запуск анализа для документа (с проверкой размера файла) |
| `/api/v4/dam/ai-analysis/bulk_analyze/` | POST | `DocumentAIAnalysisViewSet.bulk_analyze` | Массовый анализ |
| `/api/v4/dam/metadata-presets/` | GET, POST | `DAMMetadataPresetViewSet` | Список/создание пресетов |
| `/api/v4/dam/metadata-presets/{id}/` | GET, PATCH, DELETE | `DAMMetadataPresetViewSet` | Детали пресета |
| `/api/v4/dam/analysis-status/` | GET | `AIAnalysisStatusView` | Статус анализа |
| `/api/v4/dam/document-detail/{id}/` | GET | `DAMDocumentDetailView` | Детали документа с AI-данными |
| `/api/v4/dam/documents/` | GET | `DAMDocumentListView` | Список документов (оптимизированный) |
| `/api/v4/dam/dashboard-stats/` | GET | `DAMDashboardStatsView` | Статистика дашборда |
| `/api/v4/dam/documents/{id}/processing_status/` | GET | `DocumentProcessingStatusView` | Статус обработки (progress) |
| `/api/v4/dam/documents/{id}/ocr/extract/` | GET | `DocumentOCRExtractView` | Извлечение OCR-текста |

#### Фоновые Задачи

##### `analyze_document_with_ai` (`tasks.py:178`)
- **Queue:** `tools`
- **Retries:** 3 (max_retries=3, default_retry_delay=60)
- **Триггер:** 
  - Автоматически через signal `post_save` на `DocumentFile` (`signals.py:148`)
  - Вручную через API endpoint `/api/v4/dam/ai-analysis/analyze/`
- **Логика:**
  1. Проверка `DAM_AI_ANALYSIS_ENABLED`
  2. Получение документа и latest file
  3. **Проверка размера файла** (дифференцированные лимиты по MIME типу через `utils.get_max_file_size_for_mime_type()`)
  4. Проверка доступности файла в storage (S3 race condition fix)
  5. Создание/обновление `DocumentAIAnalysis` со статусом `processing`
   6. Попытка анализа через провайдеры (fallback sequence из `DAM_AI_PROVIDER_SEQUENCE`: qwenlocal → gigachat → openai → claude → gemini → yandexgpt → kieai)
   7. Обновление прогресса (`progress`, `current_step`) на каждом этапе
   8. Сохранение результатов в `DocumentAIAnalysis` (ai_description, ai_tags, categories, people, locations, dominant_colors, alt_text, etc.)
   9. Обновление статуса на `completed` или `failed`
   10. Интеграция результатов с системой метаданных Mayan через `update_document_metadata_from_ai()` (`tasks.py:358, 986`):
       - Теги (ai_tags, people, locations, categories) → Mayan `Tag` через `tag.attach_to(document)` (`tasks.py:1027-1040`)
       - Текстовые поля (ai_description, alt_text, copyright_notice) → `MetadataType` через `DocumentMetadata` (`tasks.py:1042-1080`)
       - Принцип "Человек > AI": перезапись только если значение пустое (кроме `force_reanalyze=True`)
   11. Реиндексация документа через `reindex_document_assets()` (`tasks.py:359, 1157`) для обновления поискового индекса с новыми AI-данными

##### `bulk_analyze_documents` (`tasks.py`)
- **Queue:** `tools`
- **Триггер:** API endpoint `/api/v4/dam/ai-analysis/bulk_analyze/`
- **Логика:** Массовый запуск `analyze_document_with_ai` для списка документов

##### `import_yandex_disk` (`tasks.py`)
- **Queue:** `tools`
- **Триггер:** Management command или API
- **Логика:** Импорт файлов из Яндекс.Диск

#### Утилиты
- **`mayan.apps.dam.utils`** (`utils.py`) — утилиты для работы с лимитами размеров файлов и тегами:
  - `get_max_file_size_for_mime_type(mime_type: str) -> int` — определение лимита по MIME типу (дифференцированные лимиты для изображений, RAW, PDF, документов, видео, аудио)
  - `format_file_size(size_bytes: int) -> str` — форматирование размера для сообщений (B, KB, MB)
  - `get_or_create_tag(label: str, color: Optional[str] = None) -> Optional[Tag]` — создание/получение тега для интеграции AI-результатов (использует `DAM_AI_TAG_DEFAULT_COLOR` из settings)
- **`mayan.apps.dam.cache_utils`** (`cache_utils.py`) — утилиты для кеширования подсчета документов пресета:
  - `get_preset_count_cache_key(preset_id, user_id=None)` — генерация ключа кеша (user-specific или global)
  - `get_preset_count_cache_ttl()` — получение TTL из настроек (`DAM_PRESET_DOCUMENT_COUNT_CACHE_TTL`, по умолчанию 600 секунд)
  - `invalidate_preset_count_cache(preset_id, user_id=None)` — инвалидация кеша (вызывается через сигналы при изменении пресета)

#### Использование Core Mayan
- **Модели:** `Document`, `DocumentFile`, `DocumentType`, `Tag`, `MetadataType`, `DocumentMetadata`
- **Signals:** 
  - `post_save` на `DocumentFile` (`signals.py:148`) — автоматический триггер AI-анализа с проверкой размера файла и MIME типа
  - `post_save`/`post_delete` на `DAMMetadataPreset` (`signals.py:245, 251`) — инвалидация кеша подсчета документов
- **ACL:** 
  - `AccessControlList.objects.check_access()` для проверки прав на документ
  - `AccessControlList.objects.restrict_queryset()` для подсчета документов пресета с учетом прав доступа (`serializers.py:232`)
- **Permissions:** `permission_document_view`, `permission_ai_analysis_create`
- **Tags:** Интеграция AI-тегов с системой тегов Mayan через `Tag.attach_to(document)` (`tasks.py:1027-1040`):
  - `ai_tags` → Tag (каждый тег создается/получается через `get_or_create_tag()`)
  - `people`, `locations`, `categories` → Tag (с префиксами для группировки)
- **Metadata:** Интеграция AI-описаний с системой метаданных Mayan через `DocumentMetadata` (`tasks.py:1042-1080`):
  - `ai_description` → MetadataType (настраивается через `DAM_AI_METADATA_MAPPING`)
  - `alt_text`, `copyright_notice` → MetadataType
  - Принцип "Человек > AI": перезапись только если значение пустое (кроме `force_reanalyze=True`)
- **Search:** Интеграция с `mayan.apps.dynamic_search` для индексации AI-тегов через `reindex_document_assets()` (`tasks.py:1157`)
- **OCR:** Использование `mayan.apps.ocr.models.DocumentVersionPageOCRContent` для извлечения текста

**Примеры сигналов:**
```python
# signals.py:148
@receiver(post_save, sender=DocumentFile)
def trigger_ai_analysis(sender, instance, created, **kwargs):
    # Автоматический запуск AI-анализа при создании нового файла
    # Проверка через should_trigger_analysis() включает: MIME тип, размер файла, существующий анализ
    if created and should_trigger_analysis(instance, instance.document):
        analyze_document_with_ai.apply_async(
            args=[instance.document.id], 
            countdown=DAM_AI_ANALYSIS_DELAY_SECONDS
        )
```

---

### 2.3. `mayan.apps.distribution` — Distribution & Sharing

**Назначение:** Управление публикациями, share links, распространением контента, генерацией rendition'ов.

#### Ключевые Модели

##### `Recipient` (`models.py:13`)
**Поля:**
- `email` — EmailField (уникальный)
- `name` — CharField
- `organization` — CharField
- `locale` — CharField (язык)
- `created`, `modified` — DateTimeField

##### `RecipientList` (`models.py:48`)
**Поля:**
- `name` — CharField
- `recipients` — ManyToManyField(Recipient)
- `internal_users` — ManyToManyField(User)
- `owner` — ForeignKey(User)
- `created`, `modified` — DateTimeField

##### `RenditionPreset` (`models.py:86`)
**Поля:**
- `resource_type` — CharField (image/video/document)
- `format` — CharField (jpeg/png/webp/tiff/pdf/mp4)
- `width`, `height` — IntegerField (опционально)
- `quality` — IntegerField (0-100)
- `crop` — BooleanField
- `dpi_x`, `dpi_y` — IntegerField
- `filters` — JSONField (список фильтров)
- `watermark` — JSONField (настройки водяного знака)
- `adjust_brightness`, `adjust_contrast`, `adjust_color`, `adjust_sharpness` — FloatField
- `recipient` — ForeignKey(Recipient)
- `name` — CharField (уникальное)
- `description` — TextField
- `created`, `modified` — DateTimeField

##### `Publication` (`models.py`)
**Поля:**
- `title` — CharField
- `description` — TextField
- `status` — CharField (draft/published/scheduled)
- `created_date`, `updated_date`, `published_date` — DateTimeField
- `created_by` — ForeignKey(User)
- `assets` — ManyToManyField(Document) через `PublicationItem`

##### `ShareLink` (`models.py`)
**Поля:**
- `token` — CharField (уникальный UUID)
- `rendition` — ForeignKey(GeneratedRendition)
- `expires_at` — DateTimeField (опционально)
- `max_downloads` — IntegerField (опционально)
- `downloads_count` — IntegerField
- `created`, `modified` — DateTimeField

##### `GeneratedRendition` (`models.py`)
**Поля:**
- `publication_item` — ForeignKey(PublicationItem)
- `preset` — ForeignKey(RenditionPreset)
- `file` — FileField (хранится в S3 через DefinedStorageLazy)
- `status` — CharField (pending/processing/completed/failed)
- `file_size` — BigIntegerField
- `checksum` — CharField
- `error_message` — TextField
- `created`, `modified` — DateTimeField

#### API Эндпоинты

| URL | Метод | View | Описание |
|-----|-------|------|----------|
| `/api/v4/distribution/recipients/` | GET, POST | `APIRecipientListView` | Список/создание получателей |
| `/api/v4/distribution/recipients/{id}/` | GET, PATCH, DELETE | `APIRecipientDetailView` | Детали получателя |
| `/api/v4/distribution/recipient_lists/` | GET, POST | `APIRecipientListListView` | Список/создание списков получателей |
| `/api/v4/distribution/recipient_lists/{id}/` | GET, PATCH, DELETE | `APIRecipientListDetailView` | Детали списка |
| `/api/v4/distribution/rendition_presets/` | GET, POST | `APIRenditionPresetListView` | Список/создание пресетов |
| `/api/v4/distribution/rendition_presets/{id}/` | GET, PATCH, DELETE | `APIRenditionPresetDetailView` | Детали пресета |
| `/api/v4/distribution/publications/` | GET, POST | `APIPublicationListView` | Список/создание публикаций |
| `/api/v4/distribution/publications/{id}/` | GET, PATCH, DELETE | `APIPublicationDetailView` | Детали публикации |
| `/api/v4/distribution/publications/{id}/generate_renditions/` | POST | `APIGenerateRenditionsView` | Генерация rendition'ов |
| `/api/v4/distribution/publication_items/` | GET, POST | `APIPublicationItemListView` | Список/создание элементов публикации |
| `/api/v4/distribution/publication_items/{id}/` | GET, PATCH, DELETE | `APIPublicationItemDetailView` | Детали элемента |
| `/api/v4/distribution/share_links/` | GET, POST | `APIShareLinkListView` | Список/создание share links |
| `/api/v4/distribution/share_links/create_simple/` | POST | `create_share_link_simple` | Упрощенное создание share link |
| `/api/v4/distribution/share_links/{id}/` | GET, PATCH, DELETE | `APIShareLinkDetailView` | Детали share link |
| `/api/v4/distribution/campaigns/` | GET, POST | `APIDistributionCampaignListView` | Список/создание кампаний |
| `/api/v4/distribution/campaigns/{id}/` | GET, PATCH, DELETE | `APIDistributionCampaignDetailView` | Детали кампании |
| `/api/v4/distribution/generated_renditions/` | GET | `APIGeneratedRenditionListView` | Список сгенерированных rendition'ов |
| `/api/v4/distribution/generated_renditions/{id}/` | GET | `APIGeneratedRenditionDetailView` | Детали rendition |
| `/api/v4/distribution/access_logs/` | GET | `APIAccessLogListView` | Логи доступа |

#### Фоновые Задачи

##### `generate_rendition_task` (`tasks.py:20`)
- **Queue:** `converter` (worker_a)
- **Триггер:** При создании `GeneratedRendition` через API
- **Логика:**
  1. Получение `GeneratedRendition`, `RenditionPreset`, `DocumentFile`
  2. Конвертация файла через `converter_pipeline_extension` с параметрами пресета
  3. Применение фильтров (grayscale, invert, autocontrast, etc.)
  4. Применение водяных знаков (если настроено)
  5. Сохранение результата в `GeneratedRendition.file`
  6. Обновление статуса на `completed` или `failed`

#### Использование Core Mayan
- **Модели:** `Document`, `DocumentFile`
- **Storage:** `mayan.apps.storage.classes.DefinedStorageLazy` для S3-хранилища rendition'ов
- **Converter:** `mayan.apps.converter_pipeline_extension` для конвертации файлов
- **ACL:** Проверка прав на документы перед созданием share links

---

### 2.4. `mayan.apps.image_editor` — Image Editor

**Назначение:** Server-side редактор изображений с поддержкой сессий, трансформаций, водяных знаков.

**Особенность:** Не установлен в INSTALLED_APPS, функционал экспонируется через `headless_api` endpoints.

#### Ключевые Модели
- **`ImageEditSession`** (`mayan/apps/image_editor/models.py`) — модель сессии редактирования изображения
  - Связь с `Document` через ForeignKey
  - Хранение состояния редактирования (трансформации, фильтры, водяные знаки)
  - Статус сессии (draft, processing, completed, failed)

#### API Эндпоинты
**Интегрированы в headless_api через `HeadlessImageEditor*View`:**

| URL | Метод | View | Описание |
|-----|-------|------|----------|
| `/api/v4/headless/image-editor/sessions/` | POST | `HeadlessImageEditorSessionCreateView` | Создание сессии редактора |
| `/api/v4/headless/image-editor/sessions/{id}/` | GET, PATCH | `HeadlessImageEditorSessionDetailView` | Управление сессией (получение/обновление состояния) |
| `/api/v4/headless/image-editor/sessions/{id}/preview/` | GET | `HeadlessImageEditorPreviewView` | Превью отредактированного изображения |
| `/api/v4/headless/image-editor/sessions/{id}/commit/` | POST | `HeadlessImageEditorCommitView` | Коммит изменений (асинхронно, возвращает 202 Accepted + task_id) |
| `/api/v4/headless/image-editor/watermarks/` | GET | `HeadlessImageEditorWatermarkListView` | Список доступных водяных знаков |

#### Фоновые Задачи
**Использует Celery tasks из `headless_api`:**
- `process_editor_version_task` (`headless_api/tasks.py`) — асинхронная обработка изображений из редактора (очередь `converter`)
  - Вызывается из `HeadlessImageEditorCommitView` при коммите изменений
  - Поддерживает конвертацию форматов, применение фильтров, водяных знаков
  - Создает новую версию документа через `document.file_new()`

---

### 2.5. `mayan.apps.analytics` — Corporate Analytics

**Назначение:** Корпоративная аналитика для DAM-системы: сбор событий активов, метрики кампаний, аналитика поиска, workflow-аналитика, CDN-метрики, отслеживание использования функций.

#### Ключевые Модели

##### `AssetEvent` (`models.py:9`)
**Связь:** `ForeignKey(Document, related_name='analytics_events')`

**Поля:**
- `document` — ForeignKey(Document)
- `event_type` — CharField (download/view/share/upload/deliver)
- `user` — ForeignKey(User, null=True)
- `user_department` — CharField
- `channel` — CharField (dam_interface/public_link/portal/api)
- `intended_use` — CharField (email/social/print/web)
- `bandwidth_bytes` — BigIntegerField
- `latency_seconds` — IntegerField
- `timestamp` — DateTimeField (auto_now_add, indexed)
- `metadata` — JSONField

**Индексы:** `(document, -timestamp)`, `(event_type, timestamp)`, `(user, timestamp)`

##### `AssetDailyMetrics` (`models.py:86`)
**Связь:** `ForeignKey(Document, related_name='analytics_daily_metrics')`

**Поля:**
- `document` — ForeignKey(Document)
- `date` — DateField (indexed)
- `downloads`, `views`, `shares` — PositiveIntegerField
- `cdn_bandwidth_gb` — FloatField
- `performance_score` — FloatField (0-10, вычисляется через `calculate_performance_score()`)
- `top_channel` — CharField

**Unique together:** `(document, date)`

##### `Campaign` (`models.py:142`)
**Поля:**
- `id` — UUIDField (primary key)
- `label` — CharField
- `description` — TextField
- `status` — CharField (draft/active/completed/archived)
- `start_date`, `end_date` — DateField
- `created_by` — ForeignKey(User)
- `cost_amount`, `revenue_amount` — DecimalField (ROI inputs)
- `currency` — CharField (default: 'RUB')
- `created_at`, `updated_at` — DateTimeField

**Методы:** `get_roi()` — возвращает ROI ratio (revenue / cost)

##### `CampaignAsset` (`models.py:211`)
**Связь:** Many-to-Many между Campaign и Document

**Поля:**
- `campaign` — ForeignKey(Campaign)
- `document` — ForeignKey(Document)
- `sequence` — PositiveIntegerField
- `added_at` — DateTimeField

**Unique together:** `(campaign, document)`

##### `CampaignDailyMetrics` (`models.py:243`)
**Связь:** `ForeignKey(Campaign, related_name='daily_metrics')`

**Поля:**
- `campaign` — ForeignKey(Campaign)
- `date` — DateField
- `views`, `downloads`, `shares` — PositiveIntegerField
- `roi` — FloatField
- `top_document` — ForeignKey(Document, null=True)
- `channel_breakdown` — JSONField
- `avg_engagement_minutes` — FloatField

##### `UserSession` (`models.py:283`)
**Связь:** `ForeignKey(User, related_name='analytics_sessions')`

**Поля:**
- `user` — ForeignKey(User)
- `session_key` — CharField
- `login_timestamp`, `logout_timestamp` — DateTimeField
- `session_duration_seconds` — IntegerField
- `geo_country`, `geo_city` — CharField
- `ip_address` — GenericIPAddressField (анонимизированный)
- `user_agent` — TextField

##### `UserDailyMetrics` (`models.py:315`)
**Связь:** `ForeignKey(User, related_name='analytics_daily_metrics')`

**Поля:**
- `user` — ForeignKey(User)
- `date` — DateField
- `logins`, `searches`, `downloads` — PositiveIntegerField
- `search_success_rate` — FloatField
- `avg_search_to_find_minutes` — IntegerField
- `user_department` — CharField

**Unique together:** `(user, date)`

##### `SearchQuery` (`models.py:524`)
**Связь:** `ForeignKey(User, related_name='analytics_search_queries', null=True)`

**Поля:**
- `user` — ForeignKey(User, null=True)
- `query_text` — CharField (indexed)
- `search_type` — CharField (keyword/filter/faceted/ai)
- `results_count` — IntegerField
- `response_time_ms` — IntegerField
- `filters_applied` — JSONField
- `search_session_id` — UUIDField
- `was_clicked_result_document_id` — IntegerField
- `click_position` — IntegerField
- `time_to_click_seconds` — IntegerField
- `was_downloaded` — BooleanField
- `time_to_download_seconds` — IntegerField
- `timestamp` — DateTimeField (auto_now_add, indexed)
- `user_department` — CharField

##### `SearchSession` (`models.py:346`)
**Связь:** `ForeignKey(User, related_name='analytics_search_sessions')`

**Поля:**
- `id` — UUIDField (primary key)
- `user` — ForeignKey(User)
- `started_at`, `ended_at` — DateTimeField
- `first_search_query` — ForeignKey(SearchQuery, null=True)
- `last_download_event` — ForeignKey(AssetEvent, null=True)
- `time_to_find_seconds` — IntegerField (Search-to-Find Time)

##### `ApprovalWorkflowEvent` (`models.py:396`)
**Связь:** `ForeignKey(Document, related_name='analytics_approval_events')`

**Поля:**
- `document` — ForeignKey(Document)
- `workflow_instance` — ForeignKey(WorkflowInstance)
- `submitter`, `approver` — ForeignKey(User, null=True)
- `submitted_at`, `approved_at`, `rejected_at` — DateTimeField
- `approval_time_days` — FloatField
- `status` — CharField (pending/approved/rejected)
- `rejection_reason` — TextField
- `attempt_number` — PositiveIntegerField
- `created_at` — DateTimeField

##### `AnalyticsAlert` (`models.py:466`)
**Связь:** `ForeignKey(Document, related_name='analytics_alerts', null=True)`, `ForeignKey(Campaign, related_name='analytics_alerts', null=True)`

**Поля:**
- `alert_type` — CharField (underperforming_asset/no_downloads/approval_rejected/storage_limit)
- `severity` — CharField (critical/warning/info)
- `title`, `message` — CharField/TextField
- `document`, `campaign` — ForeignKey (optional)
- `created_at`, `resolved_at` — DateTimeField
- `metadata` — JSONField

##### `SearchDailyMetrics` (`models.py:582`)
**Поля:**
- `date` — DateField (primary key)
- `total_searches`, `successful_searches`, `null_searches` — PositiveIntegerField
- `ctr` — FloatField (Click-Through Rate)
- `avg_response_time_ms` — IntegerField
- `top_queries`, `null_queries` — JSONField (список топ-запросов)

##### `CDNRate` (`models.py:603`)
**Поля:**
- `region` — CharField
- `channel` — CharField
- `cost_per_gb_usd` — DecimalField
- `effective_from`, `effective_to` — DateField

**Unique together:** `(region, channel, effective_from)`

##### `CDNDailyCost` (`models.py:627`)
**Поля:**
- `date` — DateField
- `region`, `channel` — CharField
- `bandwidth_gb` — FloatField
- `cost_usd` — DecimalField

**Unique together:** `(date, region, channel)`

##### `FeatureUsage` (`models.py:650`)
**Связь:** `ForeignKey(User, related_name='analytics_feature_usage', null=True)`

**Поля:**
- `user` — ForeignKey(User, null=True)
- `feature_name` — CharField (indexed)
- `timestamp` — DateTimeField (auto_now_add, indexed)
- `was_successful` — BooleanField
- `metadata` — JSONField

##### `CampaignEngagementEvent` (`models.py:679`)
**Связь:** `ForeignKey(Campaign, related_name='engagement_events')`

**Поля:**
- `campaign` — ForeignKey(Campaign)
- `user` — ForeignKey(User, null=True)
- `started_at`, `ended_at` — DateTimeField
- `duration_seconds` — PositiveIntegerField
- `metadata` — JSONField

##### `DistributionEvent` (`models.py:714`)
**Связь:** `ForeignKey(Document, related_name='analytics_distribution_events', null=True)`, `ForeignKey(Campaign, related_name='analytics_distribution_events', null=True)`

**Поля:**
- `channel` — CharField (indexed)
- `event_type` — CharField (synced/converted/published/delivered/error)
- `status` — CharField (ok/warning/error/syncing)
- `document`, `campaign` — ForeignKey (optional)
- `views`, `clicks`, `conversions` — PositiveIntegerField
- `revenue_amount` — DecimalField
- `currency` — CharField
- `bandwidth_bytes` — BigIntegerField
- `latency_ms` — IntegerField
- `external_id` — CharField (indexed)
- `occurred_at` — DateTimeField (indexed)
- `metadata` — JSONField

#### API Эндпоинты
**Интегрированы в headless_api через `*AnalyticsViewSet`:**

##### Asset Bank (Phase 1 / Level 1)
| URL | Метод | View | Описание |
|-----|-------|------|----------|
| `/api/v4/headless/analytics/dashboard/assets/top-metrics/` | GET | `AssetBankViewSet.top_metrics` | Топ-метрики активов (total assets, storage used, downloads/views за 30 дней) |
| `/api/v4/headless/analytics/dashboard/assets/distribution/` | GET | `AssetBankViewSet.distribution` | Распределение активов по типам документов |
| `/api/v4/headless/analytics/dashboard/assets/distribution-trend/` | GET | `AssetBankViewSet.distribution_trend` | Тренд распределения активов по времени |
| `/api/v4/headless/analytics/dashboard/assets/most-downloaded/` | GET | `AssetBankViewSet.most_downloaded` | Самые скачиваемые активы |
| `/api/v4/headless/analytics/dashboard/assets/detail/` | GET | `AssetBankViewSet.asset_detail` | Детальная аналитика по активу (document_id) |
| `/api/v4/headless/analytics/dashboard/assets/reuse-metrics/` | GET | `AssetBankViewSet.reuse_metrics` | Метрики повторного использования активов |
| `/api/v4/headless/analytics/dashboard/assets/storage-trends/` | GET | `AssetBankViewSet.storage_trends` | Тренды использования хранилища |
| `/api/v4/headless/analytics/dashboard/assets/alerts/` | GET | `AssetBankViewSet.alerts` | Алерты по активам (underperforming, no downloads, etc.) |

##### Campaign Performance (Phase 2 / Level 2)
| URL | Метод | View | Описание |
|-----|-------|------|----------|
| `/api/v4/headless/analytics/campaigns/` | GET | `CampaignPerformanceViewSet.list` | Список кампаний |
| `/api/v4/headless/analytics/campaigns/create/` | POST | `CampaignPerformanceViewSet.create` | Создание кампании |
| `/api/v4/headless/analytics/campaigns/add-assets/` | POST | `CampaignPerformanceViewSet.add_assets` | Добавление активов в кампанию |
| `/api/v4/headless/analytics/campaigns/update-financials/` | POST | `CampaignPerformanceViewSet.update_financials` | Обновление финансовых данных (cost/revenue) |
| `/api/v4/headless/analytics/campaigns/{campaign_id}/engagement/` | POST | `CampaignPerformanceViewSet.engagement` | Отслеживание engagement события |
| `/api/v4/headless/analytics/dashboard/campaigns/` | GET | `CampaignPerformanceViewSet.dashboard` | Дашборд кампаний |
| `/api/v4/headless/analytics/dashboard/campaigns/top-assets/` | GET | `CampaignPerformanceViewSet.top_assets` | Топ-активы кампании |
| `/api/v4/headless/analytics/dashboard/campaigns/timeline/` | GET | `CampaignPerformanceViewSet.timeline` | Временная линия кампании |
| `/api/v4/headless/analytics/dashboard/campaigns/geography/` | GET | `CampaignPerformanceViewSet.geography` | Географическое распределение |

##### Search Analytics (Phase 2 / Level 4)
| URL | Метод | View | Описание |
|-----|-------|------|----------|
| `/api/v4/headless/analytics/dashboard/search/top-queries/` | GET | `SearchAnalyticsViewSet.top_queries` | Топ-поисковые запросы |
| `/api/v4/headless/analytics/dashboard/search/null-searches/` | GET | `SearchAnalyticsViewSet.null_searches` | Поисковые запросы без результатов |
| `/api/v4/headless/analytics/dashboard/search/daily/` | GET | `SearchAnalyticsViewSet.daily` | Ежедневные метрики поиска |
| `/api/v4/headless/analytics/track/search/click/` | POST | `SearchAnalyticsViewSet.click` | Отслеживание клика по результату поиска |

##### User Activity (Phase 2 / Level 3)
| URL | Метод | View | Описание |
|-----|-------|------|----------|
| `/api/v4/headless/analytics/dashboard/users/adoption-heatmap/` | GET | `UserActivityViewSet.adoption_heatmap` | Heatmap принятия функций пользователями |
| `/api/v4/headless/analytics/dashboard/users/login-patterns/` | GET | `UserActivityViewSet.login_patterns` | Паттерны входа пользователей |
| `/api/v4/headless/analytics/dashboard/users/cohorts/` | GET | `UserActivityViewSet.cohorts` | Когорты пользователей |
| `/api/v4/headless/analytics/dashboard/users/feature-adoption/` | GET | `UserActivityViewSet.feature_adoption` | Принятие функций пользователями |

##### Approval Workflow Analytics (Phase 2 / Level 3)
| URL | Метод | View | Описание |
|-----|-------|------|----------|
| `/api/v4/headless/analytics/dashboard/approvals/summary/` | GET | `ApprovalAnalyticsViewSet.summary` | Сводка по workflow-аналитике |
| `/api/v4/headless/analytics/dashboard/approvals/timeseries/` | GET | `ApprovalAnalyticsViewSet.timeseries` | Временные ряды workflow-событий |
| `/api/v4/headless/analytics/dashboard/approvals/recommendations/` | GET | `ApprovalAnalyticsViewSet.recommendations` | Рекомендации по оптимизации workflow |

##### ROI Dashboard (Phase 2)
| URL | Метод | View | Описание |
|-----|-------|------|----------|
| `/api/v4/headless/analytics/dashboard/roi/summary/` | GET | `ROIDashboardViewSet.summary` | Сводка ROI по кампаниям |

##### Distribution Analytics (Release 3)
| URL | Метод | View | Описание |
|-----|-------|------|----------|
| `/api/v4/headless/analytics/dashboard/distribution/` | GET | `DistributionAnalyticsViewSet.dashboard` | Дашборд распределения по каналам |
| `/api/v4/headless/analytics/ingest/distribution-events/` | POST | `DistributionAnalyticsViewSet.ingest` | Импорт событий распределения из внешних источников |

##### Content Intelligence (Release 3)
| URL | Метод | View | Описание |
|-----|-------|------|----------|
| `/api/v4/headless/analytics/dashboard/content-intel/content-gaps/` | GET | `ContentIntelligenceViewSet.content_gaps` | Выявление пробелов в контенте |
| `/api/v4/headless/analytics/dashboard/content-intel/compliance/metadata/` | GET | `ContentIntelligenceViewSet.metadata_compliance` | Соответствие метаданных требованиям |

#### Фоновые Задачи

##### `aggregate_daily_metrics` (`tasks.py:25`)
- **Queue:** `documents`
- **Retries:** 3 (max_retries=3, default_retry_delay=60)
- **Триггер:** Периодическая задача (по умолчанию ежедневно для вчерашнего дня)
- **Логика:**
  1. Агрегация `AssetEvent` за указанную дату в `AssetDailyMetrics`
  2. Подсчет downloads, views, shares, bandwidth_bytes по document_id
  3. Вычисление `performance_score` через `calculate_performance_score()` (weighted log-scale)
  4. Определение `top_channel` для каждого документа
  5. Upsert в `AssetDailyMetrics` (unique_together: document, date)
  6. Уведомление через WebSocket (`notify_analytics_refresh`)

##### `aggregate_search_daily_metrics` (`tasks.py:92`)
- **Queue:** `documents`
- **Триггер:** Периодическая задача (ежедневно)
- **Логика:**
  1. Агрегация `SearchQuery` за указанную дату в `SearchDailyMetrics`
  2. Подсчет total_searches, successful_searches (was_downloaded=True или was_clicked=True), null_searches (results_count=0)
  3. Вычисление CTR (Click-Through Rate)
  4. Вычисление avg_response_time_ms
  5. Топ-20 запросов и null-запросов
  6. Upsert в `SearchDailyMetrics` (date как primary key)

##### `aggregate_user_daily_metrics` (`tasks.py:399`)
- **Queue:** `documents`
- **Триггер:** Периодическая задача (ежедневно)
- **Логика:**
  1. Агрегация `SearchSession` за указанную дату
  2. Вычисление avg_search_to_find_minutes для каждого пользователя
  3. Upsert в `UserDailyMetrics` (unique_together: user, date)

##### `calculate_cdn_daily_costs` (`tasks.py:444`)
- **Queue:** `documents`
- **Триггер:** Периодическая задача (ежедневно)
- **Логика:**
  1. Получение `CDNRate` для указанной даты (effective_from <= date <= effective_to)
  2. Агрегация `AssetDailyMetrics.cdn_bandwidth_gb` по channel
  3. Расчет cost_usd = bandwidth_gb * cost_per_gb_usd
  4. Upsert в `CDNDailyCost` (unique_together: date, region, channel)

##### `generate_analytics_alerts` (`tasks.py:246`)
- **Queue:** `documents`
- **Триггер:** Периодическая задача (по умолчанию каждые 90 дней)
- **Логика:**
  1. Генерация алертов для активов без downloads (из `AssetDailyMetrics`)
  2. Генерация алертов для недавних rejections (из `ApprovalWorkflowEvent`)
  3. Генерация алертов для storage limit (из `DocumentFile.size` aggregate)
  4. Генерация алертов для metadata completeness (из `DocumentMetadata`)
  5. Создание записей в `AnalyticsAlert` (без дубликатов для unresolved alerts)

##### `cleanup_old_events` (`tasks.py:174`)
- **Queue:** `documents`
- **Триггер:** Периодическая задача (по умолчанию retention_days=90)
- **Логика:**
  1. Удаление `AssetEvent`, `SearchQuery`, `SearchSession` старше retention_days
  2. Опциональное удаление агрегированных метрик старше `ANALYTICS_AGGREGATED_RETENTION_DAYS` (по умолчанию 365 дней)
  3. Возврат словаря с количеством удаленных записей

##### `aggregate_campaign_engagement_daily_metrics` (`tasks.py:513`)
- **Queue:** `documents`
- **Триггер:** Периодическая задача (ежедневно)
- **Логика:**
  1. Агрегация `CampaignEngagementEvent` за указанную дату
  2. Вычисление avg_engagement_minutes для каждой кампании
  3. Upsert в `CampaignDailyMetrics.avg_engagement_minutes`

#### Утилиты
- **`mayan.apps.analytics.utils`** (`utils.py`) — утилиты для отслеживания событий:
  - `track_asset_event(...)` — создание `AssetEvent` (download/view/share/upload/deliver)
  - `track_cdn_delivery(...)` — отслеживание CDN-доставки (helper для `track_asset_event` с event_type=deliver)
  - `anonymize_ip_address(ip_address)` — анонимизация IP-адресов для GDPR (IPv4: первые 2 октета, IPv6: первые 4 hextets)
- **`mayan.apps.analytics.services`** (`services.py`) — сервисы для связывания событий:
  - `link_download_to_latest_search_session(...)` — связывание download события с открытой поисковой сессией для вычисления Search-to-Find Time
  - `track_feature_usage(...)` — отслеживание использования функций (создание `FeatureUsage`)

#### Middleware
- **`mayan.apps.analytics.middleware.FeatureUsageMiddleware`** (`middleware.py`) — отслеживание использования функций через HTTP-запросы (регистрируется в `MIDDLEWARE`, строка 178 `base.py`)

#### Использование Core Mayan
- **Модели:** `Document`, `DocumentFile`, `User`, `WorkflowInstance` (из `document_states`)
- **Signals:** 
  - `user_logged_in` (`signals.py:42`) — создание `UserSession` при входе пользователя
  - `user_logged_out` (`signals.py:78`) — закрытие `UserSession` при выходе
  - `post_save` на `DocumentFile` (`signals.py:105`) — создание `AssetEvent(EVENT_TYPE_UPLOAD)` при загрузке файла
  - `post_save` на `WorkflowInstanceLogEntry` (`signals.py:148`) — создание/обновление `ApprovalWorkflowEvent` при переходах workflow
- **ACL:** Не используется напрямую (аналитика доступна через permissions)
- **Permissions:** 
  - `permission_analytics_view_asset_bank`
  - `permission_analytics_view_campaign_performance`
  - `permission_analytics_view_search_analytics`
  - `permission_analytics_view_user_activity`
  - `permission_analytics_view_content_intelligence`
  - `permission_analytics_view_distribution`
- **Интеграция с другими модулями:**
  - `dam` — отслеживание download/view через `track_asset_event()` в `DocumentFileDownloadView`, `DocumentDetailView`
  - `distribution` — отслеживание share/deliver через `track_asset_event()` в `ShareLink` views и models
  - `headless_api` — экспонирование аналитики через REST API endpoints

---

### 2.6. `mayan.apps.notifications` — Notification Center

**Назначение:** Расширенная система уведомлений с шаблонами, настройками пользователей, email-рассылкой и WebSocket-доставкой. Интегрируется со стандартной системой уведомлений Mayan (`events.Notification`).

#### Ключевые Модели

##### `NotificationTemplate` (`models.py:8`)
**Поля:**
- `event_type` — CharField (unique, indexed) — тип события (например, 'documents.document_created')
- `title_template` — CharField — шаблон заголовка уведомления
- `message_template` — TextField — шаблон сообщения
- `icon_type` — CharField (default: 'info') — тип иконки
- `icon_url` — URLField — URL иконки
- `default_priority` — CharField (default: 'NORMAL') — приоритет по умолчанию
- `recipients_config` — JSONField — конфигурация получателей
- `actions` — JSONField — список действий (кнопки/ссылки)
- `is_active` — BooleanField (default: True)
- `created_at`, `updated_at` — DateTimeField

**Индексы:** `(event_type,)`

##### `NotificationPreference` (`models.py:55`)
**Связь:** `OneToOneField(User, related_name='notification_preference')`

**Поля:**
- `user` — OneToOneField(User)
- `notifications_enabled` — BooleanField (default: True)
- `email_notifications_enabled` — BooleanField (default: True)
- `push_notifications_enabled` — BooleanField (default: True)
- `email_digest_enabled` — BooleanField (default: False)
- `email_digest_frequency` — CharField (default: 'never')
- `quiet_hours_enabled` — BooleanField (default: False)
- `quiet_hours_start`, `quiet_hours_end` — TimeField (optional)
- `notification_language` — CharField (default: 'ru')
- `created_at`, `updated_at` — DateTimeField

**Примечание:** Подписки на события управляются через стандартную систему Mayan (`EventSubscription`), эта модель хранит только дополнительные настройки доставки.

##### `NotificationLog` (`models.py:101`)
**Связь:** `ForeignKey(events.Notification, related_name='logs')`

**Поля:**
- `notification` — ForeignKey(events.Notification)
- `action` — CharField (read/deleted/etc.)
- `action_data` — JSONField
- `timestamp` — DateTimeField (auto_now_add)
- `uuid` — UUIDField (для идемпотентности/внешней корреляции)

**Индексы:** `(notification, -timestamp)`

#### API Эндпоинты
**Интегрированы в headless_api через `HeadlessNotification*View`:**

| URL | Метод | View | Описание |
|-----|-------|------|----------|
| `/api/v4/headless/notifications/` | GET | `HeadlessNotificationsListView.list` | Список уведомлений пользователя (с пагинацией, фильтрацией по state/event_type) |
| `/api/v4/headless/notifications/{id}/` | GET | `HeadlessNotificationsDetailView.retrieve` | Детали уведомления |
| `/api/v4/headless/notifications/{id}/read/` | PATCH | `HeadlessNotificationsDetailView.mark_read` | Отметить уведомление как прочитанное |
| `/api/v4/headless/notifications/read-all/` | POST | `HeadlessNotificationsReadAllView.read_all` | Отметить все уведомления как прочитанные |
| `/api/v4/headless/notifications/unread-count/` | GET | `HeadlessNotificationsUnreadCountView.unread_count` | Количество непрочитанных уведомлений |
| `/api/v4/headless/notifications/preferences/` | GET, PATCH | `HeadlessNotificationPreferenceView` | Получение/обновление настроек уведомлений пользователя |

#### Фоновые Задачи

##### `send_notification_async` (`tasks.py:14`)
- **Queue:** `notifications` (по умолчанию)
- **Retries:** 3 (max_retries=3, default_retry_delay=60)
- **Триггер:** Через сигналы или прямой вызов при создании уведомления
- **Логика:**
  1. Получение `EventNotification` по ID
  2. Проверка `NotificationPreference.notifications_enabled`
  3. Установка `sent_at` и `state='SENT'`
  4. Запуск `send_notification_email.apply_async()` если `email_notifications_enabled=True`
  5. Запуск `send_websocket_notification.apply_async()` если `push_notifications_enabled=True`

##### `send_notification_email` (`tasks.py:46`)
- **Queue:** `notifications`
- **Триггер:** Из `send_notification_async`
- **Логика:**
  1. Получение `EventNotification` по ID
  2. Проверка наличия email у пользователя
  3. Рендеринг HTML-шаблона `notifications/notification_email.html`
  4. Отправка email через `django.core.mail.send_mail()`

##### `send_websocket_notification` (`tasks.py:102`)
- **Queue:** `notifications`
- **Триггер:** Из `send_notification_async`
- **Логика:**
  1. Получение `EventNotification` по ID
  2. Отправка в Channels group `notifications_{user_id}` через `channel_layer.group_send()`
  3. Тип сообщения: `notification.new` с данными (id, title, message, priority, icon_type, created_at)

##### `cleanup_old_notifications` (`tasks.py:84`)
- **Queue:** `notifications`
- **Триггер:** Периодическая задача (по умолчанию каждые 90 дней)
- **Логика:**
  1. Удаление `EventNotification` старше 90 дней со статусом `ARCHIVED` или `DELETED`
  2. Использует `action.timestamp` для определения возраста

#### Сериализаторы
- **`NotificationSerializer`** (`serializers.py:19`) — полный сериализатор уведомления с fallback для legacy уведомлений (без title)
- **`NotificationListSerializer`** (`serializers.py:70`) — оптимизированный сериализатор для списка (popover)
- **`NotificationPreferenceSerializer`** (`serializers.py:112`) — сериализатор настроек пользователя

#### Использование Core Mayan
- **Модели:** `events.Notification` (расширяется через миграции), `events.EventSubscription`, `events.StoredEventType`
- **Signals:** 
  - `post_save` на `User` (`signals.py:12`) — автоматическое создание `NotificationPreference` для новых пользователей и подписка на стандартные события документов (`documents.document_file_created`, `documents.document_created`, `documents.document_edited`, `documents.document_version_created`)
- **Интеграция:** Расширяет стандартную систему уведомлений Mayan через миграции (добавление полей `title`, `message`, `priority`, `icon_type`, `icon_url`, `state`, `actions` в `events.Notification`)
- **Permissions:** Использует стандартные permissions Mayan для уведомлений

---

## 3. Анализ Использования Core Mayan

### 3.1. Расширение Моделей

#### Паттерн: OneToOneField (не модификация core)
**Пример:** `DocumentAIAnalysis.document = OneToOneField(Document, related_name='ai_analysis')`

**Преимущества:**
- Не модифицирует core Mayan
- Обратная совместимость при обновлениях
- Легко удалить через миграцию

**Использование:**
```python
# Получение AI-анализа для документа
document = Document.objects.get(pk=1)
ai_analysis = document.ai_analysis  # через related_name
```

#### Паттерн: ForeignKey к Core Models
**Примеры:**
- `GeneratedRendition.publication_item` → `PublicationItem` → `Document`
- `ShareLink.rendition` → `GeneratedRendition` → `DocumentFile`

### 3.2. Перехват Сигналов

#### `post_save` на `DocumentFile` (`dam/signals.py:148`)
**Назначение:** Автоматический запуск AI-анализа при загрузке нового файла.

**Логика:**
1. Проверка `created=True` (только для новых файлов)
2. Проверка `should_trigger_analysis()` (`signals.py:86`):
   - Проверка `DAM_AI_ANALYSIS_AUTO_TRIGGER` (включение/выключение автозапуска)
   - Проверка MIME-типа (только изображения/PDF из `ANALYZABLE_MIMETYPES`)
   - Проверка размера файла через `get_max_file_size_for_mime_type()` (дифференцированные лимиты)
   - Проверка существующего анализа (пропуск если уже `completed` или `processing`)
3. Создание/обновление `DocumentAIAnalysis` со статусом `pending`
4. Запуск `analyze_document_with_ai.apply_async()` с задержкой (по умолчанию 10 секунд для S3)
5. Сохранение `task_id` для отслеживания прогресса

**Настройки:**
- `DAM_AI_ANALYSIS_AUTO_TRIGGER` — включение/выключение автозапуска (по умолчанию `True`)
- `DAM_AI_ANALYSIS_DELAY_SECONDS` — задержка перед запуском (по умолчанию 10s для S3 propagation)

#### `post_save`/`post_delete` на `DAMMetadataPreset` (`dam/signals.py:245, 251`)
**Назначение:** Инвалидация кеша подсчета документов при изменении пресета.

**Логика:**
- При сохранении или удалении пресета вызывается `invalidate_preset_count_cache(preset_id)`
- Кеш инвалидируется для всех пользователей (user-specific кеши будут обновлены при следующем запросе)

#### `user_logged_in` / `user_logged_out` (`analytics/signals.py:42, 78`)
**Назначение:** Отслеживание пользовательских сессий для аналитики.

**Логика:**
- `user_logged_in`: Создание `UserSession` с данными о входе (session_key, login_timestamp, geo_country, geo_city, ip_address анонимизированный, user_agent)
- `user_logged_out`: Закрытие последней открытой `UserSession` (установка logout_timestamp и session_duration_seconds)

#### `post_save` на `DocumentFile` (`analytics/signals.py:105`)
**Назначение:** Отслеживание загрузки файлов как аналитических событий.

**Логика:**
- При создании нового `DocumentFile` создается `AssetEvent(EVENT_TYPE_UPLOAD)` через `track_asset_event()`
- Канал: `dam_interface`
- Метаданные: document_file_id, mimetype, size

#### `post_save` на `WorkflowInstanceLogEntry` (`analytics/signals.py:148`)
**Назначение:** Отслеживание workflow-переходов для аналитики approval процессов.

**Логика:**
- Эвристическое определение типа перехода (submit/approve/reject) по имени/лейблу перехода
- При submit: создание нового `ApprovalWorkflowEvent` со статусом `pending` (increment attempt_number)
- При approve/reject: обновление последнего pending `ApprovalWorkflowEvent` (установка approver, approved_at/rejected_at, approval_time_days)

#### `post_save` на `User` (`notifications/signals.py:12`)
**Назначение:** Автоматическое создание настроек уведомлений для новых пользователей.

**Логика:**
- При создании нового пользователя создается `NotificationPreference` с настройками по умолчанию
- Автоматическая подписка на стандартные события документов через `EventSubscription`:
  - `documents.document_file_created`
  - `documents.document_created`
  - `documents.document_edited`
  - `documents.document_version_created`

### 3.3. Использование ACL (Access Control Lists)

#### Паттерны использования ACL

**1. `restrict_queryset()` — фильтрация queryset по правам:**
```python
# version_views.py:54
queryset = AccessControlList.objects.restrict_queryset(
    permission=permission_document_version_create,
    queryset=Document.valid.all(),
    user=request.user
)
document = get_object_or_404(queryset, pk=document_id)
```

**2. `check_access()` — проверка прав на объект:**
```python
# api_views.py:65
AccessControlList.objects.check_access(
    obj=document,
    permissions=(permission_document_view,),
    user=request.user
)
```

**Использование в headless_api:**
- `HeadlessEditView` — проверка `permission_document_version_create`
- `HeadlessFavoriteListView` — проверка `permission_document_view`
- `HeadlessMyUploadsView` — проверка `permission_document_view`
- `HeadlessActivityFeedView` — фильтрация документов по ACL

**Использование в dam:**
- `DocumentAIAnalysisViewSet.get_document()` — проверка `permission_document_view`
- `DocumentAIAnalysisViewSet._assert_analysis_permission()` — проверка `permission_ai_analysis_create`
- `DAMMetadataPresetSerializer.get_applicable_documents_count()` — фильтрация документов по ACL через `restrict_queryset()` для подсчета с учетом прав доступа

### 3.4. Использование Permissions

**Кастомные permissions в `dam/permissions.py`:**
- `permission_ai_analysis_view`
- `permission_ai_analysis_create`
- `permission_ai_analysis_edit`
- `permission_ai_analysis_delete`
- `permission_metadata_preset_view/create/edit/delete`

**Кастомные permissions в `analytics/permissions.py`:**
- `permission_analytics_view_asset_bank` — просмотр Asset Bank dashboard
- `permission_analytics_view_campaign_performance` — просмотр Campaign Performance dashboard
- `permission_analytics_view_search_analytics` — просмотр Search Analytics dashboard
- `permission_analytics_view_user_activity` — просмотр User Activity dashboard
- `permission_analytics_view_content_intelligence` — просмотр Content Intelligence dashboard
- `permission_analytics_view_distribution` — просмотр Distribution Analytics dashboard

**Core permissions (из Mayan):**
- `permission_document_view`
- `permission_document_version_create`
- `permission_document_edit`
- `permission_document_metadata_edit`

---

## 4. API Реестр (Headless & REST)

### 4.1. Группировка по Функционалу

#### Authentication & User Management
| Endpoint | Method | Auth | ACL | Описание |
|----------|--------|------|-----|----------|
| `/api/v4/auth/token/obtain/` | POST | None | None | Получение токена |
| `/api/v4/users/current/` | GET | Token/Session | None | Текущий пользователь |
| `/api/v4/headless/auth/me/` | GET | Token/Session | None | Расширенная информация о пользователе |
| `/api/v4/headless/password/change/` | POST | Token/Session | IsAuthenticated | Смена пароля |
| `/api/v4/headless/profile/` | GET | Token/Session | IsAuthenticated | Профиль пользователя |
| `/api/v4/headless/users/` | GET, POST | Token/Session | IsAuthenticated | Список/создание пользователей |
| `/api/v4/headless/users/{id}/` | GET, PATCH, DELETE | Token/Session | IsAuthenticated | Детали пользователя |

#### Documents & Assets
| Endpoint | Method | Auth | ACL | Описание |
|----------|--------|------|-----|----------|
| `/api/v4/documents/` | GET, POST | Token/Session | IsAuthenticated | Список/создание документов |
| `/api/v4/documents/{id}/` | GET, PATCH, DELETE | Token/Session | `permission_document_view` | Детали документа |
| `/api/v4/documents/optimized/` | GET | Token/Session | IsAuthenticated | Оптимизированный список (N+1 fixes) |
| `/api/v4/dam/document-detail/{id}/` | GET | Token/Session | `permission_document_view` | Детали с AI-данными |
| `/api/v4/dam/documents/` | GET | Token/Session | IsAuthenticated | Список документов (DAM) |
| `/api/v4/documents/{id}/files/` | GET, POST | Token/Session | `permission_document_view` | Список/загрузка файлов |
| `/api/v4/documents/{id}/metadata/` | GET, POST | Token/Session | `permission_document_view` | Метаданные |
| `/api/v4/documents/{id}/tags/` | GET, POST | Token/Session | `permission_document_view` | Теги |
| `/api/v4/documents/{id}/versions/` | GET | Token/Session | `permission_document_view` | Версии документа |
| `/api/v4/headless/documents/my_uploads/` | GET | Token/Session | IsAuthenticated | Мои загрузки (с ACL) |
| `/api/v4/headless/documents/{id}/versions/new_from_edit/` | POST | Token/Session | `permission_document_version_create` | Создание версии из редактора |
| `/api/v4/headless/documents/{id}/convert/` | POST | Token/Session | `permission_document_view` | Конвертация документа |

#### AI Analysis
| Endpoint | Method | Auth | ACL | Описание |
|----------|--------|------|-----|----------|
| `/api/v4/dam/ai-analysis/` | GET, POST | Token/Session | `permission_ai_analysis_view` | Список/создание AI-анализа |
| `/api/v4/dam/ai-analysis/{id}/` | GET, PATCH, DELETE | Token/Session | `permission_ai_analysis_view` | Детали AI-анализа |
| `/api/v4/dam/ai-analysis/analyze/` | POST | Token/Session | `permission_ai_analysis_create` | Запуск анализа (проверка размера файла, ошибка `FILE_TOO_LARGE` при превышении) |
| `/api/v4/dam/ai-analysis/bulk_analyze/` | POST | Token/Session | `permission_ai_analysis_create` | Массовый анализ |
| `/api/v4/dam/documents/{id}/processing_status/` | GET | Token/Session | `permission_document_view` | Статус обработки (progress) |
| `/api/v4/dam/documents/{id}/ocr/extract/` | GET | Token/Session | `permission_document_view` | Извлечение OCR-текста |

#### Distribution & Sharing
| Endpoint | Method | Auth | ACL | Описание |
|----------|--------|------|-----|----------|
| `/api/v4/distribution/publications/` | GET, POST | Token/Session | IsAuthenticated | Список/создание публикаций |
| `/api/v4/distribution/publications/{id}/` | GET, PATCH, DELETE | Token/Session | IsAuthenticated | Детали публикации |
| `/api/v4/distribution/share_links/` | GET, POST | Token/Session | IsAuthenticated | Список/создание share links |
| `/api/v4/distribution/share_links/{id}/` | GET, PATCH, DELETE | Token/Session | IsAuthenticated | Детали share link |
| `/api/v4/distribution/rendition_presets/` | GET, POST | Token/Session | IsAuthenticated | Список/создание пресетов |
| `/api/v4/distribution/generated_renditions/` | GET | Token/Session | IsAuthenticated | Список rendition'ов |

#### Configuration & Metadata
| Endpoint | Method | Auth | ACL | Описание |
|----------|--------|------|-----|----------|
| `/api/v4/headless/config/document_types/` | GET | Token/Session | IsAuthenticated | Список типов документов |
| `/api/v4/headless/config/document_types/{id}/` | GET | Token/Session | IsAuthenticated | Детальная конфигурация типа |
| `/api/v4/dam/metadata-presets/` | GET, POST | Token/Session | `permission_metadata_preset_view` | Список/создание пресетов |

#### Activity & Dashboard
| Endpoint | Method | Auth | ACL | Описание |
|----------|--------|------|-----|----------|
| `/api/v4/headless/activity/feed/` | GET | Token/Session | IsAuthenticated | Персонализированная лента |
| `/api/v4/headless/dashboard/activity/` | GET | Token/Session | IsAuthenticated | Активность дашборда |
| `/api/v4/headless/dashboard/stats/` | GET | Token/Session | IsAuthenticated | Статистика дашборда |
| `/api/v4/dam/dashboard-stats/` | GET | Token/Session | IsAuthenticated | Статистика DAM |

#### Favorites & Collections
| Endpoint | Method | Auth | ACL | Описание |
|----------|--------|------|-----|----------|
| `/api/v4/headless/favorites/` | GET | Token/Session | IsAuthenticated | Список избранного (с ACL) |
| `/api/v4/headless/favorites/{id}/toggle/` | POST | Token/Session | `permission_document_view` | Переключение избранного |

### 4.2. Критические Эндпоинты (Детальный Анализ)

#### 4.2.1. Upload (Загрузка файлов)

**Endpoint:** `POST /api/v4/documents/{id}/files/`

**Входные данные:**
- `file_new` — файл (multipart/form-data)
- `action` — ID действия (по умолчанию 1 = `DocumentFileActionUseNewPages`)
- `filename` — имя файла
- `comment` — комментарий (опционально)

**Логика обработки:**
1. Получение документа через ACL: `AccessControlList.objects.restrict_queryset(permission_document_view, ...)`
2. Проверка прав на создание версии
3. Создание `DocumentFile` через `document.file_new()`
4. Асинхронная обработка (конвертация, OCR, AI-анализ через signals)

**Оптимизации:**
- Использование `DocumentFileActionUseNewPages` для создания новой версии
- Автоматический запуск AI-анализа через signal (с задержкой 10s для S3)

**Проблемы:**
- Нет chunked upload для больших файлов (только через стандартный Mayan API)
- Нет прогресс-трекинга в реальном времени

---

#### 4.2.2. AI Analysis (AI-анализ)

**Endpoint:** `POST /api/v4/dam/ai-analysis/analyze/`

**Входные данные (Serializer):**
```python
class AnalyzeDocumentSerializer(serializers.Serializer):
    document_id = serializers.IntegerField()
    provider = serializers.CharField(required=False)
    force_reanalyze = serializers.BooleanField(default=False)
```

**Логика обработки:**
1. Валидация через `AnalyzeDocumentSerializer` (с проверкой ACL в `validate_document_id()`)
2. Проверка доступности Celery worker
3. Проверка прав: `permission_ai_analysis_create`
4. Создание/обновление `DocumentAIAnalysis` со статусом `pending`
5. Запуск Celery task: `analyze_document_with_ai.apply_async()`
6. Возврат `task_id` для отслеживания прогресса

**Оптимизации:**
- Использование `select_related('document')` в ViewSet
- Throttling: `AIAnalysisThrottle` (10/minute, 50/hour, 500/day)
- Retry logic в Celery task (3 попытки)

**Проблемы:**
- ~~Нет проверки размера файла перед анализом (может привести к таймаутам)~~ ✅ **РЕШЕНО:** Реализована система дифференцированных лимитов (`DAM_AI_MAX_FILE_SIZE_*`) с проверкой в API, Celery task и signals
- Нет очереди для приоритетных анализов

---

#### 4.2.3. Search (Поиск)

**Endpoint:** `GET /api/v4/documents/optimized/` (DAM) или `/api/v4/documents/` (core)

**Входные данные (Query Parameters):**
- `q` — поисковый запрос
- `page`, `page_size` — пагинация
- `ordering` — сортировка
- `document_type__label` — фильтр по типу
- `cabinets__id` — фильтр по папке
- `datetime_created__gte`, `datetime_created__lte` — фильтр по дате

**Логика обработки:**
1. Получение queryset через ACL: `AccessControlList.objects.restrict_queryset(permission_document_view, ...)`
2. Применение фильтров и поиска
3. Оптимизация через `select_related('document_type')`, `prefetch_related('files')`
4. Пагинация через `MayanPageNumberPagination`

**Оптимизации:**
- `OptimizedDocumentSerializer` использует `select_related()` для `document_type`
- `prefetch_related()` для `files` (избежание N+1)
- Кеширование результатов поиска (если настроено)

**Проблемы:**
- Поиск по JSON-полям (`ai_tags`, `categories`) требует transformation функций (см. `dam/search.py`)
- Нет полнотекстового поиска по AI-описанию

---

#### 4.2.4. Download (Скачивание)

**Endpoint:** `GET /api/v4/documents/{id}/files/{file_id}/download/`

**Логика обработки:**
1. Проверка ACL: `permission_document_file_download`
2. Получение `DocumentFile`
3. Отправка файла через Django `FileResponse`

**Оптимизации:**
- Использование `select_related('document')` для избежания дополнительных запросов
- Streaming для больших файлов

**Проблемы:**
- Нет rate limiting на скачивание (только общий throttle)
- ~~Нет поддержки range requests (для возобновления загрузки)~~ ✅ **РЕШЕНО:** добавлена поддержка HTTP Range Requests (RFC 7233) в `DownloadViewMixin` (ответы `206 Partial Content` / `416 Range Not Satisfiable`, заголовки `Accept-Ranges`, `Content-Range`). Для S3 предусмотрен опциональный режим `?direct=1` (redirect на storage URL) для offload на storage/CDN.

---

### 4.3. Оптимизации (Prefetch, Cache)

#### Использование `select_related()`

**Примеры:**
```python
# headless_api/views/activity_views.py:171
queryset = Action.objects.select_related(
    'actor', 'target_content_type'
)

# headless_api/views/favorites_views.py:61
Favorite.objects.select_related('document', 'document__document_type')

# dam/api_views.py:50
DocumentAIAnalysis.objects.select_related('document').prefetch_related('document__files')
```

#### Использование `prefetch_related()`

**Примеры:**
```python
# headless_api/views/favorites_views.py:81-97
# Оптимизированный prefetch для files и versions
documents_qs.prefetch_related(
    'tags',
    Prefetch('files', queryset=DocumentFile.objects.order_by('-timestamp'), to_attr='_prefetched_latest_file_list'),
    Prefetch('versions', queryset=DocumentVersion.objects.filter(active=True).prefetch_related('version_pages'), to_attr='_prefetched_version_active_list')
)

# headless_api/views/activity_views.py:277-298
# Batch prefetch для Document объектов через GenericForeignKey
def _prefetch_documents_for_actions(self, actions):
    documents = Document.objects.filter(pk__in=document_ids).only(
        'id', 'label', 'uuid', 'datetime_created'
    ).prefetch_related('files', 'versions__version_pages')

# dam/api_views.py:50
DocumentAIAnalysis.objects.prefetch_related('document__files')
```

#### Кеширование
- **DRF Pagination:** Кеширование страниц через `cacheService` на фронтенде
- **Django Cache:** Redis (django-redis) для throttling counters, sessions и общего кеша (работает в multi-process/multi-server окружении)
- **Кеширование подсчета документов пресета:** 
  - TTL: 10 минут (настраивается через `DAM_PRESET_DOCUMENT_COUNT_CACHE_TTL`)
  - User-specific ключи для учета ACL при подсчете
  - Автоматическая инвалидация через сигналы при изменении `DAMMetadataPreset` (`signals.py:245, 251`)
  - Утилиты: `mayan/apps/dam/cache_utils.py`
- **Нет кеширования:** AI-анализ, метаданные (каждый раз запрос к БД)

---

## 5. Технический Долг и Уязвимости

### 5.1. N+1 Запросы

#### Выявленные проблемы

1. **`HeadlessActivityFeedView` (`activity_views.py:169`):**
   - Использует `select_related('actor', 'target_content_type')`
   - ~~**Проблема:** Нет `prefetch_related()` для `target` (Document), что может привести к N+1 при сериализации~~ ✅ **РЕШЕНО**
   - **Реализация:** Добавлен batch prefetch для Document объектов через `_prefetch_documents_for_actions()` с использованием `only()` для оптимизации. Реализовано кеширование ContentType на уровне класса. Методы сериализации обновлены для использования prefetched documents. Добавлена обработка ошибок для удаленных объектов.

2. **`HeadlessFavoriteListView` (`favorites_views.py:61`):**
   - Использует `select_related('document', 'document__document_type')`
   - ~~**Проблема:** Нет `prefetch_related()` для `document__files`, `document__tags`~~ ✅ **РЕШЕНО**
   - **Реализация:** Добавлен `Prefetch` для `files` с `order_by('-timestamp')` и `to_attr='_prefetched_latest_file_list'`. Добавлен `Prefetch` для `versions` с фильтром `active=True` и `to_attr='_prefetched_version_active_list'`. Применена оптимизация `only()` для минимизации передачи данных. Все prefetch'и соответствуют ожиданиям `OptimizedDocumentListSerializer`.

3. **`DAMDocumentListView` (`api_views.py`):**
   - Использует `OptimizedDocumentSerializer` с оптимизациями
   - **Статус:** Оптимизирован (использует `select_related`, `prefetch_related`)

4. **`DashboardActivityView` (`activity_views.py:372`):**
   - ~~**Проблема:** Потенциальные N+1 запросы при сериализации через `ActivityFeedSerializer`~~ ✅ **РЕШЕНО**
   - **Реализация:** Применены те же оптимизации, что и для `HeadlessActivityFeedView` - batch prefetch для Document объектов. `ActivityFeedSerializer` обновлен для использования prefetched documents из context.

### 5.2. Отсутствие Проверок Прав Доступа

#### Выявленные проблемы

1. **`HeadlessDashboardStatsView`:**
   - **Проблема:** Нет явной проверки ACL для документов в статистике
   - **Рекомендация:** Использовать `AccessControlList.objects.restrict_queryset()` для фильтрации документов

2. **`HeadlessDocumentConvertView`:**
   - **Статус:** Использует ACL (`restrict_queryset` с `permission_document_view`)
   - **Статус:** ✅ Корректно

3. **`HeadlessMyUploadsView`:**
   - **Статус:** Использует ACL (`restrict_queryset` с `permission_document_view`)
   - **Статус:** ✅ Корректно

### 5.3. Хардкод Конфигурации

1. **`dam/tasks.py:25`:**
   ```python
   DEFAULT_PROVIDER_SEQUENCE = ['qwenlocal', 'gigachat', 'openai', 'claude', 'gemini', 'yandexgpt', 'kieai']
   ```
   - ~~**Проблема:** Хардкод последовательности провайдеров~~ ✅ **РЕШЕНО**
   - **Реализация:** Вынесено в settings (`DAM_AI_PROVIDER_SEQUENCE`). Константа удалена, используется `dam_settings.setting_ai_provider_sequence.value` с fallback логикой через `_coerce_list()`.

2. **`dam/signals.py:189`:**
   ```python
   countdown_seconds = getattr(settings, 'DAM_AI_ANALYSIS_DELAY_SECONDS', 10)
   ```
   - **Статус:** ✅ Использует settings с fallback

3. **`dam/tasks.py:40`:**
   ```python
   def _shrink_image_bytes(image_data: bytes, max_width: int = 1600) -> bytes:
   ```
   - ~~**Проблема:** Хардкод `max_width=1600`~~ ✅ **РЕШЕНО**
   - **Реализация:** Вынесено в settings (`DAM_AI_IMAGE_MAX_WIDTH`). Сигнатура функции обновлена на `max_width: Optional[int] = None`, значение получается из `dam_settings.setting_ai_image_max_width.value` с fallback на 1600.

### 5.4. Deprecated Методы Mayan

**Не обнаружено** — используется актуальный API Mayan EDMS 4.3.

### 5.5. TODO и FIXME в Коде

1. **`dam/tasks.py:984` (было 939):**
   ```python
   # TODO: Integrate with Mayan metadata system to automatically
   ```
   - ~~**Описание:** Интеграция AI-тегов с системой метаданных Mayan~~ ✅ **РЕШЕНО**
   - **Реализация:** Реализована гибридная интеграция AI-результатов с системой метаданных Mayan:
     - **Теги** (ai_tags, people, locations, categories) → Mayan `Tag` через `tag.attach_to(document)`
     - **Текстовые поля** (ai_description, alt_text, copyright_notice) → `MetadataType` через `DocumentMetadata`
     - **Принцип "Человек > AI":** Перезапись только если значение пустое (кроме `force_reanalyze=True`)
     - **Настройки:** `DAM_AI_METADATA_MAPPING` для конфигурации маппинга, `DAM_AI_TAG_DEFAULT_COLOR` для цвета тегов
     - **Утилита:** `get_or_create_tag()` для создания/получения тегов
     - **Важно:** MetadataType должны быть созданы администратором вручную перед использованием

2. **`dam/serializers.py:189` (было 192):**
   ```python
   return 0  # TODO: Implement actual counting logic
   ```
   - ~~**Описание:** Реализовать подсчет документов для пресета~~ ✅ **РЕШЕНО**
   - **Реализация:** Реализован метод `get_applicable_documents_count()` с:
     - **ACL-фильтрацией:** Использование `AccessControlList.objects.restrict_queryset()` для учета прав доступа
     - **Фильтрацией по MIME типам:** Через Subquery для latest file mimetype
     - **Кешированием:** TTL 10 минут (настраивается через `DAM_PRESET_DOCUMENT_COUNT_CACHE_TTL`)
     - **Инвалидацией кеша:** Автоматическая через сигналы при изменении `DAMMetadataPreset`
     - **Утилиты:** `mayan/apps/dam/cache_utils.py` для управления кешем

3. **`image_editor/views.py:35` (было 36):**
   ```python
   # [DEPRECATED] ImageEditorSaveView - удален 2025-12-23
   ```
   - ~~**Описание:** Deprecated view (заменен на `HeadlessEditView`)~~ ✅ **РЕШЕНО**
   - **Реализация:** 
     - URL-маршрут удален из `mayan/apps/image_editor/urls.py:14` (комментарий: `[DEPRECATED] ImageEditorSaveView URL removed 2025-12-23`)
     - Класс `ImageEditorSaveView` закомментирован в `mayan/apps/image_editor/views.py:35-59` с пояснением о замене на `HeadlessEditView`
     - Оставлен закомментированным на 1 спринт для возможности быстрого восстановления при необходимости
     - Новый endpoint: `POST /api/v4/headless/documents/{id}/versions/new_from_edit/` (`HeadlessEditView`)

### 5.6. Уязвимости Безопасности

1. **Отсутствие Rate Limiting на AI-анализ:**
   - ~~**Проблема:** Throttling есть (`AIAnalysisThrottle`), но LocMemCache не работает в multi-process окружении (5 воркеров = 5-кратный лимит)~~ ✅ **ЧАСТИЧНО РЕШЕНО** (инфраструктура)
   - **Реализация (инфраструктура):** Исправлена конфигурация Redis для distributed rate limiting:
     - Заменен `LocMemCache` на `RedisCache` (django-redis) в `mayan/settings/base.py`
     - Разделение Redis databases: DB 0 (Application Cache), DB 1 (Celery Result Backend), DB 2 (Lock Manager)
     - Централизация конфигурации в `base.py` через переменные окружения (`MAYAN_REDIS_HOST`, `MAYAN_REDIS_PORT`, `MAYAN_REDIS_PASSWORD`, `MAYAN_REDIS_DB_CACHE`)
     - Удалено дублирование `CACHES` из `production.py` (DRY принцип)
     - Добавлен `KEY_PREFIX: 'mayan_v4'` для версионирования ключей
     - Enterprise настройки connection pool для надежности
   - **Осталось:** Реализовать Quota Management (Service Layer Quotas) для bulk-операций и Token Bucket / Burst Protection (P1)

2. **Отсутствие валидации размера файла:**
   - ~~**Проблема:** Нет проверки размера файла перед AI-анализом (может привести к DoS)~~ ✅ **РЕШЕНО**
   - **Реализация:** Добавлена система дифференцированных лимитов:
     - `DAM_AI_MAX_FILE_SIZE_IMAGES` = 20MB (JPEG, PNG, GIF, WebP, BMP)
     - `DAM_AI_MAX_FILE_SIZE_RAW` = 50MB (RAW, DNG, TIFF)
     - `DAM_AI_MAX_FILE_SIZE_PDF` = 30MB
     - `DAM_AI_MAX_FILE_SIZE_DOCUMENTS` = 15MB (DOCX, DOC, TXT)
     - `DAM_AI_MAX_FILE_SIZE_VIDEO` = 500MB (для будущей поддержки)
     - `DAM_AI_MAX_FILE_SIZE_AUDIO` = 100MB (для будущей поддержки)
     - `DAM_AI_MAX_FILE_SIZE_DEFAULT` = 15MB
   - **Места проверки:** API endpoint (`api_views.py`), Celery task (`tasks.py`), Signal handler (`signals.py`)
   - **Утилиты:** `mayan.apps.dam.utils.get_max_file_size_for_mime_type()`, `format_file_size()`

3. **Хранение credentials в settings:**
   - **Проблема:** AI-провайдеры credentials хранятся в Django settings (может быть в БД через smart_settings)
   - **Рекомендация:** Использовать environment variables или encrypted storage

4. **Отсутствие CSRF-защиты для Token Auth:**
   - **Статус:** ✅ Корректно — Token auth не требует CSRF (только для Session auth)

### 5.7. Проблемы Производительности

1. **Синхронная конвертация изображений:**
   - ~~**Проблема:** `HeadlessEditView._convert_image()` выполняется синхронно в request handler~~ ✅ **РЕШЕНО**
   - **Реализация:** Реализована полностью асинхронная обработка через Celery tasks:
     - Создана задача `process_editor_version_task()` в очереди `converter`
     - `HeadlessEditView` и `HeadlessImageEditorCommitView` возвращают `202 Accepted` с `task_id`
     - Добавлена проверка размера файла (лимит 500MB через `HEADLESS_EDITOR_MAX_UPLOAD_SIZE`)
     - Создан endpoint `GET /api/v4/headless/tasks/{task_id}/status/` для поллинга статуса через Celery Result Backend
     - Использование `SharedUploadedFile` для временного хранения файлов перед обработкой
     - TTFB < 200ms независимо от размера файла

2. **Отсутствие индексов на JSON-поля:**
   - ~~**Проблема:** Поиск по `ai_tags`, `categories` (JSONField) может быть медленным~~ ✅ **РЕШЕНО**
   - **Реализация:** Созданы GIN-индексы с операторным классом `jsonb_path_ops` для оптимизации оператора `@>` (contains):
     - `dam_ai_tags_gin_idx` на поле `ai_tags`
     - `dam_categories_gin_idx` на поле `categories`
     - `dam_people_gin_idx` на поле `people`
     - `dam_locations_gin_idx` на поле `locations`
   - **Особенности:** Индексы создаются через `CREATE INDEX CONCURRENTLY` для неблокирующего создания на production. Использование `jsonb_path_ops` обеспечивает меньший размер индекса и лучшую производительность для оператора `@>`. Ожидаемое ускорение: 10-100x для больших таблиц.

3. **Нет кеширования конфигурации типов документов:**
   - ~~**Проблема:** `HeadlessDocumentTypeConfigView` каждый раз делает запросы к БД~~ ✅ **РЕШЕНО**
   - **Реализация:** Реализовано кеширование конфигурации типов документов с настраиваемым TTL (по умолчанию 1 час). Кеш автоматически инвалидируется при изменении `DocumentType`, `DocumentTypeMetadataType` и связей `Workflow.document_types` через сигналы Django. Используются версионированные ключи кеша (`_v1`) для безопасности при изменении схемы API. TTL настраивается через `HEADLESS_DOC_TYPE_CONFIG_CACHE_TTL` в smart_settings. Реализован fallback на БД при ошибках кеша.

---

## 6. Зависимости между Модулями

### 6.1. Граф Зависимостей

```
headless_api
  ├── depends on: documents, acls, permissions, rest_api (core)
  ├── uses: dam (для AI-анализа через DocumentAIAnalysis)
  └── uses: distribution (для share links через API)

dam
  ├── depends on: documents, metadata, ocr, acls, permissions, tags (core)
  ├── uses: dynamic_search (для индексации AI-тегов)
  ├── uses: storage (для S3/Yandex Disk)
  └── integrates: tags (для AI-тегов через tag.attach_to()), metadata (для AI-описаний через DocumentMetadata)

distribution
  ├── depends on: documents, acls, permissions (core)
  ├── uses: converter_pipeline_extension (для конвертации)
  └── uses: storage (для S3-хранилища rendition'ов)

image_editor
  ├── depends on: documents, acls, permissions (core)
  └── integrated via: headless_api (endpoints)
```

### 6.2. Циклические Зависимости

**Не обнаружено** — архитектура модульная, зависимости однонаправленные.

---

## 7. Заключение

### 7.1. Сильные Стороны

1. **Четкое разделение Core и Custom:**
   - Кастомные приложения не модифицируют core Mayan
   - Использование OneToOneField/ForeignKey для расширения
   - Обратная совместимость при обновлениях

2. **Правильное использование ACL:**
   - Все критические endpoints используют `AccessControlList.objects.restrict_queryset()` или `check_access()`
   - Соблюдение прав доступа на уровне объектов

3. **Защита от DoS атак:**
   - Реализована система дифференцированных лимитов размера файлов для AI-анализа
   - Проверка размера на трех уровнях: API endpoint, Celery task, Signal handler
   - Поддержка различных лимитов для разных типов медиа-файлов (изображения, RAW, PDF, документы, видео, аудио)

4. **Оптимизации запросов:**
   - Использование `select_related()`, `prefetch_related()` в большинстве views
   - Оптимизированный serializer для списка документов
   - Кеширование подсчета документов пресета с ACL-фильтрацией (TTL 10 минут)

5. **Асинхронная обработка:**
   - AI-анализ через Celery tasks
   - Генерация rendition'ов через Celery
   - Правильное использование очередей

### 7.2. Слабые Стороны

1. **Технический долг:**
   - ~~TODO в коде (интеграция с метаданными, подсчет документов)~~ ✅ **РЕШЕНО:** Реализована интеграция AI-метаданных с Mayan (гибридная стратегия: теги → Tag, остальное → MetadataType), реализован подсчет документов для пресета с ACL и кешированием, удален deprecated ImageEditorSaveView
   - ~~Хардкод конфигурации (последовательность провайдеров, max_width)~~ ✅ **РЕШЕНО:** Вынесено в settings (`DAM_AI_PROVIDER_SEQUENCE`, `DAM_AI_IMAGE_MAX_WIDTH`)

2. **Производительность:**
   - ~~Синхронная конвертация изображений в request handler~~ ✅ **РЕШЕНО:** Реализована полностью асинхронная обработка через Celery tasks с TTFB < 200ms
   - ~~Отсутствие кеширования конфигурации типов документов~~ ✅ **РЕШЕНО:** Реализовано кеширование с TTL 1 час и автоматической инвалидацией через сигналы
   - ~~Отсутствие кеширования подсчета документов пресета~~ ✅ **РЕШЕНО:** Реализовано кеширование с TTL 10 минут, ACL-фильтрацией и автоматической инвалидацией через сигналы (`signals.py:245, 251`)
   - ~~Потенциальные N+1 в некоторых views~~ ✅ **РЕШЕНО:** Оптимизированы `HeadlessActivityFeedView`, `HeadlessFavoriteListView` и `DashboardActivityView`

3. **Безопасность:**
   - ~~Отсутствие валидации размера файла перед AI-анализом~~ ✅ **РЕШЕНО:** Реализована система дифференцированных лимитов с проверкой на трех уровнях
   - Хранение credentials в settings (не encrypted)

### 7.3. Рекомендации по Приоритетам

#### Приоритет 1 (Критично)
1. ~~**Добавить валидацию размера файла** перед AI-анализом~~ ✅ **ВЫПОЛНЕНО**
2. ~~**Вынести хардкод** в settings (провайдеры, max_width)~~ ✅ **ВЫПОЛНЕНО**
3. ~~**Добавить `prefetch_related()`** в `HeadlessActivityFeedView` и `HeadlessFavoriteListView`~~ ✅ **ВЫПОЛНЕНО**

#### Приоритет 2 (Важно)
4. ~~**Кешировать конфигурацию типов документов** (1 час TTL)~~ ✅ **ВЫПОЛНЕНО**
5. ~~**Вынести конвертацию изображений** в Celery task для больших файлов~~ ✅ **ВЫПОЛНЕНО**
6. ~~**Реализовать TODO** (интеграция с метаданными, подсчет документов)~~ ✅ **ВЫПОЛНЕНО**
   - Интеграция AI-метаданных с Mayan (гибридная стратегия: теги → Tag, остальное → MetadataType)
   - Подсчет документов для пресета с ACL-фильтрацией и кешированием
   - Удаление deprecated ImageEditorSaveView

#### Приоритет 3 (Желательно)
7. ~~**Добавить GIN-индексы** для JSON-полей (если используется PostgreSQL)~~ ✅ **ВЫПОЛНЕНО**
8. ~~**Улучшить rate limiting** для bulk-операций~~ ✅ **ЧАСТИЧНО ВЫПОЛНЕНО** (инфраструктура: Redis cache для distributed throttling)
   - **Осталось:** Quota Management (Service Layer Quotas) и Token Bucket / Burst Protection
9. ~~**Добавить поддержку range requests** для скачивания больших файлов~~ ✅ **ВЫПОЛНЕНО**

---

**Документ составлен:** 2025-12-09  
**Последнее обновление:** 2025-12-23 (добавлены модули analytics и notifications: модели, API endpoints, Celery tasks, сигналы, интеграция с headless_api)  
**Автор аудита:** Senior Backend Architect  
**Версия:** 2.0

