# Прогресс проекта Prime-EDMS (актуализация по коду и фактическому прогону, март 2026)

## 🟩 Реально работает

- [x] **Базовая multi-tenant инфраструктура:** `Organization`, `TenantResolverMiddleware`, tenant-aware модели, `X-Organization-Id`, новые tenant-scoped endpoints и тесты на изоляцию.
- [x] **Token-aware tenant resolution:** middleware корректно обрабатывает `Authorization: Token ...` еще до DRF auth phase, поэтому tenant context работает и для SPA/token запросов, и для containerized regression tests.
- [x] **Новый DAM-контур на `/dam`:** `GalleryView`, `ImmersiveGrid`, виртуальный скролл, blob-превью, lazy loading, горячие клавиши, работа через `/api/v4/documents/optimized/`.
- [x] **Home/activity tenant-safe слой:** HomePage и activity feed опираются на реальные tenant-scoped backend ответы; live router gap для home KPI endpoints устранен.
- [x] **Analytics geography runtime fix:** live router для `/api/v4/headless/analytics/dashboard/geography/` уже существует, frontend store/page показывают не silent-empty fallback, а явный geography error state, а targeted tests проверяют и `200` contract, и `400` без organization context.
- [x] **Routing cleanup:** основной маршрут закреплен за `/dam`, legacy `/dam/gallery` переведен в cleanup/redirect режим, коллекции собраны вокруг `/dam/collections`.
- [x] **Collections и Shared With Me:** страницы переведены с placeholder/mock-логики на реальные cabinets/collections API.
- [x] **Recently Viewed и Favorites:** backend endpoints и frontend страницы/виджеты работают на реальных `AssetEvent`/headless API.
- [x] **Trash:** отдельная страница и базовая связка с backend endpoint'ами корзины.
- [x] **Шаринг подборок и public shares:** `CabinetUserShare`, CabinetShareModal, public share API, tenant-scoped backend для ссылок.
- [x] **AI pipeline:** auto-trigger через signal, Celery task, вызовы AI-провайдеров, сохранение результата в `DocumentAIAnalysis`, исправленный quota-check и честная degraded fallback-семантика.
- [x] **Базовый QA recovery фронтенда:** `Playwright` конфиг валиден, shared `Vitest` setup централизован, targeted smoke suites проходят.
- [x] **Accessibility / product hardening для DAM gallery primitives:** обновлены семантика, keyboard/focus сценарии и автоматические smoke audits через `vitest-axe` и `@axe-core/playwright`.
- [x] **Realtime contract alignment на frontend:** notifications и analytics websocket URL теперь строятся через единый helper contract с `token`/`organization_id`; targeted Vitest для `useWebSocket` и `AssetBankPage` проходит.
- [x] **Distribution campaign tenant migration:** `0018_distributioncampaign_organization` применена в контейнерном runtime; локальная проверка подтверждает актуальную схему без непримененных migration gaps для campaigns.
- [x] **Targeted backend regression runner:** verification выполняется через контейнерный `/opt/mayan-edms/bin/mayan-edms.py`, а не через локальный `manage.py`; green run подтвержден для `headless_api`, `analytics reports`, `analytics consumers` и `distribution tenant isolation`.

## 🟨 Работает частично / есть synthetic или legacy-слой

- [~] **Live runtime smoke:** контейнерный стек поднят, admin token и organization уже получены, но отдельный live HTTP smoke по `geography` / `campaigns` / `share_links` еще не зафиксирован из-за локального shell-spawn issue на Windows.
- [~] **Saved Searches / Home contracts:** backend tenant-aware реализован, но связанные интеграции все еще требуют финальной унификации после cleanup.
- [~] **Frontend QA:** инфраструктура восстановления выполнена, но полный прогон всего набора и последующее сокращение остаточных прикладных падений еще требуют отдельного спринта.
- [~] **Backend QA в полном объеме:** targeted Django suite уже проходит, но параллельные test runs конфликтуют за `test_mayan`, а полный широкий suite все еще требует отдельной стабилизации test DB lifecycle.

## 🟥 Не готово / требует стабилизации перед MVP+

- [ ] **Полная зачистка legacy analytics/activity слоя:** старые endpoints вне нового основного пути еще требуют финальной ревизии.
- [ ] **Полный backend test environment:** tenant/DAM suite по-прежнему упирается в test runner / container-source drift и `django_test_migrations`-подобные env gaps.

## 🟦 Ближайшие продуктовые шаги

- [ ] Завершить live smoke по sharing/campaign/geography endpoint'ам на уже поднятом `:8080` / `:8001` стеке.
- [ ] Довести до конца cleanup legacy analytics/activity endpoints и убрать старые дубли из критических сценариев.
- [ ] Провести отдельный stabilization pass по полному фронтендному тестовому набору и operational monitoring.
