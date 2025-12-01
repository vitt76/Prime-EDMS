# Backend Analysis — Prime-EDMS / DAM System

**Дата анализа:** 28 ноября 2025  
**Эксперт:** Senior Backend Architect  
**Версия:** 1.0

---

## 1. Архитектурный обзор

### 1.1 Технологический стек

| Компонент | Версия / Технология |
|-----------|---------------------|
| **Python** | 3.x (Django 3.2.14) |
| **Framework** | Django 3.2.14 |
| **REST API** | Django REST Framework 3.13.1 |
| **База данных** | PostgreSQL (настраивается через settings) |
| **Task Queue** | Celery 5.2.3 + Redis |
| **Search Engine** | Whoosh 2.7.4 / Elasticsearch 7.17.1 |
| **Image Processing** | Pillow 9.2.0, CairoSVG 2.5.2 |
| **PDF Processing** | PyPDF2 1.28.4 |
| **Metadata Extraction** | EXIFTool (внешний бинарник) |
| **OCR** | Tesseract (через sh wrapper) |
| **Caching** | Redis / Django Cache Framework |
| **API Documentation** | drf-yasg (Swagger/OpenAPI) |
| **Async** | Gevent 21.12.0 |
| **Security** | python-gnupg, pycryptodome |

### 1.2 Структура приложений

Проект построен на базе **Mayan EDMS** с кастомными расширениями. Ключевые приложения:

#### Ядро системы (Core Mayan)
- `documents` — основная модель документов, версий, файлов, страниц
- `metadata` — типизированные метаданные
- `tags` — теги и классификация
- `cabinets` — папки/шкафы для организации
- `acls` — Access Control Lists (RBAC)
- `permissions` — роли и права доступа

#### [CUSTOM] DAM-расширение
- `dam` — **кастомный модуль** AI-анализа и управления цифровыми активами
- `distribution` — **кастомный модуль** дистрибуции и публикации контента

#### Обработка контента
- `converter` — конвертация форматов, генерация превью
- `ocr` — оптическое распознавание текста
- `document_parsing` — извлечение текста
- `file_metadata` — извлечение EXIF и технических метаданных

#### Автоматизация
- `document_states` — workflows и состояния документов
- `document_indexing` — автоматическая индексация
- `dynamic_search` — полнотекстовый поиск (Whoosh/Elasticsearch)

#### Источники контента
- `sources` — бэкенды загрузки (Web Form, Email, Staging Folder, Watch Folder)

---

## 2. Модель данных (Core Entities)

### 2.1 Основные сущности

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   DocumentType  │◄────│    Document     │────►│ DocumentVersion │
└─────────────────┘     └────────┬────────┘     └────────┬────────┘
                                 │                       │
                                 │                       │
                        ┌────────▼────────┐     ┌────────▼────────┐
                        │  DocumentFile   │     │DocumentVersionPage│
                        └────────┬────────┘     └─────────────────┘
                                 │
                        ┌────────▼────────┐
                        │DocumentFilePage │
                        └─────────────────┘
```

### 2.2 Document (Основная сущность)

```python
# mayan/apps/documents/models/document_models.py
class Document(ExtraDataModelMixin, HooksModelMixin, models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    document_type = models.ForeignKey(DocumentType, ...)
    label = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    datetime_created = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=8, default='en')
    in_trash = models.BooleanField(default=False)
    is_stub = models.BooleanField(default=True)
```

**Ключевые связи:**
- `document.files` — все файлы документа (ForeignKey)
- `document.versions` — все версии документа
- `document.metadata` — метаданные (ManyToMany через pivot)
- `document.tags` — теги
- `document.ai_analysis` — [CUSTOM] OneToOne на AI-анализ

### 2.3 [CUSTOM] DocumentAIAnalysis (DAM-расширение)

```python
# mayan/apps/dam/models.py
class DocumentAIAnalysis(ExtraDataModelMixin, models.Model):
    document = models.OneToOneField(Document, related_name='ai_analysis')
    
    # AI-генерируемые поля
    ai_description = models.TextField()           # Описание контента
    ai_tags = models.JSONField()                  # ["тег1", "тег2", ...]
    categories = models.JSONField()               # Категории
    dominant_colors = models.JSONField()          # Доминирующие цвета
    alt_text = models.CharField(max_length=255)   # Alt-текст для accessibility
    
    # NER-извлечение
    people = models.JSONField()                   # Распознанные люди
    locations = models.JSONField()                # Геолокации
    language = models.CharField(max_length=20)    # Язык контента (BCP-47)
    
    # Права/Governance
    copyright_notice = models.TextField()
    usage_rights = models.TextField()
    rights_expiry = models.DateField()
    
    # Метаданные обработки
    ai_provider = models.CharField(max_length=50)
    analysis_status = models.CharField(choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ])
    analysis_completed = models.DateTimeField()
