# Progress: Prime-EDMS

**Последнее обновление:** 2026-02-11  
**Источник:** Анализ последних коммитов, кодовой базы и деплоя Sprint 1 Part 3

---

## ✅ What Works (Полностью реализовано)

### Core DAM Functionality

#### 1. Document Management
- ✅ Загрузка документов через API и UI
- ✅ Версионирование документов (DocumentFile/DocumentVersion)
- ✅ Управление типами документов
- ✅ Полнотекстовый поиск с поддержкой JSON-полей (GIN индексы)
- ✅ Массовые операции (bulk operations): удаление, перемещение, тегирование
- ✅ Преобразования файлов (transformations) для превью и thumbnails
- ✅ OCR распознавание текста

#### 2. DAM Module (Digital Asset Management)
- ✅ AI-анализ документов через множественные провайдеры:
  - ✅ YandexGPT (полностью реализован)
  - ✅ GigaChat (полностью реализован)
  - ✅ OpenAI (реализован)
  - ✅ Qwen Local (реализован)
  - ✅ KieAI (реализован)
- ✅ Автоматическое извлечение метаданных:
  - ✅ Описания (AI descriptions)
  - ✅ Теги (AI tags)
  - ✅ Категории (categories)
  - ✅ Люди (people detection)
  - ✅ Локации (locations)
  - ✅ Доминирующие цвета (dominant colors)
  - ✅ Alt text для accessibility
- ✅ Модель DocumentAIAnalysis для хранения результатов
- ✅ **DocumentAIAnalysis tenant-aware (Sprint 1 Part 3):** TenantAwareMixin, FK organization, миграции dam 0007-0009, API/tasks/signals/serializers с propagation organization_id, pre-save binding, тесты изоляции; задеплоено в Docker (2026-02-11)
- ✅ Пресеты метаданных (DAMMetadataPreset) для настройки извлечения
- ✅ Интеграция с поиском через transformation функции
- ✅ Celery tasks для асинхронной AI обработки (очередь `ai_analysis`)

#### 3. Analytics Module
- ✅ Asset Bank Dashboard:
  - ✅ Топ метрики (total assets, downloads, views)
  - ✅ Распределение активов по типам
  - ✅ Топ скачиваемых активов
  - ✅ Тренды распределения
  - ✅ Метрики переиспользования
  - ✅ Тренды хранилища
  - ✅ Алерты системы
- ✅ Campaign Performance Dashboard:
  - ✅ Метрики кампаний
  - ✅ ROI tracking
  - ✅ Engagement метрики
- ✅ User Activity Dashboard:
  - ✅ Активность пользователей
  - ✅ Сессии пользователей
  - ✅ Поисковые запросы
- ✅ Search Analytics Dashboard:
  - ✅ Метрики поиска
  - ✅ Успешность поиска
  - ✅ Время поиска
- ✅ Distribution Analytics Dashboard:
  - ✅ Использование публикаций
  - ✅ Share links метрики
- ✅ Content Intelligence Dashboard:
  - ✅ Переиспользование контента
  - ✅ Тренды контента
- ✅ Real-time обновления через WebSocket (Daphne)
- ✅ Multi-tenancy поддержка (organization-specific groups)

#### 3. Analytics Module (Sprint 2 Part 3 — Tenant-aware)
- ✅ **AssetEvent tenant-aware:** TenantAwareMixin, FK `organization`, composite indexes; миграции analytics 0010 (AddField nullable), 0011 (populate from document.organization_id), 0012 (NOT NULL + indexes); pre_save binding в organizations/apps.py; consume_analytics_events — ручная подстановка organization_id перед bulk_create.
- ✅ **Ingestion:** AssetEventTrackingMiddleware (fire-and-forget), track_asset_event_async Celery task (TenantAwareTask); маршруты /api/v4/documents/, /api/v4/headless/documents/, пути с "download"; регистрация после TenantResolverMiddleware.
- ✅ **Dashboard API:** GET /api/v4/headless/analytics/dashboard/ — tenant-scoped метрики (total_documents, storage_used_gb, active_users_30d, top_documents, ai_usage); AnalyticsDashboardViewSet, DashboardMetricsSerializer; обязательный request.organization (X-Organization-Id).
- ✅ **Reports:** AnalyticsReportTask (organization, user, report_type, parameters, status, file_path); миграция 0013; generate_analytics_report (JSON в MEDIA_ROOT/reports/{org_id}/); POST .../analytics/reports/generate/, GET .../analytics/reports/{id}/; параметры date_range (from/to) в task — чтение из parameters['date_range'].
- ✅ **Tests:** test_middleware (track_asset_event_async.delay с organization_id), test_api (dashboard isolation по X-Organization-Id), test_reports (sync run + API), test_tenant_isolation (AssetEvent, dashboard, report isolation).
- ✅ **Code review (2026-02-11):** Signal vs task org_id — PASS; bulk_create org mapping — PASS; migrations deps — PASS; middleware path/non-blocking/no-org — PASS; dashboard N+1 — PASS; report org/failure — PASS; report date_range — CRITICAL fix applied.

