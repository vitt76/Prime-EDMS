# Active Context: Prime-EDMS

**Последнее обновление:** 2026-02-17  
**Текущий фокус:** Sprint 5 (High-Performance Frontend — Immersive Grid & Search) — ✅ COMPLETED; следующий — дальнейшая полировка фронта или Backend/Security итерации

---

## 🎯 Current Focus (Текущий фокус)

### Недавно завершённое (2026-02-13)

#### SEO (Public Frontend, Nuxt 3) — Yandex / Google
**Статус:** Реализовано  
**Контекст:** Индексация публичного сайта, robots.txt, sitemap, meta/OG, JSON-LD.

**Реализовано:**
- **robots.txt:** Динамический ответ `server/routes/robots.txt.get.ts` — Allow публичных страниц, Disallow `/auth/`, `/admin`, `/app/`, `/account/`, `/api/`; директива `Host` (Yandex); `Sitemap` из `NUXT_PUBLIC_SITE_URL` (production: e.g. https://maddam.io).
- **Sitemap:** @nuxtjs/sitemap в nuxt.config: exclude приватных путей; `sources: ['/api/sitemap-urls']` — динамические URL блога из Django API (`server/api/sitemap-urls.get.ts`).
- **Meta / OG / canonical:** В app.head добавлены description, og:type, og:site_name, og:image (fallback), twitter:card. Composable `useSeo()`: setPageMeta с canonicalFromRoute и абсолютными og:image/og:url через siteUrl. SEOPageMeta — проп canonicalFromRoute по умолчанию true.
- **JSON-LD:** Composable `useJsonld()` (organizationSchema, softwareApplicationSchema, setSchema, siteUrl). Главная: Organization + SoftwareApplication через @graph в index.vue. Блог-пост: BlogPosting с абсолютными URL (siteUrl) в blog/[slug].vue.
- **Документация:** `public-frontend/docs/SEO_CHECKLIST.md` — чеклист по robots, sitemap, meta, canonical, JSON-LD, production (og-default.png, logo.png, NUXT_PUBLIC_SITE_URL).

#### Аудит 152-ФЗ (Cookie Consent & Privacy)
**Статус:** Выполнен, отчёт зафиксирован  
**Документ:** `docs/legal/COMPLIANCE_REPORT_152FZ_2026.md`

**Итоги:** Критических нарушений нет. COMPLIANT: блокировка аналитики до согласия (YM только после «Принять все»), баннер с ссылкой на Политику и тремя кнопками, чекбоксы в формах регистрации/контакта, логирование согласия (UserConsentLog). RISK: раздел 9 Политики (реквизиты оператора) содержит плейсхолдеры `[указать при публикации]` — до production заменить на фактические данные ООО «Мэддам».

#### Legal & Cookie Consent (152-FZ, ООО Мэддам)
**Статус:** Реализовано  
**Контекст:** Соответствие требованиям ФЗ-152 и прозрачность обработки ПД для публичного сайта.

**Backend (mayan.apps.legal):**
- Модель `UserConsentLog`: фиксация выбора пользователя (full / necessary / rejected), IP, user_agent, timestamp, session_id, url_referer — глобальный аудит без привязки к tenant.
- API: `POST /api/v4/public/legal/consent/` — приём согласия, заполнение полей из request.
- Сериализатор, API view, URL в public API; приложение зарегистрировано в `config.yml` и `docker-compose.yml` (при необходимости).

**Документы:**
- `docs/legal/privacy-policy-ru.md` — политика конфиденциальности (оператор ООО «Мэддам», только Yandex.Metrika, без Google Analytics; определения, порядок согласия, хранение, права субъекта).
- `docs/legal/user-agreement-ru.md` — пользовательское соглашение (условия использования, ответственность, ФЗ-152).

**Public Frontend (Nuxt 3):**
- Страницы `/privacy` и `/terms`: отображение Markdown из публичного API (`/api/legal/privacy`, `/api/legal/terms` или эквивалент через server routes `server/api/legal/privacy.get.ts`, `terms.get.ts`).
- Компонент `CookieConsentModal.vue`: баннер согласия на cookies; отправка выбора через `useApi().submitConsent()` на backend; сохранение предпочтения (например, в cookie/localStorage); использование **ymId** (Yandex.Metrika) вместо gaId.
- Интеграция модалки в `layouts/default.vue` (position="banner").
- Константа API и `useApi` composable: метод `submitConsent()` для вызова `POST /api/v4/public/legal/consent/`.

**Паттерны:** Новый Django app в `mayan/apps/legal`, REST API без tenant; фронт — только Yandex.Metrika, без Google.

---

### Активная разработка (Текущий фокус)

#### 1. Multi-Tenancy Integration Part 3 (Новый ТЗ)
**Статус:** Sprint 1–3 ✅ COMPLETED & DEPLOYED; Sprint 4 (Security/Performance) завершён 2026-02-11; текущий фокус — Sprint 4 (следующая итерация): Security Polish & Backend Hardening  
**ТЗ:** `docs/transformation-2025/АНАЛИЗ КОНТЕКСТА И ОБНОВЛЕННОЕ ТЕХНИЧЕСКОЕ ЗАДАНИЕ.md` (Part 3)  
**GAPS Report:** `tmp/GAPS_REPORT_PART3.md`

**Контекст:**
- Базовая инфраструктура Multi-tenancy (Sprint 1-4) завершена
- Organizations Module полностью реализован
- Document модель имеет organization FK
- **Sprint 1 Part 3 (DAM):** DocumentAIAnalysis сделан tenant-aware, миграции применены, деплой выполнен

**Оставшиеся GAPS (из аудита):**
- ✅ ~~DocumentAIAnalysis НЕ tenant-aware~~ — **исправлено (Sprint 1 Part 3)**
- ✅ ~~AssetEvent НЕ tenant-aware~~ — **исправлено (Sprint 2)**
- ✅ ~~**ShareLink** НЕ tenant-aware~~ — **исправлено (Sprint 3)**
- ✅ ~~Analytics Dashboard не фильтрует по Organization~~ — **исправлено (Sprint 2)**
- ✅ ~~**Notifications WebSocket** не валидирует Organization~~ — **исправлено (Sprint 3)**

**Sprint'ы Part 3:**
- **Sprint 1 (Неделя 1-2):** DAM модуль — ✅ **ЗАВЕРШЁН** (DocumentAIAnalysis tenant-aware, миграции 0007-0009, API/tasks/signals, pre-save binding, тесты изоляции, Pre-Deployment Static Analysis, деплой по Action Plan)
- **Sprint 2 (Неделя 3-4):** Analytics модуль — ✅ **ЗАВЕРШЁН** (AssetEvent tenant-aware, middleware, dashboard API, reports, isolation tests; code review 2026-02-11, critical date_range fix applied)
- **Sprint 3 (Неделя 5-6):** Distribution + Notifications — ✅ **ЗАВЕРШЁН** (ShareLink tenant-aware, WebSocket org validation)
- **Sprint 4 (Неделя 7):** Security Audit + Performance Tuning — ✅ **ЗАВЕРШЁН 2026-02-11**

**Общая трудоемкость:** 50-55 story points

**Архитектурные решения:**
- Использование TenantAwareMixin для всех tenant-aware моделей
- Celery tasks передают organization_id явно (TenantAwareTask)
- Middleware устанавливает request.organization для всех запросов
- ContextVar для потокобезопасности в async контексте

**Sprint 1 Part 3 (DAM) — ЗАВЕРШЁН И ЗАДЕПЛОЕН 2026-02-11:**
- ✅ DocumentAIAnalysis: TenantAwareMixin, явный FK `organization`, composite index (organization, -created)
- ✅ Миграции dam: 0007 (AddField nullable), 0008 (RunPython populate из document.organization_id), 0009 (AlterField NOT NULL + AddIndex)
- ✅ API: DocumentAIAnalysisViewSet — select_related('organization'), _get_organization_id_for_task(), передача organization_id в Celery (analyze, reanalyze, bulk_analyze)
- ✅ Serializers: DocumentAIAnalysisSerializer — read-only поля organization, organization_name
- ✅ Tasks: analyze_document_with_ai, get_or_create с organization_id из document; fallback при отсутствии; bulk_analyze_documents передаёт org в дочерние задачи
- ✅ Signals: trigger_ai_analysis передаёт organization_id в apply_async; pre_save binding в organizations/apps.py для DocumentAIAnalysis (context → document.organization → default org)
- ✅ Тесты: mayan.apps.dam.tests.test_tenant_isolation — модель, API (X-Organization-Id), Celery, DocumentFile/DocumentVersion через Document
- ✅ Pre-Deployment Static Analysis: миграции без циклов, нет циклических импортов, organization_id передаётся как str(UUID), signal без рекурсии
- ✅ Деплой по Action Plan: бэкап БД (backup_pre_dam_tenant.sql), пересборка app, migrate dam, перезапуск app + app_websocket, smoke test (Without org: 0) — **успешно**

**Важно для Docker:** команды Django в контейнере выполняются через `/opt/mayan-edms/bin/mayan-edms.py` (не `python manage.py`).

**Deployment Hotfixes 2026-02-13 (при перезапуске контейнеров):**
- ✅ analytics/api_views.py: исправлен импорт `Permission` — был `acls.classes` (ImportError), заменён на `permissions.classes`
- ✅ analytics/api_views.py: добавлены отсутствовавшие views для rest_api/urls: `EmailClickWebhookView`, `AnalyticsEventsExportView`, `AnalyticsHealthCheckView` (заглушки: webhook 200 OK, export 501, health 200 OK)
- ✅ distribution/models.py + migration 0014: индекс `idx_distribution_sl_org_created` (31 символ) сокращён до `idx_dist_sl_org_created` — Django E034: имя индекса не более 30 символов

**Sprint 2 Part 3 (Analytics) — ЗАВЕРШЁН 2026-02-11:**
- AssetEvent: TenantAwareMixin, organization FK, migrations 0010–0012, pre_save binding в organizations/apps.py (context → document.organization → default org). Создание событий: track_asset_event_async (явный organization_id) или pre_save при ручном создании.
- Middleware: AssetEventTrackingMiddleware (sync, process_response), fire-and-forget вызов track_asset_event_async.delay(); пути /api/v4/documents/, /api/v4/headless/documents/, "download"; требует request.organization, не трекает при response.status_code >= 400.
- Dashboard: AnalyticsDashboardViewSet, GET /api/v4/headless/analytics/dashboard/, строго по request.organization (400 при отсутствии); метрики tenant-scoped.
- Reports: AnalyticsReportTask (миграция 0013), generate_analytics_report — вывод только JSON в MEDIA_ROOT/reports/{org_id}/{task_id}.json; параметр export_format в API сохраняется в parameters, но task его не использует. date_range из parameters['date_range'] (from/to или date_from/date_to).
- Tests: test_middleware (track_asset_event_async.delay с organization_id), test_api (dashboard isolation), test_reports (sync run + API), test_tenant_isolation (AssetEvent, dashboard, report isolation).
- Code review: date_range читается из parameters['date_range']; optional 0011 orphan hardening documented.

**Sprint 3 Part 3 (Distribution + Notifications) — ✅ ЗАВЕРШЁН И РАЗВЁРНУТ (2026-02-11, верификация 2026-02-17):**
- ✅ ShareLink: TenantAwareMixin в модели, миграции distribution 0012 (AddField org nullable), 0013 (populate из rendition→document + сироты → default org), 0014 (NOT NULL + индексы org, org+created).
- ✅ Pre_save binding: _connect_sharelink_tenant_binding_signal() в organizations/apps.py (lazy import ShareLink); приоритет: явное → контекст → document по rendition → default org.
- ✅ Views/signals: портал и get_object_or_404(ShareLink, token=...) переведены на ShareLink.objects_unfiltered; в сигналах очистки (file delete, document trash/delete) — objects_unfiltered; при создании ShareLink передаётся organization=request.organization при наличии.
- ✅ Notifications WebSocket: в consumers.py при connect() читается organization_id из query string; при отсутствии или при отказе проверки членства (UserOrganizationRole) соединение закрывается с кодом 4003; group_name = notifications_{organization_id}_{user_id}.
- ✅ send_websocket_notification: хелпер get_organization_id_for_notification (action.target/action_object Document → organization_id, иначе default org пользователя); group_send в группу notifications_{org_id}_{user_id}.
- ✅ **AI Analysis Event Integration:** при завершении AI-анализа (dam/tasks.py) вызывается event_dam_ai_analysis_completed.commit(actor=document, target=document); подписчики получают EventNotification → send_notification_async → send_websocket_notification в org-scoped группу. Тип события зарегистрирован в dam/events.py и dam_taxonomy ('dam.ai_analysis_completed': 'ai').
- ✅ Тесты: distribution/tests/test_tenant_isolation.py (изоляция по контексту, API с X-Organization-Id, публичный доступ по токену); notifications test_tasks (org-scoped group), test_consumers (connect без org / чужая org → 4003, с valid org → accepted).

**Sprint 4 Part 3 (Security Audit + Performance Tuning) — ЗАВЕРШЁН 2026-02-11:**
- ✅ Security: отчёт `docs/transformation-2025/SPRINT4_SECURITY_AUDIT_REPORT.md` (аудит objects_unfiltered, cross-tenant тесты); Bandit добавлен в requirements/development.txt; интеграционные тесты в `mayan/apps/organizations/tests/test_cross_tenant_security.py` (dashboard/reports с X-Organization-Id другой org → default org).
- ✅ Performance: отчёт `docs/transformation-2025/SPRINT4_PERFORMANCE_REPORT.md`; индексы проверены (дополнений не требуется); кэш ответа dashboard (TTL 5 мин, `analytics/dashboard_cache.py`), инвалидация при AssetEvent (signal в analytics/signals.py).
- ✅ Load testing: сценарии в `tests/load/locustfile.py` (AnalyticsUser: dashboard, top-metrics, document list optimized; DocumentListUser); отчёт `docs/transformation-2025/SPRINT4_LOAD_TEST_REPORT.md`.
- ✅ DoD: Security 0 High/Critical (по отчёту); Performance тесты и NFR — см. отчёты; Memory Bank обновлён.

**Sprint 5 (High-Performance Frontend — Immersive Grid & Search) — ЗАВЕРШЁН 2026-02-17:**  
- **Phase 1:** Установлен `@tanstack/vue-virtual`; создан `ImmersiveGrid.vue` с виртуализацией по строкам (useVirtualizer), расчёт колонок по ширине (useElementSize), скелетоны при подгрузке, infinite scroll (sentinel), кнопка «Наверх», Shift+Click и индексный drag-select. В `GalleryView.vue` порог 80: при < 80 активов — `AssetGrid`, при 80+ — `ImmersiveGrid`; старый кастомный виртуальный скролл (scrollTop/visibleAssets/totalHeight) удалён.  
- **Phase 2:** В `useDamSearchFilters` добавлена история поиска: localStorage `dam_search_history` (до 10 записей), `getSearchHistory()`, `applySearchFromHistory()`, запись в историю в `submitSearchNow()`. В Header при фокусе на поиске показывается блок «Недавние запросы». Фильтр «Ориентация» (portrait/landscape/square) добавлен в FiltersPanel, DamFiltersState, URL sync и assetStore (бэкенд пока не поддерживает width/height — UI готов).  
- **Phase 3:** Создан `AssetThumbnail.vue` (lazy load, плейсхолдер, ошибка); в AssetCard блок превью заменён на AssetThumbnail.  
- **Phase 4:** Создан `AssetContextMenu.vue` (правый клик: Открыть, Скачать, Поделиться, Редактировать метаданные, Удалить). В AssetCard добавлен `@contextmenu.prevent` и эмит `contextmenu`; AssetGrid и ImmersiveGrid пробрасывают `asset-contextmenu`; в GalleryView — единое контекстное меню и обработчики (в т.ч. переход на `/dam/assets/:id/edit` для редактирования метаданных). Drag-select и Shift+Click в ImmersiveGrid реализованы при создании компонента.

**Следующий фокус:** Part 3 (Sprint 1–4) и Sprint 5 (Frontend) завершены; следующий этап — **Sprint 4 (итерация 2): Security Polish & Final Backend Hardening** (см. предложенный объём ниже) или дальнейшая полировка фронта (тесты, accessibility, ориентация на бэкенде при появлении полей width/height).

**Sprint 4 (следующая итерация) — предложенный объём:**
1. **Security Audit:** Проверка edge cases TenantResolverMiddleware (публичные API без org, exempt paths, подмена X-Organization-Id).
2. **Performance Tuning:** Индексы для notification/event таблиц при необходимости; ревью тяжёлых запросов.
3. **Cleanup:** Удаление временных миграционных скриптов и отладочного кода (например debug.log в events/notifications).
4. **Documentation:** Актуализация/генерация OpenAPI (drf-spectacular) для tenant-aware endpoints (X-Organization-Id, share_links, notifications).

#### 2. Multi-tenancy Infrastructure (Завершено)
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

### Immediate (Sprint 1: DAM Module Integration)
1. **DocumentAIAnalysis Tenant-Aware:**
   - Добавить TenantAwareMixin к DocumentAIAnalysis модели
   - Миграция для добавления organization FK
   - Обновить Celery tasks для передачи organization_id
   - Тесты для изоляции AI анализов по тенантам
   - Story Points: 8-13 (US-DAM-002)

2. **DocumentFile и DocumentVersion проверка:**
   - Проверить наличие organization FK
   - При необходимости добавить TenantAwareMixin

### Short-term (Sprint 2: Analytics Module Integration)
1. **AssetEvent Tenant-Aware:**
   - Добавить TenantAwareMixin к AssetEvent модели
   - Миграция для добавления organization FK
   - Обновить middleware для автоматической регистрации событий
   - Story Points: 8 (US-ANALYTICS-001)

2. **Analytics Dashboard API:**
   - Фильтрация всех queryset'ов по request.organization
   - Обновление агрегаций для tenant-aware метрик
   - Story Points: 13 (US-ANALYTICS-002)

### Medium-term (Sprint 3: Distribution + Notifications)
1. **ShareLink Tenant-Aware:**
   - Добавить TenantAwareMixin к ShareLink модели
   - Обновить публичный API для проверки organization
   - Story Points: 8 (US-DISTRIBUTION-001)

2. **Notifications WebSocket:**
   - Валидация Organization в WebSocket consumer
   - Tenant-aware уведомления
   - Story Points: 13 (US-NOTIFICATIONS-001)

### Long-term (Sprint 4: Security + Performance)
1. **Security Audit:**
   - Penetration testing для cross-tenant access
   - Audit logging всех операций с Organization

2. **Performance Optimization:**
   - Кеширование метрик по Organization
   - Query optimization для tenant-aware запросов

### Previous Immediate (Следующие 1-2 недели)

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
