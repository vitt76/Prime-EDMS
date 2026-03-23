# Активный контекст Prime-EDMS

## Текущий фокус

Текущий фокус — **environment-dependent verification** и поддержание синхронности docs/memory bank с live router и operational snapshot. Реализация плана (раздел 15 `gitnexus-map`, hardening приоритетов) по коду закрыта: `runtime_contract_smoke` (HTTP + raw WS handshake), public/newsletter backend, удаление dead SPA drift вокруг `distribution/publications/portal/*`, расширенный `analytics/health` snapshot с broker/workers/indexing и явной деградацией при недоступном брокере.

*Memory bank обновлён: 2026-03-19.*

- **Документация архитектуры:** каноническая карта платформы — `docs/architecture/gitnexus-map.md` (GitNexus): high-level контуры, tenant/public/WS, риски §14 и приоритеты §15; при смене портов, compose-сервисов или public API держать документ и memory bank в паре.

## Подтвержденное текущее состояние

- **Backend test harness normalization:** `TenantResolverMiddleware` читает `DEPLOYMENT_MODE` и `SAAS_BASE_DOMAIN` динамически из `settings`; для tenant/DAM integration tests используется общий `SaaSTenantTestHarnessMixin`.
- **Token-aware tenant resolution:** middleware умеет резолвить пользователя из `Authorization: Token ...` еще до DRF auth phase, поэтому `X-Organization-Id` и default-org fallback работают и для SPA/token запросов, и для middleware-dependent tests.
- **Tenant/runtime hardening for published analytics:** опубликованные legacy analytics viewsets теперь требуют явный `request.organization`, а geography/asset-bank seams дополнительно закреплены через contract tests.
- **Route exposure hardening:** live router в `mayan/apps/rest_api/urls.py` теперь остается единой точкой публикации как для headless analytics geography, так и для новых public marketing/auth endpoints; `runtime_contract_smoke` расширен до tenant-scoped HTTP negative checks и raw WebSocket handshake checks для notifications/analytics seams.
- **Public contract cleanup:** backend публикует canonical routes `public/auth/login`, `public/auth/register`, `public/auth/verify-email`, `public/analytics/events`, `public/newsletter` (POST → `Lead` с `source='newsletter'`, см. `marketing_cms` + `test_public_api.py`); `public-frontend`, MSW и Playwright smoke выровнены под эти пути; мёртвый SPA-контур и методы `distributionService` под несуществующие `distribution/publications/portal/*` удалены.
- **Smoke command testability:** `mayan/apps/analytics/tests/test_runtime_contract_smoke.py` покрывает логику команды через моки HTTP (`_request`) и WebSocket handshake (`_websocket_handshake`), чтобы регрессии ловились без живого стека.
- **Operational telemetry hardening:** `analytics/health` расширен до `operational snapshot`; для analytics consumer/tasks добавлены task-specific operational markers, snapshot теперь показывает broker reachability, worker count и indexing counters, чтобы failures/lag/stale reports были наблюдаемыми, а не только косвенно видимыми через UI.
- **Runtime patch observability:** `organizations/patches.py` теперь сохраняет явный status runtime patching (`HttpRequest`, `Document.organization`, patched managers), а `OrganizationsApp.ready()` логирует итоговый patch status; добавлен test coverage на patch-status contract.
- **Backend code integrity:** новые и измененные Python-файлы проходят локальную синтаксическую проверку через `py_compile`; кодовая интеграция выполнена без синтаксических ошибок.

## Текущая архитектура (Шпаргалка)

- **Multi-tenancy:** `X-Organization-Id`, `TenantResolverMiddleware`, `TenantAwareMixin` и tenant-scoped модели остаются базовым паттерном.
- **Headless API exposure:** наличие view в `mayan/apps/headless_api/views/` недостаточно; критические SPA/public endpoints считаются готовыми только если они смонтированы в live router и покрыты smoke/contract checks.
- **Public contract:** для public frontend теперь canonical является `public/auth/*` family, а не старые смешанные пути вроде `public/register` или `public/verify-email/:token`.
- **Operational split:** SPA использует `:5173`, Django API — `:8080`, public frontend — `:3000`, а WebSocket ASGI контур живет отдельно на `:8001`; ошибки чаще возникают на seams между этими входными точками.
- **Runtime patching:** `contribute_to_class` и manager monkey-patching по-прежнему остаются частью совместимости с Mayan, но теперь этот слой должен быть явно наблюдаем и тестируем.

## Ближайшие задачи (Next Actions)

1. Подтвердить live smoke для tenant-scoped endpoint'ов (`headless geography`, `distribution campaigns`, `share_links`, `analytics/health`) и WebSocket handshake (`/ws/notifications/`, `/ws/analytics/`) на доступном Docker/localhost стеке с валидными `--token` и `--organization-id`.
2. При доступном runtime повторно прогнать targeted Django suite (`marketing_cms` public API, `analytics` health/operational, `test_runtime_contract_smoke`) через `mayan-edms.py test` или pytest в контейнере.
3. Опционально: добавить CI/ops entrypoint (отдельный workflow или job) для периодического `runtime_contract_smoke` при поднятом compose — сейчас в `.github` только `frontend.yml`, dedicated smoke pipeline отсутствует.
4. Продолжить cleanup matrix для остальных legacy маршрутов, которые реально ещё опубликованы; не трогать уже снятый dead SPA drift.
5. Держать `docs/architecture/gitnexus-map.md` и memory bank синхронными с operational snapshot и public perimeter.

## Известные проблемы / Риски (Known Issues)

- Главный незакрытый риск сейчас не в отсутствии кода, а в verification environment: локальный Docker daemon/runtime периодически недоступен, поэтому containerized regression и live smoke не удалось повторно подтвердить в конце прохода.
- Полный backend test environment по-прежнему хрупок: параллельные Django test runs конфликтуют за `test_mayan`, поэтому verification надежно работает при последовательном запуске.
- Полная зачистка legacy analytics/activity слоя еще не завершена как matrix cleanup: часть старых маршрутов все еще требует формального статуса и последующего вывода из эксплуатации, хотя dead SPA portal drift уже убран.
- Локально без контейнера: `npm run type-check` может падать на накопленных исторических ошибках фронтенда; это не индикатор регрессии от последнего hardening-прохода.
- IDE по-прежнему показывает import-resolution warnings для Django/Channels/DRF в локальном Windows окружении, но это не проявилось как синтаксическая ошибка на измененных Python файлах.
