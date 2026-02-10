# Active Context: Prime-EDMS

**Последнее обновление:** 2026-02-10  
**Текущий фокус:** Multi-tenancy Sprint 4 — Fully Verified + Upload Recovery + Gallery Preview Recovery

---

## 🎯 Current Focus (Текущий фокус)

### Активная разработка (Последние коммиты)

#### 1. Multi-tenancy Infrastructure
**Статус:** Sprint 1-4 + Hotfix + Tech Debt + Sprint 4.2 + Sprint 4.3 + Sprint 4.4 + Sprint 4.5 (Gallery Preview Recovery) завершены  
**Коммит:** `7f41e418fe`

**Что сделано (Sprint 1 Infrastructure — ЗАВЕРШЁН 2026-02-09):**
- ✅ Создан базовый модуль `mayan.apps.organizations`
- ✅ Настройки для Organizations (installation URL, base path)
- ✅ Патчи для HttpRequest (поддержка organization URLs)
- ✅ Тесты для settings и requests
- ✅ Интеграция в apps.py с патчингом при старте
- ✅ Модели: Organization (UUID PK, quotas, branding), Plan, Subscription, DomainSettings, UserOrganizationRole
- ✅ Миграция 0001_initial с полной схемой БД
- ✅ TenantAwareManager (ContextVar-based filtering) + TenantAwareMixin (abstract model)
- ✅ TenantResolverMiddleware (custom domain, subdomain, user, standalone fallback, access control)
- ✅ Middleware интегрирован в settings/base.py (после AuthenticationMiddleware)
- ✅ Unit-тесты: модели (CRUD, уникальность, квоты), managers (ContextVar, filtering), middleware (exempt paths, SaaS/standalone, access control, cleanup)

**Что сделано (Sprint 2 Data Binding & API — ЗАВЕРШЁН 2026-02-09):**
- ✅ Гибридные менеджеры: TenantAwareDocumentManager, TenantAwareTrashCanManager, TenantAwareValidDocumentManager
- ✅ Миграция 0002: nullable organization FK к Document, Tag, Cabinet + unique_together (операции в documents 0085, tags 0010, cabinets 0007; org 0002 — dependency sync)
- ✅ Миграция 0003: data migration — привязка всех данных к default Organization + UserOrganizationRole
- ✅ Миграция 0004: organization FK обязательным (NOT NULL) + composite indexes (операции в documents 0086, tags 0011, cabinets 0008; org 0004 — dependency sync)
- ✅ Monkey-patching Document.objects/trash/valid на гибридные менеджеры (patches.py + apps.py)
- ✅ Django Admin: OrganizationAdmin, PlanAdmin, SubscriptionAdmin, UserOrganizationRoleAdmin, DomainSettingsAdmin
- ✅ DRF Serializers: Organization, Plan, Subscription, UserOrganizationRole, CurrentOrganization, AddMember
- ✅ API Views + URLs: Organizations CRUD, Members, Plans, Current org — зарегистрированы в headless API
- ✅ Integration тесты: cross-tenant isolation для Document/Tag/Cabinet, hybrid managers, security tests

**Что сделано (Sprint 3 Frontend Integration, Permissions, Task Context — ЗАВЕРШЁН 2026-02-09):**
- ✅ auth/me enrichment: organization + organizations list в ответе GET /api/v4/headless/auth/me/
- ✅ Reusable DRF permission classes: IsOrganizationMember, IsOrganizationAdmin, IsOrganizationOwner, IsSuperAdminOrOrgAdmin
- ✅ api_views.py рефакторинг: ad-hoc проверки заменены на permission classes (IsTargetOrgAdminOrSuperAdmin для org-scoped views)
- ✅ X-Organization-Id header: _resolve_by_header() в TenantResolverMiddleware (между subdomain и user default)
- ✅ TenantAwareTask: base Celery Task class с organization_id kwarg → ContextVar
- ✅ DAM tasks обновлены: analyze_document_with_ai, import_yandex_disk, bulk_analyze_documents — base=TenantAwareTask
- ✅ Analytics tasks обновлены: aggregate_daily_metrics, generate_analytics_alerts — base=TenantAwareTask
- ✅ Quota enforcement: check_storage_quota (pre_save signal), check_ai_quota (в AI task), check_user_quota, QuotaExceededException
- ✅ Frontend TypeScript types: Organization, OrganizationWithRole, OrganizationDetail, Plan, OrganizationMember
- ✅ Frontend organizationService: API wrapper для /organizations/ endpoints