```

### 2.4 MetadataType (Пользовательские метаданные)

```python
# mayan/apps/metadata/models.py
class MetadataType(models.Model):
    name = models.CharField(max_length=48, unique=True)
    label = models.CharField(max_length=48)
    default = models.CharField(max_length=128)    # Template-значение
    lookup = models.TextField()                   # Lookup-шаблон (comma-separated)
    validation = models.CharField(max_length=224) # Валидатор (Python path)
    parser = models.CharField(max_length=224)     # Парсер (Python path)
```

### 2.5 [CUSTOM] Distribution Models (Публикация)

```python
# mayan/apps/distribution/models.py
class Recipient(models.Model):          # Внешние получатели
class RecipientList(models.Model):      # Списки рассылки
class RenditionPreset(models.Model):    # Пресеты конвертации (размер, формат, quality)
class Publication(models.Model):        # Публикация документов
class PublicationAsset(models.Model):   # Связь публикация <-> документ
class SharedLink(models.Model):         # Публичные ссылки с TTL и паролем
```

---

## 3. Детальный функциональный анализ

### 3.1 Ingestion (Загрузка контента)

#### Реализованные источники загрузки

| Источник | Backend Class | Описание |
|----------|---------------|----------|
| **Web Upload** | `WebFormSourceBackend` | Загрузка через браузер |
| **Email** | `EmailSourceBackend` | Импорт из почтовых ящиков |
| **Staging Folder** | `StagingFolderSourceBackend` | Промежуточная папка |
| **Watch Folder** | `WatchFolderSourceBackend` | Автоимпорт из папки |
| **[CUSTOM] Yandex Disk** | `YandexDiskImporter` | Интеграция с Яндекс.Диском |

#### Процесс загрузки

```
1. Source.handle_file_object_upload()
   ├─ Проверка на архив (Archive.open())
   │   └─ Рекурсивная распаковка вложенных файлов
   ├─ SharedUploadedFile.objects.create()
   └─ task_document_upload.apply_async()
       ├─ Document.file_new()
       │   ├─ DocumentFile.save()
       │   └─ DocumentFileAction.execute()  # Версионирование
       └─ callback_post_task_document_upload()
           └─ layer_saved_transformations.copy_transformations()
```

#### [CUSTOM] Yandex Disk Integration

```python
# mayan/apps/dam/services/yandex_disk.py
class YandexDiskClient:
    def list_files(self, path) -> List[Dict]
    def download_file(self, path) -> bytes
    def get_download_link(self, path) -> str

class YandexDiskImporter:
    def run(self) -> int  # Возвращает кол-во импортированных файлов
    # Создаёт Cabinet-структуру, сохраняет YandexDiskImportRecord
```

### 3.2 Processing & Transformation

#### Генерация превью и конвертация

```python
# mayan/apps/converter/models.py
class Asset(models.Model):
    # Водяные знаки, логотипы для наложения
    def generate_image() -> cache_filename
    def get_image() -> PIL.Image

# mayan/apps/converter/transformations.py
class BaseTransformation:
    # Rotate, Crop, Resize, Zoom, Watermark, etc.
```

**Поддерживаемые форматы (через Pillow):**
- JPEG, PNG, GIF, WebP, TIFF
- PDF (через PyPDF2 + CairoSVG)
- SVG → PNG конвертация

#### [CUSTOM] AI-обработка изображений

```python
# mayan/apps/dam/tasks.py
@shared_task(bind=True, max_retries=3, queue='documents')
def analyze_document_with_ai(self, document_id: int):
    """
    1. Получить document_file
    2. Проверить размер (max 10MB для AI)
    3. При необходимости сжать через _shrink_image_bytes()
    4. Попробовать провайдеров по цепочке fallback
    5. Сохранить результаты в DocumentAIAnalysis
    6. Переиндексировать для поиска
    """
```

**AI Provider Chain (Fallback):**
1. `qwenlocal` — локальная Qwen Vision модель (Ollama)
2. `gigachat` — Сбер GigaChat API
3. `openai` — GPT-4 Vision
4. `claude` — Anthropic Claude 3
5. `gemini` — Google Gemini Pro Vision
6. `yandexgpt` — Яндекс GPT
7. `kieai` — Kie.ai OCR/Generation

### 3.3 Metadata & AI

#### Извлечение EXIF

```python
# mayan/apps/file_metadata/drivers/exiftool.py
class EXIFToolDriver(FileMetadataDriver):
    label = 'EXIF Tool'
    internal_name = 'exiftool'
    
    def _process(self, document_file):
        # Вызов внешнего exiftool бинарника
        # Парсинг JSON-вывода
        # Сохранение в FileMetadataEntry
