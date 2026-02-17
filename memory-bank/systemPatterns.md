# System Patterns: Prime-EDMS

## Архитектурный стиль

### Монолитная модульная архитектура

Проект следует архитектуре **Django Monolith с модульной структурой приложений**. Все функциональность организована в виде отдельных Django apps внутри единого проекта, что обеспечивает:

- **Модульность**: Каждая функция реализована как отдельное приложение в `mayan/apps/`
- **Расширяемость**: Новые функции добавляются через создание новых apps без изменения core
- **Единая кодовая база**: Все компоненты находятся в одном репозитории и деплоятся вместе

## Структура проекта

### Иерархия директорий

```
Prime-EDMS/
├── mayan/                    # Основной код приложения
│   ├── apps/                 # Django приложения (модули)
│   │   ├── dam/              # DAM расширение (кастомное)
│   │   ├── documents/        # Управление документами (core)
│   │   ├── analytics/        # Аналитика (кастомное)
│   │   ├── headless_api/     # REST API для фронтенда (кастомное)
│   │   ├── image_editor/      # Редактор изображений (кастомное)
│   │   └── ...               # Другие core и кастомные apps
│   ├── settings/             # Конфигурация Django
│   ├── urls/                 # URL маршрутизация
│   └── asgi.py/wsgi.py       # ASGI/WSGI точки входа
├── frontend/                 # Vue 3 SPA фронтенд
├── public-frontend/          # Nuxt 3 публичный фронтенд
├── docker/                   # Docker конфигурация
├── requirements/             # Python зависимости
└── docker-compose.yml        # Docker Compose конфигурация
```

## Паттерны проектирования

### 1. Django App Pattern

Каждая функциональная область реализована как отдельное Django приложение:

**Пример структуры app:**
```
mayan/apps/dam/
├── models.py          # Модели данных
├── views.py           # Представления (views)
├── api_views.py       # REST API endpoints
├── serializers.py     # DRF сериализаторы
├── tasks.py           # Celery задачи
├── signals.py         # Django signals
├── urls.py            # URL маршруты
├── permissions.py     # Права доступа
├── apps.py            # Конфигурация приложения
└── migrations/        # Миграции БД
```

**Преимущества:**
- Изоляция функциональности
- Переиспользование компонентов
- Простота тестирования
- Возможность отключения модулей

### 2. Extension Pattern (Расширение через OneToOneField)

Вместо модификации core моделей, используются связанные модели:

```python
# Пример из mayan/apps/dam/models.py
class DocumentAIAnalysis(TenantAwareMixin, ExtraDataModelMixin, models.Model):
    organization = models.ForeignKey('organizations.Organization', ...)  # tenant-aware
    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        related_name='ai_analysis'
    )
    # AI метаданные...
```

**Паттерн:**
- Core модели (Document) остаются неизменными
- Расширения через ForeignKey/OneToOneField
- Обратная совместимость с базовым Mayan EDMS
- Tenant-aware расширения (например DocumentAIAnalysis) добавляют TenantAwareMixin и явный FK organization; изоляция через TenantAwareManager и pre_save binding в organizations/apps.py

### 3. Celery Task Pattern

Асинхронная обработка через Celery с разделением на очереди:

```python
# Пример из mayan/apps/dam/tasks.py
@shared_task(bind=True, queue='ai_analysis')
def analyze_document_with_ai(self, document_id: int):
    # AI обработка...
```

**Очереди задач:**
- `converter`: Конвертация файлов
- `ai_analysis`: AI обработка (отдельный worker)
- `documents`: В т.ч. track_asset_event_async, generate_analytics_report (TenantAwareTask; отчёты — только JSON в MEDIA_ROOT/reports/{org_id}/)
- `sources_fast`: Быстрые операции с источниками
- `distribution`: Распределение контента
- `notifications`: Уведомления

**Workers:**
- `worker_a`: Основные задачи (converter, sources_fast, distribution, notifications)
- `worker_d`: AI анализ (ai_analysis очередь)

### 4. AI Provider Registry Pattern

Регистрация множественных AI провайдеров через паттерн Registry:

```python
# Пример из mayan/apps/dam/ai_providers/
class AIProviderRegistry:
    _providers = {}
    
    @classmethod
    def register(cls, name, provider_class):
        cls._providers[name] = provider_class
```

**Поддерживаемые провайдеры:**
- YandexGPT
- GigaChat
- OpenAI
- Claude
- Gemini
- Qwen Local
- KieAI

### 5. Storage Backend Pattern

Абстракция хранилища через Django storage backends:

- **Локальное**: `/var/lib/mayan`
- **S3**: Beget S3 через django-storages
- **Расширяемость**: Легко добавить новые backends

