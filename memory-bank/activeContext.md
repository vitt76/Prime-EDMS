# Активный контекст Prime-EDMS

## Текущий фокус

Проект завершил Runtime Follow-up Stabilization pass как на уровне исходного кода, так и на уровне targeted backend verification. Текущий фокус сместился с исправления runtime gaps на финальный operational smoke и последующее закрытие follow-up: migration для distribution campaigns уже применена, regression suite против актуального workspace-кода уже прогнан через контейнерный runtime, остается только окончательно подтвердить live HTTP smoke на поднятом стеке.

## Подтвержденное текущее состояние

- **Backend test harness normalization:** `TenantResolverMiddleware` теперь читает `DEPLOYMENT_MODE` и `SAAS_BASE_DOMAIN` динамически из `settings`, а не только из module-level env snapshot; для новых tenant/DAM integration tests введен общий `SaaSTenantTestHarnessMixin`.
- **Token-aware tenant resolution:** `TenantResolverMiddleware` теперь умеет резолвить пользователя из `Authorization: Token ...` еще до DRF auth phase, поэтому `X-Organization-Id` и default-org fallback корректно работают и для SPA/token запросов, и для containerized API tests.
- **Distribution tenant contract:** `DistributionCampaign` переведен на first-class tenant model через `TenantAwareMixin`; миграция `0018_distributioncampaign_organization` уже применена в контейнерном runtime.
- **Realtime/WebSocket contract:** analytics stream больше не открывается “анонимно”; frontend строит analytics websocket URL через единый helper с `token` и `organization_id`, backend consumer валидирует membership так же, как notifications consumer.
- **Verification hardening:** geography flow теперь проверяется на live route contract, targeted backend tests проходят через `mayan-edms.py`, а frontend stores/pages показывают явную ошибку для geography вместо тихого пустого списка.
- **Backend QA:** targeted Django suite для `home_stats`, `analytics reports`, `analytics consumers` и `distribution tenant isolation` проходит green run в Docker runtime через `/opt/mayan-edms/bin/mayan-edms.py`.
- **Frontend QA:** targeted Vitest suite для `useWebSocket`, `AssetBankPage` и distribution store проходит green run на текущем workspace.
- **Operational stack:** `app` (`:8080`) и `app_websocket` (`:8001`) подняты и healthy; admin token и default organization для live smoke уже получены из контейнерного runtime.

## Текущая архитектура (Шпаргалка)

- **Multi-tenancy:** `X-Organization-Id`, `TenantResolverMiddleware`, `TenantAwareMixin` и tenant-scoped модели остаются базовым паттерном.
- **Headless API exposure:** наличие view в `mayan/apps/headless_api/views/` недостаточно само по себе; критические SPA endpoints должны быть одновременно смонтированы в live `mayan/apps/rest_api/urls.py`.
- **Frontend QA/A11y:** accessibility теперь закреплена не только компонентными тестами, но и Playwright axe smoke для основного gallery flow.
- **Operational split:** SPA использует `:5173`, Django API — `:8080`, а WebSocket ASGI контур живет отдельно на `:8001`; ошибки чаще возникают на seams между этими тремя точками входа, а не внутри самого UI.
- **Distribution campaigns:** для campaigns больше не считается нормой tenant scoping через `metadata` и join-ы; canonical contract теперь должен идти через явный `organization` FK с metadata как backward-compatible fallback.

## Ближайшие задачи (Next Actions)

1. Завершить live smoke для tenant-scoped endpoint'ов (`headless geography`, `distribution campaigns`, `share_links`) на уже поднятом `:8080` стеке.
2. При необходимости подтвердить websocket smoke для `:8001` уже вне unit/integration уровня.
3. После live smoke обновить итоговый operational статус и закрыть Runtime Follow-up Stabilization pass.

## Известные проблемы / Риски (Known Issues)

- Код runtime follow-up pass подтвержден targeted regression suite, но live smoke по HTTP endpoint'ам еще не зафиксирован отдельным успешным прогоном из shell/browser из-за проблем со spawn отдельных curl-команд в локальной Windows shell-сессии.
- Полный backend test environment в широком смысле все еще хрупок: параллельные Django test runs конфликтуют за `test_mayan`, поэтому verification надежно работает при последовательном прогоне с очисткой тестовой БД.
- IDE по-прежнему показывает import-resolution warnings для Django/Channels в локальном окружении Windows, но это не проявилось как синтаксическая ошибка на измененных Python файлах.