#### 4. Distribution Module
- ✅ Публикации (Publications) для группировки активов
- ✅ Рендишены (Renditions) - преобразованные версии файлов
- ✅ Share Links - защищенные ссылки с паролями, лимитами, сроками
- ✅ Recipient Lists - списки получателей
- ✅ Distribution Campaigns - маркетинговые кампании
- ✅ Access Log - логирование доступа
- ✅ Интеграция с аналитикой для трекинга использования

#### 5. Workflow & Document States
- ✅ Система workflow с состояниями документов
- ✅ Переходы между состояниями (transitions)
- ✅ Автоматические действия при смене состояний
- ✅ Отслеживание прогресса согласования
- ✅ ApprovalWorkflowEvent для аналитики workflow

#### 6. Permissions & Access Control
- ✅ Система ролей (Roles → Groups → Users)
- ✅ Access Control Lists (ACL) для объектов
- ✅ Гранулярные permissions по namespace
- ✅ Проверка прав доступа в API endpoints

#### 7. Frontend DAM Components (Vue 3)
- ✅ GalleryView с grid layout
- ✅ AssetCard с immersive design (Google Photos style)
- ✅ AssetGrid для оптимизированного рендеринга
- ✅ FiltersPanel с auto-apply фильтрами
- ✅ Search functionality с instant results
- ✅ Bulk operations (выбор, перемещение, тегирование)
- ✅ GalleryHeaderActions для context-aware controls
- ✅ Lazy loading активов
- ✅ Persistence UI preferences (density, layout, sort)
- ✅ Error handling и retry механизмы
- ✅ Loading states и skeletons
- ✅ Восстановлен рендер превью в SPA-галерее для защищённых API thumbnail URL (blob/object URL через auth)

#### 8. Headless API
- ✅ REST API v4 endpoints для фронтенда
- ✅ Оптимизированные document API views
- ✅ Analytics API endpoints
- ✅ Notifications API endpoints
- ✅ Token-based аутентификация
- ✅ WebSocket поддержка для real-time уведомлений

#### 9. Notifications System
- ✅ Event-based уведомления
- ✅ Notification preferences
- ✅ Real-time доставка через WebSocket
- ✅ Notification popover в UI
- ✅ Error handling для corrupted notifications

#### 10. Marketing CMS Module (Новый)
- ✅ Модели: Page, Post, Plan, FAQ, Lead, EmailVerificationToken
- ✅ REST API endpoints для контента
- ✅ Сериализаторы для всех моделей
- ✅ Admin интерфейс
- ✅ Миграции и fixtures
- ✅ Интеграция в docker-compose

#### 11. Public Frontend (Nuxt 3)
- ✅ Полностью реализованный публичный сайт
- ✅ Страницы: Home, Blog, Pricing, Contact, About, Privacy, Terms
- ✅ Новые страницы: Forgot Password, Changelog, Roadmap
- ✅ Компоненты: Hero, Features, CTA, FAQ, Pricing Calculator
- ✅ Формы: Contact, Login, Register, Forgot Password
- ✅ SSR support для animations (client-side плагины)
- ✅ SEO оптимизация (PageMeta, JsonLd)
- ✅ Analytics интеграция
- ✅ i18n поддержка (en/ru)
- ✅ Оптимизация bundle size (manual chunks)
- ✅ E2E тесты (Playwright)
- ✅ Unit тесты (Vitest)

#### 12. Infrastructure
- ✅ Docker Compose конфигурация
- ✅ PostgreSQL база данных
- ✅ Redis для кэша и блокировок
- ✅ RabbitMQ для Celery broker
- ✅ Gunicorn для WSGI
- ✅ Daphne для ASGI (WebSocket)
- ✅ S3 Storage backend (Beget)
- ✅ Health checks для всех сервисов

