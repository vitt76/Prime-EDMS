# 🚀 КОМПЛЕКСНЫЙ ПЛАН ТРАНСФОРМАЦИИ DAM ФРОНТЕНДА
## Версия 3.0: Архитектура + Аналитика + Пошаговый алгоритм для Cursor

**Дата:** 25 Ноября 2025  
**Версия:** 3.0 (Complete Transformation Blueprint)  
**Аудитория:** CDTO, Cursor AI, Senior Frontend Architects, DevOps  
**Уровень детализации:** Enterprise-Grade (Senior 20+ лет experience)  
**Статус:** ✅ READY FOR CURSOR DEVELOPMENT

---

## 📑 ОГЛАВЛЕНИЕ

1. [Исполнительное резюме](#исполнительное-резюме)
2. [Анализ текущего состояния (критические проблемы)](#анализ-текущего-состояния)
3. [Архитектурное видение (target state)](#архитектурное-видение)
4. [Критические исправления API (Phase 0 - MUST DO)](#критические-исправления-api)
5. [Детальный план по фазам с алгоритмами Cursor](#детальный-план-по-фазам)
6. [Пошаговые алгоритмы для Cursor AI](#пошаговые-алгоритмы-для-cursor)
7. [DevOps & Ubuntu/WSL Setup](#devops-ubuntu-wsl-setup)
8. [Метрики успеха и мониторинг](#метрики-успеха)
9. [Roadmap & Timeline](#roadmap)
10. [Appendix: Prompt Templates для Cursor](#appendix-cursor-prompts)

---

## 📊 ИСПОЛНИТЕЛЬНОЕ РЕЗЮМЕ

### Текущее состояние: 2.7/5 ⭐

| Метрика | Текущее | Целевое | Дельта |
|---------|---------|---------|--------|
| **UI/UX оценка** | 2.7/5 | 4.5/5 | +67% |
| **API качество** | 6.3/10 | 9.2/10 | +46% |
| **Производительность (LH)** | 62 | 92+ | +30 пунктов |
| **Время загрузки** | 2.7s | <1.5s | -45% |
| **Безопасность (OWASP)** | 5/10 | 9.5/10 | +90% |
| **User adoption** | 45% | 95% | +110% |
| **Кол-во критических уязвимостей** | 5 | 0 | -5 |

### Ключевые инсайты

**✅ Что хорошо:**
- Стабильный Django бэкенд
- Существующая БД с достаточными данными
- Четко определенные бизнес-требования (DAM, Distribution, AI)
- Команда готова к переходу (Cursor-optimized process)

**🔴 Критические проблемы API (blocking frontend):**
1. DAMDocumentDetailView без аутентификации (любой может получить доступ)
2. Отсутствие валидации входных данных (инъекции, DoS)
3. Нет пагинации (500+ документов → OutOfMemory)
4. N+1 запросы (100 документов = 100+ SQL queries)
5. HTML в JSON ответах (не REST, неиспользуемо для мобильных)

**⚠️ Архитектурные недостатки:**
- Bootstrap 3 (EOL 2019) - security risks
- jQuery inline scripts (нетестируемо, нещкалируемо)
- Table-first вместо gallery-first
- Поиск внизу, не в топе (bad UX discovery)
- Нет фасетной фильтрации (долгий поиск активов)

### ROI & Timeline

```
Investment: 12 недель (2 разработчика на фронтенд, 1 на бэкенд)
Backend fixes: 1-2 недели (критические)
Frontend build: 10 недель (с Cursor ускорением 30-40%)

Expected ROI:
- User adoption: +110% (45% → 95%)
- Performance: +30 пунктов Lighthouse
- Security: 0 known vulnerabilities (vs 5 критических)
- Cost savings: -40% support tickets (лучше UX)
- Revenue impact: +25% через интеграции (API-ready)
```

---

## 🔍 АНАЛИЗ ТЕКУЩЕГО СОСТОЯНИЯ

### Architecture Assessment

#### Frontend Stack (текущее)
```yaml
Framework:           Django Templates (SSR)
CSS:                Bootstrap 3.4.1 (EOL 2019) ❌
JavaScript:         jQuery 3.6.0 + inline scripts
Icons:              FontAwesome 5.15.4 (dated)
State Management:   None (server-side session)
HTTP:               AJAX (jQuery $.ajax)
Build Tool:         None (direct script loading)
Testing:            Minimal
Performance Score:  62/100 ⚠️
```

#### Backend API (текущее)
```yaml
Framework:          Django REST Framework 3.x
Endpoints:          /api/v4/ (несогласованные) 
Authentication:     Session + Token (но не везде)
Authorization:      ACL (но не везде проверяется)
Validation:         Partial (serializers есть, но не везде)
Pagination:         Absent on some endpoints ❌❌
Caching:            None
Rate Limiting:      None ❌❌
Error Handling:     Generic exceptions (security risk)
Security:           Critical issues found ❌❌❌
Query Optimization: N+1 problems ❌❌
API Quality:        6.3/10
```

#### Database & Infrastructure
```yaml
Database:           PostgreSQL ✅
Message Queue:      Celery (async tasks) ✅
Cache:              Redis (optional)
Storage:            File system / S3
Monitoring:         Basic (or none)
Logging:            Basic (or none)
CI/CD:              Minimal
```

### Критические проблемы (Issue Matrix)

#### Severity P0 - БЛОКИРУЮЩИЕ

```
Issue #1: DAMDocumentDetailView authentication bypass
┌─────────────────────────────────────────────────────────────┐
│ Severity: CRITICAL | Priority: P0 | Timeline: Week 1 Block  │
├─────────────────────────────────────────────────────────────┤
│ Description:                                                │
│   permission_classes = ()  # Anyone can access!             │
│   No mayan_object_permissions check                         │
│   Returns sensitive metadata without authorization           │
│                                                              │
│ Impact:                                                     │
│   ⚠️ Unauthorized users can download all assets              │
│   ⚠️ GDPR/data privacy violation                             │
│   ⚠️ Compliance risk (SOC 2, ISO 27001)                      │
│                                                              │
│ Exploitation:                                               │
│   curl http://api/v4/dam/documents/123/details/             │
│   → Returns full metadata (no auth required!)                │
│                                                              │
│ Fix: Add permission_classes + check_object_permissions     │
│ Effort: 1-2 hours | Risk: Low (backward compat)            │
└─────────────────────────────────────────────────────────────┘

Issue #2: Input validation missing in custom actions
┌─────────────────────────────────────────────────────────────┐
│ Severity: CRITICAL | Priority: P0 | Timeline: Week 1 Block  │
├─────────────────────────────────────────────────────────────┤
│ Description:                                                │
│   @action methods use request.data.get() directly          │
│   No serializer validation on custom endpoints             │
│   Accepts any data format                                  │
│                                                              │
│ Impact:                                                     │
│   ⚠️ SQL injection risks (if not using ORM)                  │
│   ⚠️ DoS via malformed requests                              │
│   ⚠️ Invalid state transitions                               │
│                                                              │
│ Exploitation:                                               │
│   POST /analyze/ with 1M document IDs (DoS)                 │
│   POST /bulk/ with invalid format (error explosion)        │
│                                                              │
│ Fix: Create serializers for all custom actions            │
│ Effort: 3-4 hours | Risk: Low (validation only)           │
└─────────────────────────────────────────────────────────────┘

Issue #3: Missing pagination on list endpoints
┌─────────────────────────────────────────────────────────────┐
│ Severity: CRITICAL | Priority: P0 | Timeline: Week 1 Block  │
├─────────────────────────────────────────────────────────────┤
│ Description:                                                │
│   Some endpoints return ALL records without pagination     │
│   500+ documents = 500+ MB in memory                       │
│   No max_page_size protection                              │
│                                                              │
│ Impact:                                                     │
│   ⚠️ OutOfMemory errors (production crash)                   │
│   ⚠️ Bandwidth exhaustion                                    │
│   ⚠️ Poor frontend performance (rendering 10k items)        │
│                                                              │
│ Exploitation:                                               │
│   GET /api/v4/dam/documents/ (no limit)                     │
│   → 500 items × 50KB each = 25 MB response                  │
│                                                              │
│ Fix: Add pagination_class to all ListAPIView              │
│ Effort: 2-3 hours | Risk: Low (backward compat)           │
└─────────────────────────────────────────────────────────────┘

Issue #4: HTML in API responses (not REST)
┌─────────────────────────────────────────────────────────────┐
│ Severity: CRITICAL | Priority: P0 | Timeline: Week 1 Block  │
├─────────────────────────────────────────────────────────────┤
│ Description:                                                │
│   DAMDocumentDetailView returns HTML in JSON               │
│   Response: {name: "...", html: "<html>...</html>"}        │
│   Frontend can't parse/render (expects structured JSON)    │
│                                                              │
│ Impact:                                                     │
│   ⚠️ Breaks mobile app compatibility                         │
│   ⚠️ Not true REST API                                       │
│   ⚠️ Frontend must render HTML (XSS risk)                    │
│                                                              │
│ Exploitation:                                               │
│   React/Vue frontend can't parse HTML string               │
│   Must use dangerouslySetInnerHTML (XSS vector)            │
│                                                              │
│ Fix: Return pure JSON structure                            │
│ Effort: 2-3 hours | Risk: Medium (requires refactoring)   │
└─────────────────────────────────────────────────────────────┘

Issue #5: N+1 queries in serializers (performance)
┌─────────────────────────────────────────────────────────────┐
│ Severity: HIGH | Priority: P0.5 | Timeline: Week 1 Block   │
├─────────────────────────────────────────────────────────────┤
│ Description:                                                │
│   SerializerMethodField calls database in loop             │
│   get_document_filename() for each record                  │
│   100 documents = 1 + 100 additional SQL queries           │
│                                                              │
│ Impact:                                                     │
│   ⚠️ API response time: 100ms → 5+ seconds                   │
│   ⚠️ Database connection pool exhaustion                     │
│   ⚠️ Poor UX (slow gallery load)                             │
│                                                              │
│ Current:  1 + 100 = 101 queries                             │
│ After fix: 1 + 1 = 2 queries                                │
│                                                              │
│ Fix: Use prefetch_related, annotate, select_related       │
│ Effort: 2-3 hours | Risk: Low (optimization only)         │
└─────────────────────────────────────────────────────────────┘
```

#### Severity P1 - HIGH PRIORITY

| Issue | Description | Impact | Fix Time |
|-------|-------------|--------|----------|
| No rate limiting | DoS attacks possible | Downtime risk | 1h |
| Unsafe error handling | Info leakage (stack traces) | Security | 1h |
| Weak CORS config | CSRF attacks | Security | 1h |
| No query optimization | Slow responses | Performance | 3h |
| Missing tests | Regression risk | Quality | 2h |

---

## 🏗️ АРХИТЕКТУРНОЕ ВИДЕНИЕ (Target State)

### Frontend Target Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Modern SPA Frontend                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ User Interface Layer (Vue 3 + TypeScript)           │  │
│  │ • Gallery Grid View (4-6 columns, responsive)       │  │
│  │ • Smart Search (instant results, facets)            │  │
│  │ • Asset Detail (preview + metadata sidebar)         │  │
│  │ • Bulk operations (select, tag, export)             │  │
│  │ • Real-time collaboration (comments, approvals)     │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↕                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Component Library (Headless UI + Tailwind)          │  │
│  │ • 50+ reusable, accessible components               │  │
│  │ • Dark mode support (CSS variables)                 │  │
│  │ • Mobile-optimized (touch, responsive)              │  │
│  │ • Storybook documentation                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↕                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ State Management (Pinia)                             │  │
│  │ • Assets store (gallery data)                       │  │
│  │ • Search store (query, facets, results)             │  │
│  │ • UI store (modals, sidebar, theme)                 │  │
│  │ • Auth store (user, permissions)                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↕                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ HTTP Client (Axios + Interceptors)                  │  │
│  │ • Request interceptors (CSRF token, auth)           │  │
│  │ • Response interceptors (structured error handling)  │  │
│  │ • Automatic retry logic                              │  │
│  │ • Offline support (IndexedDB)                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↕                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Real-time Communication (WebSocket + Polling)       │  │
│  │ • Live notifications (asset uploaded, commented)    │  │
│  │ • Collaborative updates (who's editing)             │  │
│  │ • Async task status (AI analysis complete)          │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↕                                  │
└─────────────────────────────────────────────────────────────┘
                    NETWORK BOUNDARY
                          ↕
┌─────────────────────────────────────────────────────────────┐
│              REST API Gateway                               │
│ • CORS handling | • Rate limiting | • Token refresh        │
└─────────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────────┐
│          Production-Grade Django REST API                  │
├─────────────────────────────────────────────────────────────┤
│ ✅ DAM Module                                               │
│    GET  /api/v4/dam/assets/                (paginated)      │
│    POST /api/v4/dam/assets/search/         (with facets)    │
│    POST /api/v4/dam/assets/bulk/           (with validation)│
│    GET  /api/v4/dam/assets/{id}/           (auth required)  │
│    PUT  /api/v4/dam/assets/{id}/           (validated)      │
│    DELETE /api/v4/dam/assets/{id}/         (validated)      │
│    POST /api/v4/dam/assets/{id}/comments/  (validated)      │
│                                                              │
│ ✅ Distribution Module                                      │
│    GET  /api/v4/distribution/publications/ (paginated)      │
│    POST /api/v4/distribution/publications/ (validated)      │
│    GET  /api/v4/distribution/stats/        (cached)         │
│                                                              │
│ ✅ AI Module                                                │
│    POST /api/v4/ai/analyze/               (with validation)  │
│    GET  /api/v4/ai/results/{id}/          (auth required)   │
│    POST /api/v4/ai/bulk-analyze/          (rate limited)    │
│                                                              │
│ ✅ Real-time Layer                                          │
│    WS /ws/dam/notifications/              (secure WebSocket)│
│    WS /ws/distribution/events/            (secure WebSocket)│
│                                                              │
│ Features:                                                   │
│   • All endpoints return pure JSON                          │
│   • All inputs validated through serializers                │
│   • All queries optimized (prefetch, annotate)              │
│   • All list endpoints paginated (limit: 50, max: 100)      │
│   • All custom actions have permission checks               │
│   • Rate limiting on bulk operations                        │
│   • Structured error responses                              │
│   • Response times < 500ms (p95)                            │
│   • 0 known security vulnerabilities                        │
│   • Full test coverage (>85%)                               │
└─────────────────────────────────────────────────────────────┘
```

### Component Hierarchy & Data Flow

```
┌─ App.vue (Root)
│
├─ Header (fixed)
│  ├─ Logo → Dashboard
│  ├─ SearchBar
│  │  └─ Instant Results (from searchStore)
│  ├─ UploadButton → UploadModal
│  ├─ FilterToggle → toggles FiltersPanel
│  ├─ NotificationsBell
│  │  └─ NotificationCenter (from notificationStore)
│  └─ UserMenu
│     ├─ Profile → SettingsPage
│     └─ Logout
│
├─ Sidebar (collapsible, 280px)
│  ├─ Navigation
│  │  ├─ Dashboard → router.push('/')
│  │  ├─ DAM → router.push('/dam')
│  │  ├─ Distribution → router.push('/distribution')
│  │  └─ Admin → router.push('/admin')
│  ├─ Collections (expandable tree)
│  │  ├─ My Uploads (assetStore.userAssets)
│  │  ├─ Favorites (assetStore.favorites)
│  │  ├─ Recent (assetStore.recent)
│  │  └─ Shared with me (assetStore.shared)
│  └─ Quick Actions
│     └─ [+ New Folder]
│
├─ MainContent
│  └─ RouterView (current page)
│     ├─ DashboardPage
│     │  ├─ WelcomeBanner
│     │  ├─ StatsCards (from dashboardStore)
│     │  ├─ ActivityFeed (from activityStore)
│     │  └─ RecentAssets (from assetStore)
│     │
│     ├─ DAMPage
│     │  ├─ ViewToggler (grid/list/table)
│     │  ├─ SortSelector
│     │  ├─ FiltersPanel (left sidebar)
│     │  │  ├─ TypeFilter
│     │  │  ├─ DateRangeFilter
│     │  │  ├─ TagFilter
│     │  │  └─ CustomMetadataFilters
│     │  ├─ GalleryView
│     │  │  ├─ AssetCard (for each item in assetStore.assets)
│     │  │  │  ├─ Thumbnail (lazy-loaded)
│     │  │  │  ├─ Title
│     │  │  │  ├─ QuickActions (hover)
│     │  │  │  │  ├─ Preview
│     │  │  │  │  ├─ Share
│     │  │  │  │  ├─ Download
│     │  │  │  │  └─ More menu
│     │  │  │  └─ Checkbox (for bulk select)
│     │  │  └─ Pagination
│     │  │     ├─ Page selector
│     │  │     └─ Items per page selector
│     │  └─ BulkActions (if assetStore.selectedAssets.length > 0)
│     │     ├─ Counter ("123 selected")
│     │     ├─ Tag button → BulkTagModal
│     │     ├─ Move button → MoveAssetsModal
│     │     ├─ Delete button → DeleteConfirmModal
│     │     ├─ Download button → Export
│     │     ├─ Share button → ShareModal
│     │     └─ Clear selection
│     │
│     ├─ AssetDetailPage
│     │  ├─ PreviewPane (left 60%)
│     │  │  ├─ LargeImageViewer (or VideoPlayer)
│     │  │  ├─ ZoomControls
│     │  │  └─ NavigationArrows
│     │  └─ MetadataPane (right 40%)
│     │     ├─ FileDetails
│     │     ├─ ImageMetadata (EXIF)
│     │     ├─ AIAnalysis
│     │     │  ├─ TagSuggestions (from aiStore)
│     │     │  ├─ ColorPalette
│     │     │  └─ ObjectsDetected
│     │     ├─ VersionHistory
│     │     ├─ CommentsThread
│     │     ├─ WorkflowStatus
│     │     └─ Actions
│     │        ├─ Approve button
│     │        ├─ Share button
│     │        └─ More menu
│     │
│     ├─ DistributionPage
│     │  ├─ PublicationList
│     │  │  ├─ PublicationCard (for each in distributionStore.publications)
│     │  │  │  ├─ Title
│     │  │  │  ├─ Status badge
│     │  │  │  ├─ Channel icons
│     │  │  │  ├─ Schedule info
│     │  │  │  ├─ Metrics (views, downloads)
│     │  │  │  └─ Actions (edit, delete, preview)
│     │  │  └─ Pagination
│     │  └─ [+ Create Publication] → CreatePublicationModal
│     │
│     └─ SettingsPage
│        ├─ ProfileSettings
│        ├─ AccountSettings
│        ├─ SecuritySettings
│        ├─ NotificationPreferences
│        └─ APIKeys
│
├─ Modals (Portal)
│  ├─ UploadModal (controlled by uiStore.activeModal)
│  │  ├─ DragDropZone
│  │  ├─ FileUploader (with progress)
│  │  └─ MetadataForm (optional before upload)
│  │
│  ├─ ShareModal
│  │  ├─ GenerateLinkButton
│  │  ├─ LinkDisplay (copy button)
│  │  ├─ PermissionsSelector
│  │  ├─ ExpirationDatePicker
│  │  └─ PasswordProtection (optional)
│  │
│  ├─ BulkTagModal
│  │  ├─ OperationSelector (add/remove/replace)
│  │  ├─ TagInput (autocomplete from tagsStore)
│  │  └─ ApplyButton
│  │
│  ├─ DeleteConfirmModal
│  │  ├─ ItemsPreview
│  │  ├─ WarningMessage
│  │  └─ [Cancel] [Delete] buttons
│  │
│  └─ NotificationCenterModal
│     ├─ Tabs (All/Unread/Mentions)
│     ├─ NotificationList
│     └─ MarkAsReadButtons
│
└─ Toasts (for temporary notifications)
   ├─ Success messages
   ├─ Error messages
   └─ Info messages
```

### Key Component Examples (TypeScript + Vue 3)

**GalleryView.vue** (Gallery Grid Component)
```typescript
<template>
  <div class="gallery-container">
    <!-- Top toolbar -->
    <div class="gallery-toolbar">
      <div class="view-options">
        <button @click="viewMode = 'grid'" :class="{active: viewMode === 'grid'}">
          📊 Grid
        </button>
        <button @click="viewMode = 'list'" :class="{active: viewMode === 'list'}">
          📝 List
        </button>
      </div>
      <div class="sort-options">
        <select v-model="sortBy" @change="onSortChange">
          <option value="date_desc">Newest first</option>
          <option value="date_asc">Oldest first</option>
          <option value="name_asc">Name A-Z</option>
        </select>
      </div>
      <div class="bulk-actions" v-if="selectedCount > 0">
        <button @click="selectAll">Select all</button>
        <span>{{ selectedCount }} selected</span>
        <button @click="clearSelection">Clear</button>
      </div>
    </div>

    <!-- Asset grid with virtual scrolling (for performance) -->
    <div v-if="viewMode === 'grid'" class="grid-container" ref="scrollContainer">
      <VirtualList :items="assets" :item-size="320">
        <template #default="{ item }">
          <AssetCard 
            :asset="item"
            :selected="selectedAssets.includes(item.id)"
            @select="toggleSelect($event)"
            @click="goToDetail(item.id)"
          />
        </template>
      </VirtualList>
    </div>

    <!-- List view alternative -->
    <div v-else class="list-container">
      <table>
        <thead>
          <tr>
            <th><input type="checkbox" @change="toggleSelectAll" /></th>
            <th>Name</th>
            <th>Type</th>
            <th>Size</th>
            <th>Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in assets" :key="item.id" :class="{selected: selectedAssets.includes(item.id)}">
            <td><input type="checkbox" :checked="selectedAssets.includes(item.id)" /></td>
            <td>{{ item.name }}</td>
            <td><AssetTypeIcon :type="item.type" /> {{ item.type }}</td>
            <td>{{ formatSize(item.size) }}</td>
            <td>{{ formatDate(item.date_uploaded) }}</td>
            <td>
              <button @click="goToDetail(item.id)">View</button>
              <button @click="downloadAsset(item)">Download</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="pagination">
      <button @click="previousPage" :disabled="!hasPreviousPage">← Previous</button>
      <span>Page {{ currentPage }} of {{ totalPages }}</span>
      <button @click="nextPage" :disabled="!hasNextPage">Next →</button>
      <select v-model.number="pageSize" @change="onPageSizeChange">
        <option value="20">20 items</option>
        <option value="50">50 items</option>
        <option value="100">100 items</option>
      </select>
    </div>

    <!-- Bulk actions toolbar (sticky) -->
    <BulkActionsBar v-if="selectedCount > 0" 
      :count="selectedCount"
      @tag="openBulkTagModal"
      @move="openMoveModal"
      @delete="openDeleteModal"
      @download="bulkDownload"
      @share="openShareModal"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAssetStore } from '@/stores/assetStore'
import { useFilterStore } from '@/stores/filterStore'
import AssetCard from './AssetCard.vue'
import BulkActionsBar from './BulkActionsBar.vue'
import VirtualList from 'vue-virtual-list'

const router = useRouter()
const assetStore = useAssetStore()
const filterStore = useFilterStore()

const viewMode = ref<'grid' | 'list'>('grid')
const sortBy = ref('date_desc')
const selectedAssets = ref<number[]>([])

// Computed properties
const assets = computed(() => assetStore.currentPageAssets)
const selectedCount = computed(() => selectedAssets.value.length)
const currentPage = computed(() => assetStore.pagination.currentPage)
const totalPages = computed(() => assetStore.pagination.totalPages)
const pageSize = computed(() => assetStore.pagination.pageSize)
const hasNextPage = computed(() => assetStore.pagination.hasNextPage)
const hasPreviousPage = computed(() => assetStore.pagination.hasPreviousPage)

// Methods
const toggleSelect = (assetId: number) => {
  const index = selectedAssets.value.indexOf(assetId)
  if (index === -1) {
    selectedAssets.value.push(assetId)
  } else {
    selectedAssets.value.splice(index, 1)
  }
}

const toggleSelectAll = () => {
  if (selectedCount.value === assets.value.length) {
    selectedAssets.value = []
  } else {
    selectedAssets.value = assets.value.map(a => a.id)
  }
}

const clearSelection = () => {
  selectedAssets.value = []
}

const onSortChange = () => {
  assetStore.fetchAssets({ sort: sortBy.value })
}

const goToDetail = (assetId: number) => {
  router.push(`/dam/assets/${assetId}`)
}

const nextPage = () => {
  assetStore.nextPage()
}

const previousPage = () => {
  assetStore.previousPage()
}

const onPageSizeChange = () => {
  assetStore.setPageSize(pageSize.value)
}

// Initial load
onMounted(() => {
  assetStore.fetchAssets()
})
</script>

<style scoped>
.gallery-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.gallery-toolbar {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
  align-items: center;
}

.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  padding: 1rem;
  flex: 1;
  overflow: auto;
}

.list-container {
  flex: 1;
  overflow: auto;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-top: 1px solid var(--color-border);
}
</style>
```

---

## 🔧 КРИТИЧЕСКИЕ ИСПРАВЛЕНИЯ API (Phase 0)

### Timeline: Week 1 (Must complete before frontend development)

Все исправления должны быть выполнены к концу недели 1, чтобы фронтенд-команда имела надежный API.

### Fix #1: DAMDocumentDetailView - Add Authentication

**File:** `mayan/apps/dam/api_views.py:XXX`

```python
# BEFORE (VULNERABLE):
class DAMDocumentDetailView(mayan_generics.GenericAPIView):
    permission_classes = ()  # ❌❌❌ CRITICAL SECURITY ISSUE
    renderer_classes = (JSONRenderer,)
    
    def get(self, request, document_id, *args, **kwargs):
        try:
            document = Document.objects.get(id=document_id)
            # Returns HTML (not REST)
            html = render_to_string('dam/asset_detail.html', {
                'object': document,
                'ai_data': {...}
            })
            return Response({
                'name': document.label,
                'html': html  # ❌ HTML in JSON response
            })
        except Document.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)

# AFTER (SECURE):
class DAMDocumentDetailView(mayan_generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)  # ✅ REQUIRED
    mayan_object_permissions = {'GET': (permission_document_view,)}  # ✅ ACL CHECK
    renderer_classes = (JSONRenderer,)
    
    def get(self, request, document_id, *args, **kwargs):
        try:
            document = Document.objects.get(id=document_id)
            
            # Check permissions
            AccessControlList.objects.check_access(
                obj=document,
                permissions=(permission_document_view,),
                user=request.user
            )
            
            # Return pure JSON structure
            serializer = DAMDocumentDetailSerializer(
                document,
                context={'request': request}
            )
            return Response(serializer.data)  # ✅ JSON only
            
        except Document.DoesNotExist:
            return Response(
                {'error': {'code': 'NOT_FOUND', 'message': 'Document not found'}},
                status=404
            )
        except AccessDenied:
            return Response(
                {'error': {'code': 'PERMISSION_DENIED', 'message': 'Access denied'}},
                status=403
            )
```

**New Serializer:**
```python
# mayan/apps/dam/serializers.py

class DAMDocumentDetailSerializer(serializers.ModelSerializer):
    """Complete document detail with metadata, AI analysis, comments"""
    
    file_details = serializers.SerializerMethodField()
    ai_analysis = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    version_history = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'label', 'date_added', 'size',
            'file_details', 'ai_analysis', 'comments',
            'version_history', 'tags', 'access_level'
        ]
        read_only_fields = fields
    
    def get_file_details(self, obj):
        # Get latest file (optimized: prefetch_related in ViewSet)
        latest_file = obj.files.first()
        if not latest_file:
            return None
        
        return {
            'filename': latest_file.filename,
            'size': latest_file.size,
            'mime_type': latest_file.mime_type,
            'uploaded_date': latest_file.timestamp,
            'checksum': latest_file.checksum,
        }
    
    def get_ai_analysis(self, obj):
        # Get AI analysis (optimized: prefetch_related in ViewSet)
        if hasattr(obj, 'ai_analysis') and obj.ai_analysis:
            return {
                'tags': obj.ai_analysis.formatted_tags,
                'confidence': obj.ai_analysis.average_confidence,
                'objects_detected': obj.ai_analysis.objects,
                'colors': obj.ai_analysis.dominant_colors,
                'status': obj.ai_analysis.analysis_status,
            }
        return None
    
    def get_comments(self, obj):
        # Get comments (paginated, latest first)
        comments = obj.comments.all()[:50]  # Limit to 50
        return [{
            'id': c.id,
            'author': c.author.username,
            'text': c.text,
            'created_date': c.created_date,
            'replies': [...]  # Nested replies if needed
        } for c in comments]
    
    def get_version_history(self, obj):
        # Get version history (paginated)
        versions = obj.files.all().order_by('-timestamp')[:20]
        return [{
            'id': v.id,
            'filename': v.filename,
            'uploaded_date': v.timestamp,
            'uploaded_by': v.user.username if v.user else 'unknown',
            'size': v.size,
        } for v in versions]
```

**ViewSet Update:**
```python
class DAMDocumentDetailView(mayan_generics.GenericAPIView):
    # ... (permission classes added above)
    
    def get_queryset(self):
        # Optimize queries: prefetch related data
        return Document.objects.select_related(
            'document_type'
        ).prefetch_related(
            'files',  # For file_details
            'ai_analysis',  # For AI data
            'comments',  # For comments thread
            'comments__replies'  # For nested replies
        ).order_by('-id')
```

### Fix #2: Add Serializer Validation to Custom Actions

**File:** `mayan/apps/dam/serializers.py` (NEW)

```python
class AnalyzeDocumentSerializer(serializers.Serializer):
    """Validate document analyze request"""
    document_id = serializers.IntegerField(min_value=1, required=True)
    
    def validate_document_id(self, value):
        try:
            doc = Document.objects.get(id=value)
            return doc
        except Document.DoesNotExist:
            raise serializers.ValidationError(
                f"Document with ID {value} not found"
            )
    
    def validate(self, data):
        # Additional cross-field validation
        document = data['document_id']
        if not document.files.exists():
            raise serializers.ValidationError(
                "Cannot analyze document without files"
            )
        return data


class BulkAnalyzeDocumentsSerializer(serializers.Serializer):
    """Validate bulk analyze request (with DoS protection)"""
    document_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
        max_length=100,  # ✅ MAX LIMIT TO PREVENT DoS
        help_text='Maximum 100 document IDs allowed per request'
    )
    
    def validate_document_ids(self, value):
        if len(value) > 100:
            raise serializers.ValidationError(
                'Maximum 100 documents allowed per bulk operation'
            )
        # Verify all documents exist
        docs = Document.objects.filter(id__in=value)
        if docs.count() != len(set(value)):
            missing = set(value) - set(docs.values_list('id', flat=True))
            raise serializers.ValidationError(
                f"Documents not found: {missing}"
            )
        return value


class BulkOperationSerializer(serializers.Serializer):
    """Validate bulk operations (tag, move, delete)"""
    VALID_ACTIONS = ['add_tags', 'remove_tags', 'move', 'delete', 'export']
    
    ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
        max_length=500,  # ✅ MAX LIMIT
    )
    action = serializers.ChoiceField(choices=VALID_ACTIONS)
    data = serializers.JSONField(required=False, default={})
    
    def validate_ids(self, value):
        if len(value) > 500:
            raise serializers.ValidationError(
                'Maximum 500 items allowed per bulk operation'
            )
        return list(set(value))  # Remove duplicates
```

**API View Update:**
```python
@action(detail=False, methods=['post'], throttle_classes=[BulkOperationThrottle])
def analyze(self, request):
    """Analyze document with AI (with validation)"""
    serializer = AnalyzeDocumentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)  # ✅ VALIDATION
    
    document = serializer.validated_data['document_id']
    
    # Check permissions
    try:
        AccessControlList.objects.check_access(
            obj=document,
            permissions=(permission_document_view,),
            user=request.user
        )
    except AccessDenied:
        return Response(
            {'error': {'code': 'FORBIDDEN', 'message': 'Cannot analyze this document'}},
            status=403
        )
    
    # Trigger async task
    analyze_document_with_ai.delay(document.id)
    
    return Response({
        'success': True,
        'message': 'Analysis started',
        'document_id': document.id,
        'status': 'pending'
    })


@action(detail=False, methods=['post'], throttle_classes=[BulkOperationThrottle])
def bulk_analyze(self, request):
    """Bulk analyze documents (with DoS protection)"""
    serializer = BulkAnalyzeDocumentsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)  # ✅ VALIDATION + LIMIT
    
    document_ids = serializer.validated_data['document_ids']
    
    # Check permissions for each document
    allowed_docs = AccessControlList.objects.restrict_queryset(
        queryset=Document.objects.filter(id__in=document_ids),
        permission=permission_document_view,
        user=request.user
    )
    
    allowed_ids = list(allowed_docs.values_list('id', flat=True))
    denied_count = len(document_ids) - len(allowed_ids)
    
    # Queue analysis tasks
    for doc_id in allowed_ids:
        analyze_document_with_ai.delay(doc_id)
    
    return Response({
        'success': True,
        'message': f'Queued {len(allowed_ids)} documents for analysis',
        'queued': len(allowed_ids),
        'denied': denied_count,
    })
```

### Fix #3: Add Pagination to All List Endpoints

**File:** `mayan/apps/dam/api_views.py` (UPDATE)

```python
# Settings configuration
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,  # Default page size
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'bulk_operation': '10/hour',  # Strict limit for bulk ops
    }
}

# Custom paginator
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    page_size_query_description = 'Number of items per page'
    max_page_size = 100  # ✅ PREVENT ABUSE
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size': self.page_size,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })

# List View
class DAMDocumentListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = DAMDocumentListSerializer
    pagination_class = StandardResultsSetPagination  # ✅ ADD PAGINATION
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['label', 'tags__name', 'ai_analysis__tags']
    ordering_fields = ['date_added', 'label', 'size']
    ordering = ['-date_added']  # Default: newest first
    
    def get_queryset(self):
        # ✅ OPTIMIZE QUERIES
        queryset = AccessControlList.objects.restrict_queryset(
            queryset=Document.objects.select_related(
                'document_type'
            ).prefetch_related(
                'files',
                'ai_analysis',
                'tags'
            ),
            permission=permission_document_view,
            user=self.request.user
        )
        return queryset.order_by('-date_added')
```

### Fix #4: Remove HTML from API Responses (JSON Only)

**Before (Problematic):**
```python
def get(self, request, *args, **kwargs):
    html = render_to_string('template.html', context)
    return Response({
        'id': 1,
        'name': 'asset.jpg',
        'html': html  # ❌ NOT REST
    })
```

**After (Correct REST):**
```python
def get(self, request, *args, **kwargs):
    serializer = AssetSerializer(asset)
    return Response(serializer.data)  # ✅ PURE JSON
```

**Frontend will handle rendering:**
```vue
<!-- Frontend component renders the JSON data -->
<template>
  <div class="asset-detail">
    <img :src="asset.thumbnail_url" :alt="asset.name" />
    <h1>{{ asset.name }}</h1>
    <p>{{ asset.description }}</p>
    <!-- Frontend handles all HTML generation -->
  </div>
</template>

<script>
export default {
  props: ['asset']  // Receives JSON from API
}
</script>
```

### Fix #5: Fix N+1 Queries (Query Optimization)

**Before (N+1 problem):**
```python
class DAMDocumentListSerializer(serializers.ModelSerializer):
    filename = serializers.SerializerMethodField()
    
    def get_filename(self, obj):
        # ❌ N+1 QUERY: Called once for each document!
        return obj.files.order_by('-timestamp').first().filename
```

**After (Optimized):**
```python
# Step 1: Use prefetch_related in ViewSet
class DAMDocumentListView(generics.ListAPIView):
    def get_queryset(self):
        return Document.objects.prefetch_related(
            'files'  # Load all files in one query
        )

# Step 2: Use annotate for aggregations
from django.db.models import Subquery, OuterRef

class DAMDocumentListView(generics.ListAPIView):
    def get_queryset(self):
        return Document.objects.annotate(
            latest_filename=Subquery(
                DocumentFile.objects.filter(
                    document=OuterRef('pk')
                ).order_by('-timestamp').values('filename')[:1]
            )
        )

# Step 3: Use annotated field in serializer
class DAMDocumentListSerializer(serializers.ModelSerializer):
    filename = serializers.CharField(source='latest_filename', read_only=True)
    
    class Meta:
        model = Document
        fields = ['id', 'label', 'filename', 'size', 'date_added']
```

**Verification:**
```python
# Test N+1 fix
def test_no_n_plus_one():
    with django.test.utils.CaptureQueriesContext(connection) as ctx:
        response = client.get('/api/v4/dam/documents/')
        # ✅ Should be ~3-5 queries total, NOT 1+N
        assert len(ctx) < 10
```

---

## 📋 ДЕТАЛЬНЫЙ ПЛАН ПО ФАЗАМ

### PHASE 0: API Critical Fixes (Week 1)

**Duration:** 5-7 дней  
**Team:** 1-2 backend developer  
**Daily standup:** 15 min  
**Deliverables:** ✅ All 5 critical fixes complete, tested, deployed to staging

**Tasks Breakdown:**

**Day 1: Analysis & Planning**
```
[ ] Review code review report (code-review-report.md)
[ ] Identify all affected endpoints
[ ] Create detailed fix specification
[ ] Setup staging environment for testing
[ ] Create branch: feature/critical-api-fixes-phase0
```

**Days 2-3: Authentication & Validation Fixes**
```
[ ] Fix DAMDocumentDetailView (add auth + serializer)
[ ] Add validation serializers to custom actions
[ ] Add Rate Limiting decorator
[ ] Write unit tests for each fix
[ ] Code review (peer)
```

**Days 4-5: Pagination & Query Optimization**
```
[ ] Add pagination to list endpoints
[ ] Fix N+1 queries (prefetch_related, annotate)
[ ] Remove HTML from responses (JSON only)
[ ] Performance test (django-extensions shell_plus)
[ ] Load test (100+ concurrent requests)
```

**Days 6-7: Testing & Deployment**
```
[ ] Integration tests (all endpoints)
[ ] Backward compatibility check
[ ] Documentation update
[ ] Deploy to staging
[ ] Final verification
```

**Quality Gates:**
- [ ] All tests pass (>95% coverage)
- [ ] Lighthouse API audit: 90+
- [ ] No security warnings (bandit)
- [ ] No linting errors (flake8, black)
- [ ] Performance: <500ms per endpoint (p95)

---

### PHASE 1: Foundation & MVP (Weeks 2-4)

**Duration:** 3 weeks  
**Team:** 2 frontend developers, 1 backend for ongoing support  
**Daily standup:** 15 min  
**Weekly demo:** Friday 2 PM  

#### Week 2: Project Setup & Components

**Frontend Setup:**
```bash
# Setup new Vue project
pnpm create vite dam-frontend --template vue-ts
cd dam-frontend

# Install dependencies
pnpm install vite@latest tailwindcss@latest
pnpm install typescript vue-router pinia axios
pnpm install @headlessui/vue @heroicons/vue
pnpm install vitest @testing-library/vue playwright

# Setup eslint & prettier
pnpm install -D eslint prettier eslint-plugin-vue

# Create structure
mkdir src/{components,pages,stores,services,types,utils}
mkdir src/styles
```

**Tailwind Configuration:**
```typescript
// tailwind.config.ts
export default {
  content: ['./src/**/*.{vue,js,ts}'],
  theme: {
    extend: {
      colors: {
        'dam-primary': 'var(--color-primary)',
        'dam-secondary': 'var(--color-secondary)',
      },
      spacing: {
        'header': '64px',
        'sidebar': '280px',
      }
    }
  },
  plugins: [require('@tailwindcss/forms')],
  darkMode: 'class',
}
```

**Component Library Setup (Storybook):**
```bash
# Initialize Storybook
pnpm exec storybook@latest init --type vue

# Example story
src/components/Button/Button.stories.ts
```

**Deliverables Week 2:**
- [ ] Project initialized with correct structure
- [ ] Tailwind configured + dark mode working
- [ ] ESLint/Prettier setup complete
- [ ] Storybook with 5+ components documented
- [ ] First PR review complete

**Components to create:**
1. Button (primary, secondary, danger, outline)
2. Input (text, email, password, number)
3. Select (dropdown with options)
4. Modal (reusable modal wrapper)
5. Card (content container)

---

#### Week 3: Core Features - Gallery & API

**Gallery MVP:**
```typescript
// GalleryView component
- Grid layout (4 columns, responsive)
- Lazy loading images
- Asset cards with hover actions
- Simple pagination (Next/Previous)
- Loading states
- Error handling
```

**API Integration:**
```typescript
// API Service
- GET /api/v4/dam/assets/ → fetch with pagination
- Structured response handling (count, next, previous, results)
- Error middleware (catch 401, 403, 500)
- CSRF token handling
```

**Store Setup:**
```typescript
// Pinia stores
assetStore: {
  assets: Asset[]
  totalCount: number
  currentPage: number
  pageSize: number
  isLoading: boolean
  error: string | null
  
  actions: {
    fetchAssets(page, pageSize)
    nextPage()
    previousPage()
    setPageSize(size)
  }
}
```

**Tests:**
```typescript
// Unit tests (Vitest)
- GalleryView renders correct columns
- Pagination buttons work
- API integration works
- Error states display properly

// E2E tests (Playwright)
- Load page → see 50 assets
- Click next → load page 2
- Click image → detail view
```

**Deliverables Week 3:**
- [ ] GalleryView component working with API
- [ ] Pagination functional
- [ ] 20+ unit tests passing
- [ ] 10+ E2E tests passing
- [ ] Lighthouse score 80+

---

#### Week 4: Search & Detail Page

**Search Component:**
```typescript
// SearchBar + instant results
- Input field (with Ctrl+K focus)
- Instant results dropdown (limit 8)
- Result items with thumbnail
- Debounce (300ms)
- Keyboard navigation
```

**Asset Detail Page:**
```typescript
// AssetDetailPage
- Large image preview
- Metadata panel (right sidebar)
- EXIF data display
- Comments thread (if available)
- Related assets (if available)
- Download button
- Share button
```

**Deliverables Week 4:**
- [ ] Search working with instant results
- [ ] Detail page with preview
- [ ] Metadata panel functional
- [ ] All components styled + responsive
- [ ] Phase 1 MVP ready for UAT

**Phase 1 Completion Checklist:**
- [ ] Gallery loads 50+ assets
- [ ] Search returns instant results
- [ ] Detail view works
- [ ] Pagination works
- [ ] No API errors
- [ ] Lighthouse 85+
- [ ] Mobile responsive
- [ ] 100+ tests passing
- [ ] Zero known bugs

---

### PHASE 2: DAM Features (Weeks 5-8)

#### Week 5: Filters & Advanced Search

**Faceted Filters:**
```typescript
// FiltersPanel component
- Type filter (checkbox list)
- Date range filter
- Size filter
- Tags filter (autocomplete)
- Custom metadata filters
- Apply/Reset buttons
```

**Advanced Search:**
```typescript
// API: POST /api/v4/dam/assets/search/
{
  q: "campaign AND hero",
  filters: {
    type: ["image"],
    tags: ["hero", "social"],
    date_range: ["2025-01-01", "2025-12-31"]
  },
  sort: "relevance",
  limit: 50,
  offset: 0
}

Response:
{
  count: 156,
  results: [...],
  facets: {
    type: {image: 145, video: 11},
    tags: {hero: 89, social: 76}
  }
}
```

**Deliverables Week 5:**
- [ ] Filters component UI complete
- [ ] API integration working
- [ ] Faceted search working
- [ ] 30+ filter tests passing
- [ ] UX testing with users

---

#### Week 6: Bulk Operations

**Bulk Select & Actions:**
```typescript
// BulkActions toolbar
- Checkbox to select all
- Counter ("123 selected")
- Bulk tag button
- Bulk move button
- Bulk delete button
- Bulk download button
- Bulk share button
```

**Modal for each operation:**
```typescript
// BulkTagModal
- Tag input (autocomplete)
- Operation selector (add/remove/replace)
- Confirm button
- Progress indicator
```

**Deliverables Week 6:**
- [ ] Bulk selection UI working
- [ ] All bulk operation modals
- [ ] API integration (POST /api/v4/dam/assets/bulk/)
- [ ] Progress tracking
- [ ] Error handling (partial failures)
- [ ] 20+ bulk operation tests

---

#### Week 7: Collaboration Features

**Comments System:**
```typescript
// CommentsThread component
- Comment display
- Add comment form
- Replies (nested)
- @mentions
- Timestamps

// API: POST /api/v4/dam/assets/{id}/comments/
```

**Version History:**
```typescript
// VersionHistory component
- List of versions
- Download each version
- Restore to version (if permission)

// API: GET /api/v4/dam/assets/{id}/versions/
```

**Deliverables Week 7:**
- [ ] Comments system working
- [ ] Version history display
- [ ] Real-time updates (WebSocket stub)
- [ ] 25+ collaboration tests

---

#### Week 8: Distribution Module

**Publication Management:**
```typescript
// DistributionPage
- List of publications
- Create publication button
- Publication cards
- Edit/delete/preview actions
- Analytics display
```

**Create Publication Workflow:**
```typescript
// Step 1: Select assets
// Step 2: Configure channels
// Step 3: Set schedule & permissions
// Step 4: Preview & publish
```

**Deliverables Week 8:**
- [ ] Publication list page
- [ ] Create publication workflow
- [ ] Edit publication
- [ ] Delete confirmation
- [ ] Analytics display
- [ ] Phase 2 complete

**Phase 2 Completion:**
- [ ] All DAM features working
- [ ] All Distribution features working
- [ ] 200+ tests passing
- [ ] Lighthouse 88+
- [ ] Ready for UAT round 2

---

### PHASE 3: Polish & Launch (Weeks 9-12)

#### Week 9: Performance Optimization

**Code Splitting:**
```typescript
// Route-based code splitting
const routes = [
  {
    path: '/dam',
    component: () => import('@/pages/DAMPage.vue')  // Lazy load
  },
  {
    path: '/distribution',
    component: () => import('@/pages/DistributionPage.vue')
  }
]
```

**Image Optimization:**
```typescript
// Lazy loading images
<img 
  v-lazy="asset.thumbnail_url"
  :alt="asset.name"
  loading="lazy"
/>

// WebP with fallback
<picture>
  <source srcset="image.webp" type="image/webp" />
  <img src="image.jpg" alt="..." />
</picture>
```

**Virtual Scrolling:**
```typescript
// For large lists
import VirtualList from 'vue-virtual-scroll-list'

<VirtualList :items="assets" :item-size="320">
  <template #default="{ item }">
    <AssetCard :asset="item" />
  </template>
</VirtualList>
```

**Lighthouse Targets:**
- Performance: 90+
- Accessibility: 95+
- Best Practices: 95+
- SEO: 90+

**Deliverables Week 9:**
- [ ] Code splitting working
- [ ] Image optimization complete
- [ ] Virtual scrolling for large lists
- [ ] Lighthouse 90+ on all metrics

---

#### Week 10: Mobile & Accessibility

**Responsive Design:**
```typescript
// Mobile-first breakpoints
const breakpoints = {
  sm: '640px',    // Mobile
  md: '768px',    // Tablet
  lg: '1024px',   // Desktop
  xl: '1280px'    // Large desktop
}

// Tailwind responsive classes
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4">
```

**Accessibility Audit:**
```typescript
// WCAG 2.1 AA compliance
- Color contrast: 4.5:1
- Focus indicators: visible
- Keyboard navigation: full support
- ARIA labels: semantic
- Screen reader: tested with NVDA

// Test with axe-core
import { axe, toHaveNoViolations } from 'jest-axe'
expect(await axe(container)).toHaveNoViolations()
```

**Deliverables Week 10:**
- [ ] Mobile responsive
- [ ] Accessibility audit passed
- [ ] Touch targets 44px+
- [ ] WCAG 2.1 AA compliant
- [ ] Screen reader tested

---

#### Week 11: UAT & Feature Parity

**User Acceptance Testing:**
```
- Invite 5-10 power users
- Test all DAM features
- Test all Distribution features
- Gather feedback
- Fix critical issues
```

**Feature Parity Check:**
```
Old UI:         New UI:
- Gallery ✅    ✅ Gallery (better)
- Search ✅     ✅ Search (better)
- Detail ✅     ✅ Detail (better)
- Filters ✅    ✅ Filters (better)
- Bulk ops ✅   ✅ Bulk ops (better)
```

**Deliverables Week 11:**
- [ ] UAT passed (>95% pass rate)
- [ ] All critical bugs fixed
- [ ] Feature parity confirmed
- [ ] User documentation ready
- [ ] Training materials prepared

---

#### Week 12: Launch Preparation

**Pre-Launch Checklist:**
```
Security:
  [ ] Penetration testing passed
  [ ] OWASP Top 10 check
  [ ] Secrets not in code
  [ ] SSL certificate valid
  [ ] API rate limiting working

Performance:
  [ ] Load testing (1000 concurrent users)
  [ ] Lighthouse 90+
  [ ] API response <500ms (p95)
  [ ] Uptime SLA 99.9%

Operations:
  [ ] Runbook created
  [ ] Monitoring setup (Sentry, DataDog)
  [ ] Logging configured
  [ ] Rollback procedure documented
  [ ] On-call process established

Documentation:
  [ ] User guide written
  [ ] Admin guide written
  [ ] API documentation complete
  [ ] Troubleshooting guide
  [ ] FAQ prepared

Training:
  [ ] User training sessions (2-3)
  [ ] Admin training sessions (1-2)
  [ ] Videos recorded
  [ ] Cheat sheets created
```

**Launch Day:**
```
Timeline:
09:00 - Final smoke test (staging)
09:30 - Notify users (maintenance window)
10:00 - Deploy to production
10:15 - Smoke test (production)
10:30 - Enable new UI for 10% users
11:00 - Monitor metrics (no issues? expand to 50%)
12:00 - Full rollout to all users
13:00 - Open support channel
```

**Deliverables Week 12:**
- [ ] Pre-launch checklist 100% complete
- [ ] Deployment executed successfully
- [ ] Monitoring shows healthy metrics
- [ ] Zero critical production issues
- [ ] User support operational

---

## 🤖 ПОШАГОВЫЕ АЛГОРИТМЫ ДЛЯ CURSOR AI

### Algorithm 1: Create React/Vue Component

**Prompt Template:**
```
I'm building a modern DAM frontend in Vue 3 + TypeScript + Tailwind CSS.

Create a reusable component called "GalleryView" that:
1. Displays assets in a responsive grid (4-6 columns)
2. Shows loading states while fetching
3. Handles pagination (Next/Previous buttons)
4. Shows asset cards with image, name, size, date
5. Supports bulk selection (checkbox)
6. Lazy loads images
7. Shows error messages

Requirements:
- Use Vue 3 Composition API
- TypeScript with strict mode
- Tailwind CSS for styling
- Props: assets[], isLoading, currentPage, pageSize, totalPages
- Emits: @next-page, @previous-page, @select-asset, @bulk-select
- 100% test coverage with Vitest

File structure:
src/components/Gallery/GalleryView.vue
src/components/Gallery/AssetCard.vue
src/components/Gallery/Pagination.vue

Include:
- Component code
- Unit tests (Vitest)
- Storybook story
- TypeScript interfaces
```

**Expected Output:**
- 3 component files (Vue)
- 1 test file (spec.ts)
- 1 Storybook story
- All with proper TypeScript types

---

### Algorithm 2: Implement API Integration

**Prompt Template:**
```
Create an API service for DAM frontend that:
1. Handles GET /api/v4/dam/assets/ (list with pagination)
2. Handles POST /api/v4/dam/assets/search/ (search with filters)
3. Implements request interceptors for CSRF token
4. Implements response interceptors for error handling
5. Handles 401 (redirect to login) and 403 (show error)
6. Retries failed requests (up to 3 times)
7. Caches responses in memory (with TTL)

Requirements:
- Use Axios with TypeScript
- Structured error responses
- Automatic token refresh
- Request/response logging
- 100% test coverage

File structure:
src/services/apiService.ts
src/services/assetService.ts
src/types/api.ts
src/services/__tests__/apiService.spec.ts

Include:
- API service code
- Interceptor setup
- Error handling
- Unit tests
- Types/interfaces
```

---

### Algorithm 3: Setup State Management

**Prompt Template:**
```
Setup Pinia state management for DAM frontend with:
1. assetStore (gallery data)
   - assets[]
   - selectedAssets[]
   - pagination {currentPage, pageSize, totalPages}
   - filters {type, date, tags}
   - loading, error states
   
2. searchStore (search results)
   - query: string
   - results[]
   - facets {}
   - recentSearches[]
   
3. uiStore (UI state)
   - sidebarOpen: boolean
   - activeModal: string | null
   - theme: 'light' | 'dark'
   - notifications[]

Requirements:
- Full TypeScript typing
- Actions for all state changes
- Computed properties for derived state
- Persistence to localStorage (preferences only)
- Plugin for logging/debugging
- 100% test coverage

File structure:
src/stores/assetStore.ts
src/stores/searchStore.ts
src/stores/uiStore.ts
src/stores/__tests__/

Include:
- Store code with actions
- Computed properties
- Persistence layer
- Unit tests
```

---

### Algorithm 4: Create API Endpoints (Backend)

**Prompt Template:**
```
I'm fixing Django REST API for DAM frontend.

Create these endpoints following REST best practices:
1. GET /api/v4/dam/assets/
   - Query params: page, page_size, sort, type, tags
   - Response: {count, next, previous, results}
   - Pagination: 50 default, max 100
   - Optimization: prefetch_related('files', 'ai_analysis')

2. POST /api/v4/dam/assets/search/
   - Body: {q, filters, sort, limit, offset}
   - Response: {count, results, facets}
   - Full-text search on title + description
   - Facets: {type: {...}, tags: {...}}

3. POST /api/v4/dam/assets/bulk/
   - Body: {ids, action, data}
   - Actions: add_tags, move, delete, export
   - Max 500 items per request (rate limited)
   - Response: {success, updated, failed}

Requirements:
- Use DRF serializers for validation
- Add permission_classes checks
- Add rate limiting decorators
- Optimize queries (no N+1)
- Return JSON only (no HTML)
- Full error handling
- 100% test coverage

Include:
- ViewSet/View code
- Serializers
- Permissions
- Tests (unit + integration)
- API documentation
```

---

## 🐧 DEVOPS & UBUNTU/WSL SETUP

### Development Environment Setup (Ubuntu/WSL)

**System Requirements:**
```bash
# System info
uname -a  # Should show: Linux ... x86_64 GNU/Linux

# Docker (required)
docker --version  # v20+
docker-compose --version  # v2+

# Node.js & pnpm
node --version  # v18+
pnpm --version  # v8+

# Python & Django
python3 --version  # 3.10+
pip --version

# PostgreSQL client
psql --version  # 12+
```

**Project Setup Script:**
```bash
#!/bin/bash
# setup-dev-environment.sh

set -e

echo "🚀 Setting up DAM development environment..."

# Create project directories
mkdir -p ~/projects/dam-system
cd ~/projects/dam-system

# Clone repos (or create new)
git clone <backend-repo> backend
git clone <frontend-repo> frontend

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # Create admin user

# Create .env for development
cat > .env << EOF
DEBUG=True
SECRET_KEY=dev-key-change-in-production
DATABASE_URL=postgresql://user:pass@localhost/dam_db
REDIS_URL=redis://localhost:6379/0
CORS_ALLOWED_ORIGINS=http://localhost:5173
EOF

# Frontend setup
cd ../frontend
pnpm install

# Create .env for frontend
cat > .env.local << EOF
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
EOF

echo "✅ Setup complete!"
echo "Backend: cd backend && python manage.py runserver"
echo "Frontend: cd frontend && pnpm dev"
```

**Docker Compose for Local Development:**
```yaml
# docker-compose.yml
version: '3.9'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: dam_db
      POSTGRES_USER: dam_user
      POSTGRES_PASSWORD: dam_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://dam_user:dam_password@db:5432/dam_db
      - REDIS_URL=redis://redis:6379/0
      - DEBUG=True
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    command: pnpm dev
    volumes:
      - ./frontend:/app
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000/api

volumes:
  postgres_data:
```

**Quick Start Script (WSL/Ubuntu):**
```bash
# start-dev.sh
#!/bin/bash

# Start Docker services
docker-compose up -d

# Wait for services to be ready
sleep 5

# Open browser
if command -v wslview &> /dev/null; then
  wslview http://localhost:5173  # WSL
elif command -v xdg-open &> /dev/null; then
  xdg-open http://localhost:5173  # Linux
fi

# Show URLs
echo ""
echo "🎉 DAM System development environment started!"
echo ""
echo "Frontend: http://localhost:5173"
echo "Backend:  http://localhost:8000"
echo "Admin:    http://localhost:8000/admin"
echo "API Docs: http://localhost:8000/api/v4/"
echo ""
echo "Stop with: docker-compose down"
```

### CI/CD Pipeline (GitHub Actions)

**Frontend Pipeline:** `.github/workflows/frontend.yml`
```yaml
name: Frontend CI/CD

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'pnpm'
      
      - name: Install dependencies
        run: cd frontend && pnpm install
      
      - name: Lint
        run: cd frontend && pnpm lint
      
      - name: Unit tests
        run: cd frontend && pnpm test
      
      - name: Build
        run: cd frontend && pnpm build
      
      - name: E2E tests
        run: cd frontend && pnpm test:e2e

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to production
        run: |
          # Deploy script here
          echo "Deploying frontend..."
```

**Backend Pipeline:** `.github/workflows/backend.yml`
```yaml
name: Backend CI/CD

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Lint (flake8)
        run: flake8 mayan/
      
      - name: Format check (black)
        run: black --check mayan/
      
      - name: Security (bandit)
        run: bandit -r mayan/ -ll
      
      - name: Run tests
        run: pytest tests/ --cov=mayan --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to production
        run: |
          # Deploy script here
          echo "Deploying backend..."
```

---

## 📈 МЕТРИКИ УСПЕХА

### KPI Tracking

```yaml
User Adoption:
  Target: 95% within 30 days
  Metric: % of active users using new UI
  Baseline: 0%
  Weekly tracking: Thursdays 10 AM

Performance:
  Lighthouse Score: 90+ (all metrics)
  Page Load: < 1.5s (was 2.7s)
  API Response: < 500ms (p95)
  Uptime: 99.9%

User Satisfaction:
  NPS Score: > 40 (was -15)
  Feature Satisfaction: 4.2+/5 (was 2.7)
  Support Tickets: -40% reduction

Security:
  Critical Vulnerabilities: 0 (was 5)
  OWASP Top 10: All fixed
  Penetration Test: Pass

Quality:
  Test Coverage: > 85%
  Bug Escape Rate: < 2%
  Code Review: 100% reviewed
```

### Monitoring & Alerts

**Sentry Setup:**
```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,  # 10% of transactions
    send_default_pii=False
)
```

**Frontend Error Tracking:**
```typescript
// src/utils/errorTracking.ts
import * as Sentry from "@sentry/vue"

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  tracesSampleRate: 0.1,
  environment: import.meta.env.MODE,
})

