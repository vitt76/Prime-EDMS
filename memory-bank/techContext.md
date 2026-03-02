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

#### Analytics (tenant-aware, Sprint 2)
- **AssetEvent:** TenantAwareMixin, FK organization (NOT NULL); индексы idx_analytics_ae_org_type_ts (organization, event_type, -timestamp), idx_analytics_ae_org_doc_ts (organization, document, -timestamp). Создание: pre_save signal в organizations/apps.py (context → document.organization → default org) или явная передача organization_id в track_asset_event_async.delay().
- **AssetEventTrackingMiddleware:** Синхронный (MiddlewareMixin, process_response). Срабатывает на GET /api/v4/documents/, /api/v4/headless/documents/ и путях, содержащих "download"; вызывает track_asset_event_async.delay(organization_id=..., document_id=..., ...) (fire-and-forget). Не трекает при отсутствии request.organization или при response.status_code >= 400. Порядок в цепочке: после TenantResolverMiddleware (чтобы request.organization был установлен).
- **Dashboard API:** GET /api/v4/headless/analytics/dashboard/ — один endpoint; строго требует request.organization (400 при отсутствии); метрики по организации: Document.valid.filter(organization=org), AssetEvent.objects.filter(organization=org), org.get_storage_used_gb(), org.get_ai_analyses_this_month(), top_documents по просмотрам за 30 дней. **Sprint 4:** ответ кэшируется в Redis (TTL 5 мин, ключ analytics:dashboard:{org_id}); инвалидация при создании/обновлении AssetEvent (analytics/dashboard_cache.py, signal в signals.py).
- **Reports:** AnalyticsReportTask (status pending/processing/completed/failed); Celery generate_analytics_report читает parameters['date_range'] (ключи from/to или date_from/date_to), фильтрует AssetEvent по organization_id, пишет только JSON в MEDIA_ROOT/reports/{org_id}/{task_id}.json. Параметр export_format в API сохраняется в parameters, но task его не использует (экспорт только JSON).
- **SearchSession:** TenantAwareMixin, FK organization (NOT NULL); связь с AssetEvent через search_session_id (UUID на AssetEvent); first_search_query (FK SearchQuery), last_download_event (FK AssetEvent), time_to_find_seconds. Создаётся в optimized_document_api_views при поиске (q=) с request.organization; при download middleware может передавать X-Search-Session-Id в track_asset_event_async.
- **OrganizationBandwidthDaily:** organization, date, bandwidth_gb, cost_usd; заполняется задачей calculate_organization_bandwidth_daily по данным AssetEvent (event_type=download, Sum(bandwidth_bytes)) по организации за день; стоимость из Plan.cdn_cost_per_gb или settings.ANALYTICS_CDN_COST_PER_GB.
- **FeatureUsage:** TenantAwareMixin, FK organization; фичи ai_analysis, share_link_create и др.; трекинг из dam/tasks (после AI analysis) и distribution (создание Share Link). Дашборд возвращает feature_adoption: по каждой фиче — users_count и adoption_rate_percent за 30 дней.
- **Geo:** IP сохраняется в AssetEvent.metadata при создании (track_asset_event_async); обогащение — задача enrich_event_geo_data (GeoIP2, get_geo_from_ip в analytics.utils); metadata дополняется полями country, city. Требуется geoip2 и GEOIP_DATABASE_PATH.
- **Отчёт (user_activity):** generate_analytics_report дополнен секцией user_activity: dau (уникальные user_id по дням за date_from–date_to), mau (за 30 дней от date_to), churn_count (UserOrganizationRole без событий за 30 дней), churn_period_days=30.

#### Веб-серверы
- **Gunicorn**: 20.1.0 (WSGI сервер для основного приложения)
- **Daphne**: 3.0.2 (ASGI сервер для WebSocket уведомлений; подключение к ws/notifications/ с query token и organization_id; группа notifications_{org_id}_{user_id})

