# Прогресс проекта Prime-EDMS (актуализация по коду и фактическому прогону, март 2026)

## 🟩 Реально работает
- [x] **Базовая multi-tenant инфраструктура:** `Organization`, `TenantResolverMiddleware`, tenant-aware модели, `X-Organization-Id`, новые tenant-scoped endpoints и тесты на изоляцию.
- [x] **Новый DAM-контур на `/dam`:** `GalleryView`, `ImmersiveGrid`, виртуальный скролл, blob-превью, lazy loading, горячие клавиши, работа через `/api/v4/documents/optimized/`.
- [x] **Home/activity tenant-safe слой для основного UI:** HomePage и activity feed переведены на реальные backend ответы без ключевых synthetic заглушек в основном контуре.
- [x] **Routing cleanup:** основной маршрут закреплен за `/dam`, legacy `/dam/gallery` переведен в cleanup/redirect режим, коллекции собраны вокруг `/dam/collections`.
- [x] **Collections и Shared With Me:** страницы переведены с placeholder/mock-логики на реальные cabinets/collections API.
- [x] **Recently Viewed:** backend endpoint + frontend блок/страница на базе реальных `AssetEvent`.
- [x] **Favorites:** headless API, фильтр `favorites_only`, UI-иконки и отдельная страница избранного.
- [x] **Trash:** отдельная страница и базовая связка с backend endpoint'ами корзины.
- [x] **Шаринг подборок и public shares:** `CabinetUserShare`, CabinetShareModal, public share API, tenant-scoped backend для ссылок.
- [x] **AI pipeline:** auto-trigger через signal, Celery task, вызовы AI-провайдеров, сохранение результата в `DocumentAIAnalysis`, исправленный quota-check и честная degraded fallback-семантика.
- [x] **Базовый QA recovery фронтенда:** `Playwright` конфиг снова валиден, e2e suite определяется корректно, общий `Vitest` setup расширен, целевые smoke tests проходят.

## 🟨 Работает частично / есть synthetic или legacy-слой
- [~] **HomePage:** основной контур уже использует реальные tenant-safe ответы, но часть связанных интеграций и UX-сценариев все еще требует финальной сверки контрактов.
- [~] **Saved Searches:** backend tenant-aware реализован, но HomePage/service-интеграция требует дополнительной унификации после cleanup.
- [~] **Analytics dashboard:** новый tenant-aware `/api/v4/headless/analytics/dashboard/` существует и используется, но рядом остается legacy analytics слой с историческим техдолгом.
- [~] **Distribution state на фронтенде:** часть shared-индикаторов и dev-состояния опирается на `mocks/publications.ts`.
- [~] **Frontend QA:** инфраструктура восстановления выполнена, но полный прогон всего набора и последующее сокращение остаточных прикладных падений еще требуют отдельного спринта.
- [~] **Backend QA:** логика по AI stabilization покрыта изменениями и частичными тестами, но полный контейнерный suite блокируется состоянием test environment.

## 🟥 Не готово / требует стабилизации перед MVP
- [ ] **Полная унификация legacy analytics/activity слоя:** старые endpoints вне нового основного пути еще требуют финальной зачистки или вывода из эксплуатации.
- [ ] **Полная синхронизация HomePage contracts:** storage/inbox/saved-searches/analytics нужно довести до полностью согласованного продуктового контракта без остаточного drift.
- [ ] **Полный backend test environment:** контейнерный прогон tenant/DAM test suite сейчас упирается в отсутствующую зависимость `django_test_migrations`.
- [ ] **Отдельный accessibility/hardening pass:** после восстановления тестовой инфраструктуры остается отдельный слой продуктовой и a11y-полировки.

## 🟦 Ближайшие продуктовые шаги
- [ ] Довести до конца cleanup legacy analytics/activity endpoints и убрать старые дубли из критических сценариев.
- [ ] Сверить и стабилизировать все оставшиеся HomePage/service contracts.
- [ ] Починить backend test environment в контейнере и прогнать полный tenant/DAM suite.
- [ ] Провести отдельный stabilization pass по полному фронтендному тестовому набору и accessibility.