#### 13. Multi-tenancy Infrastructure (Новый)
- ✅ Базовый модуль `mayan.apps.organizations` создан
- ✅ Настройки для Organizations (installation URL, base path)
- ✅ Патчи для HttpRequest (поддержка organization URLs)
- ✅ Тесты для settings и requests
- ✅ Интеграция в apps.py с патчингом при старте

---

## 🚧 In Progress (В процессе разработки)

### 1. Multi-tenancy Architecture (Tenant Isolation) — Базовая инфраструктура завершена
**Статус:** Sprint 1-4 завершены. Part 3 интеграция планируется  
**Документы:** 
- `docs/transformation-2025/TZ_Django_Tenant_Isolation.md` (Part 2 — завершено)
- `docs/transformation-2025/АНАЛИЗ КОНТЕКСТА И ОБНОВЛЕННОЕ ТЕХНИЧЕСКОЕ ЗАДАНИЕ.md` (Part 3 — планируется)
- `tmp/GAPS_REPORT_PART3.md` (GAPS отчет)  
**Коммит:** `7f41e418fe`

**Sprint 1 (ЗАВЕРШЁН):**
- ✅ Базовый модуль `mayan.apps.organizations` создан
- ✅ Настройки для Organizations (installation URL, base path)
- ✅ Патчи для HttpRequest (поддержка organization URLs)
- ✅ Модели: Organization, Plan, Subscription, DomainSettings, UserOrganizationRole
- ✅ TenantAwareManager + TenantAwareMixin (ContextVar)
- ✅ TenantResolverMiddleware (domain, subdomain, user, standalone)
- ✅ Unit-тесты

**Sprint 2 (ЗАВЕРШЁН):**
- ✅ Гибридные менеджеры: TenantAwareDocumentManager, TenantAwareTrashCanManager, TenantAwareValidDocumentManager
- ✅ Миграция 0002: nullable organization FK к Document, Tag, Cabinet (операции в documents/0085, tags/0010, cabinets/0007)
- ✅ Миграция 0003: data migration — привязка к default Organization
- ✅ Миграция 0004: NOT NULL + composite indexes (операции в documents/0086, tags/0011, cabinets/0008)
- ✅ Restructuring 2026-02-10: org 0002/0004 — dependency sync; логика в docstrings + целевых приложениях
- ✅ Monkey-patching Document managers на tenant-aware версии
- ✅ Django Admin для Organizations (все модели + inlines)
- ✅ DRF Serializers (Organization, Plan, Subscription, Members, CurrentOrg)
- ✅ REST API: Organizations CRUD, Members, Plans, Current org
- ✅ Integration тесты: cross-tenant isolation, hybrid managers, security

**Sprint 3 (ЗАВЕРШЁН):**
- ✅ auth/me enrichment: organization + organizations list
- ✅ Reusable DRF permission classes (IsOrganizationMember, IsOrganizationAdmin, IsOrganizationOwner, IsSuperAdminOrOrgAdmin)
- ✅ X-Organization-Id header resolution в middleware
- ✅ TenantAwareTask: Celery base class с organization context
- ✅ DAM/Analytics tasks обновлены на TenantAwareTask
- ✅ Quota enforcement: storage (pre_save signal), AI (task check), users
- ✅ Frontend: TypeScript types, organizationService, organizationStore (Pinia)
- ✅ Frontend: apiService X-Organization-Id header, authStore org init/cleanup
- ✅ Frontend: OrganizationSelector component в Header
- ✅ Frontend: OrganizationSettingsPage (General, Members, Quota, Plan)
- ✅ Frontend: router с requiresOrgAdmin guard
- ✅ Backend tests: permission classes (12 tests), Celery context (5 tests), X-Organization-Id header (4 tests)

**Sprint 4 (ЗАВЕРШЁН):**
- ✅ Performance indexes, Redis caching, N+1 устранение, пагинация
- ✅ Security hardening: UUID validation, audit logging, OrgScopedAPIMixin
- ✅ Hotfix: cross-org access vulnerability, URL routing mismatch
- ✅ Tech Debt: DRY annotations, specific exceptions, type cleanup
- ✅ Migration restructuring: cross-app operations moved to target apps
- ✅ Suspend/Activate API endpoints (ТЗ Section 4.5.3)
- ✅ `contribute_to_class` patch: Document/Tag/Cabinet FK `organization` зарегистрирован на уровне Python (patches.py)
- ✅ **Полная API верификация:** all endpoints 200 OK, lifecycle test passed, no 500 errors
- ✅ **Upload recovery:** исправлен 500 на `POST /api/v4/documents/` (NOT NULL `organization_id`) через pre_save tenant binding signal для Document