#### Event → Notification → WebSocket (Sprint 3)
- **Поток:** DAM/другое приложение вызывает `EventType.commit(actor=..., target=...)` (например `event_dam_ai_analysis_completed.commit(actor=document, target=document)` в dam/tasks.py после успешного AI-анализа). Событие создаёт actstream Action; events app по подпискам (EventSubscription, ObjectEventSubscription) создаёт EventNotification для каждого подписчика; для каждого уведомления вызывается `send_notification_async.apply_async(notification_id)` (notifications/utils.py при enhance). В `send_notification_async` при включённом push вызывается `send_websocket_notification.apply_async(notification_id)`. Task `send_websocket_notification` вычисляет `organization_id = get_organization_id_for_notification(notification)` (из action.target/action_object Document или default org пользователя) и выполняет `channel_layer.group_send('notifications_{org_id}_{user_id}', {'type': 'notification.new', 'data': ...})`. Клиенты, подключённые к WebSocket с тем же token и organization_id (и членством в этой org), получают сообщение.
- **Регистрация типов:** DAM события в `mayan.apps.dam.events` (namespace `dam`), для Document регистрируются через `ModelEventType.register` в dam/apps.py. Типы для DAM Notification Center перечислены в `notifications/dam_taxonomy.py` (EVENT_TYPE_TO_CATEGORY, напр. `dam.ai_analysis_completed`: `ai`).

#### API и интеграции
- **Django REST Framework**: 3.13.1 (REST API)
- **drf-spectacular**: 0.27.2 (OpenAPI документация)
- **django-cors-headers**: 3.10.0 (CORS поддержка)

#### Phase 5 (Sprint 1 Backend) — Search & History APIs
- **Orientation:** GET `/api/v4/documents/optimized/?orientation=portrait|landscape|square` — аннотации по последнему DocumentFile (latest_file_width, latest_file_height), фильтр по соотношению сторон; DocumentFile имеет nullable поля width, height (миграция 0087).
- **Recently Viewed:** GET `/api/v4/headless/documents/recently-viewed/?limit=20&days=30` — документы по AssetEvent (event_type view/download) для текущего user и organization, порядок по последнему просмотру, ACL, тот же сериализатор что и список; требует заголовок X-Organization-Id.
- **Saved Searches:** GET/POST `/api/v4/headless/saved-searches/`, GET/PATCH/DELETE `/api/v4/headless/saved-searches/<id>/`, GET `/api/v4/headless/saved-searches/<id>/run/` — tenant-aware CRUD; run применяет сохранённые query и filters через логику OptimizedAPIDocumentListView и возвращает results в том же формате. Лимит 20 сохранённых поисков на пользователя.

#### Sprint 1 Discovery UX — Frontend (2026-02-20)
- **Saved Searches UI:** Сервис `savedSearchesService.ts` (list, create, update, delete, run); все вызовы через `apiService` (X-Organization-Id из localStorage). Компоненты: SavedSearchesDropdown (кнопка в шапке через Teleport в `#header-search-actions`, список с Run/Edit/Delete, «Сохранить текущий поиск»), SaveSearchModal (имя, валидация, backendError для лимита 20), RenameSavedSearchModal. При Run вызывается `useDamSearchFilters.applySavedSearch(query, filters)` — парсинг через `parseSavedSearchFilters`, установка state и `fetchNow()`; URL синхронизируется, reload консистентен. Утилита `savedSearchFilters.ts`: buildSavedSearchFilters (frontend → backend keys), parseSavedSearchFilters (обратно).
- **Recently Viewed UI:** Сервис `recentlyViewedService.ts` — GET recently-viewed с limit/days, адаптация через mayanAdapter. Компонент RecentlyViewedBlock (горизонтальная полоса карточек, скелетон 6 ячеек, empty «Пока нет недавно просмотренных», error inline); размещён в GalleryView над сеткой; «Показать все» → `/dam/recent`. RecentPage переведён на getRecentlyViewed (limit 50, days 30), данные через CollectionBrowser. TTL/refresh: один запрос при монтировании блока, без избыточного refetch при фокусе.
- **Orientation wiring:** FiltersPanel уже отдаёт orientation в v-model; useDamSearchFilters держит state.filters.orientation; assetStore.buildQueryParams добавляет `orientation` в queryParams для GET optimized. URL sync через route.query.orientation при инициализации и при сбросе фильтров (case 'orientation' в FiltersPanel). Кэширование: без изменений — существующая логика assetStore.