export const captureException = (error: Error) => {
  Sentry.captureException(error)
}
```

**DataDog Monitoring:**
```yaml
# Infrastructure metrics
- API response time (p50, p95, p99)
- Database query time
- Redis cache hits/misses
- Active user sessions
- Error rate (5xx responses)
- Rate limiting rejections
```

---

## 🗺️ ROADMAP

### Timeline Overview

```
Week 1  │ Phase 0: API Critical Fixes
Week 2  │ Phase 1: Foundation & Setup (part 1)
Week 3  │ Phase 1: Gallery MVP (part 2)
Week 4  │ Phase 1: Search & Detail (part 3)
────────┼──────────────────────────────────
Week 5  │ Phase 2: Filters & Advanced Search
Week 6  │ Phase 2: Bulk Operations
Week 7  │ Phase 2: Collaboration (comments, versions)
Week 8  │ Phase 2: Distribution Module
────────┼──────────────────────────────────
Week 9  │ Phase 3: Performance & Optimization
Week 10 │ Phase 3: Mobile & Accessibility
Week 11 │ Phase 3: UAT & Feature Parity
Week 12 │ Phase 3: Launch Preparation & Go-Live
```

### Milestone Dependencies

```
Milestone 1: Phase 0 Complete (API Fixes)
  └─ Blocks: All frontend development

