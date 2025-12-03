# Backend Analysis — Prime-EDMS / DAM System

**Дата анализа:** 03 декабря 2025  
**Версия:** 3.0 (Полный технический анализ Legacy-кода)  
**Автор:** Senior System Analyst & Technical Writer (20+ лет опыта DAM систем)

---

## 📋 Содержание

1. [Архитектурный обзор](#1-архитектурный-обзор)
2. [Стек технологий и зависимости](#2-стек-технологий-и-зависимости)
3. [Модульная структура Mayan EDMS](#3-модульная-структура-mayan-edms)
4. [Внешние сервисы и интеграции](#4-внешние-сервисы-и-интеграции)
5. [API Endpoints — Полный маппинг](#5-api-endpoints--полный-маппинг)
6. [Модель данных](#6-модель-данных)
7. [Storage Backends](#7-storage-backends)
8. [AI Провайдеры](#8-ai-провайдеры)
9. [Celery Tasks](#9-celery-tasks)
10. [Система прав доступа (ACL)](#10-система-прав-доступа-acl)
11. [Frontend ↔ Backend соответствие](#11-frontend--backend-соответствие)
12. [Критические проблемы](#12-критические-проблемы)
13. [Рекомендации по интеграции](#13-рекомендации-по-интеграции)

---

## 1. Архитектурный обзор

### 1.1 Общая архитектура системы

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND LAYER                                     │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                    │
│  │   Vue 3 SPA    │  │  Mayan Django  │  │  Mobile Apps   │                    │
│  │  (новый DAM)   │  │   Templates    │  │   (будущее)    │                    │
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘                    │
└──────────┼───────────────────┼───────────────────┼─────────────────────────────┘
           │                   │                   │
           │ REST API v4       │ Django Views      │ REST API
           ▼                   ▼                   ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                              API GATEWAY LAYER                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    Django REST Framework 3.13.1                          │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │   │
│  │  │Token Auth   │ │Session Auth │ │  Rate Limit │ │ Permissions │        │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘        │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐     │
│  │   /api/v4/          │  │   /api/dam/         │  │   /api/v4/search/   │     │
│  │   (Mayan Core)      │  │   (DAM Extension)   │  │   (Elasticsearch)   │     │
│  └──────────┬──────────┘  └──────────┬──────────┘  └──────────┬──────────┘     │
└─────────────┼────────────────────────┼────────────────────────┼────────────────┘
              │                        │                        │
              ▼                        ▼                        ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                           APPLICATION LAYER                                     │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      Django 3.2.14 Applications                          │   │
│  │                                                                          │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐  │   │
│  │  │ documents │ │  cabinets │ │   tags    │ │ metadata  │ │   acls    │  │   │
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────┘ └───────────┘  │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐  │   │
│  │  │    dam    │ │  sources  │ │ converter │ │    ocr    │ │  mailer   │  │   │
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────┘ └───────────┘  │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐  │   │
│  │  │ workflows │ │  search   │ │  storage  │ │ checkouts │ │signatures │  │   │
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────┘ └───────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────┬─────────────────────────────────────────┘
                                       │
                                       ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                            DATA LAYER                                           │
│                                                                                 │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                    │
│  │  PostgreSQL    │  │     Redis      │  │   RabbitMQ     │                    │
│  │  12.10         │  │     6.2        │  │     3.10       │                    │
│  │  (Primary DB)  │  │  (Cache/Lock)  │  │ (Task Broker)  │                    │
│  └────────────────┘  └────────────────┘  └────────────────┘                    │
│                                                                                 │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                    │
│  │  Elasticsearch │  │  Local Storage │  │   S3 Storage   │                    │
│  │  7.17.1        │  │  (File System) │  │ (Beget/AWS)    │                    │
│  │  (Search)      │  │                │  │                │                    │
│  └────────────────┘  └────────────────┘  └────────────────┘                    │
└────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES                                       │
│                                                                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │  Qwen Local │ │  GigaChat   │ │   OpenAI    │ │   Claude    │               │
│  │  (Ollama)   │ │   (Sber)    │ │  GPT-4V     │ │ (Anthropic) │               │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │   Gemini    │ │  YandexGPT  │ │   Kie.ai    │ │ Yandex Disk │               │
│  │  (Google)   │ │  (Yandex)   │ │  (OCR/AI)   │ │ (Import)    │               │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                               │
│  │  Tesseract  │ │    LDAP     │ │    SMTP     │                               │
│  │  (OCR)      │ │   (Auth)    │ │   (Mail)    │                               │
│  └─────────────┘ └─────────────┘ └─────────────┘                               │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Стек технологий и зависимости

### 2.1 Core Dependencies (requirements/base.txt)

| Категория | Пакет | Версия | Назначение |
|-----------|-------|--------|------------|
| **Framework** | Django | 3.2.14 | Web framework |
| **API** | djangorestframework | 3.13.1 | REST API |
| **API Docs** | drf-yasg | 1.20.0 | Swagger/OpenAPI |
| **Task Queue** | celery | 5.2.3 | Async tasks |
| **Scheduler** | django-celery-beat | 2.2.1 | Periodic tasks |
| **Search** | Whoosh | 2.7.4 | Full-text search (default) |
| **Search** | elasticsearch | 7.17.1 | Full-text search (optional) |
| **Search** | elasticsearch-dsl | 7.4.0 | Elasticsearch DSL |
| **Image** | Pillow | 9.2.0 | Image processing |
| **PDF** | PyPDF2 | 1.28.4 | PDF processing |
| **SVG** | CairoSVG | 2.5.2 | SVG rendering |
| **Auth** | django-auth-ldap | 4.0.0 | LDAP integration |
| **CORS** | django-cors-headers | 3.10.0 | Cross-origin requests |
| **OTP** | pyotp | 2.6.0 | Two-factor auth |
| **QR** | qrcode | 7.3.1 | QR code generation |
| **HTTP** | requests | 2.27.1 | HTTP client |
| **Crypto** | pycryptodome | 3.10.4 | Encryption |
| **GPG** | python_gnupg | 0.4.8 | GPG signatures |
| **Graphs** | graphviz | 0.17 | Workflow visualization |
| **Server** | gunicorn | 20.1.0 | WSGI server |
| **Server** | gevent | 21.12.0 | Async workers |
| **Static** | whitenoise | 6.0.0 | Static files |
| **Monitoring** | sentry-sdk | 1.5.8 | Error tracking |
| **MIME** | python-magic | 0.4.26 | MIME detection |
| **Email** | flanker | 0.9.11 | Email parsing |
| **MSG** | extract-msg | 0.34.3 | Outlook MSG files |
| **Schema** | jsonschema | 4.4.0 | JSON validation |
| **FUSE** | fusepy | 3.0.1 | File system mirroring |
| **YAML** | PyYAML | 6.0 | Config parsing |

### 2.2 S3 Storage Dependencies (опционально)

```python
# Устанавливаются отдельно при включении S3
boto3>=1.26.0
django-storages>=1.13.0
botocore>=1.29.0
```

---

## 3. Модульная структура Mayan EDMS

### 3.1 Полный список Django Applications

```
mayan/apps/
├── acls/                    # Access Control Lists (RBAC)
├── announcements/           # System announcements
├── appearance/              # UI themes, templates
├── authentication/          # Auth backends, login/logout
├── authentication_otp/      # Two-factor authentication
├── autoadmin/               # Auto-create admin user
├── cabinets/                # Folder/cabinet system
├── checkouts/               # Document checkout/lock
├── common/                  # Shared utilities
├── converter/               # Image/document conversion
├── converter_pipeline_extension/ # Conversion pipeline
├── dam/                     # DAM Extension (custom)
│   ├── ai_providers/        # AI service integrations
│   │   ├── base.py         # Base provider class
│   │   ├── claude.py       # Anthropic Claude
│   │   ├── gemini.py       # Google Gemini
│   │   ├── gigachat.py     # Sber GigaChat
│   │   ├── kieai.py        # Kie.ai OCR
│   │   ├── openai.py       # OpenAI GPT-4V
│   │   ├── qwen_local.py   # Local Qwen (Ollama)
│   │   └── yandex.py       # YandexGPT
│   ├── services/            # External service clients
│   │   ├── kie_ai_client.py
│   │   └── yandex_disk.py
│   ├── api_views.py         # REST API endpoints
│   ├── models.py            # DocumentAIAnalysis, DAMMetadataPreset
│   ├── serializers.py       # DRF serializers
│   ├── settings.py          # Smart settings
│   ├── tasks.py             # Celery tasks
│   └── throttles.py         # Rate limiting
├── dashboards/              # Dashboard widgets
├── databases/               # Database mixins
├── dependencies/            # Dependency checking
├── distribution/            # Asset distribution/publishing
├── django_gpg/              # GPG key management
├── document_comments/       # Document comments
├── document_indexing/       # Document tree indexing
├── document_parsing/        # Text extraction
├── document_signatures/     # Digital signatures
├── document_states/         # Workflow engine
│   ├── workflow_actions.py  # Built-in actions
│   └── models/              # Workflow, State, Transition
├── documents/               # Core document management
│   ├── api_views/           # Document API endpoints
│   ├── models/              # Document, DocumentFile, DocumentVersion
│   ├── serializers/         # Document serializers
│   └── storages.py          # Storage backend config
├── duplicates/              # Duplicate detection
├── dynamic_search/          # Search engine abstraction
├── events/                  # Event logging
├── file_caching/            # File cache management
├── file_metadata/           # EXIF, XMP extraction
├── image_editor/            # Image editing tools
├── linking/                 # Smart links
├── locales/                 # Localization
├── lock_manager/            # Distributed locks (Redis)
├── logging/                 # Audit logging
├── mailer/                  # Email notifications
├── mayan_statistics/        # Usage statistics
├── messaging/               # User messaging
├── metadata/                # Custom metadata types
├── mime_types/              # MIME type registry
├── mirroring/               # FUSE filesystem mirroring
├── navigation/              # Menu system
├── ocr/                     # OCR integration
│   └── backends/tesseract.py # Tesseract backend
├── organizations/           # Multi-tenancy (future)
├── permissions/             # Permission definitions
├── platform/                # Platform detection
├── quotas/                  # Storage quotas
├── redactions/              # Document redaction
├── rest_api/                # REST API core
├── signature_captures/      # Signature capture
├── smart_settings/          # Dynamic settings
├── sources/                 # Document sources
│   └── source_backends/
│       ├── email_backends.py      # Email import
│       ├── sane_scanner_backends.py # Scanner integration
│       ├── staging_folder_backends.py # Staging folders
│       ├── watch_folder_backends.py   # Watch folders
│       └── web_form_backends.py       # Web upload
├── storage/                 # Storage backends
│   └── backends/
│       ├── compressedstorage.py
│       └── encryptedstorage.py
├── tags/                    # Document tagging
├── task_manager/            # Celery management
├── templating/              # Template engine
├── testing/                 # Test utilities
├── user_management/         # User/Group management
├── views/                   # Generic views
└── web_links/               # External links
```

---

## 4. Внешние сервисы и интеграции

### 4.1 AI Провайдеры для анализа изображений

| Провайдер | Endpoint | Capabilities | Настройки |
|-----------|----------|--------------|-----------|
| **Qwen Local** | `http://192.168.1.25:11434/api/generate` | Vision, Description, Tags | `DAM_QWENLOCAL_API_URL`, `DAM_QWENLOCAL_MODEL` |
| **GigaChat** | Sber API | Vision, Description | `DAM_GIGACHAT_CREDENTIALS`, `DAM_GIGACHAT_SCOPE` |
| **OpenAI** | OpenAI API | GPT-4 Vision | `DAM_OPENAI_API_KEY`, `DAM_OPENAI_MODEL` |
| **Claude** | Anthropic API | Vision, Analysis | `DAM_CLAUDE_API_KEY`, `DAM_CLAUDE_MODEL` |
| **Gemini** | Google AI | Vision, Description | `DAM_GEMINI_API_KEY`, `DAM_GEMINI_MODEL` |
| **YandexGPT** | Yandex Cloud | Text generation | `DAM_YANDEXGPT_API_KEY`, `DAM_YANDEXGPT_FOLDER_ID` |
| **Kie.ai** | Flux Kontext | OCR, Analysis | `DAM_KIEAI_API_KEY`, `DAM_KIEAI_BASE_URL` |

### 4.2 Цепочка fallback для AI анализа

```python
DEFAULT_PROVIDER_SEQUENCE = [
    'qwenlocal',   # 1. Локальная модель (приоритет)
    'gigachat',    # 2. GigaChat (Сбер)
    'openai',      # 3. OpenAI GPT-4V
    'claude',      # 4. Anthropic Claude
    'gemini',      # 5. Google Gemini
    'yandexgpt',   # 6. YandexGPT
    'kieai'        # 7. Kie.ai
]
```

### 4.3 Yandex Disk Integration

```python
# Настройки импорта из Yandex Disk
DAM_YANDEX_DISK_TOKEN          # OAuth токен
DAM_YANDEX_DISK_BASE_PATH      # Базовый путь (default: /)
DAM_YANDEX_DISK_CABINET_ROOT_LABEL  # Корневой кабинет
DAM_YANDEX_DISK_DOCUMENT_TYPE_ID    # Тип документа
DAM_YANDEX_DISK_MAX_FILE_SIZE       # Макс. размер (20MB)
DAM_YANDEX_DISK_FILE_LIMIT          # Лимит файлов за раз
DAM_YANDEX_DISK_CLIENT_ID           # OAuth Client ID
DAM_YANDEX_DISK_CLIENT_SECRET       # OAuth Client Secret
DAM_YANDEX_DISK_REFRESH_TOKEN       # Refresh token
```

### 4.4 OCR Integration (Tesseract)

```python
# mayan/apps/ocr/backends/tesseract.py
# Использует tesseract-ocr системного уровня
# Поддерживает языки: eng, rus, deu, fra, etc.
```

### 4.5 LDAP Authentication

```python
# django-auth-ldap настройки
AUTH_LDAP_SERVER_URI
AUTH_LDAP_BIND_DN
AUTH_LDAP_BIND_PASSWORD
AUTH_LDAP_USER_SEARCH
AUTH_LDAP_GROUP_SEARCH
```

---

## 5. API Endpoints — Полный маппинг

### 5.1 Authentication API (`/api/v4/`)

| Method | Endpoint | View Class | Описание |
|--------|----------|------------|----------|
| `POST` | `/auth/token/obtain/` | `BrowseableObtainAuthToken` | Получение токена |
| `GET` | `/user_management/users/current/` | Core Mayan | Текущий пользователь |

### 5.2 Documents API (`/api/v4/documents/`)

| Method | Endpoint | View Class | Permission |
|--------|----------|------------|------------|
| `GET` | `/documents/` | `APIDocumentListView` | `document_view` |
| `POST` | `/documents/` | `APIDocumentListView` | `document_create` |
| `GET` | `/documents/{id}/` | `APIDocumentDetailView` | `document_view` |
| `PUT/PATCH` | `/documents/{id}/` | `APIDocumentDetailView` | `document_properties_edit` |
| `DELETE` | `/documents/{id}/` | `APIDocumentDetailView` | `document_trash` |
| `POST` | `/documents/{id}/type/change/` | `APIDocumentChangeTypeView` | `document_properties_edit` |
| `POST` | `/documents/upload/` | `APIDocumentUploadView` | `document_create` |
| `GET` | `/documents/file_actions/` | `APIDocumentFileActionListView` | - |

### 5.3 Document Files API (`/api/v4/documents/{id}/files/`)

| Method | Endpoint | View Class | Permission |
|--------|----------|------------|------------|
| `GET` | `/documents/{id}/files/` | `APIDocumentFileListView` | `document_file_view` |
| `POST` | `/documents/{id}/files/` | `APIDocumentFileListView` | `document_file_new` |
| `GET` | `/documents/{id}/files/{file_id}/` | `APIDocumentFileDetailView` | `document_file_view` |
| `DELETE` | `/documents/{id}/files/{file_id}/` | `APIDocumentFileDetailView` | `document_file_delete` |
| `GET` | `/documents/{id}/files/{file_id}/download/` | `APIDocumentFileDownloadView` | `document_file_download` |
| `GET` | `/documents/{id}/files/{file_id}/pages/` | `APIDocumentFilePageListView` | `document_file_view` |
| `GET` | `/documents/{id}/files/{file_id}/pages/{page_id}/` | `APIDocumentFilePageDetailView` | `document_file_view` |
| `GET` | `/documents/{id}/files/{file_id}/pages/{page_id}/image/` | `APIDocumentFilePageImageView` | `document_file_view` |

### 5.4 Document Versions API (`/api/v4/documents/{id}/versions/`)

| Method | Endpoint | View Class | Permission |
|--------|----------|------------|------------|
| `GET` | `/documents/{id}/versions/` | `APIDocumentVersionListView` | `document_version_view` |
| `POST` | `/documents/{id}/versions/` | `APIDocumentVersionListView` | `document_version_create` |
| `GET` | `/documents/{id}/versions/{version_id}/` | `APIDocumentVersionDetailView` | `document_version_view` |
| `DELETE` | `/documents/{id}/versions/{version_id}/` | `APIDocumentVersionDetailView` | `document_version_delete` |
| `GET` | `/documents/{id}/versions/{version_id}/export/` | `APIDocumentVersionExportView` | `document_version_export` |
| `GET` | `/documents/{id}/versions/{version_id}/pages/` | `APIDocumentVersionPageListView` | `document_version_view` |
| `GET` | `/documents/{id}/versions/{version_id}/pages/{page_id}/image/` | `APIDocumentVersionPageImageView` | `document_version_view` |

### 5.5 Document Types API (`/api/v4/document_types/`)

| Method | Endpoint | View Class | Permission |
|--------|----------|------------|------------|
| `GET` | `/document_types/` | `APIDocumentTypeListView` | `document_type_view` |
| `POST` | `/document_types/` | `APIDocumentTypeListView` | `document_type_create` |
| `GET` | `/document_types/{id}/` | `APIDocumentTypeDetailView` | `document_type_view` |
| `PUT/PATCH` | `/document_types/{id}/` | `APIDocumentTypeDetailView` | `document_type_edit` |
| `DELETE` | `/document_types/{id}/` | `APIDocumentTypeDetailView` | `document_type_delete` |

### 5.6 Tags API (`/api/v4/tags/`)

| Method | Endpoint | Permission |
|--------|----------|------------|
| `GET` | `/tags/` | `tag_view` |
| `POST` | `/tags/` | `tag_create` |
| `GET` | `/tags/{id}/` | `tag_view` |
| `PUT/PATCH` | `/tags/{id}/` | `tag_edit` |
| `DELETE` | `/tags/{id}/` | `tag_delete` |
| `GET` | `/documents/{id}/tags/` | `document_view` |
| `POST` | `/documents/{id}/tags/` | `tag_attach` |
| `DELETE` | `/documents/{id}/tags/{tag_id}/` | `tag_remove` |

### 5.7 Cabinets API (`/api/v4/cabinets/`)

| Method | Endpoint | Permission |
|--------|----------|------------|
| `GET` | `/cabinets/` | `cabinet_view` |
| `POST` | `/cabinets/` | `cabinet_create` |
| `GET` | `/cabinets/{id}/` | `cabinet_view` |
| `PUT/PATCH` | `/cabinets/{id}/` | `cabinet_edit` |
| `DELETE` | `/cabinets/{id}/` | `cabinet_delete` |
| `GET` | `/cabinets/{id}/documents/` | `cabinet_view` |
| `POST` | `/cabinets/{id}/documents/` | `cabinet_add_document` |
| `DELETE` | `/cabinets/{id}/documents/{doc_id}/` | `cabinet_remove_document` |

### 5.8 Metadata API (`/api/v4/metadata_types/`)

| Method | Endpoint | Permission |
|--------|----------|------------|
| `GET` | `/metadata_types/` | `metadata_type_view` |
| `POST` | `/metadata_types/` | `metadata_type_create` |
| `GET` | `/documents/{id}/metadata/` | `document_metadata_view` |
| `POST` | `/documents/{id}/metadata/` | `document_metadata_add` |
| `PUT/PATCH` | `/documents/{id}/metadata/{metadata_id}/` | `document_metadata_edit` |
| `DELETE` | `/documents/{id}/metadata/{metadata_id}/` | `document_metadata_remove` |

### 5.9 Search API (`/api/v4/search/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/search/` | Полнотекстовый поиск |
| `GET` | `/search/advanced/` | Расширенный поиск |
| `GET` | `/search/{model}/` | Поиск по модели |

### 5.10 DAM Custom API (`/api/dam/`)

| Method | Endpoint | View Class | Description |
|--------|----------|------------|-------------|
| `GET` | `/documents/` | `DAMDocumentListView` | Список с AI-метаданными |
| `GET` | `/document-detail/{id}/` | `DAMDocumentDetailView` | Детали + AI анализ |
| `GET` | `/dashboard-stats/` | `DAMDashboardStatsView` | Статистика дашборда |
| `GET` | `/analysis-status/` | `AIAnalysisStatusView` | Статус AI анализа |
| `GET` | `/ai-analysis/` | `DocumentAIAnalysisViewSet` | Список анализов |
| `POST` | `/ai-analysis/analyze/` | `DocumentAIAnalysisViewSet` | Запуск анализа |
| `POST` | `/ai-analysis/reanalyze/` | `DocumentAIAnalysisViewSet` | Повторный анализ |
| `POST` | `/ai-analysis/bulk-analyze/` | `DocumentAIAnalysisViewSet` | Массовый анализ |
| `GET` | `/metadata-presets/` | `DAMMetadataPresetViewSet` | Пресеты метаданных |

### 5.11 Supporting APIs

| Endpoint | Description |
|----------|-------------|
| `/api/v4/sources/` | Sources management |
| `/api/v4/workflows/` | Workflow management |
| `/api/v4/users/` | User management |
| `/api/v4/groups/` | Group management |
| `/api/v4/permissions/` | Permission management |
| `/api/v4/events/` | Event log |
| `/api/v4/statistics/` | System statistics |

---

## 6. Модель данных

### 6.1 Core Document Model

```python
# mayan/apps/documents/models/document_models.py

class Document(models.Model):
    """Основная сущность документа"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE)
    label = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    datetime_created = models.DateTimeField(auto_now_add=True, db_index=True)
    language = models.CharField(max_length=8, default='en')
    in_trash = models.BooleanField(default=False, db_index=True)
    is_stub = models.BooleanField(default=True)
    
    class Meta:
        ordering = ('label',)
        verbose_name = _('Document')


class DocumentFile(models.Model):
    """Файл документа (может быть несколько версий)"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='files')
    comment = models.TextField(blank=True)
    encoding = models.CharField(max_length=64, blank=True)
    file = models.FileField(storage=storage_document_files, upload_to=...)
    filename = models.CharField(max_length=255, db_index=True)
    mimetype = models.CharField(max_length=255, blank=True)
    size = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    checksum = models.CharField(max_length=64, blank=True)


class DocumentVersion(models.Model):
    """Версия документа (страницы из файлов)"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    active = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class DocumentVersionPage(models.Model):
    """Страница версии документа"""
    document_version = models.ForeignKey(DocumentVersion, related_name='pages')
    page_number = models.PositiveIntegerField(default=1, db_index=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
```

### 6.2 DAM Extension Model

```python
# mayan/apps/dam/models.py

class DocumentAIAnalysis(ExtraDataModelMixin, models.Model):
    """AI анализ документа"""
    document = models.OneToOneField(
        Document, on_delete=models.CASCADE, 
        related_name='ai_analysis'
    )
    
    # AI-генерируемые поля
    ai_description = models.TextField(blank=True, null=True)
    ai_tags = models.JSONField(blank=True, null=True)  # ["tag1", "tag2"]
    dominant_colors = models.JSONField(blank=True, null=True)  # [{"hex": "#fff", "name": "White"}]
    alt_text = models.CharField(max_length=500, blank=True, null=True)
    
    # Расширенные поля
    categories = models.JSONField(blank=True, null=True)  # ["Category1", "Category2"]
    language = models.CharField(max_length=20, blank=True, null=True)
    people = models.JSONField(blank=True, null=True)  # ["Person Name"]
    locations = models.JSONField(blank=True, null=True)  # ["Location Name"]
    
    # Права и governance
    copyright_notice = models.TextField(blank=True, null=True)
    usage_rights = models.TextField(blank=True, null=True)
    rights_expiry = models.DateField(blank=True, null=True)
    
    # Метаданные обработки
    ai_provider = models.CharField(max_length=50, blank=True, null=True)
    analysis_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    analysis_completed = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class DAMMetadataPreset(models.Model):
    """Пресет настроек AI анализа"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    ai_providers = models.JSONField(default=list)
    extract_description = models.BooleanField(default=True)
    extract_tags = models.BooleanField(default=True)
    extract_colors = models.BooleanField(default=True)
    extract_alt_text = models.BooleanField(default=True)
    supported_mime_types = models.JSONField(default=list)
    is_enabled = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)


class YandexDiskImportRecord(models.Model):
    """Запись об импорте из Yandex Disk"""
    yandex_path = models.CharField(max_length=1024, unique=True)
    document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True)
    imported_at = models.DateTimeField(auto_now_add=True)
    file_hash = models.CharField(max_length=64, blank=True)
```

### 6.3 Entity Relationship Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  DocumentType   │◄────│    Document     │────►│ DocumentVersion │
│  - label        │     │  - uuid         │     │  - active       │
│  - filename_gen │     │  - label        │     │  - comment      │
│  - retention    │     │  - description  │     │  - timestamp    │
└─────────────────┘     │  - in_trash     │     └────────┬────────┘
                        └────────┬────────┘              │
                                 │                       │
     ┌───────────────────────────┼───────────────────────┼─────────────────┐
     │                           │                       │                 │
     ▼                           ▼                       ▼                 ▼
┌────────────┐           ┌────────────────┐    ┌────────────────┐  ┌────────────┐
│ Cabinet    │           │  DocumentFile  │    │DocumentVersion │  │   Tag      │
│ (Folder)   │           │  - filename    │    │     Page       │  │  - label   │
│ - label    │           │  - mimetype    │    │  - page_number │  │  - color   │
│ - parent   │           │  - size        │    └────────────────┘  └────────────┘
└────────────┘           │  - checksum    │
                         └───────┬────────┘
                                 │
                         ┌───────▼────────┐
                         │DocumentFilePage│
                         │  - page_number │
                         │  - content     │
                         └────────────────┘
                                 
     ┌─────────────────────────────────────────────────────────────────────┐
     │                     DAM Extension Layer                             │
     │                                                                     │
     │  Document ──────────► DocumentAIAnalysis                           │
     │                       - ai_description                              │
     │                       - ai_tags (JSON)                              │
     │                       - dominant_colors (JSON)                      │
     │                       - categories (JSON)                           │
     │                       - people (JSON)                               │
     │                       - locations (JSON)                            │
     │                       - analysis_status                             │
     │                       - ai_provider                                 │
     └─────────────────────────────────────────────────────────────────────┘
```

---

## 7. Storage Backends

### 7.1 Поддерживаемые Storage Backends

| Backend | Class | Use Case |
|---------|-------|----------|
| **Local File System** | `django.core.files.storage.FileSystemStorage` | Default, development |
| **S3 Compatible** | `mayan.apps.documents.storages.BegetS3Boto3Storage` | Production (Beget, AWS) |
| **Compressed** | `mayan.apps.storage.backends.compressedstorage.ZipCompressedPassthroughStorage` | Space optimization |
| **Encrypted** | `mayan.apps.storage.backends.encryptedstorage.EncryptedPassthroughStorage` | Security |

### 7.2 S3 Storage Configuration

```python
# Environment variables / settings
STORAGE_S3_ENABLED = True/False
STORAGE_S3_ENDPOINT_URL = 'https://s3.ru1.storage.beget.cloud'  # Beget
STORAGE_S3_ACCESS_KEY = 'your-access-key'
STORAGE_S3_SECRET_KEY = 'your-secret-key'
STORAGE_S3_BUCKET_NAME = 'your-bucket'
STORAGE_S3_REGION_NAME = 'ru-1'
STORAGE_S3_USE_SSL = True
STORAGE_S3_VERIFY = True
STORAGE_S3_LOCATION = ''  # Optional prefix
STORAGE_S3_DISTRIBUTION_LOCATION = 'PRIME/publications'  # Distribution prefix
```

### 7.3 Beget S3 Custom Backend

```python
# mayan/apps/documents/storages.py
class BegetS3Boto3Storage(S3Boto3Storage):
    """
    Custom storage backend for Beget S3.
    Bypasses boto3's TransferManager to avoid SignatureDoesNotMatch errors.
    Uses direct put_object() instead of upload_fileobj().
    """
    def _save(self, name, content):
        # Direct S3 put_object for Beget compatibility
        client.put_object(
            Bucket=self.bucket_name, 
            Key=name, 
            Body=upload_content, 
            **params
        )
```

---

## 8. AI Провайдеры

### 8.1 BaseAIProvider Interface

```python
# mayan/apps/dam/ai_providers/base.py

class BaseAIProvider(metaclass=abc.ABCMeta):
    """Базовый класс для всех AI провайдеров"""
    
    # Метаданные провайдера
    name = None
    display_name = None
    description = None
    
    # Capabilities
    supports_vision = False
    supports_text = True
    supports_image_description = False
    supports_tag_extraction = False
    supports_color_analysis = False
    
    @abc.abstractmethod
    def analyze_image(self, image_data: bytes, mime_type: str) -> Dict[str, Any]:
        """Анализ изображения и извлечение метаданных"""
        pass
    
    @abc.abstractmethod
    def describe_image(self, image_data: bytes, mime_type: str) -> str:
        """Генерация текстового описания"""
        pass
    
    @abc.abstractmethod
    def extract_tags(self, image_data: bytes, mime_type: str) -> List[str]:
        """Извлечение тегов"""
        pass
    
    @abc.abstractmethod
    def extract_colors(self, image_data: bytes, mime_type: str) -> List[Dict]:
        """Извлечение доминантных цветов"""
        pass
```

### 8.2 Зарегистрированные провайдеры

```python
AIProviderRegistry.register('qwenlocal', 'mayan.apps.dam.ai_providers.qwen_local.LocalQwenVisionProvider')
AIProviderRegistry.register('gigachat', 'mayan.apps.dam.ai_providers.gigachat.GigaChatProvider')
AIProviderRegistry.register('openai', 'mayan.apps.dam.ai_providers.openai.OpenAIProvider')
AIProviderRegistry.register('claude', 'mayan.apps.dam.ai_providers.claude.ClaudeProvider')
AIProviderRegistry.register('gemini', 'mayan.apps.dam.ai_providers.gemini.GeminiProvider')
AIProviderRegistry.register('yandexgpt', 'mayan.apps.dam.ai_providers.yandex.YandexGPTProvider')
AIProviderRegistry.register('kieai', 'mayan.apps.dam.ai_providers.kieai.KieAIProvider')
```

### 8.3 AI Analysis Response Format

```python
{
    'description': 'Текстовое описание изображения...',
    'tags': ['tag1', 'tag2', 'tag3'],
    'categories': ['Category1', 'Category2'],
    'language': 'ru',
    'people': ['Имя Человека'],
    'locations': ['Москва', 'Россия'],
    'copyright': 'Copyright notice',
    'usage_rights': 'License info',
    'colors': [
        {'hex': '#4A90D9', 'name': 'Sky Blue', 'percentage': 30},
        {'hex': '#2E8B57', 'name': 'Sea Green', 'percentage': 25}
    ],
    'alt_text': 'Alt text for accessibility',
    'provider': 'qwenlocal'
}
```

---

## 9. Celery Tasks

### 9.1 DAM Tasks (`mayan/apps/dam/tasks.py`)

| Task | Queue | Max Retries | Description |
|------|-------|-------------|-------------|
| `analyze_document_with_ai` | `documents` | 3 | Анализ документа через AI |
| `import_yandex_disk` | `documents` | 0 | Импорт из Yandex Disk |
| `bulk_analyze_documents` | `documents` | 0 | Массовый AI анализ |

### 9.2 Core Mayan Tasks

| Task | Queue | Description |
|------|-------|-------------|
| `task_process_document_upload` | `uploads` | Обработка загрузки |
| `task_document_file_content_process` | `documents` | Извлечение контента |
| `task_document_file_page_image_generate` | `converter` | Генерация превью |
| `task_document_version_page_image_generate` | `converter` | Генерация страниц |
| `task_document_type_periodic_processing` | `tools` | Периодическая обработка |
| `task_index_instance` | `indexing` | Индексация для поиска |
| `task_ocr_document_version` | `ocr` | OCR обработка |
| `task_check_expired_checkouts` | `checkouts` | Проверка checkouts |
| `task_send_email` | `mailing` | Отправка email |

### 9.3 Celery Queues

```python
CELERY_QUEUES = {
    'celery': {},           # Default queue
    'uploads': {},          # Upload processing
    'documents': {},        # Document processing
    'converter': {},        # Image conversion
    'indexing': {},         # Search indexing
    'ocr': {},              # OCR processing
    'mailing': {},          # Email sending
    'tools': {},            # Tools/utilities
    'checkouts': {},        # Checkout management
}
```

---

## 10. Система прав доступа (ACL)

### 10.1 Permission Model

```python
# mayan/apps/permissions/models.py
class Permission(models.Model):
    codename = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    

# mayan/apps/acls/models.py
class AccessControlList(models.Model):
    """Object-level permissions"""
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    permissions = models.ManyToManyField(StoredPermission)
    role = models.ForeignKey(Role)
```

### 10.2 Document Permissions

```python
# mayan/apps/documents/permissions.py
permission_document_create = Permission('documents.document_create')
permission_document_view = Permission('documents.document_view')
permission_document_edit = Permission('documents.document_edit')
permission_document_trash = Permission('documents.document_trash')
permission_document_delete = Permission('documents.document_delete')
permission_document_download = Permission('documents.document_download')
permission_document_properties_edit = Permission('documents.document_properties_edit')
permission_document_file_new = Permission('documents.document_file_new')
permission_document_file_delete = Permission('documents.document_file_delete')
permission_document_file_download = Permission('documents.document_file_download')
permission_document_file_view = Permission('documents.document_file_view')
permission_document_version_create = Permission('documents.document_version_create')
permission_document_version_delete = Permission('documents.document_version_delete')
permission_document_version_view = Permission('documents.document_version_view')
permission_document_version_export = Permission('documents.document_version_export')
```

### 10.3 DAM Permissions

```python
# mayan/apps/dam/permissions.py
permission_ai_analysis_create = Permission('dam.ai_analysis_create')
permission_ai_analysis_view = Permission('dam.ai_analysis_view')
permission_ai_analysis_edit = Permission('dam.ai_analysis_edit')
permission_dam_analyze = Permission('dam.dam_analyze')
```

### 10.4 ACL Check in API Views

```python
# Проверка доступа к объекту
AccessControlList.objects.check_access(
    obj=document,
    permissions=(permission_document_view,),
    user=request.user
)

# Фильтрация queryset по правам
queryset = AccessControlList.objects.restrict_queryset(
    permission=permission_document_view,
    queryset=Document.objects.all(),
    user=request.user
)
```

---

## 11. Frontend ↔ Backend соответствие

### 11.1 Текущий маппинг сервисов

| Frontend Service | Backend Endpoint | Статус |
|------------------|------------------|--------|
| `authService.login()` | `POST /api/v4/auth/token/obtain/` | ✅ Работает |
| `authService.getCurrentUser()` | `GET /api/v4/user_management/users/current/` | ✅ Работает |
| `uploadService.uploadAsset()` | `POST /api/v4/documents/` + `POST .../files/` | ✅ Работает |
| `assetStore.fetchAssets()` | `GET /api/v4/documents/` | ✅ Работает |
| **`assetService.getAssets()`** | **`GET /v4/dam/assets/`** | ❌ **НЕ СУЩЕСТВУЕТ** |
| **`assetService.searchAssets()`** | **`POST /v4/dam/assets/search/`** | ❌ **НЕ СУЩЕСТВУЕТ** |

### 11.2 Правильные endpoints для интеграции

```typescript
// ✅ Корректные endpoints для нового фронтенда

// Документы (базовые операции)
GET  /api/v4/documents/                    // Список документов
POST /api/v4/documents/                    // Создание документа
GET  /api/v4/documents/{id}/               // Детали документа
PATCH /api/v4/documents/{id}/              // Обновление метаданных
DELETE /api/v4/documents/{id}/             // Удаление (в корзину)
POST /api/v4/documents/{id}/files/         // Загрузка файла
GET  /api/v4/documents/{id}/files/{fid}/download/  // Скачивание

// DAM с AI-данными
GET  /api/dam/documents/                   // Список с AI-анализом
GET  /api/dam/document-detail/{id}/        // Детали + AI данные
POST /api/dam/ai-analysis/analyze/         // Запуск AI анализа
POST /api/dam/ai-analysis/bulk-analyze/    // Массовый анализ

// Изображения страниц
GET  /api/v4/documents/{id}/versions/latest/pages/1/image/           // Thumbnail
GET  /api/v4/documents/{id}/versions/latest/pages/1/image/?width=800 // Preview
GET  /api/v4/documents/{id}/files/{fid}/pages/{pid}/image/           // File page

// Теги
GET  /api/v4/tags/                         // Все теги
POST /api/v4/documents/{id}/tags/          // Добавить тег

// Кабинеты (папки)
GET  /api/v4/cabinets/                     // Все кабинеты
POST /api/v4/cabinets/{id}/documents/      // Добавить в кабинет

// Поиск
GET  /api/v4/search/?q=query               // Полнотекстовый поиск

// Метаданные
GET  /api/v4/documents/{id}/metadata/      // Метаданные документа
```

---

## 12. Критические проблемы

### 12.1 🔴 CRITICAL: assetService.ts использует несуществующие endpoints

**Файл:** `frontend/src/services/assetService.ts`

```typescript
// ❌ НЕПРАВИЛЬНО — эти endpoints НЕ существуют
'/v4/dam/assets/'           // Должно быть: /api/v4/documents/ или /api/dam/documents/
'/v4/dam/assets/search/'    // Должно быть: /api/v4/search/
'/v4/dam/assets/bulk/'      // Должно быть: /api/dam/ai-analysis/bulk-analyze/
```

### 12.2 🔴 CRITICAL: Mock режим persist в localStorage

**Файл:** `frontend/src/stores/assetStore.ts`

Переменная `useMock` сохраняется в localStorage через Pinia persist, что приводит к показу mock данных даже после авторизации.

### 12.3 🟡 WARNING: LoginPage использует type="email"

**Файл:** `frontend/src/pages/LoginPage.vue`

Поле ввода имеет `type="email"`, но backend ожидает `username`.

---

## 13. Рекомендации по интеграции

### 13.1 Создание Document Adapter

```typescript
// frontend/src/services/adapters/documentAdapter.ts

interface MayanDocument {
  id: number
  label: string
  datetime_created: string
  document_type: { id: number; label: string }
  description: string
  language: string
  uuid: string
  file_latest?: {
    id: number
    filename: string
    mimetype: string
    size: number
    download_url: string
  }
}

interface Asset {
  id: number
  title: string
  filename: string
  type: 'image' | 'video' | 'document' | 'audio'
  status: 'active' | 'pending' | 'archived'
  thumbnail_url: string
  preview_url: string
  download_url: string
  file_size: number
  mime_type: string
  created_at: string
  tags: string[]
  metadata: Record<string, any>
  ai_description?: string
  ai_tags?: string[]
  dominant_colors?: Array<{hex: string; name: string}>
}

export function adaptMayanDocument(doc: MayanDocument): Asset {
  const fileLatest = doc.file_latest
  
  return {
    id: doc.id,
    title: doc.label,
    filename: fileLatest?.filename || doc.label,
    type: getMimeCategory(fileLatest?.mimetype),
    status: 'active',
    thumbnail_url: `/api/v4/documents/${doc.id}/versions/latest/pages/1/image/?width=150&height=150`,
    preview_url: `/api/v4/documents/${doc.id}/versions/latest/pages/1/image/?width=800`,
    download_url: fileLatest?.download_url || '',
    file_size: fileLatest?.size || 0,
    mime_type: fileLatest?.mimetype || 'application/octet-stream',
    created_at: doc.datetime_created,
    tags: [],
    metadata: {}
  }
}

function getMimeCategory(mimetype?: string): Asset['type'] {
  if (!mimetype) return 'document'
  if (mimetype.startsWith('image/')) return 'image'
  if (mimetype.startsWith('video/')) return 'video'
  if (mimetype.startsWith('audio/')) return 'audio'
  return 'document'
}
```

### 13.2 Рекомендуемый .env файл

```bash
# Frontend .env
VITE_API_URL=http://localhost:8080
VITE_USE_MOCK_DATA=false
VITE_USE_REAL_API=true

# Backend environment
MAYAN_DATABASES='{"default":{"ENGINE":"django.db.backends.postgresql","NAME":"mayan","USER":"mayan","PASSWORD":"mayandbpass","HOST":"postgresql","PORT":"5432"}}'
MAYAN_CELERY_BROKER_URL=amqp://mayan:mayanrabbitpass@rabbitmq:5672/mayan
MAYAN_CELERY_RESULT_BACKEND=redis://redis:6379/0
MAYAN_LOCK_MANAGER_BACKEND=mayan.apps.lock_manager.backends.redis_lock.RedisLock
MAYAN_LOCK_MANAGER_BACKEND_ARGUMENTS='{"redis_url":"redis://redis:6379/1"}'

# S3 Storage (optional)
MAYAN_STORAGE_S3_ENABLED=true
MAYAN_STORAGE_S3_ENDPOINT_URL=https://s3.ru1.storage.beget.cloud
MAYAN_STORAGE_S3_ACCESS_KEY=your-key
MAYAN_STORAGE_S3_SECRET_KEY=your-secret
MAYAN_STORAGE_S3_BUCKET_NAME=your-bucket
MAYAN_STORAGE_S3_REGION_NAME=ru-1

# AI Providers
MAYAN_DAM_AI_ANALYSIS_ENABLED=true
MAYAN_DAM_QWENLOCAL_API_URL=http://192.168.1.25:11434/api/generate
MAYAN_DAM_QWENLOCAL_MODEL=qwen3-vl:8b-instruct
MAYAN_DAM_GIGACHAT_CREDENTIALS=base64(client_id:client_secret)
```

---

## 📊 Сводная таблица API

| Категория | Endpoint Pattern | Методы |
|-----------|-----------------|--------|
| **Auth** | `/api/v4/auth/` | POST token |
| **Documents** | `/api/v4/documents/` | GET, POST, PATCH, DELETE |
| **Files** | `/api/v4/documents/{id}/files/` | GET, POST, DELETE |
| **Versions** | `/api/v4/documents/{id}/versions/` | GET, POST, DELETE |
| **Pages** | `.../pages/{id}/image/` | GET |
| **Tags** | `/api/v4/tags/` | GET, POST, PATCH, DELETE |
| **Cabinets** | `/api/v4/cabinets/` | GET, POST, PATCH, DELETE |
| **Metadata** | `/api/v4/metadata_types/` | GET, POST |
| **Search** | `/api/v4/search/` | GET |
| **DAM** | `/api/dam/` | GET, POST |
| **AI Analysis** | `/api/dam/ai-analysis/` | GET, POST |

---

**Документ обновлён:** 03 декабря 2025  
**Следующий ревью:** После интеграции нового фронтенда