#### Sprint 2 Productivity & UX — Backend и Frontend (2026-02-20)
- **Headless Favorites:** GET `/api/v4/headless/favorites/` и POST `/api/v4/headless/favorites/<document_id>/` требуют заголовок X-Organization-Id (400 без него). GET возвращает только документы с document.organization_id == request.organization; POST toggle — 403, если документ принадлежит другой организации. Реализация: `headless_api/views/favorites_views.py` (HeadlessFavoriteListView, HeadlessFavoriteToggleView).
- **Optimized list favorites_only:** В `documents/api_views/optimized_document_api_views.py` при query-параметре `favorites_only=true` список ограничивается документами из FavoriteDocument для текущего пользователя; при наличии request.organization — только документы этой организации.
- **Frontend:** Фильтр «Только избранное» — useDamSearchFilters.state.filters.favoritesOnly, URL-ключ `favorites_only`, assetStore.buildQueryParams; чекбокс в FiltersPanel. Избранное на карточке (AssetCard + favoritesStore) и в AssetContextMenu. Composable `useGalleryHotkeys`: один keydown-слушатель на document, игнор при фокусе в input/textarea/contenteditable; F — toggle избранного для выбранных, Space — AssetPreviewModal, Delete/Backspace — BulkDeleteModal, Esc — закрытие модалок или снятие выделения, Ctrl+A — выделить все, Shift+? — HotkeysCheatSheetModal. AssetPreviewModal и HotkeysCheatSheetModal подключены в GalleryView.

#### Спринт 3 Content (Доработка 2026) — Versioning, Deduplication, Renditions
- **Versioning:** POST `/api/v4/headless/documents/<id>/versions/activate/` (body: `version_id` или `file_id`); алиас POST `.../versions/<version_id>/revert/`. Загрузка новой версии: POST `/api/v4/documents/<id>/files/`. Tenant-фильтрация в version_views.
- **Potential Duplicates:** GET `/api/v4/headless/documents/<id>/potential-duplicates/` — документы той же организации с тем же checksum (file_latest), ACL, лимит 20. Требует request.organization.
- **Renditions:** RenditionPreset.organization (FK, null=global); список пресетов и выбор при Share Link фильтруются по request.organization. Publication.organization задаётся при создании Share Link. Дефолтные пресеты (миграция distribution 0015): Instagram 1:1 1080, VK 1200, Печать A4 300 dpi.
- **Watermarks:** OrganizationWatermarkSettings (organizations, OneToOne Organization): enabled, text, logo_url, position, opacity, font_size; to_watermark_dict() для distribution. GET/PATCH `/api/v4/headless/organization/watermark/`. В generate_rendition_task применяется после пресета, если у publication есть organization с включённым watermark.

#### Спринт 3.5 Collaboration & Tech Debt (Доработка 2026)
- **Cabinet Sharing:** Модель `CabinetUserShare` для шаринга подборки с конкретными пользователями внутри организации (Tenant-scoped). Headless API: GET `org-members`, POST `share-with-users`, GET `shared-with-me`. Учет прав комбинируется из `AccessControlList` и `CabinetUserShare`. На фронтенде добавлен `CabinetShareModal` и разделены сайдбар-ссылки "Мои подборки" / "Доступные мне".
- **Vitest Setup:** Глобальная настройка `createPinia()` в `beforeEach`, моки `vue-router` и `HTMLCanvasElement.getContext`, заглушки для `IntersectionObserver` и `scrollTo`. Решение проблемы ~330 падающих тестов.

#### Спринт 4 Collaboration (Доработка 2026) — Public Share API и модель безопасности
- **Public Share API:** GET `/api/v4/public/shares/<uuid>/` — доступ без авторизации (`AllowAny`). Возвращает метаданные коллекции (label, uuid) и список документов (id, label, thumbnail_url). Опционально: query-параметр `password=` для защищённых ссылок.
- **Модель безопасности (UUID + пароль):**
  - **Истечение:** при `expires_at < now` ответ 403 с `expired: true`.
  - **Пароль:** при установленном `password_hash` доступ разрешён только если передан корректный `password` в query; иначе 403 с `requires_password: true`. Брутфорс-защита (rate limit, lockout) не реализована.