```

Извлекаемые поля:
- Камера, объектив, ISO, выдержка, диафрагма
- Дата съёмки, GPS-координаты
- Цветовое пространство, разрешение
- IPTC/XMP теги

#### [CUSTOM] AI-генерируемые метаданные

| Поле | Источник | Тип |
|------|----------|-----|
| `ai_description` | Vision LLM | Text |
| `ai_tags` | Vision LLM | JSON Array |
| `categories` | Vision LLM | JSON Array |
| `people` | NER | JSON Array |
| `locations` | NER | JSON Array |
| `dominant_colors` | Color Analysis | JSON Array |
| `alt_text` | Vision LLM | Text |
| `language` | LangDetect | BCP-47 |

### 3.4 Search (Поиск)

#### Бэкенды поиска

```python
# mayan/apps/dynamic_search/backends/whoosh.py
class WhooshSearchBackend(SearchBackend):
    # Локальный индекс на файловой системе
    # Подходит для небольших инсталляций

# mayan/apps/dynamic_search/backends/elasticsearch.py  
class ElasticsearchSearchBackend(SearchBackend):
    # Elasticsearch 7.x
    # Рекомендуется для production
```

#### [CUSTOM] Расширение поиска AI-полями

```python
# mayan/apps/dam/search.py
def extend_document_search():
    """
    Добавляет AI-поля к стандартным SearchModel:
    - ai_description, ai_tags, categories
    - people, locations, dominant_colors
    - language, ai_provider, analysis_status
    
    Использует transformation functions для JSON→Text
    """
    search_model_document.add_model_field(
        field='ai_analysis__ai_tags',
        label='AI Tags',
        transformation_function=transformation_ai_tags_to_string
    )
```

### 3.5 Permissions (ACL)

#### RBAC-модель

```
User ←────────→ Group ←────────→ Role ←────────→ Permission
                                   │
                                   ▼
                          AccessControlList
                                   │
                           ┌───────┴───────┐
                           │               │
                      Document         Cabinet
                           │               │
                      (object ACL)   (inherited)
```

```python
# mayan/apps/acls/models.py
class AccessControlList(models.Model):
    content_type = models.ForeignKey(ContentType)  # Тип объекта
    object_id = models.PositiveIntegerField()      # ID объекта
    role = models.ForeignKey(Role)                 # Роль
    permissions = models.ManyToManyField(StoredPermission)
    
    @classmethod
    def check_access(cls, obj, permissions, user) -> bool
    
    @classmethod
    def restrict_queryset(cls, permission, queryset, user) -> QuerySet
```

#### [CUSTOM] DAM Permissions

```python
# mayan/apps/dam/permissions.py
permission_ai_analysis_create = ...
permission_ai_analysis_view = ...
```

---

## 4. API и Интеграции

### 4.1 REST API v4

#### Core Endpoints (Mayan)

| Endpoint | Методы | Описание |
|----------|--------|----------|
| `/api/v4/documents/` | GET, POST | Список/создание документов |
| `/api/v4/documents/{id}/` | GET, PATCH, DELETE | CRUD документа |
| `/api/v4/documents/{id}/files/` | GET, POST | Файлы документа |
| `/api/v4/document_types/` | GET, POST | Типы документов |
| `/api/v4/metadata_types/` | GET, POST | Типы метаданных |
| `/api/v4/tags/` | GET, POST | Теги |
| `/api/v4/cabinets/` | GET, POST | Шкафы/папки |
| `/api/v4/search/` | GET | Полнотекстовый поиск |

#### [CUSTOM] DAM API Endpoints

```python
# mayan/apps/dam/urls.py (api_urlpatterns)
/api/dam/ai-analysis/              # ViewSet: CRUD AI-анализов
/api/dam/ai-analysis/analyze/      # POST: Запуск анализа
/api/dam/ai-analysis/reanalyze/    # POST: Повторный анализ
/api/dam/ai-analysis/bulk-analyze/ # POST: Bulk-анализ
/api/dam/metadata-presets/         # ViewSet: CRUD пресетов
/api/dam/analysis-status/          # GET: Статус анализа
/api/dam/document-detail/{id}/     # GET: Детали документа (JSON)
/api/dam/documents/                # GET: Список документов с AI
/api/dam/dashboard-stats/          # GET: Статистика дашборда
```

### 4.2 OpenAPI/Swagger

Автоматическая документация через `drf-yasg`:
- `/api/swagger/` — Swagger UI
- `/api/redoc/` — ReDoc UI
- `/api/swagger.json` — OpenAPI spec

### 4.3 [CUSTOM] AI Provider Interface

```python
# mayan/apps/dam/ai_providers/base.py
class BaseAIProvider(metaclass=abc.ABCMeta):
    # Capabilities
    supports_vision: bool
    supports_image_description: bool
    supports_tag_extraction: bool
    supports_color_analysis: bool
    
    @abc.abstractmethod
    def analyze_image(self, image_data: bytes, mime_type: str) -> Dict[str, Any]
    
    @abc.abstractmethod
    def describe_image(self, image_data: bytes, mime_type: str) -> str
    
    @abc.abstractmethod
    def extract_tags(self, image_data: bytes, mime_type: str) -> List[str]
    
    @abc.abstractmethod
    def extract_colors(self, image_data: bytes, mime_type: str) -> List[Dict]
    
    def is_available(self) -> bool