### 6. REST API Pattern

API-first подход с версионированием:

```
/api/v4/                    # API версия 4
├── auth/token/obtain/      # Аутентификация
├── documents/documents/   # Управление документами
├── headless/               # Headless API для фронтенда
│   ├── analytics/          # Аналитика
│   └── documents/          # Документы
└── ...
```

**Аутентификация:**
- Token-based (JWT)
- Session-based (для браузеров)

### 7. Signal Pattern

Автоматизация через Django signals:

```python
# Пример из mayan/apps/dam/signals.py
@receiver(post_save, sender=DocumentFile)
def trigger_ai_analysis(sender, instance, **kwargs):
    # Автоматический запуск AI анализа
```

**Использование:**
- Автоматический AI анализ при загрузке файла
- Инвалидация кэша при изменении данных
- Обновление индексов поиска

### 8. Search Extension Pattern

Расширение поиска через transformation функции:

```python
# Пример из mayan/apps/dam/search.py
def transform_ai_tags(value):
    # Преобразование JSON массива в строку для поиска
    return ' '.join(value) if isinstance(value, list) else ''
```

**Особенности:**
- GIN индексы для JSON полей (PostgreSQL)
- Transformation функции для поиска по массивам
- Интеграция с динамическим поиском Mayan

### 9. Tenant Isolation Pattern (Multi-tenancy)

**Архитектурный подход:** Shared Database + Shared Schema + ForeignKey изоляция

**Назначение:** Поддержка SaaS-модели (один backend, много клиентов) и Standalone-модели (один клиент на выделенном сервере).

**Статус:** Базовая инфраструктура реализована (Sprint 1-4 завершены). Интеграция с модулями (Part 3) в планировании.

**Компоненты:**

#### 9.1. Organization Model
```python
# mayan/apps/organizations/models.py
class Organization(models.Model):
    """Тенант / Компания для изоляции данных"""
    id = models.UUIDField(primary_key=True)
    name = models.CharField(unique=True)
    slug = models.SlugField(unique=True)
    deployment_mode = models.CharField(choices=['saas', 'standalone'])
    # Квоты: storage_limit_gb, max_users, max_ai_analyses_monthly
    # Статус: is_active, status (trial/active/suspended/archived)
```

#### 9.2. TenantAwareManager
```python
# Автоматическая фильтрация QuerySet по Organization
class TenantAwareManager(models.Manager):
    def get_queryset(self):
        organization = self._get_current_organization()
        if organization:
            return super().get_queryset().filter(organization=organization)
        return super().get_queryset()
```

#### 9.3. TenantAwareMixin
```python
# Миксин для tenant-aware моделей
class TenantAwareMixin(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    objects = TenantAwareManager()
    objects_unfiltered = models.Manager()  # Для админки
    
    class Meta:
        abstract = True
```

#### 9.4. TenantResolverMiddleware
```python
# Определение Organization по домену/токену
class TenantResolverMiddleware:
    def process_request(self, request):
        # 1. По кастомному домену
        # 2. По поддомену (app.dam-brand.com → dam-brand)
        # 3. По токену в Authorization header
        # 4. Standalone mode (default Organization)
        request.organization = self._resolve_organization(request)
```

**Tenant-aware модели:**
- Document, DocumentFile, DocumentVersion
- Cabinet, Tag, Metadata
- DocumentAIAnalysis (DAM)
- CampaignAsset, AssetEvent (Analytics)
- Publication, ShareLink (Distribution)

**Глобальные модели (НЕ tenant-aware):**
- Plan (тарифные планы)
- MetadataType (типизация метаданных)
- Source (источники загрузки)

**Режимы развертывания:**
- **SaaS**: Множественные организации на одном сервере
- **Standalone**: Одна организация по умолчанию (on-premises)

**Изоляция данных:**
- Все tenant-aware модели имеют FK на Organization
- Автоматическая фильтрация через TenantAwareManager
- Middleware устанавливает request.organization
- ContextVar для потокобезопасности в async контексте

**Безопасность:**
- 100% защита от cross-tenant access
- Индексы на organization_id для производительности
- Audit logging всех операций с Organization

**Масштабируемость:**
- Готовность к шардированию (future)
- Поддержка ≥100 тенантов на одном сервере
- Оптимизация запросов через select_related('organization')
- Composite индексы на (organization_id, timestamp) для производительности

**Code Style Rules:**
- Всегда используй `TenantAwareManager` для бизнес-логики
- Используй `.objects_unfiltered` только для SuperAdmin операций
- Celery tasks должны явно передавать `organization_id` в kwargs
- Все tenant-aware модели должны наследовать `TenantAwareMixin`
- Middleware устанавливает `request.organization` для всех запросов