- **Авторизованные эндпоинты:** POST `/api/v4/cabinets/<id>/shares/` (создание ссылки, body: expires_at, password); GET `/api/v4/cabinets/<id>/shares/` (список); DELETE `/api/v4/cabinets/<id>/shares/<uuid>/` (отзыв, проверка прав на cabinet через ACL).
- **Комментарии:** API документов `documents/<id>/comments/` — tenant isolation (document в текущей организации); редактирование/удаление только автор комментария (`comment.user_id == request.user.pk`).

#### Спринт 5 Security & Compliance (Доработка 2026)
- **Watermarking:** headless_api/watermark_utils.py — общая логика apply_watermark и organization_watermark_to_editor_state; редактор изображений в медиатеке и задача apply_watermark_task используют её. OrganizationWatermarkSettings.apply_on_download; модель WatermarkedRendition (distribution, миграция 0017); задача apply_watermark_task в очереди `documents`, регистрация в documents/queues.py (обязательно для task_manager).
- **Audit Log:** AssetEvent.metadata хранит user_agent (до 500 символов); AssetEvent.document nullable, event_type collection_share; при создании CabinetShare вызывается track_asset_event_async. GET /api/v4/headless/audit-logs/ (фильтры, пагинация), GET .../audit-logs/export/?format=csv|json; GET .../documents/{id}/activity/ (вкладка «Активность» в AssetDetailPage). Доступ: staff/superuser или группа audit_viewer.
- **Secure Download:** APIDocumentFileDownloadView при apply_on_download отдаёт WatermarkedRendition или ставит apply_watermark_task и отдаёт оригинал; при watermarked S3 redirect (direct=1) не используется.
- **Миграции в Docker:** `docker compose exec app /opt/mayan-edms/bin/mayan-edms.py migrate --noinput`. distribution 0015 использует atomic=False (обход PostgreSQL «pending trigger events»). cabinets: APICabinetShareView наследует generics.RetrieveDestroyAPIView (в Mayan нет DestroyAPIView).

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

#### DAM Frontend (Vue 3 SPA)
**Расположение:** `frontend/`

**Основной стек:**
- **Vue**: 3.x (SPA фреймворк)
- **TypeScript**: (типизация)
- **Vite**: 5.4.11 (сборщик и dev-сервер)
- **Pinia**: (state management)
- **Axios**: (HTTP клиент)
- **@tanstack/vue-virtual**: (виртуальная прокрутка для ImmersiveGrid, 10k+ активов)
- **@vueuse/core**: 10.7.2 (useElementSize, useDebounceFn и др.)

**UI библиотеки:**
- **Tailwind CSS**: (utility-first CSS фреймворк)
- **Chart.js**: 4.5.1 (графики и визуализация)

**Ключевые компоненты галереи (Sprint 5):** ImmersiveGrid (виртуализация по строкам), AssetThumbnail (lazy load + плейсхолдер), AssetContextMenu (правый клик, Teleport to body), история поиска в localStorage (dam_search_history), фильтр ориентации в URL. **Phase 4:** AssetCardSkeleton — переиспользуемый скелетон карточки (density compact/comfortable), используется при первой загрузке в GalleryView и при load more в ImmersiveGrid. Empty state при активных фильтрах: «Ничего не найдено» + кнопка «Сбросить фильтры». **Lazy-loaded компоненты:** MetadataPanel и AssetContextMenu подгружаются через defineAsyncComponent при первом открытии (уменьшение размера основного chunk). **Виртуализация:** стек @tanstack/vue-virtual; построчная виртуализация (rowCount = ceil(assets/columns)), колонки по useElementSize(container), контейнерный скролл, estimateSize по rowHeight (compact/comfortable), overscan 3. **Фасеты в assetStore:** при каждом fetch активов из API поля typeCounts, tagCounts, statusCounts берутся из ответа (response.facets) и полностью заменяют предыдущие значения (replace, не merge) — корректно для пагинации и смены фильтров. **Техдолг / оптимизация:** loadMore использует spread (`assets.value = [...assets.value, ...results]`); для сценариев 10k+ при профилировании рассмотреть append через slice + push для снижения аллокаций.

