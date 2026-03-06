# Прогресс проекта Prime-EDMS (актуализация по коду и фактическому прогону, март 2026)

## 🟩 Реально работает

- [x] **Базовая multi-tenant инфраструктура:** `Organization`, `TenantResolverMiddleware`, tenant-aware модели, `X-Organization-Id`, новые tenant-scoped endpoints и тесты на изоляцию.
- [x] **Новый DAM-контур на `/dam`:** `GalleryView`, `ImmersiveGrid`, виртуальный скролл, blob-превью, lazy loading, горячие клавиши, работа через `/api/v4/documents/optimized/`.
- [x] **Home/activity tenant-safe слой:** HomePage и activity feed опираются на реальные tenant-scoped backend ответы; live router gap для home KPI endpoints устранен.
- [x] **Routing cleanup:** основной маршрут закреплен за `/dam`, legacy `/dam/gallery` переведен в cleanup/redirect режим, коллекции собраны вокруг `/dam/collections`.
- [x] **Collections и Shared With Me:** страницы переведены с placeholder/mock-логики на реальные cabinets/collections API.
- [x] **Recently Viewed и Favorites:** backend endpoints и frontend страницы/виджеты работают на реальных `AssetEvent`/headless API.
- [x] **Trash:** отдельная страница и базовая связка с backend endpoint'ами корзины.
- [x] **Шаринг подборок и public shares:** `CabinetUserShare`, CabinetShareModal, public share API, tenant-scoped backend для ссылок.
- [x] **AI pipeline:** auto-trigger через signal, Celery task, вызовы AI-провайдеров, сохранение результата в `DocumentAIAnalysis`, исправленный quota-check и честная degraded fallback-семантика.
- [x] **Базовый QA recovery фронтенда:** `Playwright` конфиг валиден, shared `Vitest` setup централизован, targeted smoke suites проходят.
- [x] **Accessibility / product hardening для DAM gallery primitives:** обновлены семантика, keyboard/focus сценарии и автоматические smoke audits через `vitest-axe` и `@axe-core/playwright`.

## 🟨 Работает частично / есть synthetic или legacy-слой

- [~] **Analytics dashboard:** основной tenant-aware analytics слой существует и частично используется, но live `geography` exposure еще требует отдельной починки.
- [~] **Distribution UI/state:** страницы шэринга и кампаний существуют, но live runtime все еще нестабилен из-за backend `500` и части устаревших адаптеров/mocks.
- [~] **Saved Searches / Home contracts:** backend tenant-aware реализован, но связанные интеграции все еще требуют финальной унификации после cleanup.
- [~] **Frontend QA:** инфраструктура восстановления выполнена, но полный прогон всего набора и последующее сокращение остаточных прикладных падений еще требуют отдельного спринта.
- [~] **Backend QA:** tenant/DAM targeted suite стабилизирован, но полный контейнерный suite все еще зависит от состояния test environment.

## 🟥 Не готово / требует стабилизации перед MVP+

- [ ] **Live distribution runtime stabilization:** `/api/v4/distribution/share_links/` и `/api/v4/distribution/campaigns/` нельзя считать стабилизированными до разбора текущих `500`.
- [ ] **WebSocket operational alignment:** frontend hooks/services еще не полностью синхронизированы с выделенным ASGI endpoint на `:8001`.
- [ ] **Полная зачистка legacy analytics/activity слоя:** старые endpoints вне нового основного пути еще требуют финальной ревизии.
- [ ] **Полный backend test environment:** контейнерный прогон tenant/DAM suite по-прежнему упирается в `django_test_migrations` и смежные env gaps.

## 🟦 Ближайшие продуктовые шаги

- [ ] Закрыть live runtime errors: `analytics geography`, `WebSocket`, `SharingPage IconEye`, `distribution share_links/campaigns`.
- [ ] Довести до конца cleanup legacy analytics/activity endpoints и убрать старые дубли из критических сценариев.
- [ ] Починить backend test environment в контейнере и прогнать полный tenant/DAM suite.
- [ ] Провести отдельный stabilization pass по полному фронтендному тестовому набору и operational monitoring.