**Текущая реализация (ЗАВЕРШЕНА — Sprint 1-4 + Hotfix + Tech Debt + Verification):**
- ✅ Базовый модуль `mayan.apps.organizations` создан
- ✅ Настройки через Mayan settings system
- ✅ Патчи для HttpRequest (расширение без модификации core)
- ✅ Модели: Organization, Plan, Subscription, DomainSettings, UserOrganizationRole
- ✅ TenantAwareManager + TenantAwareMixin + Hybrid Document Managers
- ✅ TenantResolverMiddleware (domain, subdomain, X-Organization-Id, user, standalone)
- ✅ `patch_organization_fields()` — contribute_to_class для core FK registration
- ✅ OrgScopedAPIMixin + IsTargetOrgAdminOrSuperAdmin
- ✅ REST API: CRUD, Members, Plans, Suspend, Activate
- ✅ Frontend: org store, selector, settings, API header, service methods
- ✅ Quota enforcement (Redis-cached), audit logging, security hardening
- ✅ Полная API верификация: все endpoints 200 OK, lifecycle test passed
- ✅ Document модель имеет organization FK
- ✅ Celery tasks используют TenantAwareTask base class
- ✅ DocumentAIAnalysis tenant-aware (Part 3 Sprint 1)
- ✅ AssetEvent tenant-aware (Part 3 Sprint 2): pre_save binding, track_asset_event_async.delay(organization_id=...)
- ✅ ShareLink tenant-aware (Part 3 Sprint 3)

### 10. Contribute-to-Class Pattern (Dynamic FK Registration)

**Назначение:** Расширение core Mayan моделей ForeignKey полями без модификации исходного кода.

**Проблема:** Django миграции (`AddField`) добавляют столбцы в БД, но **не** регистрируют поля на уровне Python-класса модели. Без регистрации ORM lookup вида `document__organization` вызывает `ValueError`.

**Решение:**
```python
# mayan/apps/organizations/patches.py
def patch_organization_fields():
    """
    Динамически регистрирует FK organization на core моделях.
    Вызывается из apps.py ДО patch_document_managers().
    """
    from mayan.apps.documents.models import Document

    if not _has_concrete_field(Document, 'organization'):
        field = models.ForeignKey(
            'organizations.Organization',
            on_delete=models.CASCADE,
            related_name='documents',
            db_index=True,
        )
        field.contribute_to_class(Document, 'organization')
    # Аналогично для Tag, Cabinet...

def _has_concrete_field(model, field_name):
    """Идемпотентная проверка наличия поля."""
    try:
        return model._meta.get_field(field_name).concrete
    except Exception:
        return False
```

**Порядок вызовов в `apps.py`:**
1. `patch_HttpRequest()` — URL support
2. `patch_organization_fields()` — FK registration (contribute_to_class)
3. `patch_document_managers()` — manager replacement

**Важно:**
- Поля **должны** совпадать с определениями в миграциях (related_name, on_delete, db_index)
- `_has_concrete_field()` обеспечивает идемпотентность (безопасен при повторных вызовах)
- Без этого патча любой ORM lookup через `organization` на core моделях невозможен

### 11. Document Tenant Binding on Create (NOT NULL Safety)

**Назначение:** Гарантировать заполнение `Document.organization` при всех create-paths (включая upload wizard), когда в БД стоит NOT NULL.

**Проблема:** При `POST /api/v4/documents/` возможно создание `Document` без `organization`, что вызывает:
`IntegrityError: null value in column "organization_id" violates not-null constraint`.

**Решение:** pre-save signal в `organizations/apps.py`:
- если `instance.organization` уже задан — не трогать;
- иначе взять tenant из ContextVar (`get_current_organization()`);
- если tenant отсутствует — fallback на default organization;
- подключение сигнала с `weak=False`, чтобы receiver не был удален GC.

**Результат:** Upload flow восстановлен (`POST /documents/` -> 201, `POST /documents/{id}/files/` -> 202).

### 12. Protected Thumbnail Rendering Pattern (SPA)

**Назначение:** Корректный показ превью в SPA, когда backend image endpoint требует токен.

**Проблема:** URL превью вида `/api/v4/.../image/` защищён. Стандартный `<img src="...">` не отправляет `Authorization` header, из-за чего в галерее появляется placeholder вместо изображения.

**Решение:**
- На фронтенде (`AssetCard`) загружать защищённые превью через `apiService` (`responseType: 'blob'`) с auth interceptor.
- Преобразовывать blob в `ObjectURL` и использовать его как `img src`.
- При unmount компонента освобождать `ObjectURL` через `URL.revokeObjectURL`.
- На backend для optimized list endpoint держать валидные `thumbnail_url/preview_url` и корректные `file_latest_*` поля (стабильный latest-file prefetch + правильный cache key).

