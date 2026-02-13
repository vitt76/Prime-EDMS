# Code Review Report: Sprint 2 — Analytics Module (Multi-Tenancy)

**Reviewer role:** Lead QA & Backend Architect  
**Scope:** Phase 1–5 (Data, Ingestion, Dashboard, Reports, Isolation tests)  
**Date:** 2026-02-11

---

## 1. Data Integrity & Signals Flow

### 1.1 Task vs Signal: explicit `organization_id` override

**Check:** Does the explicit `organization_id` passed to `AssetEvent.objects.create()` in the Task override the Signal's fallback logic?

**Result: PASS**

- In `organizations/apps.py`, `_bind_assetevent_organization` starts with:
  `if getattr(instance, 'organization_id', None): return`
- In `tasks.py`, `track_asset_event_async` calls
  `AssetEvent.objects.create(organization_id=organization.pk, document_id=..., ...)`.
- The instance is built with `organization_id` set before `pre_save` runs, so the signal sees `organization_id` and returns without overwriting. The task’s explicit ID is not replaced by document.organization.

**No change required.**

---

### 1.2 Bulk Create in `consume_analytics_events.py`

**Check:** Does bulk_create bypass signals? Is `organization_id` set manually before bulk_create?

**Result: PASS**

- Django’s `bulk_create()` does not emit `pre_save`/`post_save`.
- The command explicitly resolves organization before persist:
  - Builds `doc_to_org` from `Document.objects.filter(pk__in=doc_ids).values_list('pk', 'organization_id')`.
  - For each event: `ev.organization_id = doc_to_org.get(ev.document_id)`; events with no org are skipped (`valid_events`).
- Only events with a valid `organization_id` are passed to `AssetEvent.objects.bulk_create(asset_events)`.

**No change required.**

---

## 2. Migration Safety

### 2.1 Dependency chain

**Check:** 0010 depends on previous analytics and organizations; 0011/0012/0013 chain correct.

**Result: PASS**

- `0010`: dependencies `('analytics', '0009_portal_roi_distribution_v3')`, `('organizations', '0005_add_performance_indexes')` — Organization exists in 0001, 0005 is a later migration; correct.
- `0011`: dependencies `('analytics', '0010')`, `('documents', '0086_make_organization_required')` — correct (populate from document.organization_id after documents have required organization).
- `0012`: depends only on `0011` — correct.
- `0013`: depends on `0012` and `organizations.0005` — correct.

**No change required.**

---

### 2.2 Orphan records in 0011 (populate) and 0012 (NOT NULL)

**Check:** After populate, can any AssetEvent still have `organization_id` NULL? Would 0012 then fail?

**Result: WARNING (edge case)**

- In 0011, for each event we do: get `document` via select_related; if `document` is None (e.g. stale reference) or `document.organization_id` is None, we skip that event and do not set `organization_id`.
- After `documents.0086_make_organization_required`, every Document has non-null `organization_id`. AssetEvent has `document` FK with CASCADE, so events for deleted documents are already removed. So in practice the only theoretical case is a document row that still has NULL organization_id (should not exist after 0086).
- If for any reason one AssetEvent remains with NULL `organization_id`, 0012 `AlterField(..., null=False)` will raise an integrity error.

**Action Plan (optional hardening):**

In `0011_populate_assetevent_organization.py`, after the main loop, assign any remaining NULLs to a default organization (or delete them) so 0012 cannot fail:

```python
def populate_organization(apps, schema_editor):
    AssetEvent = apps.get_model('analytics', 'AssetEvent')
    Organization = apps.get_model('organizations', 'Organization')

    queryset = AssetEvent.objects.select_related('document').filter(organization__isnull=True)
    for event in queryset.iterator():
        document = getattr(event, 'document', None)
        if not document:
            continue
        organization_id = getattr(document, 'organization_id', None)
        if organization_id:
            event.organization_id = organization_id
            event.save(update_fields=['organization'])

    # Harden: any remaining NULLs -> assign default org so 0012 never fails
    default_org = Organization.objects.filter(slug='default').first()
    if default_org:
        AssetEvent.objects.filter(organization__isnull=True).update(organization_id=default_org.pk)
```

(Only add the final `update` if you have a `default` organization; otherwise document the risk in release notes.)

**Applied:** The CRITICAL fix (report `date_range` parameter reading) has been applied in `mayan/apps/analytics/tasks.py`. Optional 0011 orphan hardening and Memory Bank updates are left for your confirmation.

---

## 3. Middleware & Performance

### 3.1 Path robustness (exclude /static/, /admin/)

**Check:** Does the middleware avoid tracking /static/, /admin/, etc.?

**Result: PASS**

- Tracking only runs for paths that:
  - start with `/api/v4/documents/` or `/api/v4/headless/documents/` (GET), or
  - contain the substring `download`.
- `/static/`, `/admin/`, and other non-API paths do not match these prefixes/substrings, so they are not tracked.

**No change required.**

---

### 3.2 Non-blocking `.delay()`

**Check:** Is `track_asset_event_async.delay` strictly non-blocking?

