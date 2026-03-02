# Активный контекст Prime-EDMS

## Текущий фокус
Команда успешно завершила часть **Sprint 3 (Collaboration & Tech Debt)**: реализован шаринг подборок (Cabinets) внутри организации и настроено глобальное тестовое окружение Vitest (Pinia, Router, Canvas), что вывело из карантина большинство тестов (~330 исправлено). Завершено исправление роутинга и локализации HomePage Phase 1 (QuickActionsPanel, KPIBar, MyInbox) с правильными query-параметрами для фильтров (status=untagged для AI-анализа, duplicates=true для поиска дубликатов). Текущий фокус — завершение фич Sprint 3 (Корзина) и добивка оставшихся сложных тестов.

## Текущая архитектура (Шпаргалка)
- **Multi-tenancy:** Используем `X-Organization-Id` в заголовках. Бэкенд использует `TenantAwareMixin` и `TenantResolverMiddleware`.
- **Шаринг подборок:** Модель `CabinetUserShare` (изоляция по `organization`). Доступ комбинируется: `AccessControlList` (роли) + `CabinetUserShare` (прямой шаринг).
- **Frontend State:** Pinia stores (`assetStore`, `authStore`, `analyticsStore`, `collectionsStore`).
- **Стилизация:** Tailwind CSS. 
- **Компоненты:** Используем `defineAsyncComponent` для тяжелых модалок, `Teleport` для шапки (`#header-search-actions`).

## Ближайшие задачи (Next Actions)
1. Реализация функционала "Корзина" (Trash) для активов и подборок.
2. Стабилизация оставшихся ~12 тестов Vitest (ограничения jsdom для scrollTo, конфликты chai matchers в axe).
3. Интеграция дополнительных метрик аналитики (Search-to-Find Time, CDN Cost tracking).

## Известные проблемы / Риски (Known Issues)
- Небольшая часть тестов Vitest (~12) остаётся в карантине `docs/TEST_QUARANTINE.md` из-за специфики jsdom.
- Технический долг по интеграции с Claude/Gemini (необходим fallback механизм).
