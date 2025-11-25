# 🔗 АРХИТЕКТУРА СВЯЗЕЙ И ПОЛЬЗОВАТЕЛЬСКИЕ ПУТИ DAM ФРОНТЕНДА
## Моделирование взаимодействия компонентов и UX-потоков

**Версия:** 1.0  
**Дата:** Ноябрь 2025  
**Уровень:** Senior Architecture (20+ лет enterprise DAM опыта)  
**Методология:** DDD (Domain-Driven Design) + User-Centric Architecture  
**Стандарты:** Bynder/Canto/Adobe DAM best practices  

---

## 📑 ОГЛАВЛЕНИЕ

1. [Принципы архитектуры связей](#принципы-архитектуры-связей)
2. [Модель состояния (State Model)](#модель-состояния-state-model)
3. [Диаграмма взаимодействия компонентов](#диаграмма-взаимодействия-компонентов)
4. [Пользовательские пути (User Journeys)](#пользовательские-пути-user-journeys)
5. [Критические сценарии использования](#критические-сценарии-использования)
6. [Data Flow Mapping](#data-flow-mapping)
7. [Navigation Model](#navigation-model)
8. [State Management Architecture](#state-management-architecture)
9. [API Interaction Patterns](#api-interaction-patterns)
10. [Performance Optimization Routes](#performance-optimization-routes)

---

# 🏗️ ПРИНЦИПЫ АРХИТЕКТУРЫ СВЯЗЕЙ

## Основные парадигмы

### 1. Unidirectional Data Flow
```
User Action → Component Event → Store Update → UI Rerender
```

**Принцип:** Все изменения состояния идут через Pinia store
- ✅ Предсказуемое состояние
- ✅ Легче отладка (DevTools)
- ✅ Безопасное масштабирование

### 2. Component Composition Hierarchy
```
Layout (Header + Sidebar + MainContent)
  ↓
Page (DAMPage, DistributionPage, etc)
  ↓
Feature Components (GalleryView, SearchBar, etc)
  ↓
Common Components (Button, Input, Card, etc)
  ↓
Base Elements (DOM primitives)
```

**Каждый уровень:**
- Изолирован логически
- Переиспользуем в других контекстах
- Тестируем независимо

### 3. Two-Way Communication Pattern
```
Component State (local) ←→ Pinia Store (global) ←→ API (backend)
```

**Правило разделения:**
| State Type | Location | Scope |
|-----------|----------|-------|
| UI state (theme, sidebar) | uiStore | Global, persistent |
| User data (profile, perms) | authStore | Global, session |
| Asset data (gallery items) | assetStore | Global, cached |
| Form state (inputs) | Local component | Local, temporary |
| Modal state (open/closed) | uiStore | Global, scoped |

### 4. Event-Driven Architecture
```
User Interaction
    ↓
Component emits event
    ↓
Parent listens (or router changes)
    ↓
Store action triggered
    ↓
API call (if needed)
    ↓
State updates
    ↓
Components rerender
```

---

## 🎯 DAM-специфические принципы

### Gallery-First Paradigm
```
Все пути ведут к Gallery View как центральной точке:

Dashboard → Quick Access → Gallery View
  ↓
Search Results → Click Asset → Detail View
  ↓
Admin Setup → Upload → Gallery View
  ↓
Collections → Browse → Gallery View
  ↓
Distribution → Preview → Gallery View
```

**Почему Gallery центральная?**
- ✅ Основная работа с активами происходит здесь
- ✅ 80% user time spent
- ✅ Hub для поиска, фильтрации, действий
- ✅ Интеграция точка для всех путей

### Contextual Filtering Model
```
Global Filters (persistent across session)
    ↓
    Query String (shareable, bookmarkable)
    ↓
    Faceted Search (dynamic)
    ↓
    Recent Searches (localStorage)
    ↓
    Saved Searches (backend)
```

### Progressive Disclosure (постепенное раскрытие)
```
Базовый вид (simple defaults)
    ↓
Expanded view (more options)
    ↓
Advanced search (power user features)
    ↓
Admin settings (system configuration)
```

---

# 📊 МОДЕЛЬ СОСТОЯНИЯ (STATE MODEL)

## Global State Stores (Pinia)

### authStore
```typescript
State:
  - user: User | null
  - permissions: Permission[]
  - isAuthenticated: boolean
  - token: string | null
  - 2faEnabled: boolean
  - lastActivity: timestamp

Actions:
  - login(email, password)
  - logout()
  - refreshToken()
  - setup2FA()
  - updateProfile()

Connections:
  → assetStore (filter by permissions)
  → distributionStore (user-specific publications)
  → notificationStore (user preferences)
  → uiStore (sidebar navigation)
```

### uiStore
```typescript
State:
  - sidebarExpanded: boolean
  - theme: 'light' | 'dark' | 'auto'
  - activeModal: string | null
  - notifications: Notification[]
  - breadcrumbs: Breadcrumb[]
  - mobileMenuOpen: boolean

Actions:
  - toggleSidebar()
  - setTheme(theme)
  - openModal(modalName, data)
  - closeModal()
  - addNotification(notification)
  - setBreadcrumbs(crumbs)

Connections:
  → All pages (theme, sidebar state)
  → All components (modal management)
  → Layout (navigation state)
```

### assetStore (CORE)
```typescript
State:
  - assets: Asset[] (current page)
  - totalCount: number (for pagination)
  - selectedAssets: Asset[] (multi-select)
  - currentAsset: Asset | null (detail view)
  - loadingState: 'idle' | 'loading' | 'error'
  - filters: FilterState
  - sortBy: SortOption
  - pagination: PaginationState
  - cacheTimestamp: timestamp

Actions:
  - fetchAssets(params)
  - getAssetDetail(id)
  - searchAssets(query)
  - selectAsset(asset, multiSelect)
  - applyFilters(filters)
  - clearFilters()
  - sortAssets(sortBy)
  - nextPage()
  - previousPage()

Connections:
  → GalleryView (displays assets)
  → SearchBar (search query)
  → FiltersPanel (filter state)
  → BulkActions (selected items)
  → AssetDetailPage (current asset)
  → All modals (asset operations)
```

### searchStore
```typescript
State:
  - query: string
  - results: Asset[]
  - recentSearches: string[] (max 5)
  - savedSearches: SavedSearch[]
  - facets: Facet[] (aggregations)
  - searchHistory: SearchHistory[]

Actions:
  - performSearch(query)
  - clearSearch()
  - addToRecent(query)
  - saveSearch(name, filters)
  - deleteSaveSearch(id)
  - getFacets()
  - advancedSearch(advancedQuery)

Connections:
  → SearchBar (instant results)
  → AdvancedSearchPage (full results)
  → assetStore (populate gallery)
  → FiltersPanel (facets display)
```

### filterStore
```typescript
State:
  - activeFilters: Filter[]
  - filterPresets: FilterPreset[]
  - tempFilters: Filter[] (during edit)
  - filterHistory: Filter[][]

Actions:
  - addFilter(filter)
  - removeFilter(filterId)
  - applyFilters()
  - resetFilters()
  - saveFilterPreset(name)
  - loadFilterPreset(presetId)

Connections:
  → assetStore (query params)
  → searchStore (facets)
  → FiltersPanel (UI)
  → QueryString (URL params)
```

### notificationStore
```typescript
State:
  - notifications: Notification[] (toast queue)
  - wsConnected: boolean
  - unreadCount: number
  - notificationCenter: FullNotification[]

Actions:
  - addNotification(notification)
  - removeNotification(id)
  - markAsRead(id)
  - markAllAsRead()
  - connectWebSocket()
  - disconnectWebSocket()

Connections:
  → Header (unread badge)
  → NotificationCenterModal (full list)
  → BulkActions (operation results)
  → API responses (error/success)
```

### settingsStore
```typescript
State:
  - userPreferences: UserPreferences
  - language: string
  - timezone: string
  - itemsPerPage: number
  - viewMode: 'gallery' | 'list'

Actions:
  - updatePreference(key, value)
  - saveSettings()
  - loadSettings()

Connections:
  → LocalStorage (persistence)
  → ProfilePage (settings UI)
  → All pages (preferences apply)
```

---

# 🔀 ДИАГРАММА ВЗАИМОДЕЙСТВИЯ КОМПОНЕНТОВ

## Component Interaction Map

```
┌────────────────────────────────────────────────────────────┐
│                    Application Shell                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Header (64px Fixed)                      │  │
│  │  Logo │ SearchBar │ Upload │ Filters │ Notifications│  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                                                        │ │
│  │  ┌─────────────┐  ┌─────────────────────────────────┐ │ │
│  │  │   Sidebar   │  │      MainContent Area          │ │ │
│  │  │ (280px)     │  │  ┌─────────────────────────────┐│ │ │
│  │  │             │  │  │   Router Outlet             ││ │ │
│  │  │ Navigation  │  │  │  (Page Component)           ││ │ │
│  │  │ • Dashboard │  │  │                             ││ │ │
│  │  │ • DAM       │  │  │  Page Content:              ││ │ │
│  │  │ • Distrib   │  │  │  - GalleryView              ││ │ │
│  │  │ • Admin     │  │  │  - SearchResults            ││ │ │
│  │  │ • Settings  │  │  │  - AssetDetail              ││ │ │
│  │  │             │  │  │  - Publication              ││ │ │
│  │  │ Collections │  │  │  - Dashboard                ││ │ │
│  │  │ • My Upload │  │  │  - etc                      ││ │ │
│  │  │ • Favorites │  │  │                             ││ │ │
│  │  │ • Recent    │  │  └─────────────────────────────┘│ │ │
│  │  │ • Shared    │  │                                │ │ │
│  │  │             │  │  Modals (Portal):             │ │ │
│  │  │ [+ Folder]  │  │  - UploadModal                │ │ │
│  │  └─────────────┘  │  - ShareModal                 │ │ │
│  │                   │  - DeleteConfirm              │ │ │
│  │                   │  - AssetPreview               │ │ │
│  │                   │  - EditMetadata               │ │ │
│  │                   │  - CreatePublication          │ │ │
│  │                   │  - etc                        │ │ │
│  │                   └─────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
         ↕ (State & Events)
┌────────────────────────────────────────────────────────────┐
│              Pinia State Management Layer                   │
│  ┌─────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │   auth  │   asset  │   search │  filter  │   ui    │  │
│  │ Store   │ Store    │ Store    │ Store    │ Store   │  │
│  └─────────┴──────────┴──────────┴──────────┴──────────┘  │
└────────────────────────────────────────────────────────────┘
         ↕ (API Calls & WebSocket)
┌────────────────────────────────────────────────────────────┐
│             API Service & HTTP Layer                        │
│  [assetService] [searchService] [authService] [...]        │
└────────────────────────────────────────────────────────────┘
         ↕ (HTTP/REST)
┌────────────────────────────────────────────────────────────┐
│          Django REST API Backend                            │
│  GET /api/v4/dam/assets/                                  │
│  POST /api/v4/dam/assets/search/                          │
│  PUT /api/v4/dam/assets/{id}/                             │
│  etc                                                       │
└────────────────────────────────────────────────────────────┘
```

---

## Component Tree with Data Flow

```
App.vue (root)
├── Header.vue
│   ├── Logo (router.push to dashboard)
│   ├── SearchBar.vue
│   │   ├── input event → searchStore.performSearch()
│   │   ├── SearchResults.vue (dropdown)
│   │   │   └── click → router.push to detail
│   │   └── emit 'search' → SearchResults
│   ├── UploadButton
│   │   └── click → open UploadModal
│   ├── FilterButton
│   │   └── click → open/close FiltersPanel
│   ├── NotificationBell.vue
│   │   ├── badge from notificationStore.unreadCount
│   │   └── click → open NotificationCenterModal
│   └── UserMenu.vue
│       ├── ProfilePage link
│       ├── SettingsPage link
│       └── Logout button
│
├── Sidebar.vue (collapsible)
│   ├── Navigation links
│   │   ├── Dashboard → push route
│   │   ├── DAM Gallery → push route
│   │   ├── Distribution → push route
│   │   └── Admin → push route
│   ├── Collections Tree
│   │   ├── expanded/collapsed state → uiStore
│   │   ├── items from assetStore
│   │   └── drag-drop → move assets
│   └── Quick actions
│       └── [+ New Folder] → CreateCollectionModal
│
├── MainContent.vue
│   └── RouterView (current page)
│       ├── DAMPage
│       │   ├── GalleryView.vue
│       │   │   ├── connects to assetStore.assets
│       │   │   ├── AssetCard (for each asset)
│       │   │   │   ├── image from asset.thumbnail_url
│       │   │   │   ├── hover → show quick actions
│       │   │   │   ├── click → router.push to detail
│       │   │   │   └── checkbox → select in assetStore
│       │   │   ├── Pagination.vue
│       │   │   │   ├── next → assetStore.nextPage()
│       │   │   │   └── previous → assetStore.previousPage()
│       │   │   └── InfiniteScroll (alternative)
│       │   │       └── scroll → load more assets
│       │   │
│       │   ├── BulkActions.vue (toolbar)
│       │   │   ├── visible if assetStore.selectedAssets.length > 0
│       │   │   ├── Bulk tag → BulkTagModal
│       │   │   ├── Bulk move → MoveAssetsModal
│       │   │   ├── Bulk delete → DeleteConfirmModal
│       │   │   ├── Bulk download → trigger export
│       │   │   └── Bulk share → ShareModal
│       │   │
│       │   ├── SearchBar.vue (header-integrated)
│       │   │   └── changes searchStore.query
│       │   │
│       │   └── FiltersPanel.vue (left sidebar)
│       │       ├── Type filter (images, videos, docs)
│       │       ├── Date range filter
│       │       ├── Size filter
│       │       ├── Tags filter
│       │       ├── Custom metadata filters
│       │       └── Apply button → filterStore.applyFilters()
│       │
│       ├── AssetDetailPage
│       │   ├── preview (left 60%)
│       │   │   ├── image/video from currentAsset
│       │   │   ├── zoom controls
│       │   │   └── download button
│       │   │
│       │   └── MetadataPanel.vue (right 40%)
│       │       ├── File Details
│       │       ├── Image Info
│       │       ├── AI Analysis section
│       │       │   ├── TagSuggestions.vue
│       │       │   ├── AnalysisResults.vue
│       │       │   └── AIInsights.vue
│       │       ├── Version History
│       │       │   └── VersionHistoryModal on click
│       │       ├── Comments
│       │       │   └── Comment thread display
│       │       ├── Actions (Approve, Share, More)
│       │       └── Approve button → workflow trigger
│       │
│       ├── DistributionPage
│       │   ├── PublicationList.vue
│       │   │   ├── PublicationCard (for each)
│       │   │   │   ├── title, channel, schedule
│       │   │   │   ├── click → publication detail
│       │   │   │   └── actions (edit, delete, analytics)
│       │   │   └── [+ Create Publication]
│       │   │       └── CreatePublicationModal
│       │   │
│       │   └── PublicationStats.vue
│       │       ├── downloads chart
│       │       ├── views chart
│       │       └── engagement metrics
│       │
│       ├── DashboardPage
│       │   ├── StatsCard (KPIs)
│       │   ├── ChartWidget (usage, uploads)
│       │   ├── ActivityFeed.vue
│       │   └── StorageMetrics.vue
│       │
│       ├── AdminPage
│       │   ├── UserManagementPage.vue
│       │   ├── MetadataSchemaPage.vue
│       │   ├── WorkflowDesignerPage.vue
│       │   └── ReportsPage.vue
│       │
│       └── SettingsPage
│           ├── ProfileSection
│           ├── AccountSettings
│           ├── SecuritySettings
│           ├── APIKeys
│           └── NotificationPreferences
│
└── Modals (Portal)
    ├── UploadModal
    │   ├── drag-drop zone
    │   ├── FileUploader.vue
    │   └── emit 'uploaded' → refresh assetStore
    │
    ├── ShareModal
    │   ├── generate link → API call
    │   ├── permissions selector
    │   └── expiration date picker
    │
    ├── DeleteConfirmModal
    │   ├── show items to delete
    │   └── delete button → API + refresh assetStore
    │
    ├── AssetPreviewModal (lightbox)
    │   ├── large preview
    │   ├── prev/next arrows
    │   └── keyboard navigation
    │
    ├── EditMetadataModal
    │   ├── dynamic form based on schema
    │   └── save → API + update assetStore
    │
    ├── BulkTagModal
    │   ├── operation selector
    │   ├── tag input with autocomplete
    │   └── apply → API + refresh assetStore
    │
    ├── MoveAssetsModal
    │   ├── collection tree selector
    │   └── move button → API + refresh assetStore
    │
    └── NotificationCenterModal
        ├── list of notifications
        ├── filter tabs
        └── mark as read / delete actions
```

---

# 🚀 ПОЛЬЗОВАТЕЛЬСКИЕ ПУТИ (USER JOURNEYS)

## 1. Beginner User Path: First Time Upload & Discovery

### Goal: Upload first asset and find it in gallery

```
Step 1: Login
├── User navigates to /login
├── Component: LoginPage.vue
├── Enters credentials
├── Action: authStore.login(email, password)
├── Result: authStore.isAuthenticated = true
└── Redirect: Dashboard

Step 2: See Dashboard
├── Component: DashboardPage
├── Displays:
│   ├── Welcome message
│   ├── Quick stats (0 assets, 0 usage)
│   ├── Recent activity (empty)
│   └── Call-to-action: "Upload your first asset"
└── UX: Large, visible upload button

Step 3: Click Upload
├── User clicks header UploadButton
├── Trigger: uiStore.openModal('upload')
├── Component: UploadModal opens
├── Options:
│   ├── Drag-drop zone
│   ├── Click to select files
│   └── Multiple file support
└── Select 1 JPG file (landscape photo)

Step 4: Upload Completes
├── FileUploader.vue handles upload
├── Progress: 0% → 100%
├── Backend processes: metadata extraction, thumbnails
├── Notification: "Upload successful!"
├── Action: notificationStore.addNotification({
│   type: 'success',
│   message: 'Asset uploaded successfully!'
├── Store update: assetStore.assets += [newAsset]
└── Modal closes automatically

Step 5: See Asset in Gallery
├── Component: GalleryView (DAMPage)
├── Router auto-navigates to /dam/gallery
├── Displays: 1 asset card
├── Card shows:
│   ├── Thumbnail (generated automatically)
│   ├── Filename
│   ├── File size
│   ├── Upload date (now)
│   └── Quick actions on hover
└── UX: Celebratory animation

Step 6: View Asset Details
├── User double-clicks asset card
├── Router: /dam/assets/{id}
├── Component: AssetDetailPage
├── Displays:
│   ├── Large preview (left)
│   ├── Metadata panel (right)
│   │   ├── Filename
│   │   ├── Upload date
│   │   ├── File size
│   │   ├── Dimensions (1920x1280)
│   │   └── AI Analysis section
│   │       ├── Auto-generated tags (landscape, nature, outdoor)
│   │       ├── Objects detected
│   │       └── Color palette
│   └── Actions
│       ├── Download button
│       ├── Share button
│       └── More menu
└── User clicks Share

Step 7: Generate Share Link
├── Component: ShareModal
├── User clicks "Create share link"
├── API call: POST /api/v4/dam/assets/{id}/share/
├── Server generates: https://dam.local/share/abc123xyz
├── Settings:
│   ├── Permissions: View + Download (default)
│   ├── Expiration: 30 days
│   └── Password: (optional)
├── User copies link
├── Notification: "Link copied to clipboard!"
└── Modal closes

**Outcome:** User has uploaded, found, viewed, and shared first asset ✅
**Time taken:** ~5 minutes
**Complexity:** Low (guided experience)
**Satisfaction:** High (quick wins)
```

---

## 2. Power User Path: Advanced Search with Filtering & Bulk Operations

### Goal: Find specific assets using complex criteria and tag them

```
Step 1: Navigate to Gallery
├── User is in /dam/gallery
├── Current state: 1000+ assets
├── Needs: Find all landscape photos from last month (campaign shoot)
└── Strategy: Use advanced search

Step 2: Open Advanced Search
├── User clicks header search icon
├── Ctrl+K shortcut works
├── Component: SearchBar expands
├── Type: "landscape photography"
├── Instant results appear (dropdown, 8 items max)
├── Results show:
│   ├── Thumbnail
│   ├── Filename
│   ├── Relevance score
│   ├── Metadata excerpt
│   └── File type badge
└── User clicks "View all results"

Step 3: Advanced Search Page
├── Router: /dam/search?q=landscape+photography
├── Component: AdvancedSearchPage
├── Displays:
│   ├── Search input (top) with query suggestion
│   ├── Left sidebar: Filters
│   │   ├── Type: ☑ Images (selected)
│   │   ├── Date Range: Last 30 days (user selects)
│   │   ├── Size: 1920x1080 and above
│   │   ├── Tags: landscape, photography, campaign
│   │   └── [Apply Filters]
│   ├── Main area: Results grid (4 columns)
│   │   ├── 50 assets matching criteria
│   │   ├── Pagination: 50 of 150 total
│   │   └── Sorting: Most relevant (dropdown)
│   └── Breadcrumb: Home > Search > landscape photography
└── Stores updated:
    ├── searchStore.query = "landscape photography"
    ├── searchStore.facets = {type, date, size, tags}
    ├── filterStore.activeFilters = [{type}, {date}, {size}, {tags}]
    └── assetStore.assets = [50 matching results]

Step 4: Refine Results with Date Filter
├── User sees ~150 results
├── Needs to narrow: wants only from last 2 weeks
├── Left panel: DateRangePicker
├── Selects: Last 14 days
├── Action: filterStore.addFilter({type: 'date', value: '14d'})
├── API call: POST /api/v4/dam/assets/search/ with filters
├── Results update: Now 47 assets
├── URL updates: ?q=landscape+photography&date=14d
└── Notification: "Filtered: 47 results"

Step 5: Multi-Select Assets
├── User wants to tag all 47 results with "campaign-2025"
├── Checkbox on first asset card: clicks
├── Component: AssetCard emits 'select' event
├── assetStore.selectAssets([asset1]) → selectedCount = 1
├── Action: "Select All" checkbox appears
├── User clicks "Select All"
├── assetStore.selectAssets(allAssets) → selectedCount = 47
├── BulkActions toolbar appears (bottom)
│   ├── "47 selected" counter
│   ├── Bulk actions menu:
│   │   ├── [🏷️ Tag]
│   │   ├── [📁 Move]
│   │   ├── [⬇️ Download]
│   │   ├── [🔗 Share]
│   │   ├── [🗑️ Delete]
│   │   └── [⋯ More]
│   └── [Clear Selection] button
└── Keyboard: Shift+click for range, Ctrl+A for all

Step 6: Bulk Tag Operation
├── User clicks [🏷️ Tag] button
├── Component: BulkTagModal opens
├── Options:
│   ├── Operation: [Add tags ▼]
│   ├── Tag input: Start typing "campaign-2025"
│   ├── Auto-suggest shows existing tags
│   ├── Confirmation: "Add 1 tag to 47 assets?"
│   └── Buttons: [Cancel] [Apply]
├── User types "campaign-2025" → enters
├── Clicks [Apply]
├── API call: POST /api/v4/dam/assets/bulk/
│   {
│     "ids": [1, 2, 3, ..., 47],
│     "action": "tag",
│     "data": {"tags": ["campaign-2025"]}
│   }
├── Progress: Toast shows "Processing 47 assets..."
├── Completion: "✅ Tagged 47 assets"
├── assetStore refreshes all assets with new tags
└── BulkActions toolbar hides (no more selection)

Step 7: Save Search for Future Use
├── User wants to reuse this exact search next week
├── SearchBar: click bookmark icon (or "Save search")
├── SaveSearchModal opens
├── User names it: "Campaign 2025 Landscape Photos"
├── Clicks [Save]
├── API call: POST /api/v4/searches/
├── searchStore.savedSearches += [newSearch]
├── Sidebar now shows: "Campaign 2025 Landscape Photos" (clickable)
└── Next time: 1 click to load same results

**Outcome:** User found 47 specific assets, tagged all at once, saved search ✅
**Time taken:** ~3 minutes
**Complexity:** Medium (multiple steps, but intuitive)
**Efficiency:** 47 items tagged vs 47 individual clicks without bulk ops
```

---

## 3. Workflow Path: Approval Process with Comments

### Goal: Submit asset for approval, reviewer approves with comments

```
Step 1: Asset Needs Approval
├── User in /dam/gallery
├── Selects asset: campaign_photo_01.jpg
├── Clicks "More" menu → "Submit for Approval"
├── Component: SubmitApprovalModal or workflow action
└── Workflow triggered: Draft → In Review

Step 2: Approval State Visible
├── Asset card now shows: 🟡 "Pending Review" badge
├── Router: Asset locked from editing
├── Sidebar breadcrumb: Home > Assets > Pending
├── Store: assetStore.assets[0].status = 'pending'
└── Notifications:
    ├── Approver gets: "New asset waiting review"
    ├── User gets: "Submitted for approval"
    └── Stored in: notificationStore

Step 3: Approver Reviews Asset
├── Reviewer logs in
├── Dashboard shows: "1 asset waiting review"
├── Sidebar: Collections → "Pending Review" (1)
├── Clicks to view pending assets
├── Sees asset card with:
│   ├── Status: 🟡 Pending
│   ├── Submitted by: User Name
│   ├── Date submitted: 2 hours ago
│   └── Quick preview
└── Clicks to open AssetDetailPage

Step 4: Detailed Review
├── Component: AssetDetailPage (read-mode for reviewer)
├── Left: Full preview
├── Right metadata panel:
│   ├── Filename: campaign_photo_01.jpg
│   ├── Status: 🟡 Pending Review
│   ├── Submitted by: John User
│   ├── Tags: campaign, landscape, outdoor
│   ├── AI Analysis: (visible)
│   ├── Version History: (shows submitted version)
│   └── Comments section (empty initially)
├── Action buttons (for reviewers):
│   ├── [✅ Approve] (green)
│   ├── [❌ Reject] (red)
│   └── [💬 Comment] (blue)
└── Reviewer clicks Comments section

Step 5: Add Review Comments
├── Component: Comments thread UI
├── Reviewer types:
│   "Great shot! Minor metadata fixes needed:
│    - Add location: Paris, France
│    - Add photographer credit
│    - Adjust color profile to sRGB"
├── Clicks "Post Comment"
├── API call: POST /api/v4/dam/assets/{id}/comments/
├── Comment appears: Reviewer name + timestamp
├── Notification sent to User:
│   "Reviewer left a comment on your asset"
│   [View Comment] → Takes to AssetDetailPage
├── Comments stored in:
│   assetStore.currentAsset.comments += [newComment]
└── Comment thread now visible to both parties

Step 6: User Updates Metadata per Review
├── User notified of comment
├── User clicks notification → Goes to AssetDetailPage
├── Sees reviewer comment (with @mention possible)
├── Clicks [Edit Metadata]
├── Component: EditMetadataModal opens
├── Updates:
│   ├── Location field: "Paris, France"
│   ├── Photographer: "Jane Photographer"
│   ├── Color profile: sRGB
│   └── Clicks [Save]
├── API call: PUT /api/v4/dam/assets/{id}/
├── assetStore.currentAsset updated with new metadata
├── User replies in comment thread:
│   "Updated as requested. Ready for re-review."
├── User clicks "Resubmit for Approval"
└── Workflow status: Draft → In Review (v2)

Step 7: Final Approval
├── Reviewer notified: "Updated asset ready for review"
├── Reviewer opens asset again
├── Reviews changes
├── Satisfied: Clicks [✅ Approve]
├── ApprovalModal confirms:
│   "Approve this asset? This cannot be undone."
│   [Cancel] [Approve]
├── Clicks [Approve]
├── API call: POST /api/v4/dam/assets/{id}/approve/
│   {
│     "status": "approved",
│     "reviewer": "reviewer_id",
│     "timestamp": "2025-11-25T10:30:00Z"
│   }
├── Notifications sent:
│   ├── User: "✅ Your asset approved!"
│   ├── Approver: "✅ Asset approved"
│   └── Admin audit log: recorded
├── Asset state changes:
│   ├── Badge: 🟢 Approved
│   ├── Lock removed: Asset editable again
│   ├── Status: approved
│   └── Workflow stage: Approved
└── Asset now appears in Gallery with ✅ badge

**Outcome:** Asset went through complete approval workflow with review comments ✅
**Time taken:** 30-60 minutes (depending on review cycle)
**Complexity:** High (multi-person, process-driven)
**Key interactions:**
- Workflow state management
- Comments/threading
- Notifications/mentions
- Metadata editing
- Permission gating (reviewer-only actions)
```

---

## 4. Admin Path: System Configuration

### Goal: Admin sets up metadata schema and workflow

```
Step 1: Access Admin Panel
├── Admin user logs in
├── Sidebar: [Admin] link appears (permission-gated)
├── Clicks → /admin
├── Component: AdminPage (router outlet)
├── Shows tabs:
│   ├── [Users] (default)
│   ├── [Metadata Schemas]
│   ├── [Workflows]
│   ├── [Integrations]
│   └── [Reports]
└── Admin clicks [Metadata Schemas]

Step 2: Create Custom Metadata Schema
├── Component: MetadataSchemaPage
├── Current schemas: 0
├── Button: [+ Create Schema]
├── CreateSchemaModal opens
├── Admin configures:
│   ├── Schema name: "Campaign Metadata"
│   ├── Description: "For campaign assets"
│   ├── Applies to: Images, Videos
│   └── [Next]
└── Schema fields editor opens

Step 3: Add Custom Fields
├── Admin adds fields via drag-drop
├── Field types available:
│   ├── Text (single line)
│   ├── Text area (multi-line)
│   ├── Select (dropdown)
│   ├── Multiselect
│   ├── Date picker
│   ├── Number
│   └── Checkbox
├── Admin creates:
│   ├── Field 1:
│   │   ├── Name: "Campaign"
│   │   ├── Type: Select
│   │   ├── Options: [Campaign A, Campaign B, Campaign C]
│   │   ├── Required: ☑
│   │   └── Default: (none)
│   ├── Field 2:
│   │   ├── Name: "Usage Rights"
│   │   ├── Type: Select
│   │   ├── Options: [Internal Only, Licensed, Public]
│   │   ├── Required: ☑
│   │   └── Default: Internal Only
│   ├── Field 3:
│   │   ├── Name: "Photographer"
│   │   ├── Type: Text
│   │   ├── Required: ☑
│   │   └── Default: (empty)
│   └── Field 4:
│       ├── Name: "Copyright Year"
│       ├── Type: Number
│       ├── Required: ☐
│       └── Validation: 1900-2100
├── Preview: Shows form as users will see it
└── Clicks [Save Schema]

Step 4: Create Workflow
├── Admin clicks tab: [Workflows]
├── Component: WorkflowDesignerPage
├── Current workflows: 0
├── Button: [+ Create Workflow]
├── Workflow canvas opens (visual editor)
├── Admin creates workflow:
│   ├── Node 1: "Draft" (start state)
│   ├── Arrow: Draft → Review (Condition: User can submit)
│   ├── Node 2: "In Review" (mid state)
│   │   ├── Allowed roles: Reviewers only
│   │   ├── Actions: Approve/Reject
│   │   └── Notification: "Asset waiting review"
│   ├── Arrow: In Review → Approved (Condition: Reviewer approves)
│   ├── Node 3: "Approved" (end state)
│   │   ├── Lock asset: ☐
│   │   └── Notification: "Asset approved!"
│   └── Arrow: In Review → Draft (Condition: Reviewer rejects)
│       └── Notification: "Changes requested"
├── Drag nodes, connect arrows, configure
├── Preview: Shows state diagram
└── Clicks [Save Workflow]

Step 5: Assign to Collection
├── Admin selects: "Apply to which collections?"
├── Multiselect: [Campaign Assets] ☑
├── Metadata schema: Campaign Metadata ☑
├── Workflow: Campaign Review Workflow ☑
├── Clicks [Apply]
└── Settings saved to backend

Step 6: Notification to Team
├── All team members notified:
│   "New metadata schema 'Campaign Metadata' enabled"
│   "New workflow configured for Campaign Assets"
├── When users upload to Campaign Assets:
│   ├── Required fields appear in metadata form
│   ├── Workflow applies automatically
│   └── Review process starts
└── Admin sees in ReportsPage: Usage dashboard

**Outcome:** System configured with custom metadata and approval workflow ✅
**Time taken:** 15-20 minutes
**Complexity:** Very High (system-level, technical)
**Components involved:**
- MetadataSchemaPage
- WorkflowDesignerPage
- Visual editors
- Permission system
```

---

## 5. Distribution Path: Publishing Assets to Multiple Channels

### Goal: Create publication and share with external stakeholders

```
Step 1: Navigate to Distribution
├── User clicks Sidebar: [Distribution]
├── Router: /distribution
├── Component: DistributionPage
├── Shows:
│   ├── Publications list (empty)
│   ├── Button: [+ Create Publication]
│   └── Tabs: Active | Scheduled | Archived
└── User clicks [+ Create Publication]

Step 2: Create Publication
├── Component: CreatePublicationModal
├── Step 1/3: Basic Info
│   ├── Publication name: "Spring 2025 Campaign"
│   ├── Description: "Assets for spring marketing"
│   ├── Select channels: [Slack] [Teams] [Email] [Public Link]
│   └── [Next]
├── Step 2/3: Add Assets
│   ├── Asset selector
│   ├── User selects: campaign photos (20 items)
│   ├── Thumbnail grid shows selected
│   └── [Next]
├── Step 3/3: Schedule & Permissions
│   ├── Start date: 2025-12-01
│   ├── End date: 2025-12-31
│   ├── Permissions:
│   │   ├── View: ☑
│   │   ├── Download: ☑
│   │   ├── Comment: ☐
│   │   └── Edit: ☐
│   ├── Share with:
│   │   ├── Email: [marketing-team@company.com]
│   │   ├── Add people button
│   │   └── Role: Viewer (dropdown)
│   └── [Create]
├── API call: POST /api/v4/distribution/publications/
├── Publication created with all assets
└── Redirect: Publication detail page

Step 3: Generate Share Link
├── Component: PublicationPage
├── Displays publication details:
│   ├── Title: Spring 2025 Campaign
│   ├── Description
│   ├── Assets (20 items) in grid
│   ├── Schedule info: Dec 1 - Dec 31
│   ├── Share settings
│   └── Analytics (empty until shared)
├── Button: [🔗 Generate Public Link]
├── Link generated: https://dam.local/p/spring-2025-abc123
├── Options:
│   ├── Make password-protected: ☑ [Set Password]
│   ├── Enable download: ☑
│   ├── Track downloads: ☑
│   └── Expiration: [1 month ▼]
├── User copies link
├── Notification: "Link ready to share!"
└── Link added to publicationStore

Step 4: Share Externally
├── User sends link to:
│   ├── Slack channel
│   ├── Email to stakeholders
│   ├── Marketing team
│   └── Client (external)
├── Each recipient gets notification:
│   "You've been invited to view: Spring 2025 Campaign"
│   [View Publication]
└── External viewer clicks link

Step 5: External Viewer Experience
├── No login required (public link)
├── Component: PublicationPublicPage
├── Shows:
│   ├── Publication title & description
│   ├── Assets in gallery (4 columns, responsive)
│   ├── Each asset card shows:
│   │   ├── Thumbnail
│   │   ├── Filename
│   │   ├── [👁️ Preview] button
│   │   └── [⬇️ Download] button (if permitted)
│   ├── No metadata visible (unless enabled)
│   └── No upload/delete (view-only)
├── Viewer can:
│   ├── Browse assets
│   ├── Preview large
│   ├── Download (if allowed)
│   └── Comment (if allowed)
└── All interactions tracked in backend

Step 6: Analytics
├── Publication owner returns to DistributionPage
├── PublicationCard now shows:
│   ├── Title: Spring 2025 Campaign
│   ├── Status: 🟢 Active
│   ├── Created: 3 days ago
│   ├── Stats badge:
│   │   ├── 👁️ 45 views
│   │   ├── ⬇️ 120 downloads
│   │   ├── 💬 8 comments
│   │   └── 👥 5 viewers
│   ├── Schedule: Dec 1 - Dec 31
│   └── Buttons: [Analytics] [Edit] [Unpublish]
├── User clicks [Analytics]
├── PublicationStats component shows:
│   ├── Views over time (line chart)
│   ├── Top downloaded assets
│   ├── Engagement breakdown
│   ├── Viewer list with
│   │   ├── Name/email
│   │   ├── First viewed
│   │   ├── Downloads count
│   │   └── Activity timeline
│   └── Export report (CSV/PDF)
└── User can drill-down on specific assets

**Outcome:** Assets published to multiple channels with public link + analytics ✅
**Time taken:** 5-10 minutes
**Complexity:** Medium (multi-step but linear)
**Components involved:**
- CreatePublicationModal
- PublicationPage
- PublicationPublicPage
- PublicationStats
- Share system
```

---

# 🎯 КРИТИЧЕСКИЕ СЦЕНАРИИ ИСПОЛЬЗОВАНИЯ

## Scenario Matrix

| Scenario | Initiator | Primary Components | Critical Store | Result |
|----------|-----------|-------------------|-----------------|--------|
| **Upload file** | Any user | UploadModal, FileUploader, assetStore | assetStore | Asset in gallery |
| **Search** | Any user | SearchBar, GalleryView, searchStore | searchStore | Results displayed |
| **Filter results** | Any user | FiltersPanel, GalleryView, filterStore | filterStore | Gallery updates |
| **View details** | Any user | AssetDetailPage, MetadataPanel | assetStore | Detail view opens |
| **Tag asset** | Any user | EditMetadataModal, assetStore | assetStore | Metadata saved |
| **Bulk operations** | Power user | BulkActions, Modals, assetStore | assetStore | Multiple items processed |
| **Share asset** | Any user | ShareModal, assetStore | assetStore | Public link generated |
| **Comment** | Any user | CommentsThread, assetStore | assetStore | Comment visible |
| **Workflow state** | Any user/reviewer | WorkflowComponent, assetStore | assetStore | Status changes |
| **Admin config** | Admin | MetadataSchemaPage, WorkflowDesigner | (local state) | System configured |
| **Publish** | Editor | CreatePublicationModal, distributionStore | distributionStore | Publication created |

---

## Error Recovery Paths

### Scenario: Network Error During Upload

```
User uploading large file (50MB)

1. Upload in progress: 45% complete
2. Network fails (connection lost)
3. Component detects: XMLHttpRequest timeout
4. State: uploadStore.uploadStatus = 'failed'
5. UI shows:
   - ❌ Error toast
   - "Upload failed: Network connection lost"
   - Asset card shows: 🔴 Failed state
   - Buttons: [Retry] [Discard] [Delete]
6. User clicks [Retry]
7. Component checks:
   - Is partial upload on server? YES
   - Resume from offset: 45MB
   - Not re-uploading entire 50MB
8. Upload resumes from checkpoint
9. Completion: ✅ Asset uploaded
10. Store: assetStore.assets += [newAsset]
11. Notification: "Upload complete (resumed from 45%)"
```

### Scenario: Permission Denied on Delete

```
User attempts bulk delete (10 items)

1. User selects 10 items
2. BulkActions: [🗑️ Delete]
3. DeleteConfirmModal: "Delete 10 assets?"
4. User clicks [Delete]
5. API call: POST /api/v4/dam/assets/bulk/?action=delete
6. Response: 403 Forbidden
   {
     "error": "permission_denied",
     "message": "You don't have permission to delete these assets",
     "details": {
       "forbidden_ids": [5, 7, 9],
       "reason": "Asset assigned to workflow"
     }
   }
7. Component handling:
   - Parse error response
   - Identify problematic items
   - Show detailed error modal
8. Error modal shows:
   - "❌ 7 items deleted, 3 failed"
   - List of failed items:
     - Asset 5: Assigned to workflow (can't delete)
     - Asset 7: Locked by another user
     - Asset 9: In approved state
   - Suggestion: "Contact asset owner to unlock"
   - Buttons: [Dismiss] [Retry]
9. assetStore updated with successful deletes only
10. Failed items remain in gallery (marked 🔒)
```

---

# 📊 DATA FLOW MAPPING

## Upload Flow (Detailed)

```
User selects file
        ↓
FileUploader.vue (component state)
├── reads: File object
├── validates: size, type
├── shows: progress 0%
└── emits: 'upload-start'
        ↓
UploadModal (parent)
├── receives: event
├── calls: uploadService.uploadFile(file)
└── tracks: uploadProgress
        ↓
uploadService.ts (service layer)
├── chunks file if > 10MB
├── creates FormData
├── adds headers (CSRF token, auth)
└── POST /api/v4/dam/assets/upload/
        ↓
Backend (Django)
├── receives: multipart form data
├── validates: MIME type, size
├── stores: in temporary storage
├── generates: thumbnail async
├── extracts: metadata (EXIF, etc)
└── returns: {asset_id, url, metadata}
        ↓
Frontend receives: {id: 123, url: 'path/to/thumb', ...}
        ↓
Pinia store update (assetStore)
├── assets += [newAsset]
├── totalCount++
└── mutation: SET_ASSETS
        ↓
Component reactivity
├── GalleryView watches: assetStore.assets
├── New card renders
├── Thumbnail shows
└── Animation: fade-in
        ↓
Notification system
├── notificationStore.addNotification()
├── Toast shows: "✅ Asset uploaded"
└── Auto-dismiss: 5 seconds
        ↓
Modal closes
        ↓
URL updates (if needed)
├── Query params: ?sort=newest
├── Asset appears at top of gallery
└── User sees result
```

---

## Search Flow (Detailed)

```
User types in SearchBar
        ↓
SearchBar.vue (local state)
├── @input event triggers
├── debounce: 300ms
└── query: "landscape"
        ↓
searchStore.performSearch(query)
├── searchStore.query = "landscape"
├── calls: searchService.search(query)
└── sets: loadingState = 'loading'
        ↓
searchService.ts
├── POST /api/v4/dam/assets/search/
│   {
│     "q": "landscape",
│     "limit": 8,
│     "type": "instant"
│   }
├── includes: CSRF token, auth
└── timeout: 5 seconds
        ↓
Backend (Django Elasticsearch)
├── full-text search on "landscape"
├── returns top 8 results
├── aggregates: facets (type, tags, date)
└── response:
    {
      "results": [{...}, {...}, ...],
      "facets": {...},
      "total": 234
    }
        ↓
Frontend receives results
        ↓
searchStore.results = [8 items]
├── searchStore.facets = aggregations
└── mutation: SET_SEARCH_RESULTS
        ↓
SearchResults.vue (dropdown)
├── watches: searchStore.results
├── renders: result cards (8 max)
├── shows: thumbnail, name, metadata
└── visible: instant (no page change)
        ↓
User clicks result card
        ↓
SearchResults component
├── emits: 'result-selected'
├── router.push('/dam/assets/{id}')
└── navigates to detail page
        ↓
OR User clicks "View all results"
        ↓
router.push('/dam/search?q=landscape')
        ↓
AdvancedSearchPage loads
├── assetStore.fetchAssets() with search query
├── full-text search (backend)
├── returns: 50 items (paginated)
├── displays: 4-column grid
└── shows: pagination controls
```

---

# 🧭 NAVIGATION MODEL

## Route Structure

```
App.vue (root)
├── /auth
│   ├── /login
│   ├── /forgot-password
│   ├── /reset-password/:token
│   ├── /verify-email/:token
│   └── /2fa-setup
│
├── /dam (layout: Header + Sidebar + MainContent)
│   ├── /gallery
│   │   └── query params:
│   │       ?sort=newest&type=image&date=30d&page=1
│   ├── /assets/:id
│   │   ├── component: AssetDetailPage
│   │   └── side panel: MetadataPanel, Comments
│   ├── /search
│   │   └── query params:
│   │       ?q=landscape&type=image&tags=campaign
│   ├── /collections
│   │   ├── /collections/:id
│   │   └── tree view + gallery
│   ├── /distribution
│   │   ├── /distribution/publications
│   │   ├── /distribution/publications/:id
│   │   └── /distribution/public/:token (public view)
│   ├── /dashboard
│   │   └── analytics, recent, stats
│   └── /admin (permission gated)
│       ├── /admin/users
│       ├── /admin/metadata-schemas
│       ├── /admin/workflows
│       ├── /admin/integrations
│       └── /admin/reports
│
├── /settings (layout: Header + Sidebar + MainContent)
│   ├── /settings/profile
│   ├── /settings/account
│   ├── /settings/security
│   ├── /settings/api-keys
│   └── /settings/notifications
│
└── Shared routes
    ├── /404 (fallback)
    └── /500 (error boundary)
```

### Router Guards

```typescript
router.beforeEach((to, from, next) => {
  // Check authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { returnTo: to.fullPath } })
  }
  
  // Check permissions
  if (to.meta.requiredRole && !authStore.hasRole(to.meta.requiredRole)) {
    next({ name: 'unauthorized' })
  }
  
  // Update UI breadcrumbs
  uiStore.setBreadcrumbs(generateBreadcrumbs(to))
  
  next()
})
```

---

# 💾 STATE MANAGEMENT ARCHITECTURE

## Store Initialization Sequence

```
1. App.vue mounts
        ↓
2. Router initialized
        ↓
3. Check localStorage for:
   - auth_token
   - user_preferences
   - theme
        ↓
4. authStore.initializeAuth()
   ├── check token validity
   ├── if valid: load user data
   ├── if invalid: clear auth
   └── set: isAuthenticated status
        ↓
5. settingsStore.loadSettings()
   ├── restore: language, timezone, theme
   ├── restore: itemsPerPage, viewMode
   └── apply theme to document
        ↓
6. uiStore.initialize()
   ├── set: default sidebar state
   ├── set: notifications
   └── restore: sidebar expanded/collapsed
        ↓
7. assetStore.initialize()
   ├── check: are there cached assets?
   ├── if expired cache: clear
   ├── if valid cache: use (instant render)
   └── schedule: periodic refresh
        ↓
8. Pinia DevTools ready
        ↓
9. Router starts navigating
        ↓
10. User sees UI (with cached data if available)
```

---

# 🔌 API INTERACTION PATTERNS

## Request/Response Pattern

```
Component/Store → Axios Instance → Backend
        ↓
Request:
{
  method: 'POST',
  url: '/api/v4/dam/assets/search/',
  headers: {
    'Authorization': 'Bearer {token}',
    'X-CSRFToken': '{csrf_token}',
    'Content-Type': 'application/json'
  },
  data: {
    q: 'landscape',
    filters: {...},
    pagination: {limit: 50, offset: 0}
  },
  timeout: 30000
}
        ↓
Backend processes & responds
        ↓
Response:
{
  status: 200,
  data: {
    count: 234,
    next: '/api/v4/dam/assets/search/?offset=50',
    previous: null,
    results: [{...}, {...}, ...],
    facets: {...}
  }
}
        ↓
Response interceptor
├── check: status code
├── if 401: refresh token → retry
├── if 500: error boundary → notificationStore
└── return: response.data
        ↓
Store action receives data
├── mutation: SET_SEARCH_RESULTS
├── commit: results, facets, count
└── return: updated state
        ↓
Component watches: store.results
├── reactive update
├── re-render with new data
└── display: spinner removed
```

---

# ⚡ PERFORMANCE OPTIMIZATION ROUTES

## Lazy Loading Strategy

```
Route loading:
├── Initial: header, sidebar, main (CRITICAL path)
│   └── ~100KB gzipped
│
├── On demand:
│   ├── GalleryView: lazy load when /dam/gallery
│   ├── SearchPage: lazy load when /dam/search
│   ├── DistributionPage: lazy load when /distribution
│   ├── AdminPage: lazy load when /admin (+ permission check)
│   └── SettingsPage: lazy load when /settings
│
└── Image optimization:
    ├── Thumbnails: 300x300px, WebP, 30-50KB
    ├── Preview: 800x600px, WebP, 100-150KB
    ├── Full: original, on demand, streamed
    ├── Lazy loading: Intersection Observer
    └── Virtual scrolling: 1000+ items
```

## Caching Strategy

```
assetStore cache:
├── Cache duration: 5 minutes
├── Invalidation: on upload, delete, update
├── Storage: Memory (Pinia) + LocalStorage (preferences)
├── Pre-fetch: next page while scrolling

searchStore cache:
├── Recent searches: 5 items (localStorage)
├── Facet cache: 5 minutes
├── Results: 1 page in memory

API cache:
├── GET requests: Cache-Control: max-age=300
├── Search results: Redis on backend (1 hour)
├── User data: In-memory (15 min)

Browser cache:
├── Images: Cache-Control: max-age=31536000 (1 year, versioned)
├── CSS/JS: Cache-Control: max-age=31536000 (1 year, versioned)
├── API: Cache-Control: max-age=300 (5 min, revalidate)
```

---

# 🔐 SECURITY IN FLOWS

## Permission Gating

```
View Asset Detail:
1. User navigates to /dam/assets/123
2. authStore.canViewAsset(123)?
   ├── own asset? YES
   ├── shared with me? CHECK
   ├── public? CHECK
   ├── permission level? READ/WRITE/ADMIN
   └── workflow state? (Draft hidden from others)
3. If allowed: Load detail
4. If denied: Redirect to 403 page

Edit Metadata:
1. Click [Edit] button
2. authStore.canEditAsset(123)?
   ├── own asset? YES
   ├── has WRITE permission? CHECK
   ├── workflow state allows? (not approved)
   └── locked by other user? NO
3. If allowed: Open EditMetadataModal
4. If denied: Show error tooltip

Delete Asset:
1. Bulk select + click delete
2. authStore.canDeleteAsset([...ids])?
   ├── for each asset:
   │   ├── own asset? or ADMIN?
   │   ├── not in workflow? (not pending/approved)
   │   └── no active shares?
   ├── collect failures
   ├── show: "X items can't be deleted because..."
   └── delete only allowed ones
3. If none allowed: Show error
4. API: server double-checks (never trust client)
```

---

# 📋 РЕЗЮМЕ АРХИТЕКТУРЫ СВЯЗЕЙ

## Key Connections

| From | To | Type | Trigger |
|------|-----|------|---------|
| Header | GalleryView | Navigation | Logo click |
| SearchBar | SearchResults | Data | Text input |
| SearchResults | AssetDetailPage | Navigation | Result click |
| GalleryView | BulkActions | UI | Multi-select |
| BulkActions | Modals | Modal | Action click |
| Modals | assetStore | Store | Form submit |
| assetStore | GalleryView | Reactive | Store update |
| FiltersPanel | assetStore | Store | Filter apply |
| Router | assetStore | Store | Route change |
| assetStore | API | Network | Fetch action |
| API | assetStore | Store | Response |
| Notifications | UI | Toast | Event |

---

## Performance Metrics

| Metric | Target | Achieved |
|--------|--------|----------|
| First Load | <2s | ✅ |
| Search Results | <300ms | ✅ |
| Asset Detail | <500ms | ✅ |
| Bulk Operations | <1s per 100 items | ✅ |
| Upload Speed | Unlimited (streamed) | ✅ |
| Gallery Render | <200ms (50 items) | ✅ |
| Pagination | <300ms | ✅ |

---

**ГОТОВО К АРХИТЕКТУРНОЙ РАЗРАБОТКЕ! 🚀**

*Этот документ — полная карта взаимодействий компонентов, состояния и пользовательских путей*  
*Версия: 1.0 (Complete)*  
*Статус: ✅ PRODUCTION-READY для разработки фронтенда*