**Result: PASS**

- `.delay()` enqueues the task and returns immediately; the response is not waited on. The middleware does not call `.get()` or similar. So it is fire-and-forget and non-blocking.

**No change required.**

---

### 3.3 Missing `request.organization` (public share, 404)

**Check:** Does the middleware handle missing `request.organization`?

**Result: PASS**

- First check: `if getattr(response, 'status_code', 500) >= 400: return response`.
- Then: `organization = getattr(request, 'organization', None)` and `if not organization: return response`.
- So for public share links or 404s where organization is not set, the middleware returns without calling the task. No leak and no error.

**No change required.**

---

## 4. Dashboard Queries (N+1 Risk)

### 4.1 Aggregations

**Check:** Are Count/aggregations optimized?

**Result: PASS**

- `total_documents`: single `.count()` with filter.
- `active_users_30d`: single query with `.values('user_id').distinct().count()`.
- `top_documents`: single query with `.values('document_id').annotate(view_count=Count('id')).order_by('-view_count')[:5]`.
- No per-row extra queries in the dashboard view.

**No change required.**

---

### 4.2 `top_documents` and select_related

**Check:** Does the view need `select_related('document')` for titles?

**Result: PASS (current contract)**

- The view returns only `document_id` and `view_count` for `top_documents`; it does not load document labels/titles. So there is no N+1 in this view. If the frontend later fetches document details by ID, that would be a separate client-side decision.

**No change required.** If you later add document label to the payload, then add a single optimized query (e.g. by document_id list) or annotate in the same query to avoid N+1.

---

## 5. Report Generation Logic

### 5.1 Strict `organization_id` filtering

**Check:** Does the task enforce organization scoping?

**Result: PASS**

- Task gets `organization_id` from kwargs and validates:
  - `report_task = AnalyticsReportTask.objects_unfiltered.get(pk=report_task_id)` then
  - `if str(report_task.organization_id) != str(organization_id): return` (with warning log).
- Aggregation uses `AssetEvent.objects_unfiltered.filter(organization_id=report_task.organization_id)`.
- So data is strictly scoped to the task’s organization.

**No change required.**

---

### 5.2 Error handling and status 'failed'

**Check:** If report generation fails, is status set to 'failed'?

**Result: PASS**

- In `generate_analytics_report`, the main logic is in a try/except. On exception:
  - `report_task.status = AnalyticsReportTask.STATUS_FAILED`
  - `report_task.completed_at = timezone.now()`
  - `report_task.save(update_fields=['status', 'completed_at'])`
- So failed runs are correctly marked and completed_at is set.

**No change required.**

---

### 5.3 Report parameters: date_range shape

**Check:** Does the task read date range from the same structure the API sends?

**Result: CRITICAL (logic bug)**

- API in `api_views.py` does:
  `parameters={'date_range': date_range, 'export_format': export_format}` where `date_range = request.data.get('date_range') or {}`.
- Task in `tasks.py` does:
  `date_from = params.get('date_from')` and `params.get('date_to')`.
- So the task looks for `params['date_from']` / `params['date_to']`, but the API stores `params['date_range']` (e.g. `{'from': '...', 'to': '...'}`). The task never sees the dates, so filtering by date range never applies.

**Action Plan:**

In `mayan/apps/analytics/tasks.py`, inside `generate_analytics_report`, replace:

```python
params = report_task.parameters or {}
date_from = params.get('date_from')
date_to = params.get('date_to')
```

with:

```python
params = report_task.parameters or {}
date_range = params.get('date_range') or {}
date_from = date_range.get('date_from') or date_range.get('from')
date_to = date_range.get('date_to') or date_range.get('to')
```

Optionally, document the expected shape of `date_range` (e.g. ISO dates for `from`/`to`) in the API or task docstring.

---

## Summary Table

| Area                         | Result    | Action                          |
|-----------------------------|-----------|----------------------------------|
| Signal vs task org_id       | PASS      | None                             |
| consume_analytics_events    | PASS      | None                             |
| Migration dependencies      | PASS      | None                             |
| Orphan records 0011/0012    | WARNING   | Optional: default-org fallback   |
| Middleware path/regex       | PASS      | None                             |
| Middleware non-blocking     | PASS      | None                             |
| Middleware no-org handling  | PASS      | None                             |
| Dashboard N+1               | PASS      | None                             |
| Report org filtering        | PASS      | None                             |
| Report failure status       | PASS      | None                             |
| Report date_range params    | CRITICAL  | Fix param reading (see above)    |

---

## Recommended next steps

1. **Mandatory:** Apply the report `date_range` fix in `tasks.py` (critical logic bug).
2. **Optional:** Add the 0011 orphan harden (default-org update) if you want 0012 to be guaranteed safe on any legacy data.
3. Re-run analytics tests and a quick smoke test of report generation with a date range after the fix.

---

## Memory Bank Updates (Draft)

Apply the following only after your confirmation.

### progress.md — append to "What Works" (Analytics Module) or "In Progress"