Milestone 2: Phase 1 MVP (Gallery + Search + Detail)
  └─ Blocks: Phase 2 start
  └─ Input: User feedback for Phase 2 scope

Milestone 3: Phase 2 Complete (All DAM features)
  └─ Blocks: Phase 3 start
  └─ Input: Performance baseline for optimization

Milestone 4: Phase 3 Complete & Launch
  └─ Blocks: Production deployment
  └─ Input: UAT results, training materials
```

---

## 📎 APPENDIX: CURSOR PROMPTS

### Prompt #1: Initial Project Setup

```
I'm building a modern DAM (Digital Asset Management) system frontend 
with Vue 3, TypeScript, and Tailwind CSS.

Context:
- Backend: Django REST API at http://localhost:8000/api
- Architecture: Component-based with Pinia state management
- Build tool: Vite
- Target users: 1000+ concurrent users managing 100k+ assets

Project requirements:
1. Create Vue 3 + TypeScript project structure
2. Setup Tailwind CSS with dark mode
3. Configure routing (Vue Router)
4. Setup state management (Pinia)
5. Configure HTTP client (Axios) with interceptors
6. Setup testing (Vitest + Playwright)
7. Setup development tools (ESLint, Prettier, Storybook)

Deliverables:
- Complete project structure
- Configuration files (tsconfig, vite.config, tailwind.config)
- First 5 reusable components (Button, Input, Modal, Card, Badge)
- Storybook stories for components
- CI/CD pipeline setup (GitHub Actions)
- README with setup instructions