**Что сделано (Sprint 4 Polish, Performance, Security — ЗАВЕРШЁН 2026-02-09):**
- ✅ Database Indexes: composite indexes на UserOrganizationRole (user+is_default, org+role), DomainSettings (is_verified) + миграция 0005
- ✅ N+1 Устранение: OrganizationListSerializer и OrganizationSerializer используют annotated fields вместо SerializerMethodField
- ✅ Пагинация: OrganizationListCreateView теперь поддерживает page/page_size параметры (default 20, max 100)
- ✅ select_related/prefetch_related: OrgScopedAPIMixin.get_target_organization() с оптимальной загрузкой связей
- ✅ Admin annotate: OrganizationAdmin.get_queryset() с Count annotation для member_count
- ✅ Redis-кеширование квот: get_storage_used_gb(), get_active_users_count(), get_ai_analyses_this_month() — TTL 5 мин
- ✅ Cache invalidation signals: post_save/post_delete на DocumentFile → storage, UserOrganizationRole → users, DocumentAIAnalysis → AI
- ✅ UUID-валидация: middleware._resolve_by_header() валидирует формат UUID перед запросом к БД
- ✅ Input validation: RemoveMemberSerializer для DELETE members endpoint вместо raw request.data
- ✅ Audit logging: audit.py с log_org_event() для SIEM-совместимого логирования (create, update, archive, member_add, member_remove)
- ✅ Deprecated patterns: urls.py — url() заменён на path()/re_path(); permission_classes — imports на уровне модуля
- ✅ Per-request permission caching: _get_user_role() с request._org_role_cache для исключения дублирующих DB-запросов
- ✅ check_user_quota() в api_views.py вместо прямого вызова is_user_limit_exceeded()
- ✅ Улучшенный error handling: quota.py с специфичными exceptions (AttributeError, ValueError, TypeError)
- ✅ Test coverage: test_api_views.py (~20 тестов), test_quota.py (~12 тестов), test_serializers.py (~8 тестов)
- ✅ Frontend type safety: authService.ts — OrganizationWithRole вместо any; organizationService.ts — OrganizationUpdateInput
- ✅ Frontend race condition fix: organizationStore.ts — _initializing guard, isLoading корректно используется
- ✅ Frontend dynamic import: organizationStore.ts — async import() вместо require()
- ✅ Frontend UUID validation: apiService.ts — regex проверка orgId перед отправкой X-Organization-Id header
- ✅ Frontend ARIA/keyboard: OrganizationSelector.vue — role=listbox, aria-selected, Escape/Arrow keyboard navigation, loading state
- ✅ Frontend organizationStore (Pinia): state, getters (isOwner/isAdmin/isMember), actions (initialize, switchOrganization)
- ✅ Frontend apiService: X-Organization-Id header в request interceptor
- ✅ Frontend authStore + authService: org initialization из auth/me, org reset при logout
- ✅ Frontend router: /settings/organization route с requiresOrgAdmin guard
- ✅ Frontend OrganizationSelector component: dropdown в Header с переключением org
- ✅ Frontend OrganizationSettingsPage: General, Members, Quota, Plan вкладки
- ✅ Backend tests: test_permissions.py (12 tests), test_celery_context.py (5 tests)