class AIProviderRegistry:
    @classmethod
    def register(cls, provider_id: str, provider_class_path: str)
    
    @classmethod
    def get_provider_class(cls, provider_id: str) -> Type[BaseAIProvider]
    
    @classmethod
    def create_provider(cls, provider_id: str, **kwargs) -> BaseAIProvider
```

---

## 5. Скрытая логика (Automation)

### 5.1 Workflows (Document States)

```python
# mayan/apps/document_states/models/workflow_models.py
class Workflow(models.Model):
    auto_launch = models.BooleanField(default=True)  # Авто-запуск при создании
    label = models.CharField(max_length=255)
    document_types = models.ManyToManyField(DocumentType)
    
    def render(self) -> bytes  # GraphViz диаграмма
```

**Структура Workflow:**
```
Workflow
  └── WorkflowState (состояния)
        ├── initial = True/False
        ├── completion = True/False
        └── WorkflowStateAction (действия при входе/выходе)
              └── HTTPAction, EmailAction, DocumentAction, etc.
  └── WorkflowTransition (переходы)
        ├── origin_state
        ├── destination_state
        └── condition (Python-выражение)
```

### 5.2 [CUSTOM] Auto AI Analysis (Signal)

```python
# mayan/apps/dam/signals.py
@receiver(post_save, sender=DocumentFile)
def trigger_ai_analysis(sender, instance, created, **kwargs):
    """
    Автоматический запуск AI-анализа при загрузке нового файла.
    
    Условия:
    - DAM_AI_ANALYSIS_AUTO_TRIGGER = True
    - created = True (новый файл)
    - Нет завершённого анализа
    
    Действия:
    1. Создать DocumentAIAnalysis (status='pending')
    2. Запланировать analyze_document_with_ai.apply_async(countdown=5)
    """
```

### 5.3 Smart Links & Indexing

```python
# mayan/apps/linking/
# Динамические ссылки между документами на основе метаданных

# mayan/apps/document_indexing/
# Автоматическое построение древовидных индексов
# Шаблоны индексации на основе метаданных и тегов
```

### 5.4 Celery Tasks & Queues

#### Очереди

```python
# mayan/apps/dam/queues.py
queue_ai_analysis = {
    'name': 'dam_ai_analysis',
    'label': 'DAM AI Analysis',
    'worker': 'worker_d'
}

queue_bulk_operations = {
    'name': 'dam_bulk_operations', 
    'label': 'DAM Bulk Operations',
    'worker': 'worker_d'
}
```

#### Ключевые задачи

| Task | Queue | Описание |
|------|-------|----------|
| `analyze_document_with_ai` | documents | AI-анализ одного документа |
| `bulk_analyze_documents` | documents | Массовый AI-анализ |
| `import_yandex_disk` | documents | Импорт из Яндекс.Диска |
| `task_document_upload` | uploads | Обработка загрузки |
| `task_document_version_ocr_process` | ocr | OCR-обработка |
| `task_index_instance` | indexing | Индексация для поиска |

---

## 6. Конфигурация и настройки

### 6.1 [CUSTOM] DAM Settings

```python
# mayan/apps/dam/settings.py (ключевые настройки)

# AI Analysis
DAM_AI_ANALYSIS_ENABLED = True
DAM_AI_ANALYSIS_AUTO_TRIGGER = True
DAM_AI_ANALYSIS_TIMEOUT = 120
DAM_AI_ANALYSIS_MAX_RETRIES = 3
DAM_AI_PROVIDERS_ACTIVE = ['qwenlocal', 'gigachat', 'openai', ...]

