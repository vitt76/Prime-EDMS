# Master Frontend Documentation — DAM System

**Дата анализа:** 03 декабря 2025  
**Версия:** 2.0 (Deep Architecture Audit)  
**Автор:** Senior Frontend Architect & Technical Writer (Vue 3 / TypeScript)

---

## 📋 Содержание

1. [Component Architecture Map](#1-component-architecture-map)
2. [Data & State Logic (Pinia Analysis)](#2-data--state-logic-pinia-analysis)
3. [API Surface & Integration Points](#3-api-surface--integration-points)
4. [UI/UX & Code Quality Audit](#4-uiux--code-quality-audit)
5. [Архитектурный обзор](#5-архитектурный-обзор)
6. [Модель данных (Core Entities)](#6-модель-данных-core-entities)
7. [Критические проблемы и рекомендации](#7-критические-проблемы-и-рекомендации)

---

## 1. Component Architecture Map

### 1.1 Pages Overview (Views)

| Page | Location | State Dependencies | Key Actions | Mock Status |
|------|----------|-------------------|-------------|-------------|
| **LoginPage** | `pages/LoginPage.vue` | `authStore` | `login(email, password)` | 🔴 **MOCK** — Backend Ready |
| **Login2FAPage** | `pages/Login2FAPage.vue` | `authStore` | `verifyTwoFactor()`, `regenerateBackupCodes()` | 🔴 **MOCK** — UI Ready |
| **DashboardPage** | `pages/DashboardPage.vue` | `dashboardStore` | `fetchDashboardStats()`, `refresh()` | 🟡 **MOCK** — DEV fallback |
| **GalleryView** | `pages/GalleryView.vue` | `galleryStore`, `uiStore` | `loadItems()`, `setFilters()`, `selectItem()`, `bulkDelete()` | 🟢 **REAL** via assetService |
| **DAMGalleryPage** | `pages/DAMGalleryPage.vue` | `assetStore` | `fetchAssets()`, `setFilters()` | 🟡 **MOCK** — localStorage flag |
| **AssetDetailPage** | `pages/AssetDetailPage.vue` | `assetStore` | `getAssetById()`, `updateAsset()` | 🟡 **MOCK** — via assetService |
| **UploadPage** | `pages/UploadPage.vue` | `uploadWorkflowStore` | `uploadFiles()`, `saveMetadata()`, `assignToCollection()` | 🔴 **MOCK** — workflow steps |
| **DistributionPage** | `pages/DistributionPage.vue` | `distributionStore` | `fetchPublications()`, `createPublication()`, `deletePublication()` | 🟢 **REAL** via distributionService |
| **SettingsPage** | `pages/SettingsPage.vue` | `uiStore`, `authStore` | `setTheme()`, `changePassword()` | 🟡 **PARTIAL** |
| **CollectionsPage** | `pages/CollectionsPage.vue` | `collectionsStore` | `fetchCollections()`, `createCollection()` | 🟢 **REAL** via collectionsService |
| **AdvancedSearchPage** | `pages/AdvancedSearchPage.vue` | `searchStore` | `executeSearch()`, `saveSearch()` | 🟢 **REAL** via searchStore |

### 1.2 Admin Pages

| Page | Location | State Dependencies | Key Actions | Mock Status |
|------|----------|-------------------|-------------|-------------|
| **AdminDashboard** | `pages/admin/AdminDashboard.vue` | `adminStore` | `refreshData()` | 🟡 **MOCK** — hardcoded stats |
| **AdminUsers** | `pages/admin/AdminUsers.vue` | `adminStore` | `fetchUsers()`, `inviteUser()`, `deleteUser()` | 🟡 **MOCK** — local `users` array |
| **AdminUserDetail** | `pages/admin/AdminUserDetail.vue` | `adminStore` | `getUserById()`, `updateUser()` | 🟡 **MOCK** |
| **AdminRoles** | `pages/admin/AdminRoles.vue` | `adminStore` | `fetchRoles()`, `createRole()` | 🟡 **MOCK** |
| **AdminMetadata** | `pages/admin/AdminMetadata.vue` | `adminStore` | `fetchSchemas()`, `createSchema()` | 🟡 **MOCK** |
| **AdminWorkflows** | `pages/admin/AdminWorkflows.vue` | `adminStore` | `fetchWorkflows()`, `createWorkflow()` | 🟡 **MOCK** |
| **AdminSources** | `pages/admin/AdminSources.vue` | `adminStore` | `fetchSources()` | 🟡 **MOCK** |
| **AdminAILogs** | `pages/admin/AdminAILogs.vue` | `adminStore` | `fetchAILogs()` | 🟡 **MOCK** |
| **AdminHealth** | `pages/admin/AdminHealth.vue` | `adminStore` | `checkHealth()` | 🟡 **MOCK** |
| **AdminStorage** | `pages/admin/AdminStorage.vue` | `adminStore` | `fetchStorageStats()` | 🟡 **MOCK** |
| **WorkflowDesignerPage** | `pages/admin/WorkflowDesignerPage.vue` | `authStore`, `adminStore`, `notificationStore` | `createWorkflow()`, `saveWorkflow()` | 🟡 **MOCK** |

### 1.3 Collection Pages

| Page | Location | State Dependencies | Key Actions | Mock Status |
|------|----------|-------------------|-------------|-------------|
| **FavoritesPage** | `pages/collections/FavoritesPage.vue` | `notificationStore` | `loadFavorites()` | 🔴 **MOCK** — mocks/assets.ts |
| **MyUploadsPage** | `pages/collections/MyUploadsPage.vue` | `uiStore`, `notificationStore` | `loadMyUploads()` | 🔴 **MOCK** — mocks/assets.ts |
| **RecentPage** | `pages/collections/RecentPage.vue` | `notificationStore` | `loadRecentAssets()` | 🔴 **MOCK** — mocks/assets.ts |
| **SharedWithMePage** | `pages/collections/SharedWithMePage.vue` | `notificationStore` | `loadSharedAssets()` | 🔴 **MOCK** — mocks/assets.ts |

### 1.4 Mock Status Legend

| Symbol | Meaning |
|--------|---------|
| 🔴 **MOCK** | Page uses mock data from `mocks/` folder or hardcoded values |
| 🟡 **PARTIAL** | Page has mock fallback in DEV mode, but real API calls exist |
| 🟢 **REAL** | Page makes actual API calls via services (may fail if backend unavailable) |

---

## 2. Data & State Logic (Pinia Analysis)

### 2.1 Store Inventory

| Store | File | Persistence | Mock Status |
|-------|------|-------------|-------------|
| `authStore` | `stores/authStore.ts` | `['token', 'user', 'permissions']` | 🟢 Real API calls |
| `assetStore` | `stores/assetStore.ts` | `['filters', 'viewMode', 'sortBy', 'useMock']` | 🟡 `useMock` flag in localStorage |
| `galleryStore` | `stores/galleryStore.ts` | `['filters', 'searchQuery', 'sort', 'groupBy', ...]` | 🟢 Real API via assetService |
| `collectionsStore` | `stores/collectionsStore.ts` | `['expandedIds']` | 🟢 Real API calls |
| `distributionStore` | `stores/distributionStore.ts` | `false` | 🟢 Real API calls |
| `searchStore` | `stores/searchStore.ts` | `['recentSearches', 'savedSearches']` | 🟢 Real API calls |
| `uploadWorkflowStore` | `stores/uploadWorkflowStore.ts` | `['uploadedFiles', 'filesMetadata', ...]` | 🔴 Mock — no real upload |
| `dashboardStore` | `stores/dashboardStore.ts` | `false` | 🟡 Mock in DEV mode |
| `adminStore` | `stores/adminStore.ts` | `['users', 'schemas', 'workflows', ...]` | 🔴 Mock — stubbed actions |
| `uiStore` | `stores/uiStore.ts` | `['sidebarExpanded', 'theme']` | N/A — UI state only |
| `notificationStore` | `stores/notificationStore.ts` | `['notifications']` | N/A — UI state only |

### 2.2 State Tree Analysis

#### authStore State Tree

```typescript
// stores/authStore.ts
state: {
  user: User | null                    // Current logged-in user
  token: string | null                 // DRF Token (from localStorage)
  permissions: string[]                // User permissions array
  loading: boolean                     // Auth operation in progress
  error: string | null                 // Last error message
  twoFactorSetup: {                    // 2FA setup data
    secret: string
    qr_code_url: string
    backup_codes: string[]
  } | null
}

getters: {
  isAuthenticated: boolean             // token !== null
  isTwoFactorVerified: boolean         // TODO: Implement
  requiresTwoFactor: boolean           // user?.two_factor_enabled
  hasPermission(perm): boolean         // permissions.includes(perm)
  hasRole(role): boolean               // user?.role === role
}

actions: {
  login(username, password)            // 🟢 REAL → POST /api/v4/auth/token/obtain/
  logout()                             // 🟢 REAL → clears token + redirects
  checkAuth()                          // 🟢 REAL → GET /api/v4/user_management/users/current/
  verifyTwoFactor(code, method)        // 🔴 STUB → returns mock success
  regenerateBackupCodes()              // 🔴 STUB → returns mock codes
  initializeAuth()                     // 🟢 REAL → restores session from localStorage
}
```

#### assetStore State Tree

```typescript
// stores/assetStore.ts
state: {
  assets: Asset[]                      // Loaded assets
  currentAsset: Asset | null           // Selected asset for detail view
  totalCount: number                   // Total assets count
  loading: boolean                     // Loading state
  error: string | null                 // Error message
  filters: AssetFilters                // Active filters
  viewMode: 'grid' | 'list'            // View mode
  sortBy: string                       // Sort field
  page: number                         // Current page
  pageSize: number                     // Items per page
  selectedIds: Set<number>             // Selected asset IDs
  useMock: boolean                     // ⚠️ PERSISTED in localStorage!
}

actions: {
  fetchAssets(params?)                 // 🟡 CONDITIONAL → useMock ? mockAssets : API
  getAssetById(id)                     // 🟡 CONDITIONAL → useMock ? mockAsset : API
  updateAsset(id, data)                // 🟢 REAL → PUT /api/v4/documents/{id}/
  deleteAsset(id)                      // 🟢 REAL → DELETE /api/v4/documents/{id}/
  setFilters(filters)                  // Local state update
  clearSelection()                     // Local state update
}
```

**⚠️ CRITICAL ISSUE:** `useMock` is persisted in localStorage (`assetStore`). Even if `VITE_USE_MOCK_DATA=false`, the stored value overrides it. Must clear `localStorage.removeItem('assetStore')` to switch to real data.

#### galleryStore State Tree

```typescript
// stores/galleryStore.ts
state: {
  items: GalleryItem[]                 // Gallery items with visibility
  totalCount: number                   // Total items
  loadedPages: Set<number>             // Loaded page numbers
  pageSize: number                     // 100 (optimized for virtual scrolling)
  currentPage: number                  // Current page
  isLoading: boolean                   // Loading state
  hasMore: boolean                     // More items available
  filters: GalleryFilters              // Active filters
  searchQuery: string                  // Search query
  sort: GallerySort                    // Sort configuration
  groupBy: 'none' | 'type' | ...       // Grouping mode
  selectedItems: Set<string>           // Selected item IDs
  viewMode: 'grid' | 'list'            // View mode
  gridColumns: number                  // Grid columns (1-8)
  error: string | null                 // Error message
}

actions: {
  loadItems(page?)                     // 🟢 REAL → assetService.getAssets()
  loadMoreItems()                      // 🟢 REAL → loads next page
  setFilters(filters)                  // Reset + reload
  setSearchQuery(query)                // Debounced search
  selectItem(id, index)                // Selection management
  selectRange(start, end)              // Range selection
  selectAll() / deselectAll()          // Bulk selection
  initialize()                         // Initial load
}
```

#### collectionsStore State Tree

```typescript
// stores/collectionsStore.ts
state: {
  collections: Collection[]            // All collections
  collectionTree: CollectionTree[]     // Hierarchical structure
  selectedCollection: Collection | null
  specialCounts: Record<SpecialType, number>
  isLoading: boolean
  error: string | null
  expandedIds: Set<number>             // Expanded tree nodes
}

actions: {
  fetchCollections()                   // 🟢 REAL → collectionsService.getCollections()
  fetchSpecialCounts()                 // 🟢 REAL → collectionsService.getSpecialCounts()
  createCollection(name, parentId)     // 🟢 REAL → collectionsService.createCollection()
  updateCollection(id, data)           // 🟢 REAL → collectionsService.updateCollection()
  deleteCollection(id)                 // 🟢 REAL → collectionsService.deleteCollection()
  moveCollection(id, newParentId)      // 🟢 REAL → collectionsService.moveCollection()
  toggleFavorite(id)                   // 🟢 REAL → collectionsService.toggleFavorite()
}
```

#### distributionStore State Tree

```typescript
// stores/distributionStore.ts
state: {
  publications: Publication[]          // Publications list
  currentPublication: Publication | null
  isLoading: boolean
  error: string | null
  currentPage: number
  pageSize: number
  totalCount: number
}

actions: {
  fetchPublications(params?)           // 🟢 REAL → distributionService.getPublications()
  createPublication(data)              // 🟢 REAL → distributionService.createPublication()
  updatePublication(id, data)          // 🟢 REAL → distributionService.updatePublication()
  deletePublication(id)                // 🟢 REAL → distributionService.deletePublication()
  publishPublication(id)               // 🟢 REAL → distributionService.publishPublication()
  fetchShareLinks(pubId)               // 🟢 REAL → distributionService.getShareLinks()
  createShareLink(pubId, options)      // 🟢 REAL → distributionService.createShareLink()
}
```

### 2.3 Stubbed vs Real Actions

| Store | Action | Status | Notes |
|-------|--------|--------|-------|
| authStore | `login` | 🟢 REAL | POST /api/v4/auth/token/obtain/ |
| authStore | `checkAuth` | 🟢 REAL | GET /api/v4/user_management/users/current/ |
| authStore | `verifyTwoFactor` | 🔴 STUB | Returns mock `{ success: true }` |
| authStore | `regenerateBackupCodes` | 🔴 STUB | Returns mock codes array |
| assetStore | `fetchAssets` | 🟡 CONDITIONAL | Checks `useMock` flag |
| dashboardStore | `fetchDashboardStats` | 🟡 DEV MOCK | Uses mockStats in DEV mode |
| dashboardStore | `fetchActivityFeed` | 🟡 DEV MOCK | Uses mockActivity in DEV mode |
| dashboardStore | `fetchStorageMetrics` | 🟡 DEV MOCK | Uses mockStorage in DEV mode |
| adminStore | `fetchUsers` | 🔴 STUB | Returns local mock array |
| adminStore | `createWorkflow` | 🔴 STUB | Local push to workflows[] |
| uploadWorkflowStore | `uploadFiles` | 🔴 STUB | No real upload |
| uploadWorkflowStore | `saveMetadata` | 🔴 STUB | No API call |
| uploadWorkflowStore | `completeWorkflow` | 🔴 STUB | No API call |
| notificationStore | `connectWebSocket` | 🔴 STUB | TODO: Implement |

### 2.4 Frontend Types vs Backend (BACKEND_ANALYSIS.md) Divergence

| Frontend Type | Backend Model | Divergence |
|---------------|---------------|------------|
| `Asset.id: number` | `Document.id: number` | ✅ Match |
| `Asset.label: string` | `Document.label: string` | ✅ Match |
| `Asset.filename: string` | `DocumentFile.filename: string` | ⚠️ Different model |
| `Asset.mime_type: string` | `DocumentFile.mimetype: string` | ⚠️ Field name differs |
| `Asset.date_added: string` | `Document.datetime_created: datetime` | ⚠️ Field name differs |
| `Asset.thumbnail_url: string` | **Generated dynamically** | ⚠️ Not stored in DB |
| `Asset.preview_url: string` | **Generated dynamically** | ⚠️ Not stored in DB |
| `Asset.ai_analysis: AIAnalysis` | `DocumentAIAnalysis` (OneToOne) | ⚠️ Separate model via `.ai_analysis` |
| `Asset.comments: Comment[]` | `Comment` model | ✅ Match (nested) |
| `Asset.version_history: Version[]` | `DocumentFile` history | ⚠️ Different structure |
| `AIAnalysis.status` | `DocumentAIAnalysis.analysis_status` | ⚠️ Field name differs |
| `AIAnalysis.provider` | `DocumentAIAnalysis.ai_provider` | ⚠️ Field name differs |
| `Collection.id: number` | `Cabinet.id` or `Tag.id` | ⚠️ **No direct match** — Mayan uses Cabinets/Tags |
| `Publication` | **Custom DAM model** | ⚠️ Not in core Mayan |

### 2.5 Critical Type Mapping Required

```typescript
// services/adapters/documentAdapter.ts — REQUIRED ADAPTER

/**
 * Maps Mayan EDMS API response to Frontend Asset type
 */
export function mapMayanDocumentToAsset(doc: MayanDocument): Asset {
  return {
    id: doc.id,
    label: doc.label,
    filename: doc.file_latest?.filename || doc.label,
    size: doc.file_latest?.size || 0,
    mime_type: doc.file_latest?.mimetype || 'application/octet-stream',
    date_added: doc.datetime_created,
    thumbnail_url: doc.file_latest?.thumbnail_url,
    preview_url: doc.file_latest?.preview_url,
    tags: doc.tags?.map(t => t.label) || [],
    metadata: doc.metadata || {},
    ai_analysis: doc.ai_analysis ? {
      tags: doc.ai_analysis.ai_tags,
      status: doc.ai_analysis.analysis_status,
      ai_description: doc.ai_analysis.ai_description,
      colors: doc.ai_analysis.dominant_colors,
      provider: doc.ai_analysis.ai_provider,
      confidence: doc.ai_analysis.confidence_score
    } : undefined
  }
}
```

---

## 3. API Surface & Integration Points

### 3.1 Required API Endpoints (Frontend → Backend)

| Frontend Service | Method | Frontend Endpoint | Backend Endpoint (BACKEND_ANALYSIS.md) | Status |
|------------------|--------|-------------------|----------------------------------------|--------|
| **authService** | `login` | `POST /api/v4/auth/token/obtain/` | `POST /api/v4/auth/token/obtain/` | ✅ EXISTS |
| **authService** | `getCurrentUser` | `GET /api/v4/user_management/users/current/` | `GET /api/v4/user_management/users/current/` | ✅ EXISTS |
| **authService** | `logout` | `POST /api/v4/auth/logout/` | `POST /api/v4/auth/logout/` | ✅ EXISTS |
| **assetService** | `getAssets` | `GET /api/v4/dam/assets/` | `GET /api/v4/documents/` | ⚠️ **MISMATCH** |
| **assetService** | `getAsset` | `GET /api/v4/dam/assets/{id}/` | `GET /api/v4/documents/{id}/` | ⚠️ **MISMATCH** |
| **assetService** | `searchAssets` | `POST /api/v4/dam/assets/search/` | `GET /api/v4/search/` or `GET /api/v4/documents/?search=` | ⚠️ **MISMATCH** |
| **assetService** | `bulkOperation` | `POST /api/v4/dam/assets/bulk/` | **DOES NOT EXIST** | ❌ **MISSING** |
| **assetService** | `updateAsset` | `PUT /api/v4/dam/assets/{id}/` | `PATCH /api/v4/documents/{id}/` | ⚠️ **MISMATCH** |
| **assetService** | `deleteAsset` | `DELETE /api/v4/dam/assets/{id}/` | `DELETE /api/v4/documents/{id}/` | ⚠️ **MISMATCH** |
| **assetService** | `uploadAsset` | `POST /api/v4/dam/assets/upload/` | **Two-step process required** | ❌ **WRONG APPROACH** |
| **uploadService** | `uploadAsset` | 1. `POST /api/v4/documents/` + 2. `POST /api/v4/documents/{id}/files/` | ✅ Correct two-step | ✅ EXISTS |
| **collectionsService** | `getCollections` | `GET /api/v4/cabinets/` | `GET /api/v4/cabinets/` | ✅ EXISTS |
| **collectionsService** | `createCollection` | `POST /api/v4/cabinets/` | `POST /api/v4/cabinets/` | ✅ EXISTS |
| **collectionsService** | `getSpecialCounts` | `GET /api/v4/collections/special/` | **DOES NOT EXIST** | ❌ **MISSING** |
| **distributionService** | `getPublications` | `GET /api/v4/distribution/publications/` | **Custom DAM endpoint** | ⚠️ **VERIFY** |
| **distributionService** | `createPublication` | `POST /api/v4/distribution/publications/` | **Custom DAM endpoint** | ⚠️ **VERIFY** |
| **distributionService** | `getChannels` | `GET /api/v4/distribution/channels/` | **DOES NOT EXIST** | ❌ **MISSING** |
| **dashboardService** | `getDashboardStats` | `GET /api/v4/dam/dashboard-stats/` | `GET /api/v4/dam/statistics/` | ⚠️ **MISMATCH** |
| **dashboardService** | `getActivityFeed` | `GET /api/v4/dam/activity/` | **DOES NOT EXIST** | ❌ **MISSING** |
| **dashboardService** | `getStorageMetrics` | `GET /api/v4/dam/storage-metrics/` | **DOES NOT EXIST** | ❌ **MISSING** |

### 3.2 Endpoint Mapping Required

```typescript
// services/config/endpoints.ts — CENTRALIZED ENDPOINT MAPPING

export const API_ENDPOINTS = {
  // Auth
  AUTH_TOKEN: '/api/v4/auth/token/obtain/',
  AUTH_LOGOUT: '/api/v4/auth/logout/',
  CURRENT_USER: '/api/v4/user_management/users/current/',
  
  // Documents (Assets)
  DOCUMENTS: '/api/v4/documents/',                    // ✅ Correct
  DOCUMENT_DETAIL: (id: number) => `/api/v4/documents/${id}/`,
  DOCUMENT_FILES: (id: number) => `/api/v4/documents/${id}/files/`,
  DOCUMENT_UPLOAD: (id: number) => `/api/v4/documents/${id}/files/`,
  
  // Cabinets (Collections)
  CABINETS: '/api/v4/cabinets/',
  CABINET_DETAIL: (id: number) => `/api/v4/cabinets/${id}/`,
  CABINET_DOCUMENTS: (id: number) => `/api/v4/cabinets/${id}/documents/`,
  
  // DAM Custom
  DAM_STATISTICS: '/api/v4/dam/statistics/',
  DAM_AI_PROVIDERS: '/api/v4/dam/ai-providers/',
  DAM_ANALYZE: (id: number) => `/api/v4/dam/documents/${id}/analyze/`,
  
  // Distribution (Custom DAM)
  PUBLICATIONS: '/api/v4/distribution/publications/',
  PUBLICATION_DETAIL: (id: number) => `/api/v4/distribution/publications/${id}/`,
}
```

### 3.3 Missing Endpoints (Backend Must Implement)

| Endpoint | Purpose | Priority | Recommended Implementation |
|----------|---------|----------|---------------------------|
| `POST /api/v4/documents/bulk/` | Bulk operations (tag, move, delete) | 🔴 HIGH | Create custom APIView |
| `GET /api/v4/collections/special/` | Special collection counts (favorites, recent, my uploads) | 🔴 HIGH | Aggregate queries |
| `GET /api/v4/dam/activity/` | Activity feed for dashboard | 🟡 MEDIUM | Use Event model |
| `GET /api/v4/dam/storage-metrics/` | Storage usage statistics | 🟡 MEDIUM | Aggregate DocumentFile sizes |
| `GET /api/v4/distribution/channels/` | Distribution channels list | 🟡 MEDIUM | Create Channels model |
| `POST /api/v4/auth/2fa/verify/` | 2FA verification | 🔴 HIGH | django-two-factor-auth |
| `POST /api/v4/auth/2fa/backup-codes/` | Regenerate backup codes | 🟡 MEDIUM | django-two-factor-auth |

### 3.4 Service Files Summary

| Service | File | Endpoints Used | Mock Status |
|---------|------|----------------|-------------|
| `apiService` | `services/apiService.ts` | Base Axios client | 🟢 Real |
| `authService` | `services/authService.ts` | `/auth/token/`, `/users/current/` | 🟢 Real |
| `assetService` | `services/assetService.ts` | `/dam/assets/` ❌ | ⚠️ Wrong endpoints |
| `uploadService` | `services/uploadService.ts` | `/documents/`, `/documents/{id}/files/` | 🟢 Real (two-step) |
| `collectionsService` | `services/collectionsService.ts` | `/cabinets/`, `/collections/special/` ❌ | ⚠️ Partial |
| `distributionService` | `services/distributionService.ts` | `/distribution/publications/` | 🟢 Real (custom DAM) |
| `dashboardService` | `services/dashboardService.ts` | `/dam/dashboard-stats/` ❌ | ❌ Wrong endpoints |
| `cacheService` | `services/cacheService.ts` | N/A — in-memory cache | 🟢 Real |

---

## 4. UI/UX & Code Quality Audit

### 4.1 Component Reusability Analysis

#### Common Components (Highly Reusable)

| Component | Location | Usage Count | Reusability |
|-----------|----------|-------------|-------------|
| `Button` | `components/Common/Button.vue` | 50+ | ✅ Excellent |
| `Input` | `components/Common/Input.vue` | 30+ | ✅ Excellent |
| `Modal` | `components/Common/Modal.vue` | 20+ | ✅ Excellent |
| `Card` | `components/Common/Card.vue` | 15+ | ✅ Excellent |
| `Badge` | `components/Common/Badge.vue` | 25+ | ✅ Excellent |
| `Select` | `components/Common/Select.vue` | 20+ | ✅ Excellent |
| `Pagination` | `components/Common/Pagination.vue` | 10+ | ✅ Excellent |
| `ConfirmModal` | `components/Common/ConfirmModal.vue` | 8+ | ✅ Excellent |
| `OptimizedImage` | `components/Common/OptimizedImage.vue` | 15+ | ✅ Excellent |

#### Duplicated Components (Need Consolidation)

| Issue | Files | Recommendation |
|-------|-------|----------------|
| **Duplicate ShareModal** | `modals/ShareModal.vue`, `DAM/ShareModal.vue` | Consolidate into single component |
| **Duplicate AIInsightsWidget** | `asset/AIInsightsWidget.vue`, `DAM/AIInsightsWidget.vue` | Consolidate into single component |
| **Duplicate MediaEditorModal** | `asset/MediaEditorModal.vue`, `DAM/MediaEditorModal.vue` | Consolidate into single component |
| **Multiple Delete Modals** | `BulkDeleteModal.vue`, `DeleteConfirmModal.vue`, `ConfirmModal.vue` | Use generic `ConfirmModal` with props |

### 4.2 Hardcoded Values Audit

#### Magic Strings Found

| File | Line | Hardcoded Value | Recommendation |
|------|------|-----------------|----------------|
| `uploadService.ts` | 10 | `DEFAULT_CHUNK_SIZE = 5 * 1024 * 1024` | Move to `config/upload.ts` |
| `uploadService.ts` | 11 | `MAX_FILE_SIZE = 500 * 1024 * 1024` | Move to `config/upload.ts` |
| `cacheService.ts` | 12 | `defaultTTL = 5 * 60 * 1000` | Move to `config/cache.ts` |
| `apiService.ts` | 11 | `MAX_RETRIES = 3` | Move to `config/api.ts` |
| `apiService.ts` | 12 | `RETRY_DELAY = 1000` | Move to `config/api.ts` |
| `galleryStore.ts` | 92 | `pageSize = 100` | Move to `config/gallery.ts` |
| `UploadStep.vue` | 63 | `Maximum file size: 500MB` | Use constant from config |
| `UploadStep.vue` | 69 | `Total upload limit: 2GB` | Use constant from config |
| `AdminDashboard.vue` | 57 | `+12%` (hardcoded growth) | Should come from API |

#### Magic IDs Found

| File | Issue | Recommendation |
|------|-------|----------------|
| `mocks/assets.ts` | Hardcoded user IDs (1-6) | Use dynamic IDs |
| `router/index.ts` | Hardcoded route paths | OK — expected for router |
| `adminStore.ts` | Mock workflow IDs | Use UUID generation |

### 4.3 Responsiveness Audit

#### Components with Full Mobile Support ✅

| Component | Breakpoints Used |
|-----------|-----------------|
| `AdminUsers.vue` | `sm:`, `md:`, `lg:` — Desktop table / Mobile cards |
| `AdminDashboard.vue` | `sm:`, `lg:` — Responsive grid |
| `GalleryView.vue` | `sm:`, `md:`, `lg:` — Responsive grid columns |
| `LoginPage.vue` | `max-w-md` — Centered card |
| `UploadPage.vue` | `sm:` — Step indicators |

#### Components Missing Mobile Classes ⚠️

| Component | Issue | Recommendation |
|-----------|-------|----------------|
| `AssetDetailPage.vue` | Fixed width panels | Add `sm:` breakpoints |
| `WorkflowDesignerPage.vue` | Canvas not responsive | Add touch support + zoom |
| `MetadataSchemaPage.vue` | Table overflow | Add horizontal scroll or card view |
| `AdminWorkflowDetail.vue` | Fixed layout | Add responsive grid |

### 4.4 Accessibility (a11y) Audit

#### Good Practices Found ✅

| Component | Feature |
|-----------|---------|
| `UploadStep.vue` | `role="region"`, `aria-label`, `tabindex` |
| `Modal.vue` | `aria-modal="true"`, `role="dialog"` |
| `Button.vue` | `aria-label` support, focus states |
| `DashboardPage.vue` | `aria-label` on regions, `aria-hidden` on icons |

#### Accessibility Issues ⚠️

| Component | Issue | Recommendation |
|-----------|-------|----------------|
| `LoginPage.vue` | `type="email"` but accepts username | Change to `type="text"` |
| `GalleryView.vue` | No keyboard navigation for grid | Add `tabindex`, `onKeyDown` |
| `AdminUsers.vue` | Table lacks `aria-sort` | Add sort announcements |
| `SearchBar.vue` | No live region for results | Add `aria-live="polite"` |

### 4.5 Code Quality Metrics

#### TypeScript Coverage

| Category | Coverage | Notes |
|----------|----------|-------|
| Stores | 100% | All stores fully typed |
| Services | 100% | All services typed with generics |
| Components | 95% | Some `any` types in event handlers |
| Utils | 90% | Some utility functions need better types |

#### ESLint Issues (Estimated)

| Severity | Count | Common Issues |
|----------|-------|---------------|
| Error | 0 | — |
| Warning | ~15 | Unused variables, any types |
| Info | ~30 | Prefer const, naming conventions |

### 4.6 Mock Data Files Analysis

| File | Purpose | Lines | Should Be Removed for Production |
|------|---------|-------|----------------------------------|
| `mocks/assets.ts` | Mock assets with S3 fallback | 996 | ⚠️ Keep for dev, disable in prod |
| `mocks/folders.ts` | Mock folder structure | ~100 | ⚠️ Keep for dev |
| `mocks/publications.ts` | Mock publications | ~150 | ⚠️ Keep for dev |
| `mocks/workflows.ts` | Mock workflows | ~200 | ⚠️ Keep for dev |
| `mocks/metadata.ts` | Mock metadata schemas | ~100 | ⚠️ Keep for dev |
| `mocks/ai.ts` | Mock AI responses | ~100 | ⚠️ Keep for dev |
| `mocks/search.ts` | Mock search results | ~80 | ⚠️ Keep for dev |
| `mocks/s3Provider.ts` | S3/Unsplash URL provider | 237 | ✅ Keep — provides fallback URLs |
| `mocks/s3_map.json` | S3 asset mapping | varies | ✅ Keep — asset registry |

---

## 5. Архитектурный обзор

### 5.1 Технологический стек

| Категория | Технология | Версия |
|-----------|------------|--------|
| **Фреймворк** | Vue.js | 3.4.21 |
| **Язык** | TypeScript | 5.3.3 |
| **Сборщик** | Vite | 5.4.11 |
| **Стейт-менеджмент** | Pinia | 2.1.7 |
| **Маршрутизация** | Vue Router | 4.2.5 |
| **CSS Framework** | Tailwind CSS | 3.4.1 |
| **HTTP-клиент** | Axios | 1.6.5 |
| **UI-компоненты** | HeadlessUI/Vue | 1.7.16 |
| **Тестирование** | Vitest + Playwright | 4.0.14 / 1.41.2 |

### 5.2 Структура приложения

```
frontend/src/
├── components/           # 100+ UI компоненты
│   ├── admin/           # 10 компонентов админки
│   ├── collections/     # 6 компонентов коллекций
│   ├── Common/          # 10 базовых компонентов
│   ├── DAM/             # 20 DAM-компонентов
│   ├── Distribution/    # 5 компонентов публикаций
│   ├── gallery/         # 2 компонента галереи
│   ├── Layout/          # 5 компонентов макета
│   ├── modals/          # 5 модальных окон
│   ├── reports/         # 2 компонента отчетов
│   └── workflow/        # 4 компонента workflow
├── layouts/             # 1 layout (AdminLayout)
├── mocks/               # 9 файлов mock-данных
├── pages/               # 35+ страниц
│   ├── admin/           # 16 админ-страниц
│   ├── auth/            # 2 auth-страницы
│   └── collections/     # 4 collection-страницы
├── router/              # Маршрутизация
├── services/            # 8+ сервисов
├── stores/              # 11 Pinia stores
├── types/               # TypeScript типы
└── utils/               # Утилиты
```

### 5.3 Маршрутизация (50+ routes)

```typescript
// Key routes from router/index.ts
{
  '/': DashboardPage,                    // requiresAuth: true
  '/login': LoginPage,                   // requiresAuth: false
  '/auth/2fa': Login2FAPage,             // requiresAuth: false
  '/dam': DAMPage,                       // requiresAuth: true
  '/dam/gallery': DAMGalleryPage,        // requiresAuth: true
  '/dam/assets/:id': AssetDetailPage,    // requiresAuth: true
  '/dam/favorites': FavoritesPage,       // requiresAuth: true
  '/dam/my-uploads': MyUploadsPage,      // requiresAuth: true
  '/dam/recent': RecentPage,             // requiresAuth: true
  '/dam/shared': SharedWithMePage,       // requiresAuth: true
  '/sharing': SharingPage,               // requiresAuth: true
  '/admin/*': AdminLayout,               // requiresAuth: true, requiresAdmin: true
  '/collections': CollectionsPage,       // requiresAuth: true
  '/forbidden': ForbiddenPage,           // requiresAuth: false
}
```

---

## 6. Модель данных (Core Entities)

### 6.1 Frontend Types (from `types/api.ts`)

```typescript
// Asset — основная сущность
interface Asset {
  id: number
  label: string
  filename: string
  size: number
  mime_type: string
  date_added: string
  thumbnail_url?: string
  preview_url?: string
  tags?: string[]
  metadata?: Record<string, unknown>
  ai_analysis?: AIAnalysis
  comments?: Comment[]
  version_history?: Version[]
  access_level?: string
}

// AIAnalysis — результаты AI-анализа
interface AIAnalysis {
  tags?: string[]
  confidence?: number
  objects_detected?: DetectedObject[]
  colors?: string[]
  status: 'pending' | 'processing' | 'completed' | 'failed'
  ai_description?: string
  provider?: string
}

// Publication — публикация для распространения
interface Publication {
  id: number
  title: string
  description?: string
  status: 'draft' | 'scheduled' | 'published' | 'archived'
  assets: Asset[]
  channels: PublicationChannel[]
  share_links?: ShareLink[]
}

// User — пользователь
interface User {
  id: number
  username: string
  email: string
  first_name?: string
  last_name?: string
  is_active: boolean
  permissions?: string[]
  role?: 'admin' | 'editor' | 'viewer' | 'guest'
  two_factor_enabled?: boolean
}
```

---

## 7. Критические проблемы и рекомендации

### 7.1 Критические проблемы (🔴 BLOCKER)

| # | Проблема | Файл | Impact | Fix |
|---|----------|------|--------|-----|
| 1 | **assetService uses wrong endpoints** | `services/assetService.ts` | API calls fail | Change `/dam/assets/` → `/documents/` |
| 2 | **useMock persisted in localStorage** | `stores/assetStore.ts` | Users stuck in mock mode | Remove from persist paths or add UI toggle |
| 3 | **LoginPage uses type="email"** | `pages/LoginPage.vue` | Can't login with username | Change to `type="text"` |
| 4 | **uploadService needs adapter** | `services/uploadService.ts` | Response mismatch | Add documentAdapter mapping |
| 5 | **2FA endpoints don't exist** | `authStore.ts` | 2FA flow broken | Implement backend endpoints |

### 7.2 Высокий приоритет (🟡 HIGH)

| # | Проблема | Файл | Recommendation |
|---|----------|------|----------------|
| 6 | Duplicate ShareModal components | `modals/`, `DAM/` | Consolidate |
| 7 | Hardcoded file size limits | `uploadService.ts`, `UploadStep.vue` | Centralize in config |
| 8 | dashboardService wrong endpoints | `services/dashboardService.ts` | Update to match backend |
| 9 | Missing bulk operations endpoint | `assetService.ts` | Implement on backend |
| 10 | No error toast notifications | Global | Add error handling UX |

### 7.3 Средний приоритет (🟢 MEDIUM)

| # | Проблема | Recommendation |
|---|----------|----------------|
| 11 | Mixed Russian/English UI text | Standardize or add i18n |
| 12 | Missing keyboard navigation in gallery | Add `tabindex`, `onKeyDown` |
| 13 | WorkflowDesignerPage not responsive | Add touch support |
| 14 | No loading skeletons in some pages | Add consistent loading states |

### 7.4 Integration Checklist

Before API integration:
- [ ] Fix `assetService.ts` endpoints (`/dam/assets/` → `/documents/`)
- [ ] Add `documentAdapter.ts` mapping function
- [ ] Clear localStorage `assetStore` to reset `useMock` flag
- [ ] Fix `LoginPage.vue` input type
- [ ] Verify `collectionsService` uses `/cabinets/`
- [ ] Test auth flow with real backend
- [ ] Implement missing backend endpoints (bulk, special counts, activity)
- [ ] Add error handling for API failures

---

## Заключение

### Общая оценка

| Критерий | Оценка | Комментарий |
|----------|--------|-------------|
| **Архитектура** | 8/10 | Современный стек, хорошая структура |
| **Типизация** | 9/10 | Полная TypeScript типизация |
| **API Integration** | 4/10 | ⚠️ Многие endpoints неверны |
| **Mock Data** | 7/10 | Хорошие mocks, но мешают dev |
| **UI/UX** | 8/10 | Tailwind + HeadlessUI, responsive |
| **Готовность к prod** | 5/10 | Требуется исправление endpoints |

### Следующие шаги

1. **Исправить assetService endpoints** — критично для интеграции
2. **Создать Document Adapter** — маппинг Mayan → Frontend
3. **Реализовать missing backend endpoints** — bulk, activity, storage
4. **Тестирование auth flow** — с реальным бэкендом
5. **Удалить/отключить mock data** — для production

---

*Документ обновлён: 03 декабря 2025*  
*Версия анализа: 2.0*
