# Активный контекст Prime-EDMS

## Текущий фокус
Проект вышел из стадии первичного выравнивания по roadmap: tenant-safe Home/activity API, cleanup routing, стабилизация AI pipeline и базовое восстановление frontend QA-контура уже реализованы. Текущий фокус смещается с устранения самых критичных architectural debt points на доведение legacy-слоев и полную стабилизацию продуктового контура перед MVP.

## Подтвержденное текущее состояние
- **HomePage и tenant-safe API:** `home_stats_views.py` и `activity_views.py` переведены на реальные tenant-scoped данные; synthetic fallback для ключевых home/activity сценариев существенно сокращен.
- **Routing:** основной frontend-маршрут для DAM закреплен за `/dam`; legacy `/dam/gallery` и старые collection-переходы в коде в значительной степени вычищены через redirects и обновленные переходы.
- **Collections / Shared With Me:** страницы `CollectionsPage.vue` и `SharedWithMePage.vue` переведены с placeholder/mock-логики на реальные backend вызовы через cabinets/collections APIs.
- **AI pipeline:** исправлен quota bug (`created` вместо `created_at`), а fallback-анализ больше не маскируется под успешный AI-результат; деградированный результат сохраняется как `failed` с флагом `is_fallback`.
- **QA контур frontend:** `Playwright` снова корректно читает конфиг и видит e2e-набор, а общий `Vitest` setup расширен для реального DOM/browser-like окружения. Целевые smoke tests проходят.
- **Backend verification gap:** полный backend test run в контейнере уперся не в бизнес-логику, а в отсутствие зависимости `django_test_migrations` в тестовом окружении.

## Текущая архитектура (Шпаргалка)
- **Multi-tenancy:** `X-Organization-Id`, `TenantResolverMiddleware`, `TenantAwareMixin` и tenant-scoped модели продолжают быть базовым паттерном. Новый home/activity слой уже приведен к этому контракту, но legacy analytics/activity участки все еще требуют финальной унификации.
- **Frontend:** основной пользовательский контур DAM теперь опирается на `/dam`, `/dam/collections` и связанные страницы без зависимости от legacy gallery flow как primary route.
- **AI orchestration:** провайдерские ошибки теперь поднимаются в orchestration-слой, а fallback трактуется как degraded metadata, а не как success.
- **Frontend QA:** shared test bootstrap централизован в `frontend/tests/setup/vitest.setup.ts` и покрывает Pinia, router, Teleport targets, Canvas, observers и базовые browser APIs.

## Ближайшие задачи (Next Actions)
1. Довести до конца cleanup remaining legacy analytics/activity слоев и убрать дублирующиеся старые endpoints из критического пользовательского пути.
2. Синхронизировать HomePage/Saved Searches/analytics-контракты там, где еще возможен contract drift между frontend и backend.
3. Довести backend test environment до рабочего состояния для полного прогона tenant/DAM suite внутри контейнера.
4. Отдельно пройти accessibility и product hardening поверх уже восстановленного тестового контура, а не смешивать это с базовой починкой инфраструктуры.

## Известные проблемы / Риски (Known Issues)
- Старые legacy analytics/activity endpoints вне нового основного потока по-прежнему нельзя считать полностью выровненными с tenant-safe архитектурой без дополнительной ревизии.
- `Saved Searches` и часть HomePage-интеграций все еще требуют финальной сверки контрактов после cleanup.
- Полный backend test suite сейчас ограничен не кодом фичи, а состоянием test environment в контейнере.
- В frontend accessibility smoke tests инфраструктура восстановлена, но отдельные a11y-улучшения компонентов еще могут потребовать адресной доработки.
