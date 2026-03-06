# Активный контекст Prime-EDMS

## Текущий фокус

Проект завершил все 4 фазы MVP Stabilization roadmap на уровне кода: legacy cleanup, contract sync, backend tenant-suite stabilization и базовый accessibility/product hardening реализованы. Текущий фокус сместился с roadmap delivery на post-MVP runtime stabilization: устранение live-консольных ошибок, доочистка legacy integration seams и фиксация operational gaps между Vite SPA и Docker backend.

## Подтвержденное текущее состояние

- **MVP Stabilization:** все 4 фазы плана реализованы; targeted Vitest и Playwright smoke suites проходят.
- **HomePage KPI router gap:** live backend теперь экспортирует `/api/v4/headless/documents/stats/`, `/documents/ai-stats/`, `/user/inbox-stats/`, `/organization/storage-stats/` и `/user/daily-insights/` через `mayan/apps/rest_api/urls.py`; прежний live `404` на этих маршрутах устранен.
- **A11y / product hardening:** галерея переведена на более корректную `list/listitem` семантику, улучшены focus trap и keyboard сценарии для `Modal`, `MetadataPanel`, filters drawer и action menus; добавлены `vitest-axe` и `@axe-core/playwright` smoke checks.
- **Routing:** основной маршрут DAM закреплен за `/dam`, legacy `/dam/gallery` живет как redirect/compat path.
- **Backend tenant verification:** контейнерный tenant/DAM regression suite был стабилизирован и ранее проходил green run.
- **Frontend QA:** shared test bootstrap и Playwright smoke infrastructure работают стабильно для targeted suites.

## Текущая архитектура (Шпаргалка)

- **Multi-tenancy:** `X-Organization-Id`, `TenantResolverMiddleware`, `TenantAwareMixin` и tenant-scoped модели остаются базовым паттерном.
- **Headless API exposure:** наличие view в `mayan/apps/headless_api/views/` недостаточно само по себе; критические SPA endpoints должны быть одновременно смонтированы в live `mayan/apps/rest_api/urls.py`.
- **Frontend QA/A11y:** accessibility теперь закреплена не только компонентными тестами, но и Playwright axe smoke для основного gallery flow.
- **Operational split:** SPA использует `:5173`, Django API — `:8080`, а WebSocket ASGI контур живет отдельно на `:8001`; ошибки чаще возникают на seams между этими тремя точками входа, а не внутри самого UI.

## Ближайшие задачи (Next Actions)

1. Починить live analytics geography route exposure, чтобы `/api/v4/headless/analytics/dashboard/geography/` не давал `404`.
2. Привести frontend WebSocket configuration в соответствие с фактическим ASGI endpoint на `:8001`, а не вычислять его из API host.
3. Убрать frontend runtime warning в `SharingPage.vue` (`IconEye`) и довести distribution screens до clean render без component-resolution ошибок.
4. Разобрать backend `500` на `/api/v4/distribution/share_links/` и `/api/v4/distribution/campaigns/`, а также связанные task/event ошибки (`track_asset_event_async(... organization_id ...)`) как отдельный runtime stabilization pass.

## Известные проблемы / Риски (Known Issues)

- `/api/v4/headless/analytics/dashboard/geography/` в live backend все еще не отдается, хотя view существует в коде.
- WebSocket notifications/analytics configuration во frontend не до конца синхронизирована с выделенным Daphne/ASGI портом `8001`.
- `SharingPage.vue` содержит runtime проблему с неимпортированным `IconEye`.
- Distribution контур все еще нестабилен в live Docker runtime: `share_links` и `campaigns` могут отдавать `500`, а в backend логах всплывают ошибки Celery/event pipeline с отсутствующим `organization_id`.
- Полный backend suite по-прежнему ограничен состоянием общего test environment, а не только бизнес-логикой.