**Архитектурный подход:**
- Shared Database + Shared Schema
- ForeignKey изоляция через Organization
- Поддержка SaaS и Standalone режимов
- ContextVar для потокобезопасности

**Part 3 Integration:**
- ✅ **Sprint 1 (Неделя 1-2):** DAM модуль — **ЗАВЕРШЁН И ЗАДЕПЛОЕН 2026-02-11**
  - DocumentAIAnalysis → TenantAwareMixin, FK organization, миграции dam 0007-0009
  - API/views/serializers/tasks/signals обновлены (organization_id), pre-save binding в organizations
  - Тесты tenant isolation (модель, API, Celery), Pre-Deployment Static Analysis пройден
  - Деплой: backup БД, rebuild app, migrate dam, restart app/app_websocket, smoke test OK
- ✅ **Sprint 2 (Неделя 3-4):** Analytics модуль — **ЗАВЕРШЁН 2026-02-11**
  - AssetEvent → TenantAwareMixin, FK organization, миграции analytics 0010–0012, pre_save binding, consume_analytics_events org mapping
  - AssetEventTrackingMiddleware, track_asset_event_async (TenantAwareTask)
  - Analytics Dashboard API: GET /api/v4/headless/analytics/dashboard/ (tenant-scoped), AnalyticsReportTask + generate_analytics_report (JSON)
  - Тесты: middleware, dashboard/report isolation, test_tenant_isolation; code review 2026-02-11 (date_range fix applied)
- 🚧 **Sprint 3 (Неделя 5-6):** Distribution + Notifications
  - ShareLink → TenantAwareMixin
  - Notifications WebSocket с валидацией Organization
  - Story Points: 21 (US-DISTRIBUTION-001 + US-NOTIFICATIONS-001)
- 🚧 **Sprint 4 (Неделя 7):** Security + Performance
  - Security audit (penetration testing)
  - Performance optimization (caching, query optimization)

### 2. UI/UX Improvements
- 🚧 **Immersive Grid Implementation** (активно разрабатывается)
  - ✅ Убраны границы и тени в покое
  - ✅ Metadata overlay на hover
  - ✅ Google Photos style selection
  - ✅ Quick actions на hover
  - ✅ Density control (compact/comfortable)
  - ✅ Оптимизация производительности для больших списков (>100 активов) - Intersection Observer lazy rendering
  - ✅ Виртуальный скроллинг: IntersectionObserver-based lazy rendering в AssetGrid + infinite scroll sentinel

### 2. Analytics Enhancements
- 🚧 **YouTube Analytics Integration**
  - ✅ OAuth2 authentication реализован
  - ✅ Fallback на YouTube Data API v3
  - 🚧 Требуется настройка OAuth credentials в production
  - 🚧 Полная интеграция с Analytics API (watch time, geography)

### 3. Search & Filtering
- ✅ Базовый поиск работает
- ✅ Фильтры по типам документов
- ✅ Keyword search
- ✅ Расширенные фильтры (дата, размер, теги, владелец) — с persistence в URL
- ✅ Owner filter добавлен в FiltersPanel + useDamSearchFilters composable
- 🚧 Faceted search улучшения
- 🚧 Search history persistence

### 4. Performance Optimizations
- ✅ Lazy loading активов
- ✅ Оптимизация API запросов (предотвращение N+1)
- ✅ Кеширование метаданных
- ✅ Виртуальный скроллинг для больших списков (IntersectionObserver lazy rendering)
- 🚧 Оптимизация изображений (lazy loading, responsive images)
- 🚧 CDN интеграция для статики

### 5. Multi-tenancy — ЗАВЕРШЁН (Sprint 1-4)
- ✅ Organization-specific WebSocket groups в analytics
- ✅ Полная изоляция данных по организациям (Document, Tag, Cabinet FK + TenantAwareManager + OrgScopedAPIMixin)
- ✅ Organization-level settings (quotas, branding, domain settings)
- ✅ Suspend/Activate API endpoints (ТЗ 4.5.3)

