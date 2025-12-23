# BACKEND_AUDIT_V1.md

**Дата аудита:** 2025-12-09  
**Версия:** 1.2  
**Последнее обновление:** 2025-12-23 (добавлена информация о реализации проверки размера файлов и оптимизации N+1 запросов)  
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
1. **`mayan.apps.headless_api`** — BFF-адаптер для SPA
2. **`mayan.apps.dam`** — Digital Asset Management (AI-анализ, метаданные)
3. **`mayan.apps.distribution`** — Распространение контента (публикации, share links)
4. **`mayan.apps.image_editor`** — Редактор изображений (server-side)
5. **`mayan.apps.converter_pipeline_extension`** — Расширение конвертера (RAW, DNG)
6. **`mayan.apps.storage`** — Кастомные storage backends (S3, Яндекс.Диск)
7. **`mayan.apps.user_management`** — Расширенное управление пользователями
8. **`mayan.apps.autoadmin`** — Автоматическая администрирование

### 1.3. Конфигурация Инфраструктуры

#### Celery
- **Broker:** RabbitMQ (`amqp://mayan:mayanrabbitpass@rabbitmq:5672/mayan`)
- **Result Backend:** Redis (`redis://:mayanredispassword@redis:6379/1`)
- **Lock Manager:** Redis (`redis://:mayanredispassword@redis:6379/2`)
- **Queues:**
  - `tools` — AI-анализ (`mayan.apps.dam.tasks.analyze_document_with_ai`)
  - `converter` — Конвертация файлов (`mayan.apps.distribution.tasks.generate_rendition_task`)
  - `distribution` — Распространение (transient queue)

#### База Данных
- **Engine:** `django.db.backends.postgresql`
- **Database:** `mayan` (по умолчанию)
- **Host:** `postgresql` (Docker service)
- **User:** `mayan`
- **Password:** `mayandbpass` (по умолчанию, через env)

#### Кеширование
- **Backend:** `django.core.cache.backends.locmem.LocMemCache`
- **Timeout:** 300 секунд
- **Max Entries:** 1000

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
| `/api/v4/headless/documents/{id}/versions/new_from_edit/` | POST | `HeadlessEditView` | Создание версии из отредактированного изображения |
| `/api/v4/headless/documents/{id}/convert/` | POST | `HeadlessDocumentConvertView` | Конвертация документа |
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
**Нет собственных Celery tasks** — использует tasks из других приложений (dam, distribution).

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
  - Автоматически через signal `post_save` на `DocumentFile` (`signals.py:125`)
  - Вручную через API endpoint `/api/v4/dam/ai-analysis/analyze/`
- **Логика:**
  1. Проверка `DAM_AI_ANALYSIS_ENABLED`
  2. Получение документа и latest file
  3. **Проверка размера файла** (дифференцированные лимиты по MIME типу через `utils.get_max_file_size_for_mime_type()`)
  4. Проверка доступности файла в storage (S3 race condition fix)
  5. Создание/обновление `DocumentAIAnalysis` со статусом `processing`
  6. Попытка анализа через провайдеры (fallback sequence: qwenlocal → gigachat → openai → claude → gemini → yandexgpt → kieai)
  7. Обновление прогресса (`progress`, `current_step`)
  8. Сохранение результатов в `DocumentAIAnalysis`
  9. Обновление статуса на `completed` или `failed`

##### `bulk_analyze_documents` (`tasks.py`)
- **Queue:** `tools`
- **Триггер:** API endpoint `/api/v4/dam/ai-analysis/bulk_analyze/`
- **Логика:** Массовый запуск `analyze_document_with_ai` для списка документов

##### `import_yandex_disk` (`tasks.py`)
- **Queue:** `tools`
- **Триггер:** Management command или API
- **Логика:** Импорт файлов из Яндекс.Диск

#### Утилиты
- **`mayan.apps.dam.utils`** — утилиты для работы с лимитами размеров файлов:
  - `get_max_file_size_for_mime_type(mime_type: str) -> int` — определение лимита по MIME типу
  - `format_file_size(size_bytes: int) -> str` — форматирование размера для сообщений