**Sprint 4 Hotfix Applied (2026-02-09):**
- ✅ C1 SECURITY FIX: OrgScopedAPIMixin + IsTargetOrgAdminOrSuperAdmin — cross-org access vulnerability closed
- ✅ C2 URL FIX: Added `headless/` prefix to all organization URL patterns — frontend/backend routing mismatch resolved
- ✅ C2 Middleware: TENANT_EXEMPT_PATHS updated to `/api/v4/headless/organizations/`
- ✅ C2 Frontend: `listPlans()` URL fixed — plans endpoint uses separate `PLANS_BASE` constant
- ✅ I2: `check_ai_quota()` now uses cached `get_ai_analyses_this_month()` for consistency
- ✅ I3: Silent `except: pass` replaced with `logger.debug()` in cache invalidation signal handlers
- ✅ UUID regex tightened to strict format `[0-9a-f]{8}-...-[0-9a-f]{12}` in URL patterns
- ✅ 12+ cross-organization security tests added (admin cross-org denied, staff bypass, own-org allowed)

**Definition of Done — Sprint 4 Closure:**
- [ ] All tests pass: `python manage.py test mayan.apps.organizations`
- [ ] No cross-org access possible for non-staff users (verified by CrossOrganizationAccessTestCase)
- [x] Frontend organization + plans API calls return 200 (not 404) — **verified 2026-02-10**
- [x] Suspend/Activate endpoints work: POST suspend -> 200, POST activate -> 200 — **verified 2026-02-10**
- [x] GET organization detail returns 200 with storage/member data — **verified 2026-02-10 (after FK patch)**
- [x] PATCH organization update returns 200 — **verified 2026-02-10**
- [x] Full lifecycle test: create → detail → suspend → activate → detail — **passed 2026-02-10**
- [x] Production migration applied without rollback — **verified 2026-02-10 (showmigrations all [X])**
- [ ] 403/404 error rates stable post-deploy (monitor Nginx/Django logs)
- [ ] Code review approved by peer

**Sprint 4.1 Tech Debt (ЗАВЕРШЁН 2026-02-09):**
- ✅ I1: DRY annotation helper `querysets.py` — `annotate_org_counts()`, `active_users_count` aliased via `source='member_count'`
- ✅ I4: (Done in C2) Strict UUID regex in URL patterns
- ✅ I5: Specific `DoesNotExist` exceptions in middleware resolvers + fallback `logger.warning()`
- ✅ I6: `apiService.deleteWithBody()` — clean DELETE-with-body pattern, simplified `removeMember()`
- ✅ I7: activeContext.md cleanup — stale markers, contradictions, Long-term section updated

**Sprint 4.2 Stabilization (ЗАВЕРШЁН 2026-02-10):**
- ✅ Root cause analysis: migration restructuring (cross-app operations), distribution dependency fix, Docker volumes
- ✅ Suspend endpoint: `POST /api/v4/headless/organizations/{id}/suspend/` (ТЗ Section 4.5.3)
- ✅ Activate endpoint: `POST /api/v4/headless/organizations/{id}/activate/`
- ✅ OrganizationSuspendView + OrganizationActivateView (SuperAdmin only, OrgScopedAPIMixin)
- ✅ Frontend: `organizationService.suspendOrganization()` + `activateOrganization()`
- ✅ 18 tests: auth, permissions, suspend/activate lifecycle, edge cases (archived, already-suspended, 404)
- ✅ Memory Bank synchronized: progress.md cleaned up, stale markers removed

**Sprint 4.3 Verification & FK Patch (ЗАВЕРШЁН 2026-02-10):**
- ✅ **Критический баг обнаружен и исправлен:** GET `/organizations/{id}/` возвращал 500 (ValueError: Cannot query "Organization": Must be "Document" instance)
- ✅ **Корневая причина:** Миграции documents/0085-0086 добавили столбец `organization_id` в БД, но Python-класс `Document` (core Mayan) не знал об этом поле. Django ORM не мог разрешить lookup `document__organization` в `get_storage_used_gb()`
- ✅ **Исправление:** Добавлена `patch_organization_fields()` в `patches.py` — использует `contribute_to_class()` для динамической регистрации FK `organization` на моделях Document, Tag, Cabinet при старте приложения
- ✅ `_has_concrete_field()` — идемпотентная проверка наличия поля перед патчем
- ✅ Порядок вызовов в `apps.py`: `patch_organization_fields()` → `patch_document_managers()` (FK сначала, менеджеры потом)
- ✅ **Полная верификация API endpoints:**
  - GET `/organizations/` → 200 (list, 2 организации)
  - GET `/organizations/{id}/` → 200 (detail с `storage_used_gb`, `member_count`)
  - PATCH `/organizations/{id}/` → 200 (update name)
  - GET `/organizations/{id}/members/` → 200 (members list)
  - GET `/plans/` → 200 (plans list)
  - POST `/organizations/{id}/suspend/` → 200 (suspend)
  - POST `/organizations/{id}/suspend/` (повторно) → 400 (already suspended)
  - POST `/organizations/{id}/activate/` → 200 (activate)