### 6. Error Handling & Resilience
- ✅ Базовое error handling в компонентах
- ✅ Retry механизмы
- ✅ Graceful degradation
- 🚧 Улучшенная обработка ошибок API
- 🚧 Offline support

---

## ❌ Incomplete / TODO (Неполные функции)

### 1. Multi-tenancy Implementation — ЗАВЕРШЁН (Sprint 1-4 + Hotfix + Tech Debt)
- ✅ **Organizations Module** — полностью реализован
  - ТЗ: `docs/transformation-2025/TZ_Django_Tenant_Isolation.md`
  - ✅ Модели: Organization, Plan, Subscription, DomainSettings, UserOrganizationRole
  - ✅ TenantAwareManager + TenantAwareMixin + Hybrid Managers
  - ✅ TenantResolverMiddleware (domain, subdomain, X-Organization-Id header, user, standalone fallback)
  - ✅ Document, Tag, Cabinet привязаны к Organization (FK: documents 0085/0086, tags 0010/0011, cabinets 0007/0008; org 0002/0004 sync)
  - ✅ Monkey-patching Document managers (objects/trash/valid)
  - ✅ Django Admin для всех моделей Organizations
  - ✅ REST API: Organizations CRUD, Members, Plans, Current org, Suspend, Activate
  - ✅ DRF Serializers для всех endpoints
  - ✅ Reusable permission classes (IsOrganizationMember/Admin/Owner, IsSuperAdminOrOrgAdmin, IsTargetOrgAdminOrSuperAdmin)
  - ✅ auth/me enrichment: organization context в ответе
  - ✅ TenantAwareTask: Celery tasks с organization context
  - ✅ Quota enforcement: storage, AI, users (Redis-cached)
  - ✅ Frontend: org store, selector, settings page, API header, router guard, suspend/activate
  - ✅ Integration тесты: cross-tenant isolation, permissions, Celery context, header, suspend/activate
  - ✅ Sprint 4: Performance indexes, Redis caching, security hardening, audit logging
  - ✅ Migration restructuring: cross-app operations in target apps, dependency sync points

### 2. AI Providers
- ❌ **Claude Provider** - только placeholder, требует реализации
  - Файл: `mayan/apps/dam/ai_providers/claude.py`
  - Статус: Все методы возвращают пустые значения
- ❌ **Gemini Provider** - только placeholder, требует реализации
  - Файл: `mayan/apps/dam/ai_providers/gemini.py`
  - Статус: Все методы возвращают пустые значения

### 2. API Endpoints
- ✅ **Change Password API** - реализован
  - Endpoint: `POST /api/v4/headless/password/change/`
  - Файл: `mayan/apps/headless_api/views/password_views.py`
  - Поддерживает current_password, new_password, new_password_confirm
- ✅ **User Activity Feed API** - реализован
  - Endpoint: `GET /api/v4/headless/activity/feed/`
  - Файл: `mayan/apps/headless_api/views/activity_views.py`
  - Фильтры: my_actions, my_documents, all; пагинация, system events

### 3. Features Parity
- ⚠️ **Feature Parity** - большинство функций реализовано, но есть gaps
  - Документ: `frontend/docs/FEATURE-PARITY-CHECKLIST.md`
  - Статус: Core features 10/10, Advanced features 5/5
  - Performance, Accessibility, Mobile Support требуют оценки

### 4. Analytics Roadmap
- 🚧 **Analytics Transformation** - Phase 1-2 частично завершены
  - Документ: `ANALYTICS_TRANSFORMATION_ROADMAP.md`
  - ✅ Базовый трекинг событий (AssetEvent, SearchQuery)
  - ✅ Базовые дашборды
  - 🚧 Search-to-Find Time метрика (требует SearchSession)
  - 🚧 CDN Cost/month tracking
  - 🚧 Feature Adoption метрики
  - 🚧 Гео-данные
  - 🚧 Автоматизация retention

---

## 📊 Статистика реализации

### Backend Modules
- **Core Mayan EDMS**: ✅ 100% (базовый функционал)
- **DAM Module**: ✅ 90% (работает, кроме Claude/Gemini)
- **Analytics Module**: ✅ 85% (основные дашборды работают, roadmap в процессе)
- **Distribution Module**: ✅ 95% (полностью функционален)
- **Headless API**: ✅ 90% (основные endpoints работают, некоторые gaps)
- **Marketing CMS**: ✅ 100% (новый модуль полностью реализован)
- **Notifications**: ✅ 95% (работает, улучшения в процессе)
- **Organizations**: ✅ 100% (Sprint 1-4 + Hotfix + Tech Debt завершены: модели, managers, middleware, data binding, API, admin, permissions, Celery context, quota, frontend, indexes, Redis, audit, security, suspend/activate endpoints, comprehensive tests)