#### Использование Core Mayan
- **Модели:** `Document`, `DocumentFile`, `DocumentType`
- **Signals:** `post_save` на `DocumentFile` (автоматический триггер AI-анализа с проверкой размера файла)
- **ACL:** `AccessControlList.objects.check_access()` для проверки прав на документ
- **Permissions:** `permission_document_view`, `permission_ai_analysis_create`
- **Search:** Интеграция с `mayan.apps.dynamic_search` для индексации AI-тегов
- **OCR:** Использование `mayan.apps.ocr.models.DocumentVersionPageOCRContent` для извлечения текста

**Примеры сигналов:**
```python
# signals.py:125
@receiver(post_save, sender=DocumentFile)
def trigger_ai_analysis(sender, instance, created, **kwargs):
    # Автоматический запуск AI-анализа при создании нового файла
    if created and should_trigger_analysis(instance, instance.document):
        analyze_document_with_ai.apply_async(args=[instance.document.id], countdown=10)
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

#### Ключевые Модели
**Использует модели из core Mayan:** `Document`, `DocumentFile`, `DocumentVersion`

#### API Эндпоинты
**Интегрированы в headless_api:**
- `/api/v4/headless/image-editor/sessions/` — создание сессии
- `/api/v4/headless/image-editor/sessions/{id}/` — управление сессией
- `/api/v4/headless/image-editor/sessions/{id}/preview/` — превью
- `/api/v4/headless/image-editor/sessions/{id}/commit/` — коммит изменений

#### Фоновые Задачи
**Нет собственных tasks** — использует `HeadlessEditView` для синхронного создания версий.

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

#### `post_save` на `DocumentFile` (`dam/signals.py:125`)
**Назначение:** Автоматический запуск AI-анализа при загрузке нового файла.

**Логика:**
1. Проверка `created=True` (только для новых файлов)
2. Проверка MIME-типа (только изображения/PDF)
3. Проверка доступности файла в storage (S3 race condition fix)
4. Создание/обновление `DocumentAIAnalysis` со статусом `pending`
5. Запуск `analyze_document_with_ai.apply_async()` с задержкой 10 секунд

**Настройки:**
- `DAM_AI_ANALYSIS_AUTO_TRIGGER` — включение/выключение автозапуска
- `DAM_AI_ANALYSIS_DELAY_SECONDS` — задержка перед запуском (по умолчанию 10s)

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

### 3.4. Использование Permissions

**Кастомные permissions в `dam/permissions.py`:**
- `permission_ai_analysis_view`
- `permission_ai_analysis_create`
- `permission_ai_analysis_edit`
- `permission_ai_analysis_delete`
- `permission_metadata_preset_view/create/edit/delete`

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
- Нет поддержки range requests (для возобновления загрузки)

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
- **Django Cache:** LocMemCache для throttling counters
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
   - **Проблема:** Хардкод последовательности провайдеров
   - **Рекомендация:** Вынести в settings (`DAM_AI_PROVIDER_SEQUENCE`)

2. **`dam/signals.py:189`:**
   ```python
   countdown_seconds = getattr(settings, 'DAM_AI_ANALYSIS_DELAY_SECONDS', 10)
   ```
   - **Статус:** ✅ Использует settings с fallback

3. **`dam/tasks.py:40`:**
   ```python
   def _shrink_image_bytes(image_data: bytes, max_width: int = 1600) -> bytes:
   ```
   - **Проблема:** Хардкод `max_width=1600`
   - **Рекомендация:** Вынести в settings (`DAM_AI_IMAGE_MAX_WIDTH`)

### 5.4. Deprecated Методы Mayan

**Не обнаружено** — используется актуальный API Mayan EDMS 4.3.

### 5.5. TODO и FIXME в Коде

1. **`dam/tasks.py:939`:**
   ```python
   # TODO: Integrate with Mayan metadata system to automatically
   ```
   - **Описание:** Интеграция AI-тегов с системой метаданных Mayan

2. **`dam/serializers.py:192`:**
   ```python
   return 0  # TODO: Implement actual counting logic
   ```
   - **Описание:** Реализовать подсчет документов для пресета

3. **`image_editor/views.py:36`:**
   ```python
   """[DEPRECATED] Сохранение изменений изображения и создание новой версии.
   ```
   - **Описание:** Deprecated view (заменен на `HeadlessEditView`)

### 5.6. Уязвимости Безопасности

1. **Отсутствие Rate Limiting на AI-анализ:**
   - **Проблема:** Throttling есть (`AIAnalysisThrottle`), но может быть недостаточно для защиты от злоупотреблений
   - **Рекомендация:** Добавить более строгие лимиты для bulk-операций

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
   - **Проблема:** `HeadlessEditView._convert_image()` выполняется синхронно в request handler
   - **Рекомендация:** Вынести в Celery task для больших файлов

2. **Отсутствие индексов на JSON-поля:**
   - **Проблема:** Поиск по `ai_tags`, `categories` (JSONField) может быть медленным
   - **Рекомендация:** Добавить GIN-индексы для PostgreSQL (если используется)

3. **Нет кеширования конфигурации типов документов:**
   - **Проблема:** `HeadlessDocumentTypeConfigView` каждый раз делает запросы к БД
   - **Рекомендация:** Кешировать конфигурацию на 1 час

---

## 6. Зависимости между Модулями

### 6.1. Граф Зависимостей

```
headless_api
  ├── depends on: documents, acls, permissions, rest_api (core)
  ├── uses: dam (для AI-анализа через DocumentAIAnalysis)
  └── uses: distribution (для share links через API)

dam
  ├── depends on: documents, metadata, ocr, acls, permissions (core)
  ├── uses: dynamic_search (для индексации AI-тегов)
  └── uses: storage (для S3/Yandex Disk)

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

3. **Оптимизации запросов:**
   - Использование `select_related()`, `prefetch_related()` в большинстве views
   - Оптимизированный serializer для списка документов

4. **Асинхронная обработка:**
   - AI-анализ через Celery tasks
   - Генерация rendition'ов через Celery
   - Правильное использование очередей

### 7.2. Слабые Стороны

1. **Технический долг:**
   - TODO в коде (интеграция с метаданными, подсчет документов)
   - Хардкод конфигурации (последовательность провайдеров, max_width)

2. **Производительность:**
   - Синхронная конвертация изображений в request handler
   - Отсутствие кеширования конфигурации типов документов
   - ~~Потенциальные N+1 в некоторых views~~ ✅ **РЕШЕНО:** Оптимизированы `HeadlessActivityFeedView`, `HeadlessFavoriteListView` и `DashboardActivityView`

3. **Безопасность:**
   - ~~Отсутствие валидации размера файла перед AI-анализом~~ ✅ **РЕШЕНО:** Реализована система дифференцированных лимитов с проверкой на трех уровнях
   - Хранение credentials в settings (не encrypted)

### 7.3. Рекомендации по Приоритетам

#### Приоритет 1 (Критично)
1. ~~**Добавить валидацию размера файла** перед AI-анализом~~ ✅ **ВЫПОЛНЕНО**
2. **Вынести хардкод** в settings (провайдеры, max_width)
3. ~~**Добавить `prefetch_related()`** в `HeadlessActivityFeedView` и `HeadlessFavoriteListView`~~ ✅ **ВЫПОЛНЕНО**

#### Приоритет 2 (Важно)
4. **Кешировать конфигурацию типов документов** (1 час TTL)
5. **Вынести конвертацию изображений** в Celery task для больших файлов
6. **Реализовать TODO** (интеграция с метаданными, подсчет документов)

#### Приоритет 3 (Желательно)
7. **Добавить GIN-индексы** для JSON-полей (если используется PostgreSQL)
8. **Улучшить rate limiting** для bulk-операций
9. **Добавить поддержку range requests** для скачивания больших файлов

---

**Документ составлен:** 2025-12-09  
**Последнее обновление:** 2025-12-23 (добавлена информация о реализации проверки размера файлов и оптимизации N+1 запросов)  
**Автор аудита:** Senior Backend Architect  
**Версия:** 1.2