- ✅ **Lifecycle тест пройден:** CREATE(trial) → GET(detail) → SUSPEND(suspended) → GET(suspended) → ACTIVATE(active) → GET(active)
- ✅ Docker container restart достаточен (пересборка образов не требуется)

**Sprint 4.4 Upload Recovery (ЗАВЕРШЁН 2026-02-10):**
- ✅ **Критический баг обнаружен и исправлен:** Upload Wizard падал на шаге 1 (`POST /api/v4/documents/`) с HTTP 500
- ✅ **Корневая причина:** `documents_document.organization_id` имеет NOT NULL constraint, но при создании Document в API-path поле organization не проставлялось автоматически
- ✅ **Трейсбек подтвержден:** `django.db.utils.IntegrityError: null value in column "organization_id" violates not-null constraint`
- ✅ **Исправление:** в `organizations/apps.py` добавен `pre_save` binding signal для `Document`, который:
  - устанавливает `instance.organization` из tenant context (`get_current_organization()`)
  - использует fallback на default organization
  - подключается с `weak=False` (receiver не теряется GC)
- ✅ **Верификация после фикса:**
  - `POST /api/v4/documents/` -> 201 Created
  - `POST /api/v4/documents/{id}/files/` -> 202 Accepted
  - `GET /api/v4/documents/{id}/files/` -> файл присутствует в results
  - проверка в shell: у созданного `Document` `organization_id` заполнен (не NULL)
- ⚠️ Отдельное наблюдение: `ws://localhost:8080/ws/notifications/` возвращает 404 (не блокирует upload-flow, вынесено отдельно)

**Sprint 4.5 Gallery Preview Recovery (ЗАВЕРШЁН 2026-02-10):**
- ✅ **Критический регресс обнаружен:** в SPA-галерее (`http://localhost:5173/dam`) карточки показывали placeholder `DOCUMENT` вместо превью, часть file metadata не отображалась
- ✅ **Корневые причины:**
  - `optimized` API возвращал некорректный fallback `thumbnail_url` (`.../versions/latest/pages/1/image/...`) для части документов
  - prefetch latest file был нестабилен, из-за чего `file_latest_filename/mimetype/size` могли приходить `null`
  - endpoint превью защищён токеном; обычный `<img>` не отправляет `Authorization` header
- ✅ **Исправления backend:**
  - `optimized_document_api_views.py`: исправлен prefetch latest file (стабильное заполнение `file_latest_*`)
  - `optimized_document_serializers.py`: убран некорректный fallback `versions/latest`, обновлена логика fallback и cache key для `thumbnail/preview` (учёт version/page/file)
- ✅ **Исправления frontend:**
  - `frontend/src/components/DAM/AssetCard.vue`: защищённые `/api/v4/.../image` загружаются через `apiService` как `blob` + `ObjectURL` (с токеном)
- ✅ **Верификация:**
  - `GET /api/v4/documents/optimized/` возвращает заполненные `file_latest_filename`, `file_latest_mimetype`, `file_latest_size`
  - `thumbnail_url` валиден (`/api/v4/documents/{id}/versions/{version_id}/pages/{page_id}/image/...`)
  - визуальная проверка после reload: изображение в SPA-галерее отображается

**Архитектурные решения:**
- Использование патчей для расширения HttpRequest без модификации core
- Настройки через Mayan settings system
- Готовность к интеграции с существующими модулями