### Frontend Components
- **DAM Gallery**: ✅ 98% (IntersectionObserver lazy rendering, infinite scroll)
- **Search & Filters**: ✅ 95% (расширенные фильтры + owner + URL persistence)
- **Asset Management**: ✅ 90% (CRUD работает, оптимизации в процессе)
- **Analytics Dashboards**: ✅ 90% (дашборды работают, real-time улучшения в процессе)
- **Public Frontend**: ✅ 100% (полностью реализован, SSR improvements добавлены)

### Infrastructure
- **Docker Setup**: ✅ 100%
- **Database**: ✅ 100%
- **Caching**: ✅ 100%
- **Message Queue**: ✅ 100%
- **Storage Backends**: ✅ 100%

---

## 🎯 Приоритеты разработки

### Высокий приоритет
1. **Multi-tenancy Implementation** (Sprint 1-4 ЗАВЕРШЕНЫ)
   - ✅ Organizations модуль полностью реализован
   - ✅ TenantAwareManager и Middleware
   - ✅ Миграция существующих данных
   - ✅ Performance оптимизация (indexes, Redis caching, N+1 fix)
   - ✅ Security hardening (UUID validation, audit logging)
   - ✅ Frontend integration (org switching, settings page, type safety)
2. Завершение Immersive Grid оптимизаций
3. Реализация Change Password API endpoint
4. Завершение YouTube Analytics интеграции
5. Оптимизация производительности для больших коллекций

### Средний приоритет
1. Реализация Claude и Gemini AI провайдеров
2. User Activity Feed API
3. Расширенные фильтры поиска

### Низкий приоритет
1. Analytics Transformation Phase 3 (AI/ML, real-time)
2. Offline support
3. Advanced CDN интеграция
4. Mobile app support

---

## 📝 Примечания

- **Organizations migrations (2026-02-10):** Операции AddField/AlterField/AddIndex для Document, Tag, Cabinet перенесены из org 0002/0004 в documents, tags, cabinets (Django не поддерживает app_label в этих операциях). org 0002/0004 — точки синхронизации; полная логика задокументирована в docstrings миграций.
- **contribute_to_class patch (2026-02-10):** Миграции добавляют столбцы в БД, но Python-класс core моделей (Document, Tag, Cabinet) не знает о поле `organization`. Без `contribute_to_class()` ORM lookup `document__organization` вызывает ValueError. Исправлено в `patches.py:patch_organization_fields()`, вызывается в `apps.py` ДО `patch_document_managers()`.
- **Upload 500 fix (2026-02-10):** root cause в `documents_document.organization_id NOT NULL` при создании Document из Upload Wizard (`POST /api/v4/documents/`). Добавлен `pre_save` signal bind в `organizations/apps.py`, который автопроставляет `Document.organization` из tenant context + fallback default-org, подключение с `weak=False`.
- **Gallery preview regression fix (2026-02-10):** устранён кейс с placeholder `DOCUMENT` в SPA (`/dam`): исправлены latest-file prefetch и thumbnail/preview fallback в optimized API, фронтенд `AssetCard` переведён на auth blob-loading для защищённых `/api/v4/.../image`.
- **Docker:** organizations и tags добавлены в Dockerfile.app и docker-compose volumes.
- **distribution 0001:** Зависимость от documents 0081 для корректного разрешения DocumentFile.
- **Sprint 1 Part 3 деплой (2026-02-11):** Бэкап БД (backup_pre_dam_tenant.sql), применение миграций dam 0007–0009 (AddField → populate → NOT NULL+index), перезапуск app и app_websocket; smoke test: DocumentAIAnalysis без organization = 0. В контейнере Django-команды запускать через `/opt/mayan-edms/bin/mayan-edms.py`.
- Большинство core функций полностью работают и используются в production
- Активная разработка сосредоточена на UI/UX улучшениях и оптимизации производительности
- Новые модули (Marketing CMS, Public Frontend) полностью реализованы и готовы к использованию
- Некоторые AI провайдеры требуют доработки, но основные (YandexGPT, GigaChat) работают стабильно
