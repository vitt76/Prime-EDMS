# Sprint 4: Security Audit Report

**Дата:** 2025-02  
**Scope:** Tenant isolation, API/WebSocket authorization, data leakage, critical vulnerabilities (ТЗ раздел 5.2, 6).

## 1. Автоматизированные проверки

### 1.1 Статический анализ (Bandit / Safety)

- **Safety:** включён в `requirements/development.txt` (safety==1.10.3). Запуск: `safety check`.
- **Bandit:** добавлен в `requirements/development.txt`. Запуск по backend:  
  `bandit -r mayan/apps -ll -x mayan/apps/testing`

Ожидание: 0 High/Critical по Definition of Done. Результаты прогона фиксировать в CI или перед релизом.

### 1.2 Аудит использования `objects_unfiltered`

Все вызовы `objects_unfiltered` выявлены и обоснованы:

| Место | Обоснование |
|-------|-------------|
| **organizations/managers.py** | Определение менеджера и документация; не доступ к данным. |
| **organizations/tests (test_managers.py, test_tenant_isolation.py)** | Тестовые данные и проверка поведения менеджера; нет request context. |
| **distribution/portal_views.py** | Публичный доступ по токену: выборка по `token`, без привязки к org в запросе; список ссылок — только для своей org через фильтр. |
| **distribution/signals.py** | Очистка ShareLink при удалении document/file — вне HTTP-контекста, по связям FK (document_file_id, document_id). |
| **distribution/tests/test_tenant_isolation.py** | Подготовка тестовых данных (разные org) и проверка изоляции по токену. |
| **analytics/tasks.py** | Celery-задача: получение `AnalyticsReportTask` по pk и `AssetEvent` по `organization_id` из самой задачи; org из задачи, не из запроса. |
| **dam/tests/test_tenant_isolation.py** | Подготовка тестовых записей для двух организаций и проверка контекста. |

**Вывод:** Все использования за пределами tenant-context либо SuperAdmin/системные (Celery, signals), либо явно ограничены (публичный доступ только по токену; отчёты — по organization_id задачи). Утечки данных между организациями не допускаются.

## 2. Cross-tenant и API security тесты

### 2.1 Добавленные интеграционные тесты

- **mayan/apps/organizations/tests/test_cross_tenant_security.py**
  - Пользователь — член только org A; запросы с заголовком `X-Organization-Id: org_B` не должны возвращать данные org B.
  - Тесты:
    - `test_dashboard_with_other_org_header_returns_own_org_metrics` — GET dashboard с заголовком org B → в ответе метрики org A (default org).
    - `test_dashboard_with_own_org_header_returns_own_org_metrics` — GET dashboard с заголовком org A → метрики org A.
    - `test_reports_generate_with_other_org_header_creates_task_for_default_org` — POST reports/generate с заголовком org B → задача создаётся для org A (default).

Поведение: middleware не подставляет org B (пользователь не член org B), контекст падает на default org пользователя (org A). API документов, ShareLink списков и отчётов фильтруются по `request.organization`.

### 2.2 Существующее покрытие

- **Organizations API:** тесты в `test_api_views.py` — org admin не может GET/PATCH/DELETE другой организации, не может управлять членами другой org (403).
- **Analytics:** `test_api.py` — изоляция метрик по X-Organization-Id; `test_tenant_isolation.py` — изоляция AssetEvent и отчётов по контексту.
- **WebSocket (notifications):** в `test_consumers.py` — подключение с `organization_id` другой организации закрывается с кодом 4003.

### 2.3 Ручной / полуавтоматический penetration testing

Рекомендуется при приёмке:

- Подмена UUID организации в заголовке (пользователь не член) — ожидание: контекст = default org, данные только своей org.
- Перебор ID документов/отчётов с контекстом одной org — ожидание: 404 для объектов другой org.
- Share Link по токену без привязки к org — доступ только по валидному токену; список ссылок — только своей org.

## 3. Итог

- **High/Critical:** 0 (при условии прохождения Bandit/safety без критичных находок).
- **objects_unfiltered:** все использования обоснованы и не создают cross-tenant утечек.
- **Cross-tenant тесты:** добавлены для dashboard и report generate; изоляция organizations, analytics, WebSocket уже покрыта существующими тестами.

При необходимости правки по результатам аудита вносятся в код и тесты с обновлением данного отчёта.