**Restructuring миграций и FK patching (2026-02-10):**
- Django AddField/AlterField не принимают `app_label` — cross-app операции должны быть в app-владельце модели
- Операции из org 0002/0004 перенесены: documents (0085, 0086), tags (0010, 0011), cabinets (0007, 0008)
- org 0002 и 0004 — точки синхронизации зависимостей (operations = []); полная логика задокументирована в docstrings
- distribution 0001: добавлена зависимость от documents 0081 (исправлен ValueError: DocumentFile cannot be resolved)
- **ВАЖНО:** Миграции добавляют столбцы в БД, но НЕ регистрируют поля в Python-классах core моделей. Для ORM lookups вида `document__organization` необходим `contribute_to_class()` при старте — реализован в `patches.py:patch_organization_fields()`

#### 2. Public Frontend SSR Improvements
**Статус:** Реализовано  
**Коммит:** `c4e42302b9`

**Что сделано:**
- ✅ SSR support для animations (client-side плагин)
- ✅ Обновлена конфигурация Nuxt для SSR
- ✅ Оптимизация Vite build (manual chunks)
- ✅ Новые страницы: forgot-password, changelog, roadmap
- ✅ Улучшения компонентов (Footer, Navigation, Forms)
- ✅ Обновления локализации (en/ru)

**Архитектурные решения:**
- Разделение client/server плагинов для SSR compatibility
- Оптимизация bundle size через manual chunks
- Улучшенная структура компонентов

#### 3. BulkMoveModal Enhancements
**Статус:** Улучшено  
**Коммиты:** `d239401be2`, `2cf284790b`, `c4657bc2c6`

**Что сделано:**
- ✅ Улучшен UX для выбора папок
- ✅ Улучшена обработка уведомлений
- ✅ Оптимизирован workflow перемещения файлов
- ✅ Улучшена обработка ошибок

#### 4. Immersive Grid Implementation
**Статус:** Активно разрабатывается  
**Коммиты:** `55168e0166`, `9a35372d90`, `c2a4a28596`

**Что делается:**
- Реализация "премиального" дизайна в стиле Pinterest/Google Photos/Figma
- Улучшение AssetCard компонента:
  - Убраны границы и тени в покое
  - Metadata overlay появляется только на hover
  - Google Photos style checkbox selection
  - Quick actions в правом нижнем углу при hover
- Создание AssetGrid компонента для оптимизированного рендеринга
- Density control (compact/comfortable layouts)
- Context-aware GalleryHeaderActions вместо GridToolbar

**Архитектурные решения:**
- Использование Teleport для header actions (лучшая композиция компонентов)
- Persistence UI preferences через uiStore (density, layout, sort)
- Lazy loading для share links (загрузка только при открытии модала)
- Предотвращение N+1 queries (использование данных из list endpoint)

**Документация:** `docs/transformation-2025/IMMERSIVE_GRID_IMPLEMENTATION.md`

#### 2. Search & Filtering Enhancements
**Статус:** Активно улучшается  
**Коммиты:** `c2a4a28596`, `9a35372d90`

**Что делается:**
- Рефакторинг FiltersPanel для v-model two-way binding
- Auto-apply фильтров при изменении
- Новый composable `useDamSearchFilters` для централизованного управления
- Интеграция с damSearch composable в Header
- Улучшение API views для поддержки keyword search и document type filtering

**Архитектурные решения:**
- Централизация логики фильтров в composable (лучшая переиспользуемость)
- Реактивное состояние вместо deprecated методов asset store
- Улучшенная синхронизация между компонентами

#### 3. Performance Optimizations
**Статус:** Постоянные улучшения  
**Коммиты:** `331b22fe6a`, `29a9f274f6`

**Что делается:**
- Оптимизация asset fetching (предотвращение лишних запросов)
- Lazy loading share links
- Улучшение error handling и retry механизмов
- Централизация debug telemetry в API service
- Non-fatal error handling в distribution store

**Архитектурные решения:**
- Предотвращение N+1 queries через использование данных из list endpoint
- Graceful degradation при ошибках backend
- Оптимизация notification fetching (предотвращение дубликатов)

#### 4. Marketing CMS Module
**Статус:** Недавно добавлен  
**Коммит:** `8304fb2fa6`

**Что сделано:**
- Полностью новый модуль для управления маркетинговым контентом
- Модели: Page, Post, Plan, FAQ, Lead, EmailVerificationToken
- REST API endpoints для всех моделей
- Интеграция в docker-compose через MAYAN_COMMON_EXTRA_APPS

