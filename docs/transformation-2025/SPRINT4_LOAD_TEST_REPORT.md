# Sprint 4: Load Testing Report

**Дата:** 2025-02  
**Scope:** Сценарии нагрузки (ТЗ раздел 6 Phase 3), целевые NFR: p95 &lt; 200 ms, отсутствие 5xx при заданной нагрузке.

## 1. Инструменты

- **Locust** (уже в проекте): `tests/load/locustfile.py`.
- Запуск: `locust -f tests/load/locustfile.py --host=https://<host>` (или `http://localhost:8000` для локального теста).
- Опционально: переменные окружения `AUTH_TOKEN` (Token-аутентификация), `X_ORGANIZATION_ID` (UUID организации для tenant-scoped запросов).

## 2. Сценарии (Sprint 4)

В `locustfile.py` реализованы два класса пользователей:

### AnalyticsUser (основной)

- **dashboard_main** (weight 3): GET `/api/v4/headless/analytics/dashboard/` — основной dashboard с кэшем.
- **asset_bank_top_metrics** (weight 2): GET `/api/v4/headless/analytics/dashboard/assets/top-metrics/`.
- **document_list_optimized** (weight 1): GET `/api/v4/documents/optimized/` — оптимизированный список документов с пагинацией.

### DocumentListUser

- **document_list**: GET `/api/v4/documents/` — стандартный список документов.

При наличии `AUTH_TOKEN` и `X_ORGANIZATION_ID` запросы выполняются в контексте организации; без них эндпоинты могут вернуть 401/400 в зависимости от настроек.

## 3. Рекомендуемый прогон

1. Запустить приложение и (при необходимости) создать тестового пользователя и организацию.
2. Получить API Token и UUID организации.
3. Запустить Locust с числом пользователей и spawn rate (например, 10 пользователей, 2/s).
4. Собрать метрики: RPS, latency (median, p95, p99), число ошибок (по коду и по имени).
5. Цель: p95 latency GET &lt; 200 ms; 0% ошибок 5xx при заданной нагрузке.

## 4. WebSocket (notifications)

Нагрузочное тестирование WebSocket (`ws/notifications/` с `organization_id` и токеном) в Locust не реализовано (требует отдельного клиента или плагина). Рекомендуется при приёмке: ручная проверка или отдельный скрипт (например, на `websockets` или `locust-plugins` при необходимости).

## 5. Артефакты

- Скрипты: `tests/load/locustfile.py`.
- Результаты прогона: сохранять вывод Locust (HTML-отчёт или логи) в `tmp/` или CI артефакты; при необходимости добавить в отчёт конкретные цифры RPS, p95 и рекомендации по масштабированию (воркеры Celery, число Gunicorn workers и т.д.).