Include:
- TypeScript strict mode
- 100% test coverage for utilities
- Performance optimization tips
- Error handling patterns
```

### Prompt #2: API Integration

```
Create API service for DAM frontend that integrates with Django REST API.

API Endpoints:
1. GET /api/v4/dam/assets/?page=1&page_size=50
   Response: {count: number, next: url, previous: url, results: Asset[]}

2. POST /api/v4/dam/assets/search/
   Body: {q, filters, sort, limit, offset}
   Response: {count, results, facets}

3. POST /api/v4/dam/assets/bulk/
   Body: {ids: number[], action, data}
   Response: {success, updated, failed}

4. GET /api/v4/dam/assets/{id}/
   Response: Asset with metadata, comments, versions

Requirements:
- Axios with TypeScript
- Request/Response interceptors for:
  * CSRF token handling
  * Error handling (401, 403, 500)
  * Request logging
  * Auto-retry on network errors
- Response caching (in-memory, 5 min TTL)
- Structured error handling
- 100% test coverage

Deliverables:
- src/services/apiService.ts (base HTTP client)
- src/services/assetService.ts (DAM specific methods)
- src/types/api.ts (TypeScript interfaces)
- src/services/__tests__/*.spec.ts (unit tests)
- Error handling utilities
```

### Prompt #3: Gallery Component

```
Create GalleryView component for displaying DAM assets with:
1. Responsive grid (4-6 columns, auto-responsive)
2. Asset cards with:
   - Lazy-loaded thumbnail
   - Asset name, size, upload date
   - Hover quick-actions (Preview, Share, Download)
   - Checkbox for bulk selection
3. Pagination (limit: 50, max: 100)
4. Loading states with skeleton
5. Error states with retry button
6. Virtual scrolling for 1000+ items
7. Selection counter and clear button

Features:
- Props: assets[], isLoading, error, pagination
- Emits: @fetch-page, @select-asset, @bulk-select
- Keyboard navigation (Tab, Space to select)
- Accessible (WCAG 2.1 AA)
- Mobile responsive (touch-friendly 44px+ targets)

Include:
- Component code (Vue 3 Composition API)
- 3 sub-components (AssetCard, Pagination, SelectionBar)
- Storybook story with multiple states
- Unit tests (Vitest) - 90%+ coverage
- E2E tests (Playwright) - 3 main flows
```

### Prompt #4: State Management

```
Setup Pinia stores for DAM frontend with:

1. assetStore:
   - State: assets[], selectedAssets[], pagination, filters, loading, error
   - Actions: fetchAssets, selectAsset, selectAll, clearSelection, setFilters
   - Getters: currentPageAssets, selectedCount, hasNextPage

2. searchStore:
   - State: query, results, facets, recentSearches, isLoading
   - Actions: search, clearSearch, addRecent
   - Getters: facetsSummary, resultCount

3. uiStore:
   - State: sidebarOpen, activeModal, theme, notifications
   - Actions: toggleSidebar, openModal, closeModal, setTheme
   - Getters: isMobile, isDarkMode

Requirements:
- Full TypeScript typing
- Persistence to localStorage (except real-time state)
- DevTools plugin for debugging
- Performance optimized (no unnecessary re-renders)
- 100% test coverage

Include:
- Store code with all actions
- Persistence layer
- Plugin system
- Unit tests
- Documentation
```

### Prompt #5: API Critical Fixes (Backend)

```
I'm a Django REST Framework expert fixing critical API issues.

Your task: Apply these 5 critical security/performance fixes:

1. FIX: DAMDocumentDetailView authentication
   - Add: permission_classes = (IsAuthenticated,)
   - Add: mayan_object_permissions check
   - Return: JSON only (no HTML)
   
2. FIX: Input validation for all custom actions
   - Create serializers for @action methods
   - Use: serializer.is_valid(raise_exception=True)
   - Validate: document_ids, action types, data structures

3. FIX: Add pagination to list endpoints
   - Add: pagination_class = StandardPagination
   - Limit: 50 default, max 100
   - Format: {count, next, previous, results}

4. FIX: Query optimization (no N+1)
   - Use: prefetch_related, select_related, annotate
   - Test: with django.test.utils.CaptureQueriesContext

5. FIX: Structured error responses
   - Format: {error: {code, message, details}}
   - All exceptions caught and logged
   - Stack traces only in DEBUG mode

Files to modify:
- mayan/apps/dam/api_views.py
- mayan/apps/dam/serializers.py
- mayan/apps/dam/viewsets.py
- mayan/settings.py (REST_FRAMEWORK config)

Include:
- Fixed view code
- New serializers
- Migration script
- Before/after tests
- Performance comparison
```

---

## 🎯 ЗАКЛЮЧЕНИЕ

### Что получится в результате

✅ **Современная DAM система**, соответствующая стандартам Bynder/Canto  
✅ **Security**: 0 критических уязвимостей (фикс 5 issues в Phase 0)  
✅ **Performance**: Lighthouse 90+, API <500ms  
✅ **User adoption**: 95% within 30 days (from 45%)  
✅ **Developer experience**: Type-safe, well-tested, maintainable  
✅ **Operations ready**: Monitoring, logging, CI/CD  

### Investment Summary

| Component | Time | People | Cost |
|-----------|------|--------|------|
| Phase 0 (API fixes) | 1 week | 1-2 backend | 2500 EUR |
| Phase 1 (Foundation) | 3 weeks | 2 frontend | 6000 EUR |
| Phase 2 (Features) | 4 weeks | 2 frontend | 8000 EUR |
| Phase 3 (Polish) | 4 weeks | 2 frontend + QA | 10000 EUR |
| **TOTAL** | **12 weeks** | **4-5 people** | **~26,500 EUR** |

### Expected Benefits

| Metric | Before | After | ROI |
|--------|--------|-------|-----|
| User adoption | 45% | 95% | +110% |
| Page load time | 2.7s | <1.5s | 45% faster |
| Lighthouse score | 62 | 92+ | +47% |
| Security issues | 5 critical | 0 | 100% fix |
| Support tickets | 100/month | 60/month | -40% |
| Development velocity | Low | High (Cursor-aided) | 3x faster iteration |

### Next Steps (Action Items)

1. **Week 1:**
   - ✅ Approve Phase 0 plan
   - ✅ Assign backend team for API fixes
   - ✅ Provision infrastructure (DB, Redis, Docker)

2. **Week 2-4:**
   - ✅ Frontend team starts Phase 1
   - ✅ Setup monitoring & CI/CD
   - ✅ Begin UAT recruitment

3. **Week 5-8:**
   - ✅ Complete Phase 2 features
   - ✅ User feedback sessions
   - ✅ Performance tuning

4. **Week 9-12:**
   - ✅ Final polish & launch
   - ✅ Training & documentation
   - ✅ Go-live deployment

---

**Документ создан:** 25 Ноября 2025  
**Версия:** 3.0 (Production-Ready)  
**Статус:** ✅ УТВЕРЖДЕНО К РАЗВЕРТЫВАНИЮ  

**Вопросы? Контакт: CDTO / Cursor AI Team**

Документ готов к использованию с Cursor AI для разработки.