**Архитектурные решения:**
- JSON поля для мультиязычного контента (title, description)
- Отдельный модуль для маркетингового контента (не смешивается с DAM)
- Готовность к интеграции с Public Frontend

#### 5. Public Frontend (Nuxt 3)
**Статус:** Полностью реализован  
**Коммит:** `8304fb2fa6`

**Что сделано:**
- Полнофункциональный публичный сайт на Nuxt 3
- Все страницы: Home, Blog, Pricing, Contact, About, Privacy, Terms
- Компоненты: Hero, Features, CTA, FAQ, Pricing Calculator
- SEO оптимизация, i18n, analytics интеграция
- E2E и unit тесты

**Архитектурные решения:**
- Отдельное приложение от основного DAM frontend
- SSR/SSG для лучшего SEO
- Интеграция с Marketing CMS через API

#### 6. Analytics Improvements
**Статус:** Улучшения в процессе  
**Коммиты:** `31d0e00535`, `74690a55a1`

**Что делается:**
- Multi-tenancy поддержка через organization-specific WebSocket groups
- YouTube Analytics интеграция с OAuth2
- Fallback на YouTube Data API v3
- Улучшенная error handling в YouTube provider
- Улучшенное broadcasting сообщений для analytics refresh

**Архитектурные решения:**
- Organization-aware WebSocket groups для изоляции данных
- Best-effort подход к внешним API (fallback механизмы)
- Улучшенная обработка ошибок OAuth2

---

## 🏗️ Recent Architectural Decisions

### 1. Component Architecture (Frontend)

**Решение:** Переход от монолитных компонентов к композиции через composables и Teleport

**Обоснование:**
- Лучшая переиспользуемость логики (useDamSearchFilters, useAssetSelection)
- Более гибкая композиция UI (Teleport для header actions)
- Централизация состояния (stores вместо prop drilling)

**Примеры:**
- `useDamSearchFilters` - централизованная логика фильтров
- `useAssetSelection` - логика выбора активов
- `GalleryHeaderActions` с Teleport вместо GridToolbar

### 2. Performance Optimization Strategy

**Решение:** Предотвращение лишних запросов и оптимизация данных

**Обоснование:**
- Уменьшение нагрузки на backend
- Улучшение UX (меньше задержек)
- Масштабируемость для больших коллекций

**Реализация:**
- Использование данных из list endpoint вместо отдельных запросов
- Lazy loading для необязательных данных (share links)
- Кеширование UI preferences

### 3. Error Handling Philosophy

**Решение:** Graceful degradation вместо жестких ошибок

**Обоснование:**
- Лучший UX (система продолжает работать при частичных сбоях)
- Устойчивость к нестабильности backend
- Неблокирующие операции

**Реализация:**
- Non-fatal error handling в stores
- Retry механизмы для transient errors
- Fallback на альтернативные источники данных

### 4. Multi-tenancy Architecture (Tenant Isolation)

**Решение:** Shared Database + Shared Schema + ForeignKey изоляция через Organization

**Статус:** Полностью реализовано (Sprint 1-4), hotfix applied

**Обоснование:**
- Поддержка SaaS-модели (один backend, много клиентов)
- Поддержка Standalone-модели (один клиент на выделенном сервере)
- Безопасность данных между организациями
- Масштабируемость для SaaS модели
- Enforcement квот (storage, users, AI analyses)

**Архитектурные компоненты (из ТЗ):**
- **Organizations Module**: Модели Organization, Subscription, Plan, DomainSettings
- **TenantAwareManager**: Автоматическая фильтрация QuerySet по Organization
- **TenantAwareMixin**: Миксин для tenant-aware моделей
- **TenantResolverMiddleware**: Определение Organization по домену/токену
- **Migration Strategy**: Поэтапная миграция существующих данных