**AI endpoints и polling (Phase 3 Smart Metadata):** Эндпоинты: POST /api/v4/ai-analysis/analyze/ (body: document_instance), POST /api/v4/ai-analysis/bulk-analyze/ (body: document_ids, опционально ai_service), GET /api/v4/document-detail/{id}/ для получения ai_analysis. Сервис aiAnalysisService (apiService/axios), без моков; ошибки rethrow, UI показывает toast. **Polling (кнопка Magic в MetadataPanel):** после POST analyze — до 5 запросов getAIAnalysis с интервалом 2 с; выход при появлении описания (analysis.seo.description). Сохранение метаданных: assetService.updateAsset(id, { label, metadata: { description } }) → PATCH /api/v4/documents/{id}/.

**Аналитика (Frontend Visualization):** MetricCard, LineChart (Chart.js), GeoMap (барчарт по странам), AdoptionTable (feature_adoption из единого дашборда), RetentionCohort, Churn (unifiedDashboard.churn_count). ReportGenerateModal: POST .../reports/generate/, poll .../reports/{id}/, скачивание через getBlob(.../reports/{id}/download/). Store: unifiedDashboard, dashboardGeography, reportTaskId/reportTaskStatus; API: GET .../analytics/dashboard/, GET .../dashboard/geography/, GET .../reports/{id}/download/.

**Порт:** 5173 (development)

#### Public Frontend (Nuxt 3 SSR)
**Расположение:** `public-frontend/`

**Основной стек:**
- **Nuxt**: 3.8.0 (SSR/SSG фреймворк на базе Vue 3)
- **Vue**: 3.4.21 (базовый фреймворк)
- **TypeScript**: 5.3.3 (строгая типизация)
- **Node.js**: 18+ (требование)

**Nuxt модули:**
- **@nuxtjs/tailwindcss**: 6.10.0 (Tailwind CSS интеграция)
- **@nuxtjs/i18n**: 8.1.0 (интернационализация RU/EN)
- **@nuxt/image**: 1.3.0 (оптимизация изображений)
- **@pinia/nuxt**: 0.5.1 (Pinia state management)
- **@nuxtjs/sitemap**: 2.4.0 (генерация sitemap)
- **@nuxtjs/color-mode**: 3.4.0 (темная/светлая тема)

**UI библиотеки:**
- **Tailwind CSS**: (utility-first CSS фреймворк)
- **@headlessui/vue**: 1.7.16 (headless UI компоненты)
- **@heroicons/vue**: 2.1.1 (иконки)
- **@tailwindcss/forms**: 0.5.7 (стилизация форм)

**Утилиты:**
- **@vueuse/core**: 10.7.2 (Vue composition utilities)
- **axios**: 1.6.5 (HTTP клиент)
- **zod**: 3.23.8 (валидация схем)
- **markdown-it**: 14.0.0 (парсинг Markdown)
- **clsx**: 2.1.0 (условные CSS классы)

**Тестирование:**
- **Vitest**: 1.6.0 (unit тесты)
- **@vue/test-utils**: 2.4.5 (Vue компоненты тестирование)
- **Playwright**: 1.41.2 (E2E тесты)
- **MSW**: 2.0.0 (Mock Service Worker для моков API)
- **jsdom**: 23.2.0 (DOM окружение для тестов)

**Dev инструменты:**
- **Prettier**: 3.2.4 (форматирование кода)
- **ESLint**: (линтинг)
- **@types/node**: 20.11.5 (TypeScript типы для Node.js)

**Особенности:**
- **SSR**: Server-Side Rendering включен по умолчанию
- **SSG**: Static Site Generation для статических страниц
- **i18n**: Поддержка русского (по умолчанию) и английского языков
- **Dark Mode**: Поддержка темной темы с системным определением
- **Image Optimization**: Автоматическая оптимизация через IPX provider (WebP/AVIF)
- **Route Rules**: SWR кеширование для статических страниц
- **Prerendering**: Автоматический prerender для SEO-страниц

**Порт:** 3000 (development)

