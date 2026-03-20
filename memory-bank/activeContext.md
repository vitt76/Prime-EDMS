# Активный контекст Prime-EDMS

## Текущий фокус

Текущий фокус сместился с runtime follow-up stabilization на `gitnexus hardening` pass. На уровне кода уже внесены изменения по tenant/runtime seams, public auth/API drift, operational telemetry hardening и runtime patch observability; незакрытым остается прежде всего environment-dependent verification: нужно подтвердить live smoke и финальный runtime contract на доступном Docker/localhost стеке.

## Подтвержденное текущее состояние

- **Backend test harness normalization:** `TenantResolverMiddleware` читает `DEPLOYMENT_MODE` и `SAAS_BASE_DOMAIN` динамически из `settings`; для tenant/DAM integration tests используется общий `SaaSTenantTestHarnessMixin`.
- **Token-aware tenant resolution:** middleware умеет резолвить пользователя из `Authorization: Token ...` еще до DRF auth phase, поэтому `X-Organization-Id` и default-org fallback работают и для SPA/token запросов, и для middleware-dependent tests.
- **Tenant/runtime hardening for published analytics:** опубликованные legacy analytics viewsets теперь требуют явный `request.organization`, а geography/asset-bank seams дополнительно закреплены через contract tests.
- **Route exposure hardening:** live router в `mayan/apps/rest_api/urls.py` теперь остается единой точкой публикации как для headless analytics geography, так и для новых public marketing/auth endpoints; добавлен отдельный `runtime_contract_smoke` management command для live HTTP smoke без зависимости от `curl.exe`.
- **Public auth/API drift fix:** backend теперь публикует canonical routes `public/auth/login`, `public/auth/register`, `public/auth/verify-email`, `public/analytics/events`; `public-frontend`, MSW handlers и Playwright smoke синхронизированы с этими путями.
- **Operational telemetry hardening:** `analytics/health` расширен до `operational snapshot`; для analytics consumer/tasks добавлены operational markers и counters, чтобы failures/lag/stale reports были наблюдаемыми, а не только косвенно видимыми через UI.
- **Runtime patch observability:** `organizations/patches.py` теперь сохраняет явный status runtime patching (`HttpRequest`, `Document.organization`, patched managers), а `OrganizationsApp.ready()` логирует итоговый patch status; добавлен test coverage на patch-status contract.
- **Backend code integrity:** новые и измененные Python-файлы проходят локальную синтаксическую проверку через `py_compile`; кодовая интеграция выполнена без синтаксических ошибок.

## Текущая архитектура (Шпаргалка)

- **Multi-tenancy:** `X-Organization-Id`, `TenantResolverMiddleware`, `TenantAwareMixin` и tenant-scoped модели остаются базовым паттерном.
- **Headless API exposure:** наличие view в `mayan/apps/headless_api/views/` недостаточно; критические SPA/public endpoints считаются готовыми только если они смонтированы в live router и покрыты smoke/contract checks.
- **Public contract:** для public frontend теперь canonical является `public/auth/*` family, а не старые смешанные пути вроде `public/register` или `public/verify-email/:token`.
- **Operational split:** SPA использует `:5173`, Django API — `:8080`, public frontend — `:3000`, а WebSocket ASGI контур живет отдельно на `:8001`; ошибки чаще возникают на seams между этими входными точками.
- **Runtime patching:** `contribute_to_class` и manager monkey-patching по-прежнему остаются частью совместимости с Mayan, но теперь этот слой должен быть явно наблюдаем и тестируем.

## Ближайшие задачи (Next Actions)

1. Подтвердить live smoke для tenant-scoped endpoint'ов (`headless geography`, `distribution campaigns`, `share_links`, `analytics/health`) на доступном runtime стеке.
2. При доступном Docker/runtime повторно прогнать targeted Django regression suite и `runtime_contract_smoke`, чтобы формально закрыть `close-tenant-runtime-seams`.
3. Довести до конца cleanup matrix для legacy/new endpoint pairs и явно отметить `canonical`, `deprecated`, `remove-after-migration`.
4. После этого обновить итоговый operational статус и закрыть `gitnexus hardening` pass.

## Известные проблемы / Риски (Known Issues)

- Главный незакрытый риск сейчас не в отсутствии кода, а в verification environment: локальный Docker daemon/runtime периодически недоступен, поэтому containerized regression и live smoke не удалось повторно подтвердить в конце прохода.
- Полный backend test environment по-прежнему хрупок: параллельные Django test runs конфликтуют за `test_mayan`, поэтому verification надежно работает при последовательном запуске.
- Полная зачистка legacy analytics/activity слоя еще не завершена как matrix cleanup: часть старых маршрутов все еще требует формального статуса и последующего вывода из эксплуатации.
- IDE по-прежнему показывает import-resolution warnings для Django/Channels/DRF в локальном Windows окружении, но это не проявилось как синтаксическая ошибка на измененных Python файлах.