**Текущая реализация:**
- ✅ Базовый модуль `mayan.apps.organizations` создан
- ✅ Настройки и патчи для HttpRequest реализованы
- ✅ Organization-aware WebSocket groups в Analytics
- ✅ Фильтрация данных по organization в API
- ✅ Organization-specific analytics dashboards
- ✅ Модели Organization, Subscription, Plan (Sprint 1)
- ✅ TenantAwareManager и TenantAwareMixin (Sprint 1)
- ✅ TenantResolverMiddleware (Sprint 1)
- ✅ OrgScopedAPIMixin + IsTargetOrgAdminOrSuperAdmin (Sprint 4 Hotfix)

**Следующие шаги:**
- ✅ Sprint 1: Модели и Managers (ЗАВЕРШЁН)
- ✅ Sprint 2: Data Binding, API, Admin (ЗАВЕРШЁН)
- ✅ Sprint 3: Frontend интеграция, Permissions (ЗАВЕРШЁН)
- ✅ Sprint 4: Polish, Performance, Security + Hotfix (ЗАВЕРШЁН — Ready for Validation)

**Ключевые решения:**
- Shared Database + Shared Schema (не отдельные БД)
- ForeignKey изоляция (не шардирование на уровне схемы)
- ContextVar для потокобезопасности в async контексте
- User-Organization связь: ManyToMany (нужна модель UserOrganizationRole)

**Документация:** `docs/transformation-2025/TZ_Django_Tenant_Isolation.md`

### 5. Module Separation

**Решение:** Отдельные модули для разных доменов (DAM, Marketing CMS, Public Frontend)

**Обоснование:**
- Четкое разделение ответственности
- Независимое развертывание и масштабирование
- Упрощение поддержки

**Реализация:**
- Marketing CMS как отдельный Django app
- Public Frontend как отдельное Nuxt приложение
- API-first подход для интеграции

---

## 🔄 Active Workflows

### Development Workflow

1. **Feature Development:**
   - Создание feature branch
   - Разработка с тестами
   - Code review
   - Merge в main

2. **UI Improvements:**
   - Дизайн в стиле современных DAM систем
   - Итеративная разработка компонентов
   - Тестирование на реальных данных
   - Оптимизация производительности

3. **Performance Optimization:**
   - Профилирование производительности
   - Выявление узких мест
   - Оптимизация запросов и рендеринга
   - Тестирование на больших коллекциях

### Testing Strategy

- **Unit Tests:** Компоненты и утилиты
- **Integration Tests:** API endpoints и workflows
- **E2E Tests:** Критичные user flows (Playwright)
- **Performance Tests:** Нагрузочное тестирование (Locust)

---

## 📋 Next Steps (Ближайшие шаги)

### Immediate (Следующие 1-2 недели)

1. **Завершение Immersive Grid:**
   - Оптимизация для больших списков (>100 активов)
   - Виртуальный скроллинг для очень больших коллекций
   - Финальная полировка UI/UX

2. **Search Improvements:**
   - Расширенные фильтры (дата, размер, владелец)
   - Search history persistence
   - Улучшение faceted search

3. **Performance:**
   - Оптимизация изображений (lazy loading, responsive)
   - CDN интеграция для статики
   - Database query optimization

### Short-term (Следующие 1-2 месяца)

1. **API Gaps:**
   - Реализация Change Password API endpoint
   - User Activity Feed API
   - Улучшение error responses

2. **AI Providers:**
   - Реализация Claude provider
   - Реализация Gemini provider
   - Улучшение fallback механизмов

3. **Analytics:**
   - Завершение Analytics Transformation Phase 1-2
   - Search-to-Find Time метрика
   - CDN Cost tracking

### Long-term (Следующие 3-6 месяцев)

1. **Multi-tenancy — ЗАВЕРШЕНО (Sprint 1-4 + Hotfix + Tech Debt):**
   - ✅ Organizations модуль (Sprint 1-4)
   - ✅ TenantAwareManager и TenantAwareMixin
   - ✅ TenantResolverMiddleware
   - ✅ Миграция существующих данных к Organization
   - ✅ API endpoints для управления Organizations
   - ✅ Полная изоляция данных между тенантами (OrgScopedAPIMixin)
   - ✅ Organization-level settings
   - ✅ Billing integration (Subscription, Plan)