```markdown
#### 3. Analytics Module (Sprint 2 Part 3 — Tenant-aware)
- ✅ **AssetEvent tenant-aware:** TenantAwareMixin, FK `organization`, composite indexes; миграции analytics 0010 (AddField nullable), 0011 (populate from document.organization_id), 0012 (NOT NULL + indexes); pre_save binding в organizations/apps.py; consume_analytics_events — ручная подстановка organization_id перед bulk_create.
- ✅ **Ingestion:** AssetEventTrackingMiddleware (fire-and-forget), track_asset_event_async Celery task (TenantAwareTask); маршруты /api/v4/documents/, /api/v4/headless/documents/, пути с "download"; регистрация после TenantResolverMiddleware.
- ✅ **Dashboard API:** GET /api/v4/headless/analytics/dashboard/ — tenant-scoped метрики (total_documents, storage_used_gb, active_users_30d, top_documents, ai_usage); AnalyticsDashboardViewSet, DashboardMetricsSerializer; обязательный request.organization (X-Organization-Id).
- ✅ **Reports:** AnalyticsReportTask (organization, user, report_type, parameters, status, file_path); миграция 0013; generate_analytics_report (JSON в MEDIA_ROOT/reports/{org_id}/); POST .../analytics/reports/generate/, GET .../analytics/reports/{id}/; параметры date_range (from/to) в task исправлены (чтение из parameters['date_range']).
- ✅ **Tests:** test_middleware (track_asset_event_async.delay с organization_id), test_api (dashboard isolation по X-Organization-Id), test_reports (sync run + API), test_tenant_isolation (AssetEvent, dashboard, report isolation).
- ✅ **Code review (2026-02-11):** Signal vs task org_id — PASS; bulk_create org mapping — PASS; migrations deps — PASS; middleware path/non-blocking/no-org — PASS; dashboard N+1 — PASS; report org/failure — PASS; report date_range — CRITICAL fix applied.
```

### activeContext.md — replace "Current Focus" / Sprint 2 line and add transition

**Replace** the line:
`- **Sprint 2 (Неделя 3-4):** Analytics модуль — AssetEvent + Dashboard API (следующий)`

**With:**
`- **Sprint 2 (Неделя 3-4):** Analytics модуль — ✅ **ЗАВЕРШЁН** (AssetEvent tenant-aware, middleware, dashboard API, reports, isolation tests; code review 2026-02-11, critical date_range fix applied)`

**Append** to "Оставшиеся GAPS":
`- ✅ ~~AssetEvent НЕ tenant-aware~~ — **исправлено (Sprint 2)**`
`- ✅ ~~Analytics Dashboard не фильтрует по Organization~~ — **исправлено (Sprint 2)**`

**Add** a short "Transition to Sprint 3" block (e.g. after Sprint 2 closure):

```markdown
**Sprint 2 Part 3 (Analytics) — ЗАВЕРШЁН 2026-02-11:**
- AssetEvent: TenantAwareMixin, organization FK, migrations 0010–0012, pre_save binding, consume_analytics_events org mapping.
- Middleware: AssetEventTrackingMiddleware, track_asset_event_async (TenantAwareTask).
- Dashboard: AnalyticsDashboardViewSet, GET /api/v4/headless/analytics/dashboard/, tenant-scoped metrics.
- Reports: AnalyticsReportTask, 0013, generate_analytics_report (JSON), POST/GET reports API.
- Tests: middleware, dashboard isolation, reports, test_tenant_isolation.
- Code review: one CRITICAL fix (report date_range from parameters['date_range']) applied; optional 0011 orphan hardening documented.

**Следующий фокус:** Sprint 3 — Distribution + Notifications (ShareLink tenant-aware, WebSocket org validation).
```

### techContext.md — add subsection under Backend or "Multi-tenancy"

**Location:** After "Очереди и задачи" or in a "Multi-tenancy / Analytics" subsection.

```markdown
#### Analytics (tenant-aware, Sprint 2)
- **AssetEvent:** TenantAwareMixin, FK organization; индексы (organization, event_type, -timestamp), (organization, document, -timestamp). Создание: pre_save signal (organizations) или явная передача organization_id (Celery, consume_analytics_events).
- **AssetEventTrackingMiddleware:** В цепочке после TenantResolverMiddleware; срабатывает на GET /api/v4/documents/, /api/v4/headless/documents/ и путях с "download"; вызывает track_asset_event_async.delay (fire-and-forget). Не трекает при отсутствии request.organization или при response.status_code >= 400.
- **Dashboard API:** GET /api/v4/headless/analytics/dashboard/ — один endpoint с метриками по текущей организации (X-Organization-Id); Document.valid.filter(organization=org), AssetEvent.objects.filter(organization=org), org.get_storage_used_gb(), org.get_ai_analyses_this_month().
- **Reports:** AnalyticsReportTask (status pending/processing/completed/failed); Celery generate_analytics_report читает parameters['date_range']['from'|'to'], фильтрует AssetEvent по organization_id, пишет JSON в MEDIA_ROOT/reports/{org_id}/{task_id}.json.
```