**Результат:** Восстановлен рендер изображений и file metadata в SPA-галерее (`/dam`) после Sprint 4.5 fix.

## Компоненты системы

### Backend Components

1. **Core Mayan EDMS Apps** (vendor):
   - `documents`: Управление документами
   - `metadata`: Метаданные
   - `ocr`: OCR распознавание
   - `rest_api`: REST API
   - `authentication`: Аутентификация
   - И другие стандартные apps

2. **Custom Apps** (расширения):
   - `dam`: Digital Asset Management
   - `analytics`: Аналитика использования
   - `headless_api`: Headless API для фронтенда
   - `image_editor`: Редактор изображений
   - `distribution`: Распределение контента
   - `converter_pipeline_extension`: Расширение конвертера
   - `marketing_cms`: Маркетинговый CMS

### Frontend Components

1. **Vue 3 SPA** (`frontend/`):
   - Компонентная архитектура
   - Pinia stores для state management
   - TypeScript для типизации
   - **Sprint 5:** Для больших коллекций (80+) используется ImmersiveGrid с @tanstack/vue-virtual (виртуализация по строкам); поиск и фильтры синхронизируются с URL (useDamSearchFilters); контекстное меню и мультивыбор (Shift+Click, drag-select по индексам) в гриде.
   - Vite для сборки

2. **Nuxt 3 Public Frontend** (`public-frontend/`):
   - SSR/SSG для публичных страниц
   - Отдельный от основного приложения

### Infrastructure Components

1. **Database Layer**:
   - PostgreSQL для основных данных
   - Redis для кэша и блокировок
   - S3 для файлового хранилища

2. **Message Queue**:
   - RabbitMQ как Celery broker
   - Redis как Celery result backend

3. **Web Servers**:
   - Gunicorn для WSGI (основное приложение)
   - Daphne для ASGI (WebSocket уведомления)

## Паттерны интеграции

### 1. Docker Volume Mount Pattern

Кастомные apps монтируются как volumes в Docker:

```yaml
volumes:
  - ./mayan/apps/dam:/opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/dam
```

**Преимущества:**
- Hot reload при разработке
- Не требует пересборки образа для изменений кода

### 2. Environment-based Configuration

Конфигурация через переменные окружения:

```python
# Пример из docker-compose.yml
MAYAN_DATABASES: "{'default':{'ENGINE':'django.db.backends.postgresql',...}}"
MAYAN_CELERY_BROKER_URL: amqp://...
```

### 3. Auto-admin Pattern

Автоматическая генерация учетных данных при первом запуске:

```python
# Пример из mayan/apps/autoadmin/
AutoAdminSingleton.objects.create_autoadmin()
```

## Масштабируемость

### Горизонтальное масштабирование

- **Stateless приложение**: Gunicorn workers могут масштабироваться
- **Celery workers**: Разделение по очередям для разных типов задач
- **Database**: PostgreSQL с поддержкой репликации
- **Cache**: Redis для распределенного кэширования

### Вертикальное масштабирование

- Настройка количества Gunicorn workers
- Настройка concurrency для Celery workers
- Оптимизация запросов к БД через индексы

## Безопасность

### Паттерны безопасности

1. **RBAC**: Role-Based Access Control через Mayan permissions
2. **ACL**: Access Control Lists для объектов
3. **Token Authentication**: JWT токены для API
4. **CSRF Protection**: Django CSRF для форм
5. **Input Validation**: Django Forms и DRF Serializers

## Тестирование

### Структура тестов

```
mayan/apps/dam/tests/
├── test_api_views.py
├── test_models.py
├── test_tasks.py
└── ...
```

**Паттерны:**
- Unit тесты для моделей и сервисов
- Integration тесты для API
- Celery task тесты с моками

## Миграции и версионирование

### Database Migrations

- Каждое изменение модели требует миграцию
- Миграции в `migrations/` директории каждого app
- GIN индексы для JSON полей (PostgreSQL специфичные)

**Cross-app migrations (organizations):**
- Django AddField/AlterField **не принимают** параметр `app_label` — операции должны быть в app-владельце модели
- Для привязки Document, Tag, Cabinet к Organization: операции в documents (0085/0086), tags (0010/0011), cabinets (0007/0008)
- org 0002 и 0004 — точки синхронизации зависимостей (operations = []); полная логика в docstrings

**Index names:** Django E034 — имя индекса ≤30 символов (Oracle limit; distribution: idx_dist_sl_org_created).

### API Versioning

- Версионирование через URL: `/api/v4/`
- Обратная совместимость при обновлениях