2. **Analytics Phase 3:**
   - AI/ML для рекомендаций
   - Real-time analytics
   - Predictive analytics

3. **Mobile Support:**
   - Responsive design improvements
   - Mobile app (опционально)
   - Touch gestures

---

## 🎨 Design Philosophy

### Current Approach

1. **Content-First Design:**
   - Минимальные UI элементы в покое
   - Фокус на контенте, а не на интерфейсе
   - Metadata появляется только при необходимости

2. **Progressive Disclosure:**
   - Базовые функции всегда доступны
   - Продвинутые функции скрыты до необходимости
   - Context-aware actions

3. **Performance as Feature:**
   - Оптимизация для больших коллекций
   - Lazy loading везде где возможно
   - Кеширование агрессивное но умное

4. **Accessibility:**
   - Keyboard navigation
   - Screen reader support
   - WCAG compliance (в процессе)

---

## 🔍 Key Insights

### Что работает хорошо

1. **DAM Core:** Стабильная работа всех основных функций
2. **AI Integration:** YandexGPT и GigaChat работают надежно
3. **Analytics:** Дашборды предоставляют ценную информацию
4. **Distribution:** Публикации и share links работают как ожидается

### Что требует внимания

1. **Performance:** Большие коллекции (>1000 активов) требуют оптимизации
2. **API Gaps:** Некоторые endpoints отсутствуют для полного self-service
3. **Error Handling:** Можно улучшить user-friendly сообщения
4. **Mobile:** Responsive design требует доработки

### Архитектурные сильные стороны

1. **Modularity:** Четкое разделение модулей
2. **API-First:** Хорошая база для интеграций
3. **Scalability:** Горизонтальное масштабирование через Celery
4. **Extensibility:** Легко добавлять новые модули и функции

---

## 📚 Relevant Documentation

- `docs/transformation-2025/IMMERSIVE_GRID_IMPLEMENTATION.md` - Детали реализации Immersive Grid
- `docs/transformation-2025/UI_UX_AUDIT_2025.md` - UI/UX аудит и рекомендации
- `docs/transformation-2025/ARCHITECTURE_GAP_REPORT_V2.md` - Анализ gaps между frontend и backend
- `docs/transformation-2025/TZ_Django_Tenant_Isolation.md` - **ТЗ по Multi-tenancy архитектуре** (Ready for Development)
- `ANALYTICS_TRANSFORMATION_ROADMAP.md` - Roadmap для аналитики
- `frontend/docs/FEATURE-PARITY-CHECKLIST.md` - Сравнение Old UI vs New UI

## 🏗️ Планируемые Архитектурные Изменения

### Multi-tenancy Implementation (ТЗ готово)

**Источник:** `docs/transformation-2025/TZ_Django_Tenant_Isolation.md`

**Цель:** Реализовать мульти-тенантную архитектуру для поддержки SaaS и Standalone моделей.

**Подход:** Shared Database + Shared Schema + ForeignKey изоляция через Organization.

**Ключевые компоненты:**
1. **Organizations Module** (`mayan.apps.organizations`)
   - Модели: Organization, Subscription, Plan, DomainSettings
   - TenantAwareManager для автоматической фильтрации
   - TenantAwareMixin для tenant-aware моделей
   - TenantResolverMiddleware для определения тенанта

2. **Миграция существующих данных:**
   - Добавить FK на Organization ко всем tenant-aware моделям
   - Создать default Organization для Standalone mode
   - Привязать все существующие данные к default Organization

3. **API и Admin:**
   - ViewSet'ы для управления Organizations
   - Django Admin панель для SuperAdmin
   - Permissions для Super Admin vs Org Admin

**Timeline:** 6 недель (Sprint 1-4)

**KPI:**
- ≥100 тенантов на одном сервере
- 100% защита от cross-tenant access
- ≤200ms время запроса с фильтрацией
- ≤5 мин время создания нового тенанта

**Риски:**
- Ошибка в Middleware → Data Leak (mitigation: unit-тесты, security audit)
- Performance degradation с FK-фильтром (mitigation: индексы, кеширование)
- Сложность миграции данных (mitigation: staging окружение, dry-run)
