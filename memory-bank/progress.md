# Прогресс проекта Prime-EDMS (по состоянию на Март 2026)

## 🟩 ЗАВЕРШЕНО (В проде / History)
- [x] **Базовый функционал:** Core DAM, Analytics Module, Distribution, Marketing CMS, Nuxt 3 Public Frontend.
- [x] **Multi-Tenancy (Фаза 1-4):** Изоляция данных, Shared Database/Shared Schema, TenantResolverMiddleware, кэширование, quota enforcement, патчинг Document managers.
- [x] **High-Performance UI (Sprint 5):** ImmersiveGrid, виртуальный скролл, lazy loading.
- [x] **Security & Compliance:** Audit Logs, Watermarking, Cookie Consent (152-ФЗ).
- [x] **Analytics Transformation:** Графики (Chart.js), GeoMap, Retention Cohort, Churn, выгрузка отчетов.

## 🟦 ТЕКУЩИЙ ЦИКЛ: ДОРАБОТКИ 2026 (UI/UX & Productivity)

### Sprint 1: Discovery & UX (ЗАВЕРШЕН)
- [x] Saved Searches (API + UI: Dropdown, модалки создания/переименования).
- [x] Recently Viewed (API + UI блок над сеткой, страница /dam/recent).
- [x] Orientation Filter (URL sync).
- [x] Tenant-isolation для новых API (X-Organization-Id).

### Sprint 2: Productivity & UX (ЗАВЕРШЕН)
- [x] Избранное (Favorites): Headless API (toggle, list), фильтр favoritesOnly, UI иконки на карточках.
- [x] Горячие клавиши (Hotkeys): `useGalleryHotkeys` (F, Space, Delete, Esc, Ctrl+A), модалка Cheat Sheet.

### Sprint 3: Collaboration & Tech Debt (В ПРОЦЕССЕ)
- [x] Шаринг подборок (Cabinets): Backend (CabinetUserShare, headless API org-members, share-with-users, shared-with-me), Frontend (CabinetShareModal, Sidebar разделение).
- [x] Tech Debt: Глобальное тестовое окружение Vitest (Pinia, Router, Canvas), исправление ~330 падающих тестов (VirtualScroller, ChartComponent, FiltersPanel, BulkTagModal).
- [ ] Корзина (Trash): реализация перемещения и восстановления активов.

## 🟨 БЭКЛОГ (TODO / Gaps)
- **API & Integrations:** Change Password API, User Activity Feed API, YouTube Analytics OAuth2, Интеграция с Claude/Gemini (fallback).
- **Analytics:** Search-to-Find Time, CDN Cost tracking, Geo IP enrichment.
- **Tech Debt:** Стабилизация оставшихся ~12 тестов Vitest (jsdom restrictions, a11y matchers).
- **Спринты 4-7 (Из плана 2026):** AI-тегирование, массовые операции, улучшенный поиск.