**Структура проекта:**
```
public-frontend/
├── assets/css/          # Глобальные стили (Tailwind)
├── components/          # Vue компоненты
│   ├── Blog/          # Компоненты блога
│   ├── Common/         # Переиспользуемые UI компоненты
│   ├── Forms/         # Формы (Contact, Login, Register)
│   ├── Sections/      # Секции страниц (Hero, Features, CTA, FAQ, Pricing)
│   └── SEO/           # SEO компоненты (PageMeta, JsonLd)
├── composables/        # Vue composables (useApi, useAuth, useForm, useSeo)
├── layouts/           # Layouts (default, auth)
├── locales/           # Переводы (ru.json, en.json)
├── middleware/        # Nuxt middleware (analytics, redirects)
├── pages/             # File-based routing
│   ├── index.vue      # Главная страница
│   ├── blog/          # Блог (index, [slug])
│   ├── pricing.vue    # Страница цен
│   ├── contact.vue    # Контакты
│   └── auth/          # Авторизация (login, register, verify-email)
├── plugins/           # Nuxt plugins (analytics, animations, crisp)
├── server/            # Server-side код
│   ├── api/           # API routes
│   └── middleware/    # Server middleware (security headers)
├── stores/            # Pinia stores (authStore, contentStore)
├── tests/             # Тесты
│   ├── e2e/          # Playwright E2E тесты
│   ├── integration/  # Интеграционные тесты
│   ├── mocks/        # MSW mock handlers
│   └── unit/         # Vitest unit тесты
└── types/             # TypeScript типы
```

**API интеграция:**
- Проксирование API запросов через Vite dev server (`/api` → `http://localhost:8080`)
- Endpoints:
  - `/api/v4/public/pages/:slug/` - Получение страниц
  - `/api/v4/public/posts/` - Список постов блога
  - `/api/v4/public/plans/` - Тарифные планы
  - `/api/v4/public/faq/` - FAQ элементы
  - `/api/v4/public/leads/` - Отправка форм обратной связи
  - `/api/v4/public/register/` - Регистрация пользователей
  - `/api/v4/public/verify-email/:token/` - Подтверждение email

**Оптимизации производительности:**
- Image optimization через Nuxt Image (WebP/AVIF форматы)
- Code splitting (vendor chunks для Vue, UI библиотек, утилит)
- Route-based caching (SWR для статических страниц)
- Prerendering для SEO-страниц (/, /pricing, /about, /blog)
- Compression для публичных ассетов
- Lazy loading компонентов и изображений

**SEO оптимизация:**
- Server-Side Rendering для лучшей индексации
- Автоматическая генерация sitemap
- JSON-LD structured data
- Meta tags через PageMeta компонент
- Оптимизированные URLs с i18n префиксами

**Доступность:**
- WCAG 2.1 Level AA compliance (в процессе)
- Keyboard navigation
- Screen reader support
- Semantic HTML

