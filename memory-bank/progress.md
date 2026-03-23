# Прогресс проекта Prime-EDMS (актуализация по коду и фактическому прогону, март 2026)

> **Журнал memory bank (2026-03-19):** повторная синхронизация записей без изменений кодовой базы в этой сессии; зафиксировано: источник правды по топологии и контрактам — `docs/architecture/gitnexus-map.md`; открытые пункты прежние (live smoke, CI smoke, legacy matrix).
>
> **Журнал memory bank (2026-03-23):** синхронизация с закрытым планом §15 — newsletter в `marketing_cms`, unit-тесты `runtime_contract_smoke`, расширенный operational snapshot (broker, workers, indexing, переименование recent counters), `degraded` при проблемах брокера, tenant negative checks для distribution HTTP + WS handshake; зафиксирован gap: нет отдельного GitHub workflow под compose-smoke.

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
- [x] **Operational hardening для analytics:** `analytics/health` отдает `operational snapshot`; добавлены operational markers/counters для consumer/tasks, чтобы stream/report/task проблемы были видимы вне UI.
- [x] **Public auth/public telemetry/newsletter contract alignment:** backend публикует canonical routes `public/auth/login`, `public/auth/register`, `public/auth/verify-email`, `public/analytics/events`, `public/newsletter`; `public-frontend`, MSW и Playwright smoke выровнены под этот контракт.
- [x] **Runtime patch observability:** runtime patching в `organizations` теперь имеет явный status/visibility слой и test coverage, а не остается полностью неявным monkey-patching behavior.
- [x] **Runtime HTTP smoke harness:** добавлен `runtime_contract_smoke` management command для live tenant-scoped HTTP smoke без зависимости от `curl.exe`.
- [x] **Runtime WS smoke harness:** `runtime_contract_smoke` проверяет HTTP seams и raw WebSocket handshake для notifications/analytics, включая negative checks без `organization_id`; дефолт `--base-url` — `http://localhost:8080`, WS — `--ws-base-url` или авто-порт `8001` при split-topology.
- [x] **Smoke command regression tests:** `mayan/apps/analytics/tests/test_runtime_contract_smoke.py` фиксирует поведение команды без живого Docker.
- [x] **Public contract cleanup для newsletter/perimeter:** `public/newsletter` теперь опубликован в backend как canonical public route; старый dead SPA drift вокруг несуществующих `distribution/publications/portal/*` JSON endpoints убран из frontend.
- [x] **Operational snapshot expansion:** `analytics/health` теперь показывает broker reachability, worker count, task-specific markers и indexing counters вместо только общих task markers и двусмысленных `24h` counters.

## 🟨 Работает частично / есть synthetic или legacy-слой

- [~] **Live runtime smoke:** harness готов (HTTP + WebSocket), но финальный live прогон по `geography` / `campaigns` / `share_links` / `analytics/health` / WS seams не зафиксирован из-за периодически недоступного Docker engine в среде разработки.
- [~] **CI smoke entrypoint:** отдельного workflow/job под `runtime_contract_smoke` при поднятом compose пока нет (в репозитории — `frontend.yml` и `FUNDING.yml`).
- [~] **Saved Searches / Home contracts:** backend tenant-aware реализован, но связанные интеграции все еще требуют финальной унификации после cleanup.
- [~] **Frontend QA:** инфраструктура восстановления выполнена, но полный прогон всего набора и последующее сокращение остаточных прикладных падений еще требуют отдельного спринта.
- [~] **Backend QA в полном объеме:** targeted Django suite уже проходит, но повторный подтверждающий прогон в текущем состоянии среды уперся в недоступный Docker daemon; кроме этого, параллельные runs конфликтуют за `test_mayan`.
- [~] **Legacy contract cleanup:** часть published seams уже переведена на canonical contract и tenant guards, dead SPA portal drift удален, но финальная matrix-ревизия `canonical/deprecated/remove-after-migration` для остальных legacy маршрутов еще не завершена.

## 🟥 Не готово / требует стабилизации перед MVP+

- [ ] **Полное подтверждение runtime seams на живом стеке:** до завершения hardening нужен успешный live smoke для tenant-scoped HTTP/WS контуров на доступном runtime.
- [ ] **Полная зачистка legacy analytics/activity слоя:** старые endpoints вне нового основного пути еще требуют финальной ревизии и формального статуса в cleanup matrix.
- [ ] **Полный backend test environment:** tenant/DAM suite по-прежнему упирается в test runner / container-source drift и environment gaps вокруг Docker/test DB lifecycle.

## 🟦 Ближайшие продуктовые шаги

- [ ] Восстановить доступный Docker/runtime и завершить live smoke по `geography`, `campaigns`, `share_links`, `analytics/health` и WebSocket seams (команда: `mayan-edms.py runtime_contract_smoke` с реальными учётными данными).
- [ ] При необходимости добавить CI шаг или scheduled job для smoke против staging/compose.
- [ ] Довести до конца cleanup matrix для legacy analytics/activity/public contracts и убрать оставшиеся старые дубли из критических сценариев.
- [ ] Повторно подтвердить targeted backend regression suite в доступной containerized среде.
- [ ] Провести отдельный stabilization pass по полному фронтендному тестовому набору и operational monitoring.