# Provider-specific
DAM_QWENLOCAL_API_URL = 'http://192.168.1.25:11434/api/generate'
DAM_QWENLOCAL_MODEL = 'qwen3-vl:8b-instruct'
DAM_GIGACHAT_CREDENTIALS = ''  # base64(client_id:client_secret)
DAM_OPENAI_API_KEY = ''
DAM_CLAUDE_API_KEY = ''
DAM_GEMINI_API_KEY = ''
DAM_YANDEXGPT_API_KEY = ''
DAM_KIEAI_API_KEY = ''

# Yandex Disk
DAM_YANDEX_DISK_TOKEN = ''
DAM_YANDEX_DISK_BASE_PATH = '/'
DAM_YANDEX_DISK_MAX_FILE_SIZE = 20 * 1024 * 1024
DAM_YANDEX_DISK_FILE_LIMIT = 500

# Performance
DAM_ANALYSIS_IMAGE_MAX_SIZE = 10 * 1024 * 1024
DAM_ANALYSIS_CONCURRENT_LIMIT = 2
```

### 6.2 Throttling (Rate Limiting)

```python
# mayan/apps/dam/throttles.py
class AIAnalysisThrottle(UserRateThrottle):
    scope = 'ai_analysis'
    rate = '10/minute'  # Агрессивный лимит для AI
```

---

## 7. Резюме по функциональности

### 7.1 Что система УМЕЕТ делать (Реализовано)

| Функция | Статус | Примечание |
|---------|--------|------------|
| **Ingestion** |||
| Web Upload | ✅ Core | Drag&drop, multi-file |
| Email Import | ✅ Core | IMAP/POP3 |
| Watch Folder | ✅ Core | Auto-import |
| Yandex Disk Import | ✅ [CUSTOM] | OAuth + folder sync |
| **Processing** |||
| Thumbnail Generation | ✅ Core | Multiple sizes |
| PDF Preview | ✅ Core | Page-by-page |
| Image Resize/Crop | ✅ Core | Transformations |
| OCR | ✅ Core | Tesseract |
| EXIF Extraction | ✅ Core | EXIFTool driver |
| AI Vision Analysis | ✅ [CUSTOM] | Multi-provider fallback |
| **Metadata** |||
| Custom Metadata Types | ✅ Core | Validation, Lookup |
| Tags | ✅ Core | Hierarchical |
| AI-generated Tags | ✅ [CUSTOM] | Auto-tagging |
| NER (People/Locations) | ✅ [CUSTOM] | Entity extraction |
| **Search** |||
| Full-text Search | ✅ Core | Whoosh/Elasticsearch |
| AI Metadata Search | ✅ [CUSTOM] | JSON transformation |
| Faceted Search | ✅ Core | Elasticsearch |
| **Security** |||
| RBAC | ✅ Core | Roles/Groups |
| Object-level ACL | ✅ Core | Per-document |
| API Throttling | ✅ [CUSTOM] | Rate limiting |
| **Automation** |||
| Workflows | ✅ Core | State machine |
| Auto AI Analysis | ✅ [CUSTOM] | Signal-based |
| Smart Links | ✅ Core | Dynamic linking |
| **Distribution** |||
| Recipient Lists | ✅ [CUSTOM] | Internal + External |
| Rendition Presets | ✅ [CUSTOM] | Format conversion |
| Shared Links | ✅ [CUSTOM] | TTL + Password |

### 7.2 Архитектурные особенности

**Сильные стороны:**
- Чистое расширение Mayan через OneToOneField (не патчит core)
- Pluggable AI providers с fallback chain
- Async processing через Celery
- ACL-проверки на всех уровнях API
- Полноценная интеграция с поиском

**Области для улучшения:**
- Нет video processing (FFmpeg интеграция)
- Нет CDN для thumbnails
- Нет GraphQL API
- Нет MCP Server для AI интеграций

---

## 8. Рекомендации

### 8.1 Для Production

1. **Переключить поиск на Elasticsearch** для масштабируемости
2. **Настроить S3-совместимый storage** для файлов
3. **Увеличить workers** для AI-анализа при большом объёме
4. **Настроить CDN** для раздачи превью
5. **Мониторинг** через Sentry + Prometheus

### 8.2 Для развития DAM

1. **Video Processing** — интеграция FFmpeg для видео-превью
2. **Face Recognition** — расширение people extraction
3. **Similarity Search** — vector embeddings для "похожие изображения"
4. **Batch Operations UI** — массовое редактирование метаданных
5. **Asset Lifecycle** — архивирование, TTL, retention policies

---

*Документ сгенерирован на основе анализа исходного кода проекта Prime-EDMS.*

