# Analytics Transformation Roadmap (MADDAM)

Документ фиксирует инженерный план трансформации модуля корпоративной аналитики до уровня Enterprise DAM (Aprimo/Bynder) с фокусом на целостность данных, интерактивность и поведенческую аналитику.

## Контекст и цель

**Текущее состояние:** Phase 1–2 MVP (частично). Есть базовый трекинг событий (`AssetEvent`, `SearchQuery`), базовые дашборды Asset Bank / Campaign Performance, базовый ROI.  
**Критические разрывы:** Search-to-Find, CDN Cost/month, Feature Adoption, интерактивность (drill-down, trend), гео-данные, автоматизация retention.

**Цель:** довести Phase 1–2 до уровня “Data-Driven DAM” и подготовить Phase 3 (AI/ML, real-time).

## Sprint 1: Data Integrity & Core Metrics

### 1.1 Avg Search-to-Find Time (Search→Download)

- **Backend**
  - Добавить `SearchSession` для группировки “поиск→нахождение”.
  - Добавить `SearchQuery.search_session_id` (UUID) и индексирование.
  - Best-effort связывание `download` с открытой `SearchSession` в окне 30 минут.
  - Celery task `aggregate_user_daily_metrics` → заполняет `UserDailyMetrics.avg_search_to_find_minutes`.
  - Обновить `/api/v4/headless/analytics/dashboard/assets/top-metrics/` → возвращает `avg_find_time_minutes` не `None`.
- **Frontend**
  - Отобразить `avg_find_time_minutes` в `TopMetricsCard`.

### 1.2 CDN Cost/month

- **Backend**
  - Модели `CDNRate`, `CDNDailyCost`.
  - Celery task `calculate_cdn_daily_costs`.
  - Команда `init_cdn_rates` для инициализации default rate.
  - `top_metrics` возвращает `cdn_cost_per_month` на основе `CDNDailyCost`.
- **Frontend**
  - Отобразить `cdn_cost_per_month` в `TopMetricsCard`.

### 1.3 Data Retention Automation

- **Backend**
  - Management command `setup_analytics_periodic_tasks` для регистрации periodic tasks через `django-celery-beat`.
  - Расширить `cleanup_old_events` (raw + агрегаты по retention).

## Sprint 2: Interactive Visualization (UX Upgrade)

### 2.1 Cross-chart filtering + Drill-down

- **Frontend**
  - Расширить фильтры (date, asset type, department/owner — best-effort).
  - Включить cross-filtering от клика на pie chart.
  - Drill-down modal (`AssetDetailModal`) для просмотра динамики и рефереров поиска.
- **Backend**
  - Endpoint `assets/detail/` для drill-down.

### 2.2 12-month trend под Asset Distribution

- **Backend**
  - Endpoint `assets/distribution-trend/` (12 месяцев).
- **Frontend**
  - Line chart под pie chart (4 линии: images/videos/documents/other).

## Sprint 3: Advanced Analytics & Behavioral Tracking

### 3.1 Feature Adoption Tracking

- **Backend**
  - Модель `FeatureUsage`.
  - Middleware `FeatureUsageMiddleware` (best-effort трекинг через URL).
  - Endpoint `users/feature-adoption/`.

### 3.2 Audience Geography

- **Backend**
  - GeoIP enrichment для `UserSession` (best-effort).
  - `adoption_by_department` возвращает `geo_data`.
  - Campaign geography endpoint `dashboard/campaigns/geography/`.
- **Frontend**
  - Компонент `AudienceGeographyMap` отображает top countries (bar chart).

### 3.3 Collection Engagement

- **Backend**
  - `CampaignDailyMetrics.avg_engagement_minutes`
  - raw events `CampaignEngagementEvent`
  - endpoint `campaigns/<id>/engagement/`
  - task `aggregate_campaign_engagement_daily_metrics`
- **Frontend**
  - В Campaign Performance — best-effort замер времени на странице кампании и POST в `engagement/`.

## Technical Debt (обязательные инженерные улучшения)

- **Performance**
  - Индексы для больших объёмов событий (user_id, timestamp DESC).
- **Security/Compliance**
  - Анонимизация IP для `UserSession`.
  - “Right to be Forgotten” management command для удаления персональных analytics-данных.


