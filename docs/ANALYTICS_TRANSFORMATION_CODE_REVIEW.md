# Analytics Transformation — Code Review & Logic Consistency Report

**Дата:** 2026-02-17  
**Роль:** Lead QA Engineer & Data Architect  
**Объект:** Фичи Search-to-Find, CDN Cost, Feature Adoption, Geo, Retention.

---

## 1. REVIEW REPORT: **PASS** (с замечаниями WARNING)

### 1.1 Migration dependency — **PASS**

- **analytics 0014** зависит от `analytics.0013` и `organizations.0005` — корректно.
- **0015** — от `0014` и `organizations.0005` — корректно.
- **0016** — от `0015` (без org) — корректно.
- **0017** — от `0016` и **organizations.0006** — корректно; перед применением analytics 0017 необходимо применить `migrate organizations` (в т.ч. 0006).
- **0018, 0019** — от `organizations.0006` — корректно.
- **0020** — от `0019` — корректно.

**Рекомендация:** При деплое выполнять `migrate organizations` перед `migrate analytics`.

---

### 1.2 Data integrity

#### track_asset_event_async (tasks.py, ~39–141)

- **document_id=None / document not found:** Обрабатывается: ранний return с `logger.warning` (строки 64–66, 72–75). Событие не создаётся — **OK**.
- **bandwidth_bytes=None при download:** Fallback на `document.files.order_by('-timestamp').first().size` (84–90). Выполняется только при `event_type == EVENT_TYPE_DOWNLOAD` и `bandwidth_bytes is None`. При отсутствии файла или `size` остаётся `None` — в `AssetEvent.objects.create` передаётся `bandwidth_bytes=bandwidth_bytes` (допускается NULL) — **OK**.

#### enrich_event_geo_data (tasks.py, ~283–340) и get_geo_from_ip (utils.py, ~139–168)

- **Отсутствие GeoIP БД или ошибка:** В `get_geo_from_ip`: при отсутствии `GEOIP_DATABASE_PATH` или при любом `Exception` (import, Reader, city()) возвращается `('', '')`. Задача не падает, событие либо не обновляется (нет ip в metadata), либо получает пустые country/city — **OK**, graceful degradation.
- **WARNING (minor):** В `get_geo_from_ip` объект `reader = geoip2.database.Reader(db_path)` не закрывается (нет `reader.close()` или `with`). При частых вызовах возможна утечка файловых дескрипторов. Рекомендация: использовать `with geoip2.database.Reader(db_path) as reader:` в блоке try.

---

### 1.3 Performance

#### calculate_organization_bandwidth_daily (tasks.py, ~964–1017)

- Агрегация по организации за день выполняется через **Sum** в БД:  
  `.values('organization_id').annotate(total_bytes=Sum('bandwidth_bytes'))` (979–987) — **OK**, без N+1.
- Цикл по строкам результата с одной выборкой организации на org (`select_related('subscription__plan')`) — приемлемо.

#### FeatureUsage (track_feature_usage)

- Вызов из **dam/tasks.py** (после AI analysis) и **distribution/views/share_link_views.py** — **синхронный** (прямой вызов `track_feature_usage(...)`). Один INSERT в БД, влияние на время отклика задачи/запроса минимально. Критичным не считается; при желании можно вынести в `track_feature_usage_async.delay(...)` — **WARNING (низкий приоритет)**.

---

### 1.4 Логика и краевые случаи

- **generate_analytics_report / user_activity:**  
  - DAU считается по дням из `date_from`–`date_to`; MAU — уникальные user_id за 30 дней от `date_to`; churn — члены организации без событий за 30 дней. Учтён `user_id__isnull=False` для событий. **OK**.
- **Migration 0019 (populate FeatureUsage):** После цикла выполняется `if default_org is None: default_org = Organization.objects...` и затем `FeatureUsage.objects.filter(organization__isnull=True).update(...)` — оставшиеся NULL заполняются. **OK**.

---

## 2. MEMORY BANK UPDATES

Ниже — готовые фрагменты для вставки в файлы Memory Bank.

### 2.1 activeContext.md

**Где:** Секция «Следующий фокус» или блок после Sprint 5 — добавить подсекцию.

**Вставить (или заменить соответствующий пункт в разделе Analytics / Next Steps):**

```markdown
#### Analytics Transformation (Backlog) — ✅ COMPLETED 2026-02-17
- **Search-to-Find Time:** SearchSession tenant-aware (FK organization), AssetEvent.search_session_id; middleware передаёт X-Search-Session-Id; при download — обновление SearchSession или link_download_to_latest_search_session; дашборд: avg_search_to_find_seconds.
- **CDN Cost:** Plan.cdn_cost_per_gb; при download в track_asset_event_async подставляется размер файла в bandwidth_bytes; модель OrganizationBandwidthDaily; задача calculate_organization_bandwidth_daily (агрегация по org, стоимость из Plan или ANALYTICS_CDN_COST_PER_GB).
- **Feature Adoption:** FeatureUsage tenant-aware; константы ai_analysis, share_link_create; вызовы из dam/tasks и distribution (share link create); дашборд: feature_adoption (users_count, adoption_rate_percent по фичам).
- **Geo:** IP в AssetEvent.metadata при создании события; get_geo_from_ip в utils; задача enrich_event_geo_data (batch или event_id); обогащение metadata полями country, city.
- **Retention:** В generate_analytics_report добавлена секция user_activity: dau (по дням), mau, churn_count (члены org без событий 30 дней), churn_period_days.
- Миграции: analytics 0014–0020, organizations 0006. Единый дашборд GET /api/v4/headless/analytics/dashboard/ возвращает в т.ч. avg_search_to_find_seconds и feature_adoption.
```