**Переменные окружения:**
- `NUXT_PUBLIC_API_URL` - URL Django backend (по умолчанию: http://localhost:8080)
- `NUXT_PUBLIC_APP_URL` - URL основного DAM приложения (по умолчанию: http://localhost:5173)
- `NUXT_PUBLIC_SITE_URL` - URL публичного сайта (по умолчанию: http://localhost:3000)
- `NUXT_PUBLIC_ENVIRONMENT` - Окружение (development/production)
- `NUXT_PUBLIC_GA_ID` - Google Analytics ID (опционально)

### Инфраструктура

#### Контейнеризация
- **Docker**: (контейнеризация приложения)
- **Docker Compose**: (оркестрация сервисов)
- **Django-команды в контейнере:** выполняются через `/opt/mayan-edms/bin/mayan-edms.py` (в образе Mayan EDMS нет `python manage.py` в PATH). Пример: `docker compose exec app /opt/mayan-edms/bin/mayan-edms.py showmigrations dam`, `migrate dam`, `shell -c "..."`.

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

#### Задействованные порты (текущий dev-статус)
- **8080** → `app` (Django/Gunicorn + REST API), внешний доступ: `http://localhost:8080`
- **8001** → `app_websocket` (Daphne/ASGI), внешний доступ: `ws://localhost:8001/ws/notifications/`
- **5173** → DAM SPA (Vite dev server), внешний доступ: `http://localhost:5173/dam`
- **3000** → Public Frontend (Nuxt dev server), внешний доступ: `http://localhost:3000`
- **5432 / 6379 / 5672 / 15672** — внутренние порты Docker-сети для PostgreSQL, Redis, RabbitMQ (в хост обычно не проброшены)

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

### Краткая инструкция по подъёму всех сервисов
1. В корне проекта (`c:\\DAM\\Prime-EDMS`) проверить Docker Engine и Docker Compose.
2. Запустить backend стек:
   - `docker compose up -d --build postgresql redis rabbitmq app app_websocket`
3. Проверить готовность:
   - `docker compose ps`
   - `docker compose logs --tail 100 app`
4. Запустить DAM SPA:
   - `cd frontend && npm install && npm run dev`
5. (Опционально) запустить Public Frontend:
   - `cd public-frontend && npm install && npm run dev`
6. Проверка доступности:
   - API: `http://localhost:8080/api/v4/`
   - DAM UI: `http://localhost:5173/dam`
   - Public UI: `http://localhost:3000`

### Остановка, перезапуск и проверка здоровья

- **Остановить весь backend:** `docker compose down` (опционально `-v` для удаления volumes).
- **Перезапуск одного сервиса:** `docker compose restart app` или `docker compose restart app_websocket`.
- **Статус контейнеров:** `docker compose ps` (healthy/unhealthy по healthcheck).
- **Логи:** `docker compose logs --tail 100 app`, `docker compose logs -f app` для follow.
- **Smoke-check endpoints (без токена):**
  - `curl -s -o NUL -w "%{http_code}" http://localhost:8080/api/v4/` → ожидается 200 или 401.
- **С токеном (после логина):** `GET http://localhost:8080/api/v4/documents/optimized/?page_size=1` → 200, `GET http://localhost:8080/api/v4/headless/auth/me/` → 200.

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
- **Organizations app**: Multi-tenancy изоляция (полностью реализован: модели, managers, middleware, API, permissions, quotas, frontend, suspend/activate, contribute_to_class FK patch)

## Multi-tenancy Architecture

### Подход: Shared Database + Shared Schema

**Архитектура:** Одна PostgreSQL база данных, одна схема, изоляция через ForeignKey на Organization.

**Критический компонент:** `TenantResolverMiddleware` — определяет текущую Organization для каждого запроса (Domain → Subdomain → X-Organization-Id → Token → Standalone) и выставляет `request.organization` и ContextVar для TenantAwareManager.

**Связь данных (Data Model):** Organization → Document (1:N). У Document обязательный FK `organization`; у DocumentAIAnalysis, AssetEvent, ShareLink — FK на Organization (tenant-aware). Доступ к документам и аналитике только в рамках текущей организации.

**Компоненты:**

#### Organizations Module (mayan.apps.organizations)
**Статус:** Полностью реализован (Sprint 1-4 + Hotfix + Tech Debt + Verification)  
**Коммит:** `7f41e418fe`

**Реализовано:**
- ✅ Базовый модуль создан (`mayan.apps.organizations`)
- ✅ Настройки: `ORGANIZATIONS_INSTALLATION_URL`, `ORGANIZATIONS_URL_BASE_PATH`
- ✅ Патчи: HttpRequest, organization FK (contribute_to_class), document managers
- ✅ Тесты: settings, requests, API views, permissions, cross-tenant isolation, suspend/activate
- ✅ Интеграция в apps.py с тремя уровнями патчей при старте
- ✅ REST API: CRUD, Members, Plans, Current org, Suspend, Activate
- ✅ Frontend: org store, selector, settings page, service methods
- ✅ Quota enforcement (Redis-cached), audit logging, security hardening

**Модели:**
- **Organization**: Тенант/компания (UUID primary key)
  - Поля: name, slug, email, industry, status, deployment_mode
  - Квоты: storage_limit_gb, max_users, max_ai_analyses_monthly
  - Кастомные домены для SaaS клиентов
- **Subscription**: Подписка на тарифный план
  - Связь с Plan
  - Биллинг: billing_cycle, amount, currency, payment_status
  - Статусы: trial, active, paused, cancelled, expired
- **Plan**: Тарифные планы (система-уровне)
  - Pricing: price_monthly, price_yearly
  - Лимиты: storage_gb, max_users, max_ai_analyses_monthly
  - Features: has_advanced_ai, has_analytics, has_distribution, etc.
- **DomainSettings**: Кастомные домены для SaaS (опционально)

**Middleware:**
- **TenantResolverMiddleware**: Определение Organization по:
  1. Кастомному домену (dam.company.com)
  2. Поддомену (app.dam-brand.com → slug='dam-brand')
  3. Токену в Authorization header
  4. Standalone mode (default Organization)

**Managers:**
- **TenantAwareManager**: Автоматическая фильтрация QuerySet по Organization
- Использует ContextVar для потокобезопасности
- Методы: `for_organization()`, `all_organizations()`

**Миксин:**
- **TenantAwareMixin**: Добавляет FK на Organization и TenantAwareManager
- Индексы на organization_id для производительности

**Режимы развертывания:**
- **SaaS** (`DEPLOYMENT_MODE=SAAS`): Множественные организации
- **Standalone** (`DEPLOYMENT_MODE=STANDALONE`): Одна организация по умолчанию

**Переменные окружения:**
- `DEPLOYMENT_MODE`: SAAS или STANDALONE
- `MAYAN_ORGANIZATIONS_AUTO_CREATE`: Автосоздание при регистрации

**Индексы БД:** Django E034 — имя индекса не более 30 символов (distribution: idx_dist_sl_org_created, не idx_distribution_sl_org_created).

**Миграции (структура после restructuring 2026-02-10):**
- Фаза 1: AddField organization (nullable) — операции в documents/0085, tags/0010, cabinets/0007; org 0002 — sync point
- Фаза 2: RunPython populate — org 0003 привязывает данные к default Organization
- Фаза 3: AlterField NOT NULL + AddIndex — операции в documents/0086, tags/0011, cabinets/0008; org 0004 — sync point
- Причина: Django AddField/AlterField не принимают app_label; cross-app операции должны быть в app-владельце модели

**Part 3 Integration (ЗАВЕРШЕНО — 2026-02-11):**
- ✅ **Sprint 1 (Неделя 1-2):** DAM модуль — DocumentAIAnalysis → TenantAwareMixin, миграции dam 0007–0009, API/tasks/signals, pre-save binding
- ✅ **Sprint 2 (Неделя 3-4):** Analytics модуль — AssetEvent → TenantAwareMixin, middleware, Dashboard API (tenant-scoped), Reports, geography
- ✅ **Sprint 3 (Неделя 5-6):** Distribution + Notifications — ShareLink tenant-aware, Notifications WebSocket org-scoped (organization_id в query, group notifications_{org_id}_{user_id})
- ✅ **Sprint 4 (Неделя 7):** Security Audit + Performance Tuning — отчёты, cross-tenant тесты, кэш dashboard, load testing

**Tenant-aware модели (реализовано):**
- ✅ Document (имеет organization FK, миграции documents/0085, 0086)
- ✅ Cabinet, Tag (имеют organization FK)

**Tenant-aware модели (реализовано — Part 3):**
- ✅ DocumentAIAnalysis (DAM) — TenantAwareMixin (Sprint 1)
- ✅ AssetEvent (Analytics) — TenantAwareMixin (Sprint 2)
- ✅ ShareLink (Distribution) — TenantAwareMixin (Sprint 3)
- **Фаза 4 (runtime):** `patch_organization_fields()` регистрирует FK organization на Document/Tag/Cabinet через `contribute_to_class()` — необходимо для ORM lookups (`document__organization`)

**Tenant-aware модели (реализовано):**
- ✅ Document (имеет organization FK)
- ✅ Cabinet, Tag (имеют organization FK)
- ✅ DocumentAIAnalysis, AssetEvent, ShareLink (Part 3 Sprints 1–3)
- ⚠️ DocumentFile, DocumentVersion — доступ к organization через document (проверка при необходимости)

**Глобальные модели (НЕ tenant-aware):**
- Plan (тарифные планы)
- MetadataType (типизация метаданных)
- Source (источники загрузки)

**Производительность:**
- Индексы на organization_id для всех tenant-aware моделей
- Composite индексы: (organization_id, created_at)
- select_related('organization') для оптимизации запросов
- Целевое время запроса: ≤200ms (vs 150ms без фильтра)

**Безопасность:**
- 100% защита от cross-tenant access
- Middleware проверяет is_active перед доступом
- Audit logging всех операций с Organization
- Rate limiting по Organization (в зависимости от Plan)

**Масштабируемость:**
- Поддержка ≥100 тенантов на одном сервере
- Готовность к шардированию (future)
- Database connection pooling (min 10, max 50)
- Redis кеширование для часто читаемых данных (Plans, User counts)