**Дополнительно:** В блоке «Short-term» или «Analytics» заменить пункт про Analytics Transformation на:  
«**Analytics Transformation** — ✅ завершён (Search-to-Find, CDN Cost, Feature Adoption, Geo, Retention); см. раздел выше.»

---

### 2.2 progress.md

**Где:** Секция «### 4. Analytics Roadmap» (около строк 357–368).

**Заменить блок:**

```markdown
### 4. Analytics Roadmap
- ✅ **Analytics Transformation** — Phase 1–2 и Backlog завершены (2026-02-17)
  - Документ: `ANALYTICS_TRANSFORMATION_ROADMAP.md` (или план в .cursor/plans)
  - ✅ Базовый трекинг событий (AssetEvent, SearchQuery)
  - ✅ Базовые дашборды
  - ✅ Search-to-Find Time (SearchSession tenant-aware, search_session_id, дашборд avg_search_to_find_seconds)
  - ✅ CDN Cost/month tracking (OrganizationBandwidthDaily, Plan.cdn_cost_per_gb, calculate_organization_bandwidth_daily)
  - ✅ Feature Adoption (FeatureUsage tenant-aware, ai_analysis/share_link_create, виджет в дашборде)
  - ✅ Гео-данные (IP в metadata, enrich_event_geo_data, get_geo_from_ip)
  - ✅ Автоматизация retention (user_activity в отчёте: DAU, MAU, churn_count)
```

---

### 2.3 techContext.md

**Где:** Подсекция «Analytics (tenant-aware, Sprint 2)» (примерно строки 23–27). **Дополнить** следующими абзацами после описания Reports:

```markdown
- **SearchSession:** TenantAwareMixin, FK organization (NOT NULL); связь с AssetEvent через search_session_id (UUID на AssetEvent); first_search_query (FK SearchQuery), last_download_event (FK AssetEvent), time_to_find_seconds. Создаётся в optimized_document_api_views при поиске (q=) с request.organization; при download middleware может передавать X-Search-Session-Id в track_asset_event_async.
- **OrganizationBandwidthDaily:** organization, date, bandwidth_gb, cost_usd; заполняется задачей calculate_organization_bandwidth_daily по данным AssetEvent (event_type=download, Sum(bandwidth_bytes)) по организации за день; стоимость из Plan.cdn_cost_per_gb или settings.ANALYTICS_CDN_COST_PER_GB.
- **FeatureUsage:** TenantAwareMixin, FK organization; фичи ai_analysis, share_link_create и др.; трекинг из dam/tasks (после AI analysis) и distribution (создание Share Link). Дашборд возвращает feature_adoption: по каждой фиче — users_count и adoption_rate_percent за 30 дней.
- **Geo:** IP сохраняется в AssetEvent.metadata при создании (track_asset_event_async); обогащение — задача enrich_event_geo_data (GeoIP2, get_geo_from_ip в analytics.utils); metadata дополняется полями country, city. Требуется geoip2 и GEOIP_DATABASE_PATH.
- **Отчёт (user_activity):** generate_analytics_report дополнен секцией user_activity: dau (уникальные user_id по дням за date_from–date_to), mau (за 30 дней от date_to), churn_count (UserOrganizationRole без событий за 30 дней), churn_period_days=30.
```

---

## 3. NEXT STEPS (Frontend / Sprint 5)

### 3.1 Доступность Analytics API в headless_api

- **Есть:**  
  - `GET /api/v4/headless/analytics/dashboard/` — единый дашборд (AnalyticsDashboardViewSet).  
  - В ответ уже входят поля: `avg_search_to_find_seconds`, `feature_adoption` (список с feature_name, users_count, adoption_rate_percent).  
  - Отчёты: `POST /api/v4/headless/analytics/reports/generate/`, `GET /api/v4/headless/analytics/reports/{id}/` — в сгенерированном JSON есть секция `user_activity` (dau, mau, churn_count, churn_period_days).
- **Итог:** Новые метрики Analytics Transformation отдаются через существующие headless-маршруты; отдельные новые endpoints не требуются.

### 3.2 Блокирующие моменты для фронта

- **Нет блокировок.** Для Sprint 5 (Immersive Grid) бэкенд готов: дашборд и отчёты расширены данными; фронт может подключать виджеты (search-to-find, adoption, при необходимости — CDN/retention) по уже существующему контракту.
- **Рекомендация фронту:** При использовании дашборда учесть в типах/контракте поля `avg_search_to_find_seconds` (number | null) и `feature_adoption` (массив объектов с feature_name, users_count, adoption_rate_percent).

---

## 4. ACTION PLAN

| Приоритет | Действие | Файл/место |
|-----------|----------|------------|
| Рекомендуется | Закрывать GeoIP Reader (with context manager) | analytics/utils.py, get_geo_from_ip |
| По желанию | Вынести track_feature_usage в async (Celery) из dam/tasks и distribution | dam/tasks.py, distribution/views/share_link_views.py |
| Обязательно | Применить миграции: `migrate organizations` затем `migrate analytics` | Деплой |
| Обязательно | Обновить Memory Bank (activeContext, progress, techContext) по тексту выше | memory-bank/*.md |

**Вердикт:** Код готов к продакшену с учётом миграций и опциональных улучшений (GeoIP reader, асинхронный feature tracking). Переход к Sprint 5 (Frontend) по Analytics не блокируется.
