# 🏗️ АРХИТЕКТУРНОЕ ТЕХНИЧЕСКОЕ ЗАДАНИЕ НА ФРОНТЕНД DAM-СИСТЕМЫ
## Версия 2.0 — Полный мастер-документ для разработки

**Дата:** Ноябрь 2025  
**Версия:** 2.0 (Complete Master Document + Full Audit Integration)  
**Статус:** ✅ Готово к разработке  
**Аудитория:** Cursor AI, Frontend команда, Tech Lead, Архитекторы  
**Язык:** Русский  

---

## 📑 ОГЛАВЛЕНИЕ (ПОЛНОЕ)

1. [Резюме проекта](#резюме-проекта)
2. [Анализ текущего состояния](#анализ-текущего-состояния)
3. [Видение нового фронтенда](#видение-нового-фронтенда)
4. [Технический стек](#технический-стек)
5. [Design System](#design-system)
6. [Структура проекта](#структура-проекта)
7. [Страницы и компоненты](#страницы-и-компоненты)
8. [Дополнительные критические страницы и окна](#дополнительные-критические-страницы-и-окна)
9. [API интеграция](#api-интеграция)
10. [Требования по производительности](#требования-по-производительности)
11. [План реализации (12 недель)](#план-реализации-12-недель)
12. [Критерии готовности](#критерии-готовности)
13. [Промпты для Cursor AI](#промпты-для-cursor-ai)
14. [Расширенные сценарии и edge cases](#расширенные-сценарии-и-edge-cases)

---

# 🎯 РЕЗЮМЕ ПРОЕКТА

## Проблема
Текущий фронтенд DAM-системы использует **устаревший Bootstrap 3** (EOL 2019) с jQuery. Это создает проблемы:
- 📉 Низкая оценка UX: 2.7/5 ⭐
- 🚫 Отсутствие modern паттернов (Gallery View, Smart Search)
- 📱 Плохой мобильный опыт
- 🐌 Производительность: 2.7s load time
- ⚠️ **Критические API проблемы безопасности**

## Цель
Трансформировать фронтенд в **современную DAM-платформу уровня Bynder/Canto** с:
- ✅ Vue.js 3 + Tailwind CSS
- ✅ Gallery-first интерфейс
- ✅ Smart Search + Faceted Filters
- ✅ Mobile-first responsive design
- ✅ Light + Dark themes
- ✅ WCAG 2.1 AA accessibility
- ✅ Performance < 2s load time

## Объем
- **Временной горизонт:** 12 недель
- **Модули:** DAM (основной), Distribution, Dashboard, Settings, Admin
- **Технологии:** Vue.js 3, TypeScript, Tailwind CSS, Pinia, Axios
- **Параллельный запуск:** Старый UI + новый UI (migration period)
- **Команда:** 2-3 разработчика + 1 UI/UX дизайнер

## Метрики успеха
| Метрика | Текущее состояние | Целевое значение |
|---------|------------------|------------------|
| Page Load Time | 2.7s | < 2s |
| Lighthouse Score | 45/100 | 90+/100 |
| Accessibility | 2/5 | WCAG 2.1 AA |
| Mobile Support | 40% | 100% |
| API Response Time | 1-2s | < 500ms |
| User Satisfaction | 2.7/5 ⭐ | 4.5+/5 ⭐ |

---

# 📊 АНАЛИЗ ТЕКУЩЕГО СОСТОЯНИЯ

## Текущая архитектура
```yaml
Frontend Stack:
  - Framework: Bootstrap 3.4.1 (EOL 2019) ❌
  - JS Library: jQuery 3.6.0
  - Icons: FontAwesome 5.15.4
  - Rendering: Server-side (Django templates)
  - Navigation: Partial AJAX + Inline JS

Backend API:
  - Endpoints: /api/v4/ + /digital-assets/api/
  - Format: Inconsistent (HTML + JSON mixed) ❌
  - Authentication: Session-based
  - Pagination: Missing ❌ (returns all data)
  - Validation: Minimal ❌ (security issues)

Performance:
  - Load time: 2.7s
  - Lighthouse: 45/100
  - API response: 1-2s
```

## Критические проблемы

| # | Проблема | Критичность | Тип | Решение |
|---|----------|-------------|------|---------
| 1 | Bootstrap 3 EOL | 🔴 P0 | Frontend | Migrate to Vue.js + Tailwind |
| 2 | DAM Document Detail: No Auth | 🔴 P0 SECURITY | API | Add @permission_classes |
| 3 | No input validation | 🔴 P0 SECURITY | API | Add serializer validation |
| 4 | No pagination | 🔴 P0 PERFORMANCE | API | Add PageNumberPagination |
| 5 | HTML in JSON responses | 🔴 P0 | API | JSON-only responses |
| 6 | N+1 queries | 🔴 P1 | API | select_related/prefetch_related |
| 7 | No Gallery View | 🔴 P1 | Frontend | Create gallery component |
| 8 | Search at bottom | 🔴 P1 | Frontend | Move to header + smart search |
| 9 | No mobile support | 🔴 P1 | Frontend | Mobile-first responsive |
| 10 | Accordion navigation | 🟡 P2 | Frontend | Flat sidebar structure |

## Benchmarking конкурентов

**Bynder (Leader):**
- Load time: < 1.5s ✅
- Gallery view: 6-8 columns responsive ✅
- Smart search: NLP + image search ✅
- Mobile: Full parity ✅
- Themes: Light + Dark ✅
- Accessibility: WCAG 2.1 AAA ✅

**Canto (Mid-market):**
- Load time: < 2s ✅
- Gallery view: 4 columns ✅
- Smart search: Basic facets ✅
- Mobile: Responsive ✅

**Наша цель:** Bynder-level качество с Canto-level простотой ✅

---

# 🎨 ВИДЕНИЕ НОВОГО ФРОНТЕНДА

## Архитектура высокого уровня

```
┌─────────────────────────────────────────────────────────┐
│        Vue 3 + TypeScript + Tailwind CSS Frontend        │
│  (Components Library: 20+ reusable, Storybook ready)    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Header (Fixed 64px)                 │   │
│  │ Logo │ Smart Search │ Upload │ Filters │ User   │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────┬──────────────────────────────────────┐   │
│  │          │                                      │   │
│  │ Sidebar  │         Main Content Area            │   │
│  │ (280px)  │  • Gallery View (responsive grid)    │   │
│  │          │  • List View (table with thumbnail)  │   │
│  │ Fixed    │  • Asset Detail (preview + metadata) │   │
│  │ Left     │  • Distribution (publications)       │   │
│  │          │  • Dashboard (analytics)             │   │
│  │          │  • Settings (preferences)            │   │
│  │          │                                      │   │
│  └──────────┴──────────────────────────────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
                         ↕
              State Management (Pinia)
              HTTP Client (Axios)
              Real-time (WebSocket)
                         ↕
         ┌───────────────────────────────┐
         │   Django REST API v4          │
         │  (Fixed + Optimized)          │
         │  • Auth enabled on all        │
         │  • Serializer validation      │
         │  • Paginated responses        │
         │  • JSON-only format           │
         │  • Optimized queries          │
         └───────────────────────────────┘
```

## Ключевые улучшения

| Аспект | Было | Стало | Улучшение |
|--------|------|-------|---------:|
| **Поиск** | Внизу страницы | В топ-баре с instant search | +300% видимость |
| **Медиа просмотр** | Таблица с именами | Gallery grid (4 колонки) | Visual-first |
| **Фильтры** | Accordion меню | Sidebar facets | +60% удобство |
| **Навигация** | Сложная иерархия | Плоская структура | -40% кликов |
| **Мобильность** | Хрупкая адаптивность | Mobile-first responsive | Full parity |
| **Темы** | Только светлая | Light + Dark | Modern UX |
| **Accessibility** | 2/5 | WCAG 2.1 AA | Production-ready |
| **Performance** | 2.7s load | < 2s load | +30% скорость |

---

# 🛠️ ТЕХНИЧЕСКИЙ СТЕК

## Frontend Dependencies

```yaml
Core Framework:
  vue: ^3.4.0                    # SPA framework
  typescript: ^5.3.0             # Type safety
  vite: ^5.0.0                   # Build tool

UI & Styling:
  tailwindcss: ^3.4.0            # Utility-first CSS
  @headlessui/vue: ^1.7.0        # Headless components
  heroicons: ^2.1.0              # Icon library (24x24px)

State Management:
  pinia: ^2.1.0                  # Store management
  pinia-plugin-persistedstate: ^2.1.0  # Auto-save state

HTTP & Data:
  axios: ^1.6.0                  # HTTP client
  qs: ^6.11.0                    # Query string parser

Routing:
  vue-router: ^4.2.0             # Client-side routing
  vue-router-layout: ^0.0.0      # Layout wrapper

Forms & Validation:
  vee-validate: ^4.11.0          # Form validation
  yup: ^1.3.0                    # Schema validation

Real-time:
  socket.io-client: ^4.7.0       # WebSocket client
  universal-cookie: ^4.0.0       # Cookie handling

Performance:
  @vueuse/core: ^10.7.0          # Vue composition utilities
  @vueuse/router: ^10.7.0        # Router integration
  vue-virtual-scroller: ^2.1.0   # Virtual scrolling

Testing:
  vitest: ^1.0.0                 # Unit testing
  @testing-library/vue: ^8.0.0   # Vue component testing
  @playwright/test: ^1.40.0      # E2E testing
  msw: ^2.0.0                    # API mocking

Development:
  eslint: ^8.55.0                # Linting
  prettier: ^3.1.0               # Code formatting
  @typescript-eslint/eslint-plugin: ^6.13.0
  husky: ^8.0.0                  # Git hooks
  lint-staged: ^15.2.0           # Pre-commit linting
  storybook: ^7.6.0              # Component documentation

Build Optimization:
  compression: ^1.7.0            # Gzip compression
  sharp: ^0.33.0                 # Image optimization
  vite-plugin-compression: ^0.5.0
```

## Backend Requirements (API Fixes)

```yaml
Framework: Django 4.2+
REST Framework: djangorestframework 3.14+
CORS: django-cors-headers 4.3+
Database: PostgreSQL 14+
Cache: Redis 7.0+
Async: Celery 5.3+ + RabbitMQ

CRITICAL FIXES:
  ✅ Add authentication to ALL endpoints
  ✅ Add serializer validation to ALL inputs
  ✅ Add pagination to ALL list endpoints
  ✅ Return JSON-only (no HTML in responses)
  ✅ Optimize queries (select_related, prefetch_related)
  ✅ Add rate limiting for bulk operations
```

## Development Environment

```yaml
Node.js: 18.0+ LTS
npm: 9.0+ (or pnpm 8.0+)
Python: 3.10+
PostgreSQL: 14+
Redis: 7.0+
Docker: Latest stable

IDE: VS Code + Extensions:
  - Volar (Vue 3 support)
  - TypeScript Vue Plugin
  - ESLint
  - Prettier
  - Thunder Client (API testing)
  - Better Comments
```

---

# 🎨 DESIGN SYSTEM (ПОЛНЫЙ)

## Color Palette

### Light Mode
```yaml
Primary Colors:
  primary-0: #0052CC          # Deep Blue (buttons, links)
  primary-50: #EBF5FF         # Light Blue (backgrounds)
  primary-100: #C7E0FF        # Light Blue
  primary-500: #0052CC        # Primary (main action)
  primary-600: #0042A8        # Darker blue (hover)

Neutral Colors:
  neutral-0: #FFFFFF          # White (surfaces)
  neutral-50: #F9FAFB         # Almost white
  neutral-100: #F3F4F6        # Light gray (backgrounds)
  neutral-300: #E1E4E8        # Medium gray (borders)
  neutral-600: #4B5563        # Medium gray (secondary text)
  neutral-900: #111827        # Dark gray (text)

Semantic Colors:
  success: #10B981            # Green
  warning: #F59E0B            # Amber
  error: #EF4444              # Red
  info: #06B6D4               # Cyan

Accent:
  accent-primary: #00875A     # Green (success)
  accent-secondary: #4C8CFF   # Light blue (secondary)
```

### Dark Mode
```yaml
Primary Colors:
  primary-0: #4C8CFF          # Light blue
  primary-50: #1F3A7A         # Dark blue
  primary-500: #4C8CFF        # Primary (main action)
  primary-600: #5D96FF        # Lighter blue (hover)

Neutral Colors:
  neutral-0: #1F2937          # Dark gray (surfaces)
  neutral-50: #111827         # Darker gray
  neutral-100: #374151        # Medium dark gray (backgrounds)
  neutral-300: #6B7280        # Medium gray (borders)
  neutral-600: #E5E7EB        # Light gray (secondary text)
  neutral-900: #F9FAFB        # Almost white (text)

Semantic Colors:
  success: #00C853            # Light green
  warning: #FFB81C            # Light amber
  error: #FF6B6B              # Light red
  info: #00BFD9               # Light cyan

Accent:
  accent-primary: #00C853     # Light green (success)
  accent-secondary: #4C8CFF   # Light blue (secondary)
```

## Typography

```yaml
Font Family:
  primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif
  mono: 'Berkeley Mono', 'Menlo', 'Monaco', 'Courier New', monospace

Font Sizes:
  xs: 11px (0.6875rem)
  sm: 12px (0.75rem)
  base: 14px (0.875rem)
  lg: 16px (1rem)
  xl: 18px (1.125rem)
  2xl: 20px (1.25rem)
  3xl: 24px (1.5rem)
  4xl: 32px (2rem)

Font Weights:
  normal: 400
  medium: 500
  semibold: 600
  bold: 700

Line Heights:
  tight: 1.2
  normal: 1.5
  relaxed: 1.75

Heading Styles:
  H1: 32px / 600 weight / 1.2 line-height (Display)
  H2: 24px / 600 weight / 1.2 line-height (Page title)
  H3: 20px / 600 weight / 1.2 line-height (Section)
  H4: 16px / 600 weight / 1.5 line-height (Subsection)

Body Styles:
  Regular: 14px / 400 weight / 1.5 line-height
  Emphasis: 14px / 600 weight / 1.5 line-height
  Small: 12px / 400 weight / 1.5 line-height
  Mono: 12px / 400 weight / 1.5 line-height (monospace)
```

## Spacing & Layout

```yaml
Base Unit: 8px (Tailwind default)

Spacing Scale:
  0: 0px
  1: 4px         (0.25rem)
  2: 8px         (0.5rem)
  3: 12px        (0.75rem)
  4: 16px        (1rem)
  5: 20px        (1.25rem)
  6: 24px        (1.5rem)
  8: 32px        (2rem)
  10: 40px       (2.5rem)
  12: 48px       (3rem)
  16: 64px       (4rem)

Key Dimensions:
  header-height: 64px (fixed)
  sidebar-width-expanded: 280px
  sidebar-width-collapsed: 64px
  sidebar-toggle-duration: 300ms
  container-max-width: 1280px
  grid-gap: 16px (between items)
  card-padding: 16px
  section-padding: 20px
  page-padding: 24px

Responsive Breakpoints:
  sm: 640px (phones)
  md: 768px (tablets)
  lg: 1024px (desktops)
  xl: 1280px (large screens)
  2xl: 1536px (very large screens)

Grid System:
  Desktop: 4 columns (gallery), 12 columns (flexible)
  Tablet (md): 2 columns (gallery)
  Mobile (sm): 1 column (gallery)
```

## Shadows & Elevation

```yaml
Shadow Tokens:
  shadow-none: 0px 0px 0px transparent
  shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05)
  shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)
  shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)
  shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)
  shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)
  shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25)

Elevation Map:
  Base/Surface: shadow-none or shadow-xs
  Cards: shadow-sm (light) / shadow-md (elevated)
  Modals: shadow-xl
  Floating Actions: shadow-lg (with hover shadow-xl)
  Notifications: shadow-lg
```

## Border Radius

```yaml
Radius Scale:
  none: 0px
  sm: 4px
  base: 6px
  md: 8px
  lg: 12px
  xl: 16px
  2xl: 20px
  full: 9999px (circles)

Component Usage:
  Buttons: radius-base (6px)
  Inputs: radius-base (6px)
  Cards: radius-lg (12px)
  Modals: radius-lg (12px)
  Dialogs: radius-lg (12px)
  Avatars: radius-full (circles)
  Tags/Pills: radius-full (pill-shaped)
  Images: radius-base (6px)
```

## Animations & Transitions

```yaml
Duration:
  fast: 150ms
  normal: 250ms (default)
  slow: 350ms
  slower: 500ms

Timing Functions:
  ease-in: cubic-bezier(0.4, 0, 1, 1)
  ease-out: cubic-bezier(0, 0, 0.2, 1)
  ease-in-out: cubic-bezier(0.4, 0, 0.2, 1)
  ease-linear: linear

Key Animations:
  Fade in/out: opacity 250ms ease-in-out
  Slide in/out: transform translateX/Y 250ms ease-out
  Scale: transform scale 250ms ease-out
  Rotate: transform rotate 300ms ease-out
  Skeleton loading: opacity pulse 1s ease-in-out infinite
  Button hover: all 150ms ease-out

Transition Defaults:
  - All state changes: 150-250ms ease-out
  - Modal open/close: 300ms ease-in-out
  - Sidebar collapse: 300ms ease-in-out
  - Page transitions: 200ms fade
  - Hover states: 150ms
  - Focus states: 0ms (instant)
```

---

# 📁 СТРУКТУРА ПРОЕКТА

```
dam-frontend-vue3/
│
├── public/                          # Статические файлы
│   ├── favicon.ico
│   ├── robots.txt
│   └── manifest.json
│
├── src/
│   ├── components/                  # Переиспользуемые компоненты
│   │   ├── Layout/
│   │   │   ├── Header.vue          # Топ-бар с поиском
│   │   │   ├── Sidebar.vue         # Боковая навигация
│   │   │   ├── MainContent.vue     # Контент область
│   │   │   └── Footer.vue          # Нижний колонтитул
│   │   │
│   │   ├── Common/
│   │   │   ├── Button.vue          # Base button component
│   │   │   ├── Input.vue           # Text input field
│   │   │   ├── Select.vue          # Dropdown select
│   │   │   ├── Modal.vue           # Dialog/Modal
│   │   │   ├── Pagination.vue      # Pagination controls
│   │   │   ├── Badge.vue           # Status badge
│   │   │   ├── Skeleton.vue        # Loading skeleton
│   │   │   ├── Spinner.vue         # Loading spinner
│   │   │   ├── Alert.vue           # Alert message
│   │   │   ├── Tooltip.vue         # Tooltip
│   │   │   ├── Card.vue            # Card container
│   │   │   ├── FileUploader.vue    # Drag-drop upload
│   │   │   ├── ImageCropper.vue    # Image crop/rotate
│   │   │   ├── TagInput.vue        # Autocomplete tags
│   │   │   ├── DateRangePicker.vue # Date range selector
│   │   │   ├── PermissionSelector.vue # Role picker
│   │   │   ├── Breadcrumb.vue      # Navigation trail
│   │   │   ├── ContextMenu.vue     # Right-click menu
│   │   │   ├── ErrorBoundary.vue   # JS error catcher
│   │   │   ├── EmptyState.vue      # No data placeholder
│   │   │   ├── ProgressBar.vue     # Progress indicator
│   │   │   ├── ColorPicker.vue     # Color selector
│   │   │   ├── Accordion.vue       # Collapsible sections
│   │   │   ├── Tabs.vue            # Tab navigation
│   │   │   ├── Dropdown.vue        # Action menu
│   │   │   ├── Popover.vue         # Tooltip with actions
│   │   │   ├── Avatar.vue          # User profile pic
│   │   │   ├── FilePreview.vue     # Document viewer
│   │   │   ├── Timeline.vue        # Timeline display
│   │   │   └── Notification.vue    # Toast message
│   │   │
│   │   ├── DAM/
│   │   │   ├── GalleryView.vue     # Gallery grid (main view)
│   │   │   ├── ListView.vue        # Table view
│   │   │   ├── AssetCard.vue       # Asset card component
│   │   │   ├── AssetDetail.vue     # Detail page
│   │   │   ├── MetadataPanel.vue   # Right metadata sidebar
│   │   │   ├── SearchBar.vue       # Smart search input
│   │   │   ├── SearchResults.vue   # Results dropdown
│   │   │   ├── FiltersPanel.vue    # Left filters sidebar
│   │   │   ├── BulkActions.vue     # Bulk toolbar
│   │   │   ├── UploadDropZone.vue  # Drag-drop upload
│   │   │   └── FilterTags.vue      # Active filters display
│   │   │
│   │   ├── Distribution/
│   │   │   ├── PublicationList.vue      # Publications view
│   │   │   ├── PublicationCard.vue      # Publication card
│   │   │   ├── PublicationForm.vue      # Create/edit form
│   │   │   └── PublicationStats.vue     # Analytics
│   │   │
│   │   ├── Dashboard/
│   │   │   ├── StatsCard.vue       # KPI card
│   │   │   ├── ChartWidget.vue     # Chart component
│   │   │   ├── ActivityFeed.vue    # Recent activity
│   │   │   └── StorageMetrics.vue  # Storage breakdown
│   │   │
│   │   ├── Modals/
│   │   │   ├── UploadModal.vue
│   │   │   ├── ShareModal.vue
│   │   │   ├── DeleteConfirmModal.vue
│   │   │   ├── AssetPreviewModal.vue
│   │   │   ├── EditMetadataModal.vue
│   │   │   ├── CreatePublicationModal.vue
│   │   │   ├── CreateCollectionModal.vue
│   │   │   ├── MoveAssetsModal.vue
│   │   │   ├── BulkTagModal.vue
│   │   │   ├── VersionHistoryModal.vue
│   │   │   ├── ExportModal.vue
│   │   │   ├── InviteUserModal.vue
│   │   │   ├── CreateWorkflowModal.vue
│   │   │   ├── CropImageModal.vue
│   │   │   └── NotificationCenterModal.vue
│   │   │
│   │   └── AI/
│   │       ├── TagSuggestions.vue  # AI tag suggestions
│   │       ├── AnalysisResults.vue # Analysis display
│   │       └── AIInsights.vue      # AI insights panel
│   │
│   ├── pages/                       # Page/route components
│   │   ├── DashboardPage.vue       # Home page
│   │   ├── DAMPage.vue             # DAM module page
│   │   ├── AssetDetailPage.vue     # Asset detail page
│   │   ├── DistributionPage.vue    # Distribution module
│   │   ├── AdminPage.vue           # Admin settings
│   │   ├── SettingsPage.vue        # User settings
│   │   ├── LoginPage.vue           # Authentication
│   │   ├── UserManagementPage.vue  # Admin: Users
│   │   ├── MetadataSchemaPage.vue  # Admin: Schemas
│   │   ├── WorkflowDesignerPage.vue # Admin: Workflows
│   │   ├── AdvancedSearchPage.vue  # Full search page
│   │   ├── CollectionsPage.vue     # User collections
│   │   ├── ReportsPage.vue         # Analytics & reports
│   │   ├── ProfilePage.vue         # User profile
│   │   └── NotFoundPage.vue        # 404 page
│   │
│   ├── stores/                      # Pinia stores
│   │   ├── assetStore.ts           # Asset state (list, detail, etc)
│   │   ├── searchStore.ts          # Search state (query, filters)
│   │   ├── uiStore.ts              # UI state (sidebar, theme, etc)
│   │   ├── authStore.ts            # Auth state (user, permissions)
│   │   ├── filterStore.ts          # Filter state
│   │   ├── notificationStore.ts    # Notifications state
│   │   └── settingsStore.ts        # App settings
│   │
│   ├── services/                    # API & business logic
│   │   ├── apiService.ts           # Base HTTP client (axios)
│   │   ├── assetService.ts         # Asset operations
│   │   ├── searchService.ts        # Search operations
│   │   ├── distributionService.ts  # Distribution operations
│   │   ├── authService.ts          # Auth operations
│   │   ├── uploadService.ts        # File upload service
│   │   ├── notificationService.ts  # WebSocket notifications
│   │   └── analyticsService.ts     # Analytics/tracking
│   │
│   ├── composables/                 # Vue 3 composition functions
│   │   ├── useAssets.ts            # Fetch + manage assets
│   │   ├── useSearch.ts            # Search operations
│   │   ├── usePagination.ts        # Pagination logic
│   │   ├── useFilters.ts           # Filter management
│   │   ├── useBulkActions.ts       # Bulk operations
│   │   ├── useInfiniteScroll.ts    # Infinite scroll
│   │   ├── useLocalStorage.ts      # Persistent state
│   │   ├── useTheme.ts             # Theme switching
│   │   ├── useResize.ts            # Window resize
│   │   ├── useDebounce.ts          # Debounce utility
│   │   └── useKeyboard.ts          # Keyboard shortcuts
│   │
│   ├── utils/                       # Utility functions
│   │   ├── formatters.ts           # Format dates, sizes, etc
│   │   ├── validators.ts           # Validation rules
│   │   ├── helpers.ts              # General helpers
│   │   ├── constants.ts            # App constants
│   │   ├── mappers.ts              # Data mapping functions
│   │   ├── errors.ts               # Error handling
│   │   └── logger.ts               # Logging utility
│   │
│   ├── directives/                  # Vue directives
│   │   ├── v-click-outside.ts      # Click outside directive
│   │   ├── v-intersection.ts       # Intersection observer
│   │   ├── v-focus.ts              # Auto-focus directive
│   │   └── v-tooltip.ts            # Tooltip directive
│   │
│   ├── styles/
│   │   ├── index.css               # Global styles + Tailwind imports
│   │   ├── tailwind.css            # Tailwind directives
│   │   ├── variables.css           # CSS variables (theme)
│   │   ├── animations.css          # Custom animations
│   │   ├── utilities.css           # Utility classes
│   │   └── globals.css             # Global element styles
│   │
│   ├── types/                       # TypeScript types
│   │   ├── index.ts                # Re-exports all types
│   │   ├── asset.ts                # Asset types
│   │   ├── api.ts                  # API response types
│   │   ├── user.ts                 # User types
│   │   ├── publication.ts          # Publication types
│   │   ├── filter.ts               # Filter types
│   │   └── common.ts               # Common types
│   │
│   ├── router/
│   │   ├── index.ts                # Router configuration
│   │   ├── routes.ts               # Route definitions
│   │   └── guards.ts               # Route guards (auth, etc)
│   │
│   ├── App.vue                      # Root component
│   └── main.ts                      # Entry point
│
├── .cursor/                         # Cursor AI rules & documentation
│   ├── design-system.md             # Color, typography, spacing
│   ├── component-specs.md           # Component specifications
│   ├── api-endpoints.md             # API endpoint documentation
│   └── cursor-rules.md              # Cursor coding standards
│
├── .env.example                     # Environment variables template
├── .eslintrc.cjs                   # ESLint config
├── .prettierrc.json                # Prettier config
├── tsconfig.json                   # TypeScript config
├── tailwind.config.js              # Tailwind config
├── vite.config.ts                  # Vite config
├── vitest.config.ts                # Vitest config
├── package.json                    # Dependencies
├── pnpm-lock.yaml                  # Dependency lock
│
├── tests/
│   ├── unit/                        # Unit tests
│   │   ├── components/
│   │   ├── services/
│   │   ├── stores/
│   │   └── utils/
│   │
│   ├── e2e/                         # E2E tests (Playwright)
│   │   ├── gallery.spec.ts
│   │   ├── search.spec.ts
│   │   ├── upload.spec.ts
│   │   └── auth.spec.ts
│   │
│   └── setup/
│       ├── vitest.setup.ts
│       ├── mocks.ts
│       └── fixtures.ts
│
├── docs/                            # Documentation
│   ├── SETUP.md                    # Setup instructions
│   ├── CONTRIBUTING.md             # Contribution guidelines
│   ├── API.md                      # API integration guide
│   ├── COMPONENTS.md               # Component documentation
│   └── DEPLOYMENT.md               # Deployment guide
│
├── README.md                        # Project overview
├── CHANGELOG.md                     # Version history
└── LICENSE                          # License
```

---

# 📄 СТРАНИЦЫ И КОМПОНЕНТЫ

## 1. Layout Components

### Header (64px Fixed)
```vue
Props: None (layout component)
Emits: 
  - search: (query: string) => void
  - filter-toggle: () => void
  - upload: () => void

Structure:
- Left: Logo (200px)
- Center: Smart Search
- Right: Upload, Filters, Notifications, User menu

Features:
- Fixed positioning (z-index: 50)
- Height exactly 64px
- Responsive: hamburger menu on mobile (sm: 640px)
- Search shortcut: Ctrl+K focus
- Sticky during scroll
- Dark mode support
```

### Sidebar (280px/64px Collapsible)
```
Navigation Items:
1. Dashboard
2. DAM Gallery
3. Distribution
4. AI Insights
5. Settings

Collections:
1. My Uploads
2. Favorites
3. Recent
4. Shared with me

Quick Actions:
- New Folder button

Props: None
Emits:
  - navigate: (path: string) => void
  - sidebar-toggle: () => void

Features:
- Toggle: 280px ↔ 64px
- Transition: 300ms ease-in-out
- Smooth animation
- Icons auto-show on collapse
- Labels hide on collapse
```

### MainContent
```
Props: None
Emits: None

Features:
- Fixed layout below header
- Scrollable content
- Responsive: adjusts for sidebar width
- Dark mode support
```

---

## 2. DAM Module - Gallery View

### GalleryView Component

**Структура:**
```
┌─────────────────────────────────────────┐
│ Toolbar                                 │
│ [View: Grid/List] [Sort: Date↓]         │
│ [☑ Select All] [3 selected] [Bulk]      │
├─────────────────────────────────────────┤
│ ┌──────┬──────┬──────┬──────┐          │
│ │ Img  │ Img  │ Img  │ Img  │          │
│ │ 300  │ 300  │ 300  │ 300  │          │
│ └──────┴──────┴──────┴──────┘          │
│                                         │
│ < 1  2  3  4  5 >  50 of 1,234         │
└─────────────────────────────────────────┘

Filters (Collapsible Right):
- Type (Images, Videos, Docs)
- Date Range
- Size
- Tags
- [Apply Filters]
```

### AssetCard Component
```vue
Props:
  asset: Asset
  isSelected: boolean
  isLoading: boolean
  showCheckbox: boolean

Emits:
  - select: () => void
  - open: () => void
  - delete: () => void
  - favorite: () => void
  - more: () => void

Features:
- 300x260px card (300x200px image + 60px metadata)
- Thumbnail image with lazy loading
- Hover: show quick actions, checkbox
- Status badge (Approved/Pending)
- File name (truncated)
- File size + date
- Double-click to open detail
- Single-click to select
```

---

## 3. Asset Detail Page

**Layout:**
- Left 60%: Preview (800x600px, 16:9 aspect)
- Right 40%: Metadata sidebar (scrollable)

**Metadata Sections:**
1. File Details (name, size, type, created, creator)
2. Image Info (dimensions, DPI, color profile, EXIF)
3. AI Analysis (tags, objects with confidence, colors)
4. Version History (with restore option)
5. Comments (threaded, @mentions, edit/delete)

**Actions:**
- Top: Approve (green), Share (outline), More menu
- Connect to apiService.getAsset(id)
- WebSocket for real-time updates
- Dark mode support
- Mobile: stack vertically, sidebar → modal

---

## 4. Search & Filters

### SearchBar Component
```
Features:
- Instant results dropdown (max 8 items)
- Debounced search: 300ms
- Min query length: 2 chars
- Recent searches: max 5 (localStorage)
- Show thumbnail + name + metadata
- Click result → navigate to detail
- View all results link
- Ctrl+K shortcut
- Support boolean search (AND, OR, NOT)
- Filter support (type, tags, date)
```

### Advanced Search Page
```
Layout:
- Search input (top)
- Filters (left sidebar, collapsible)
- Results grid (main area, 4 columns)
- Pagination

Features:
- Full-text search
- Boolean operators
- Faceted search
- Date range picker
- Tag selector
- File type filter
- Advanced options
```

---

# 🔴 ДОПОЛНИТЕЛЬНЫЕ КРИТИЧЕСКИЕ СТРАНИЦЫ, ПОДСТРАНИЦЫ, ОКНА

## Критические страницы и подстраницы (8 шт)

### 1. LoginPage.vue
```
Функции:
- Форма входа (email, password)
- OAuth/SSO поддержка
- "Remember me" checkbox
- Forgot password link
- Error handling (401, network)
- Капча поддержка
- Два фактора аутентификация
- Redirect на /dam после входа
- Redirect with returnTo для protected routes

Поля:
- Email input (validation)
- Password input (masked)
- "Remember me" checkbox
- Login button
- OAuth buttons (if configured)
- Forgot password link
- Sign up link (if allowed)

Обработка ошибок:
- Invalid credentials
- Account locked
- Session expired
- Network error
- 2FA required
```

### 2. UserManagementPage.vue (Admin)
```
Функции:
- Таблица пользователей
- CRUD операции (Create, Read, Update, Delete)
- Назначение ролей
- Поиск по email/имени
- Пагинация (50 users/page)
- Bulk actions (delete, change role)
- Filter by status (active, inactive, pending)

Таблица столбцы:
- Checkbox (select)
- Avatar
- Name
- Email
- Role (select)
- Status (Active/Inactive/Pending)
- Created date
- Actions (Edit, Delete, More)

Модальное окно (Add/Edit User):
- Name input
- Email input
- Role selector
- Status selector
- Permissions checkboxes
- Save/Cancel buttons
```

### 3. MetadataSchemaPage.vue (Admin)
```
Функции:
- Редактор схем метаданных
- Drag-drop поля
- Группы атрибутов
- Типы полей (text, select, date, number, multiselect)
- Required/Optional флаги
- Default values
- Validation rules

Interface:
- Left: Field list (drag-drop)
- Center: Schema preview
- Right: Field editor
- Bottom: Save/Cancel buttons

Field types:
- Text (single line)
- Text area (multi-line)
- Select (dropdown)
- Multiselect
- Date picker
- Date range
- Number
- Checkbox
- File upload
```

### 4. WorkflowDesignerPage.vue (Admin)
```
Функции:
- Визуальный редактор Workflow
- Nodes (states): Draft → Review → Approved
- Arrows (transitions): с условиями
- Roles: кто может перейти на следующий stage
- Notifications: при переходе
- Comments: на каждом stage

Canvas:
- Drag-drop nodes
- Connect nodes with arrows
- Node properties editor
- Transition conditions
- Role assignment
- Notification settings

Nodes:
- Create/edit/delete states
- Set entry/exit actions
- Configure roles per state
- Setup notifications
```

### 5. AdvancedSearchPage.vue
```
Функции:
- Расширенный поиск
- Булева логика (AND, OR, NOT)
- Facet-фильтры
- Фильтрация по датам/размерам/тегам
- Сохранение saved searches
- Export results

Layout:
- Top: Search input + advanced options
- Left: Filters (collapsible)
- Main: Results grid (4 columns)
- Bottom: Pagination

Advanced Options:
- Boolean operators
- Phrase search ("exact phrase")
- Exclude words (-word)
- Wildcards (*)
- Field search (filename:*.jpg)
```

### 6. CollectionsPage.vue
```
Функции:
- Древовидный список коллекций
- Grid/Gallery по выбранной коллекции
- Метаданные коллекции (справа)
- CRUD операции (create, rename, delete, move)
- Share collection
- Права доступа

Layout:
- Left: Tree view (collapsible folders)
- Center: Gallery grid of items
- Right: Collection metadata

Features:
- Expand/collapse folders
- Drag-drop items between collections
- Rename collection
- Delete collection with confirmation
- Share collection (permission modal)
- Collection settings (privacy, access)
```

### 7. ReportsPage.vue
```
Функции:
- Аналитика по активам
- Usage reports
- Download tracking
- Export reports
- Drill-down analytics

Reports:
- Most viewed assets
- Most downloaded assets
- Assets by type
- Upload activity
- User activity
- Storage usage by type
- Collaboration metrics

Features:
- Date range picker
- Export to CSV/PDF
- Drill-down on charts
- Real-time updates
```

### 8. ProfilePage.vue
```
Функции:
- Профиль пользователя
- Фото профиля
- Смена пароля
- API ключи
- Timezone, язык
- 2FA настройки
- Безопасность

Sections:
1. Profile Info
   - Avatar (upload)
   - Name
   - Email (read-only)
   - Bio

2. Account Settings
   - Language selector
   - Timezone selector
   - Theme (light/dark/auto)

3. Security
   - Change password
   - 2FA toggle
   - Recent logins (log list)
   - Session management

4. API Keys
   - Generate new key
   - Revoke key
   - Key list with created/last used dates

5. Notifications
   - Email notifications toggle
   - Push notifications toggle
   - In-app notifications toggle
   - Notification preferences
```

---

## 🔴 Критически важные модальные окна (15 шт)

### UploadModal
```
Функции:
- Загрузка новых файлов
- Drag-drop или click to select
- Прогрессбар для каждого файла
- Отмена загрузки
- Ошибки обработка + retry

Элементы:
- Drag-drop zone
- "Click to select files" button
- File list with progress bars
- Cancel button per file
- Upload all button
- Close modal button

Валидация:
- Max file size (display warning)
- Allowed file types
- Total upload limit
```

### ShareModal
```
Функции:
- Генерация публичной ссылки
- Права (view, download, edit)
- Сроки публикации
- Список получателей

Элементы:
- "Create share link" button
- Link display + copy button
- Expiration date picker
- Permissions: View/Download/Edit
- Add people (email input)
- Share link list
- Revoke link button
```

### DeleteConfirmModal
```
Функции:
- Подтверждение удаления
- Массовое/одиночное удаление
- Warning text
- Список удаляемых items (если bulk)

Элементы:
- Warning icon
- Confirmation text
- Item list (if multiple)
- Cancel button
- Delete button (red)
```

### AssetPreviewModal (Lightbox)
```
Функции:
- Быстрый просмотр актива
- Полное разрешение
- Навигация (prev/next)
- Zoom in/out
- Download button
- Share button
- Close button (ESC)

Элементы:
- Large image/preview
- Navigation arrows
- Zoom controls
- Action buttons
- Close button (X)
- Keyboard: arrow keys, ESC
```

### EditMetadataModal
```
Функции:
- Редактирование/создание метаданных
- Dynamic form based on schema
- Save changes
- Cancel

Элементы:
- Form based on MetadataSchema
- Save button
- Cancel button
- Error validation messages
```

### CreatePublicationModal
```
Функции:
- Создание публикации
- Выбор канала
- Параметры сроков
- Выбор активов

Элементы:
- Publication name input
- Channel selector (multiselect)
- Start date picker
- End date picker
- Add assets button (opens asset selector)
- Asset list
- Create button
```

### CreateCollectionModal
```
Функции:
- Создание новой коллекции/папки
- Выбор родительской папки
- Приватность/публичность

Элементы:
- Collection name input
- Parent folder selector
- Privacy selector (private/shared)
- Create button
- Cancel button
```

### MoveAssetsModal
```
Функции:
- Массовое перемещение активов
- Выбор целевой коллекции
- Confirmation

Элементы:
- Target folder tree
- Folder selector
- Asset count display
- Move button
- Cancel button
```

### BulkTagModal
```
Функции:
- Групповое редактирование тегов
- Add tags
- Remove tags
- Replace tags

Элементы:
- Operation selector (add/remove/replace)
- Tag input (with autocomplete)
- Asset count display
- Apply button
- Cancel button
```

### VersionHistoryModal
```
Функции:
- Просмотр версий файла
- Откат на предыдущую версию
- Сравнение версий
- Download версии

Элементы:
- Version timeline
- Version list (table)
- Version details (date, author, size)
- Preview panel
- Restore button
- Download button
- Compare button (if 2 selected)
```

### ExportModal
```
Функции:
- Экспорт выбранных активов
- Опции: ZIP, преобразование формата
- Выбор разрешения

Элементы:
- Format selector (ZIP, individual)
- Resolution selector (if images)
- Include metadata checkbox
- Download button
- Cancel button
```

### InviteUserModal
```
Функции:
- Приглашение пользователя в систему
- Email ввод
- Выбор роли

Элементы:
- Email input (with validation)
- Role selector
- Send invite button
- Cancel button
```

### CreateWorkflowModal
```
Функции:
- Создание нового Workflow
- Запуск шаблона Workflow

Элементы:
- Workflow template selector
- Workflow name input
- Start workflow button
- Cancel button
```

### CropImageModal
```
Функции:
- Базовый image editor
- Crop
- Rotate
- Resize
- Aspect ratio lock

Элементы:
- Image canvas
- Crop handles
- Rotate button
- Resize input fields
- Aspect ratio lock checkbox
- Save button
- Cancel button
```

### NotificationCenterModal
```
Функции:
- Просмотр всех нотификаций
- Фильтр по типу
- Mark as read
- Delete notification

Элементы:
- Notification list
- Filter tabs (All, Unread, Updates, etc)
- Notification items (with avatar, time, message)
- Mark as read button
- Delete button
- Clear all button
```

---

## 🔴 Вспомогательные компоненты (20+ шт)

```yaml
Critical Components:
  - FileUploader (drag-drop + file selection)
  - ImageCropper (crop, rotate, resize)
  - TagInput (autocomplete with suggestions)
  - DateRangePicker (date range selector)
  - PermissionSelector (role/permission picker)
  - WorkflowCanvas (workflow editor with nodes)
  - Breadcrumb (navigation trail)
  - ContextMenu (right-click menu)
  - ErrorBoundary (JS error catcher)
  - EmptyState (no data illustrations)

Important Components:
  - ProgressBar (upload/download progress)
  - ColorPicker (brand colors)
  - Accordion (collapsible sections)
  - Tabs (tabbed interface)
  - Dropdown (action menus)
  - Popover (tooltips with actions)
  - Avatar (user profile picture)
  - FilePreview (PDF/doc/xls viewer)
  - Timeline (version history view)
  - Notification (toast messages)
```

---

## 🔴 Error/Empty/Loading States

### Error States
```yaml
401 Unauthorized:
  - Redirect to login
  - Show "Session expired" message
  - Save return URL

403 Forbidden:
  - Show "Access denied" page
  - Explain why access blocked
  - Link to request access

404 Not Found:
  - Show "Asset not found" page
  - Link to gallery
  - Recent items suggestion

500 Server Error:
  - Show error page
  - Retry button
  - Contact support link

Network offline:
  - Show offline banner
  - Disable upload/share buttons
  - Cache available data

Upload failed:
  - Show error message
  - Retry button
  - Delete failed item option

Large file warning:
  - Show file size warning
  - Compression recommendations
  - Proceed anyway button

Quota exceeded:
  - Show quota warning
  - Upgrade prompt
  - Contact admin link

Session expired:
  - Auto-logout
  - Show reason
  - Redirect to login
```

### Empty States
```yaml
No assets uploaded:
  - Call-to-action: "Upload your first asset"
  - Illustration
  - Upload button

No search results:
  - Suggest filter changes
  - Show popular tags
  - Link to browse all

No collections:
  - "Create your first collection"
  - Illustration
  - Create button

No notifications:
  - "You're all caught up!"
  - Illustration

No activity:
  - "No recent activity"
  - Suggestion to upload/share
```

### Loading States
```yaml
Page loading:
  - Show skeleton (content shape)
  - Animate pulse
  - 300-500ms min display

Infinite scroll:
  - Show spinner at bottom
  - "Loading more..."

Image loading:
  - Show placeholder (gray bg)
  - Fade in when loaded

Search loading:
  - Show spinner in search box
  - 300ms debounce

Upload progress:
  - Show percentage (0-100%)
  - Animated progress bar
  - File name display
```

---

## 🔴 User Flows (6 главных сценариев)

### 1. Onboarding Flow
```
1. Login (email + password)
2. Welcome screen (skip or tutorial)
3. Create first collection (optional)
4. Upload first asset (drag-drop or click)
5. View in gallery
6. Edit metadata
7. Share asset
8. Done - welcome to DAM
```

### 2. Search & Download Flow
```
1. Search (type query)
2. See instant results
3. Apply filters (type, date, tags)
4. Click asset for preview
5. Download (in detail view)
6. Or download from gallery (bulk)
7. ZIP download (if bulk)
```

### 3. Approval Workflow
```
1. Submit asset for approval
2. Notification to reviewer
3. Reviewer sees pending assets
4. Preview asset
5. Approve or Reject
6. Uploader gets notification
7. Status updates in gallery
```

### 4. Bulk Operations Flow
```
1. Select multiple assets (ctrl+click)
2. Select all toggle
3. Bulk actions menu
4. Choose action (tag/move/delete/share)
5. Modal with options
6. Apply action
7. See success confirmation
8. Optional: Undo action
```

### 5. Publishing Flow
```
1. Create publication
2. Select channel(s)
3. Add assets to publication
4. Set schedule (start/end dates)
5. Generate share link
6. Share externally (email/social)
7. Track downloads/views
8. Report analytics
```

### 6. Admin Setup Flow
```
1. Create user (email, role)
2. Assign permissions
3. Create metadata schema (fields)
4. Create workflow (states, transitions)
5. Setup integrations (API keys)
6. Configure API endpoints
7. Test setup
8. Go live
```

---

# 🔌 API ИНТЕГРАЦИЯ

## API Client Setup

```typescript
// src/services/apiService.ts
import axios, { AxiosInstance, AxiosError } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class APIClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api/v4`,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor
    this.client.interceptors.request.use((config) => {
      // Add CSRF token
      const csrfToken = document.querySelector('meta[name="csrf-token"]')
        ?.getAttribute('content')
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken
      }

      // Add auth token
      const token = localStorage.getItem('auth_token')
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`
      }

      return config
    })

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired, redirect to login
          window.location.href = '/login'
        }

        // Handle structured errors
        if (error.response?.data?.error) {
          const err = error.response.data.error
          throw new APIError(err.code, err.message, err.details)
        }

        throw error
      }
    )
  }

  // Asset operations
  async getAssets(params: GetAssetsParams) {
    const response = await this.client.get('/dam/assets/', { params })
    return response.data
  }

  async getAsset(id: number) {
    const response = await this.client.get(`/dam/assets/${id}/`)
    return response.data
  }

  async searchAssets(query: SearchQuery) {
    const response = await this.client.post('/dam/assets/search/', query)
    return response.data
  }

  async bulkOperations(operation: BulkOperation) {
    const response = await this.client.post('/dam/assets/bulk/', operation)
    return response.data
  }

  // ... more methods
}

export const apiClient = new APIClient()
```

## Required API Endpoints

```yaml
Assets Management:
  GET /api/v4/dam/assets/
    Query params:
      - limit: 50 (default)
      - offset: 0 (pagination)
      - type: image|video|document (filter)
      - tags: tag1,tag2 (filter)
      - sort: -created_at (sort)
    Response:
      - count: integer (total items)
      - next: string|null (next page URL)
      - previous: string|null (prev page URL)
      - results: Asset[

]

  GET /api/v4/dam/assets/{id}/
    Response: Asset (full detail)

  POST /api/v4/dam/assets/search/
    Body:
      - q: string (query)
      - filters: object (facets)
      - limit: 20
      - offset: 0
    Response:
      - count: integer
      - results: Asset[]
      - facets: Facets (type, tags, date)

  POST /api/v4/dam/assets/bulk/
    Body:
      - ids: number[]
      - action: 'tag'|'move'|'delete'
      - data: object (action-specific)
    Response:
      - success: boolean
      - updated: integer

Collections:
  GET /api/v4/collections/
    Response: paginated list of collections

  POST /api/v4/collections/
    Create new collection

  GET /api/v4/collections/{id}/items/
    Response: items in collection

Publishing & Distribution:
  GET /api/v4/distribution/publications/
    Response: paginated list of publications

  POST /api/v4/distribution/publications/
    Create new publication

  GET /api/v4/distribution/publications/{id}/links/
    Response: array of share links

Admin:
  GET /api/v4/users/
    Response: list of users

  POST /api/v4/users/
    Create new user

  GET /api/v4/metadata-schemas/
    Response: list of schemas

  POST /api/v4/workflows/
    Create new workflow

Analytics & Stats:
  GET /api/v4/analytics/dashboard/
    Response: dashboard metrics

  GET /api/v4/analytics/assets/{id}/stats/
    Response: asset usage stats
```

---

# ⚡ ТРЕБОВАНИЯ ПО ПРОИЗВОДИТЕЛЬНОСТИ

## Performance Targets

```yaml
Page Load Time:
  Metric: First Contentful Paint (FCP)
  Target: < 1.5s
  Threshold: < 2s

Time to Interactive (TTI):
  Target: < 2.5s
  Threshold: < 3.5s

Lighthouse Score:
  Target: 90+
  Threshold: 80+

API Response Time:
  Target: < 300ms
  Threshold: < 500ms

Image Optimization:
  Format: WebP with PNG fallback
  Sizes: Responsive (300px, 600px, 1200px)
  Lazy loading: Intersection Observer

Bundle Size:
  Target: < 200KB (gzipped)
  Threshold: < 300KB
  Code splitting: By route

Memory Usage:
  Limit: < 50MB for 100+ assets
  Virtual scrolling: For large lists

Database Queries:
  N+1 Prevention: select_related/prefetch_related
  Query time: < 200ms per request

Caching Strategy:
  Browser: Cache-Control headers
  Server: Redis caching (15 min default)
  Service Worker: Offline support
```

## Optimization Techniques

```yaml
Frontend:
  1. Code Splitting
     - Route-based splitting
     - Component lazy loading
     - Separate vendor bundle

  2. Image Optimization
     - WebP format with fallback
     - Responsive images (srcset)
     - Lazy loading (Intersection Observer)
     - Thumbnail generation on server

  3. Bundle Optimization
     - Tree-shaking
     - Minification
     - CSS purging (Tailwind)
     - Gzip/Brotli compression

  4. Runtime Optimization
     - Virtual scrolling (1000+ items)
     - Debounced search (300ms)
     - Pagination (50 items/page)
     - Memoization of expensive computations

Backend:
  1. Query Optimization
     - select_related for FK
     - prefetch_related for reverse FK
     - Database indexing
     - Query analysis/profiling

  2. Caching Layer
     - Redis for search results
     - Asset metadata cache
     - Dashboard stats cache

  3. Pagination
     - Default: 50 items/page
     - Max: 100 items/page
     - Cursor-based (optional for performance)

  4. Async Processing
     - Celery for long-running tasks
     - WebSocket for notifications
     - Background job monitoring
```

---

# 📅 ПЛАН РЕАЛИЗАЦИИ (12 НЕДЕЛЬ)

## Phase 1: Foundation (Weeks 1-4)

### Week 1: Project Setup & Infrastructure
**Цель:** Базовая инфраструктура, build tool, design system

**Frontend Tasks:**
☐ Create new Vue 3 project with Vite  
☐ Setup TypeScript (strict mode)  
☐ Install Tailwind CSS + configure  
☐ Setup Pinia for state management  
☐ Configure ESLint, Prettier, Husky  
☐ Create project directory structure  
☐ Setup environment (.env)  
☐ Create design system tokens (CSS variables)  

**Backend - CRITICAL:**
☐ Fix DAMDocumentDetailView (add authentication)  
☐ Add serializer validation framework  
☐ Add pagination to ListViews  
☐ Configure CORS  
☐ Setup API error handling  

**Testing Infrastructure:**
☐ Setup Vitest for unit tests  
☐ Configure @testing-library/vue  
☐ Setup Playwright for E2E tests  
☐ CI/CD pipeline (GitHub Actions)  

**Documentation:**
☐ Create .cursor/design-system.md  
☐ Create .cursor/component-specs.md  
☐ Create developer setup guide  

**Deliverables:**
- ✅ Frontend + Backend projects running locally
- ✅ Design tokens defined and exportable
- ✅ All critical API security issues fixed
- ✅ CI/CD pipeline working
- 📊 Baseline metrics recorded

---

### Week 2: Core Layout Components
**Цель:** Header, Sidebar, MainContent компоненты

**Components:**
☐ Create Header.vue (64px fixed, responsive)  
☐ Create Sidebar.vue (280px/64px collapsible)  
☐ Create MainContent.vue wrapper  
☐ Create responsive grid system  

**Styling:**
☐ Global styles (Tailwind + custom CSS)  
☐ Light/Dark theme system  
☐ Animations & transitions  
☐ Color palette CSS variables  

**Integration:**
☐ Router setup (Vue Router)  
☐ Layout wrapper component  
☐ Navigation routing  

**Testing:**
☐ Unit tests for each component  
☐ E2E tests for navigation  
☐ Snapshot tests for layout  

**Documentation:**
☐ Storybook stories for components  
☐ Component documentation  

**Deliverables:**
- ✅ Layout components rendering
- ✅ Responsive design working (sm/md/lg)
- ✅ Navigation functioning
- ✅ 80%+ code coverage
- 📊 Performance baseline established

---

### Week 3: Common Components
**Цель:** Button, Input, Modal, Pagination, Card, Badge, etc.

**Components to create:** (20+ components)
- Button (variants: primary, secondary, outline, ghost)
- Input (text, with icons, states)
- Select/Dropdown
- Modal/Dialog
- Pagination controls
- Card container
- Badge/Status
- Skeleton loader
- Spinner/Loading
- Alert messages
- Tooltip
- FileUploader (drag-drop)
- ImageCropper (crop/rotate)
- TagInput (autocomplete)
- DateRangePicker
- PermissionSelector
- Breadcrumb
- ContextMenu
- ErrorBoundary
- EmptyState

**Features per component:**
- TypeScript types
- All states (default, hover, focus, disabled, error)
- Dark mode support
- Accessibility (ARIA labels, keyboard nav)
- Unit tests (80%+ coverage)
- Storybook stories

**Testing:**
☐ Visual regression tests  
☐ Accessibility audits  
☐ Interactive state tests  

**Deliverables:**
- ✅ 20+ reusable components
- ✅ Storybook documentation
- ✅ 100+ unit tests
- ✅ Accessibility compliance (WCAG AA)
- 📊 Component coverage report

---

### Week 4: Gallery View MVP
**Цель:** Gallery Grid с асинхронной загрузкой данных

**Backend:**
☐ Implement GET /api/v4/dam/assets/ (paginated)  
☐ Implement proper error responses  
☐ Setup API mocking for frontend dev  
☐ Database seed with test data (100+ items)  

**Frontend:**
☐ Create GalleryView.vue component  
☐ Create AssetCard.vue component  
☐ Implement responsive grid (4/2/1 columns)  
☐ Lazy load images  
☐ Implement pagination  
☐ Create loading skeleton states  
☐ Error handling & retry logic  
☐ Empty state UI  

**State Management:**
☐ Create assetStore (Pinia)  
☐ Implement asset fetching logic  
☐ Cache management  
☐ Pagination state  

**Performance:**
☐ Image lazy loading  
☐ Virtual scrolling setup  
☐ Lighthouse audit  
☐ Performance profiling  

**Testing:**
☐ Mock API responses  
☐ Test pagination  
☐ Test lazy loading  
☐ Performance tests (load 1000+ items)  

**Documentation:**
☐ API integration guide  
☐ Component specifications  

**Deliverables:**
- ✅ Gallery view rendering 50 items/page
- ✅ Pagination working
- ✅ Images lazy loading
- ✅ Lighthouse 80+
- ✅ Performance: < 2s load time
- 📊 All metrics baseline established

---

## Phase 2: DAM Features (Weeks 5-8)

### Week 5: Search & Filters
```
☐ Create SearchBar.vue component
☐ Create SearchResults dropdown
☐ Implement POST /api/v4/dam/assets/search/
☐ Create FiltersPanel.vue (faceted)
☐ Implement filter state management
☐ Add debounced search (300ms)
☐ Instant results with preview
☐ Search history (localStorage, max 5)
☐ Advanced search page
☐ Search unit tests (50+ tests)
☐ Accessibility audit

Metrics:
- Search response: < 300ms
- Results rendering: < 200ms
- Filter application: instant
```

---

### Week 6: Asset Detail & Comments
```
☐ Create AssetDetailPage.vue
☐ Create MetadataPanel.vue (right sidebar)
☐ Implement GET /api/v4/dam/assets/{id}/
☐ File properties display
☐ Image info (dimensions, EXIF)
☐ AI analysis results
☐ Version history
☐ Comments system (threaded)
☐ WebSocket notifications
☐ Action buttons (Approve, Share)
☐ E2E tests for detail flow
```

---

### Week 7: Bulk Operations
```
☐ Create BulkActions.vue toolbar
☐ Multi-select checkboxes
☐ Select All toggle
☐ Bulk tag operation
☐ Bulk move operation
☐ Bulk delete with confirmation
☐ Bulk download (ZIP)
☐ Bulk share
☐ Progress tracking
☐ Undo functionality
☐ Test with 100+ items
```

---

### Week 8: AI Features Display
```
☐ Display auto-generated tags
☐ Show object detection results
☐ Dominant colors visualization
☐ Quality score display
☐ AI suggestions editing
☐ Confidence bar charts
☐ Tag editing interface
☐ Manual tag addition
☐ Tag management (create/edit/delete)
```

---

## Phase 3: Additional Modules (Weeks 9-10)

### Week 9: Distribution Module
```
☐ Create Distribution page
☐ Publication list view
☐ Publication card component
☐ Create publication form
☐ Channel management
☐ Schedule publishing
☐ Share link generation
☐ Analytics display
☐ Download tracking
```

---

### Week 10: Dashboard & Settings
```
☐ Create Dashboard page
☐ Stats cards (KPI metrics)
☐ Activity feed
☐ Storage metrics
☐ Recent items
☐ Create Settings page
☐ User preferences
☐ Theme switcher
☐ Notification settings
```

---

## Phase 4: Polish & Launch (Weeks 11-12)

### Week 11: Performance & Accessibility
```
☐ Lighthouse audit (target: 90+)
☐ Code splitting optimization
☐ Image optimization (WebP)
☐ Virtual scrolling implementation
☐ WCAG 2.1 AA compliance full audit
☐ Keyboard navigation complete
☐ Screen reader testing
☐ Mobile device testing (iOS/Android)
☐ Browser compatibility (Chrome 90+, FF 88+, Safari 14+, Edge 90+)
```

---

### Week 12: Launch Prep & Documentation
```
☐ User documentation
☐ API documentation (Swagger)
☐ Deployment guide
☐ Troubleshooting guide
☐ Security audit
☐ Final performance testing
☐ UAT with stakeholders
☐ Migration plan from old UI
☐ Rollout strategy
```

---

# ✅ КРИТЕРИИ ГОТОВНОСТИ

## Definition of Done для каждого компонента

```yaml
Component Criteria:
  Code:
    ☐ TypeScript 100% typed (no 'any')
    ☐ No console errors/warnings
    ☐ ESLint 0 issues
    ☐ Prettier formatted
  
  Functionality:
    ☐ Feature complete per spec
    ☐ All user interactions working
    ☐ Error states handled
    ☐ Loading states implemented
    ☐ Empty states designed
  
  Testing:
    ☐ Unit tests: >= 80% coverage
    ☐ Component tests: All states tested
    ☐ E2E tests: Critical user flows
    ☐ Visual regression: Approved
  
  Design System:
    ☐ Uses Tailwind utilities only
    ☐ No inline styles
    ☐ Respects design tokens
    ☐ Supports dark mode
    ☐ Responsive (sm/md/lg/xl)
  
  Accessibility:
    ☐ ARIA labels where needed
    ☐ Keyboard navigation works
    ☐ Color contrast >= 4.5:1
    ☐ Focus indicators visible
    ☐ Screen reader tested
  
  Performance:
    ☐ Lighthouse audit passed (80+)
    ☐ Component load: < 100ms
    ☐ No memory leaks
    ☐ Virtual scrolling if 100+ items
  
  Documentation:
    ☐ Storybook story created
    ☐ Props documented
    ☐ Events documented
    ☐ Usage examples provided
    ☐ Accessibility notes
  
  Code Review:
    ☐ Tech lead approval
    ☐ Design review passed
    ☐ QA sign-off
    ☐ Merged to main branch

Page Criteria:
  All component DOD +
    ☐ Routing configured
    ☐ State management connected
    ☐ API integration tested
    ☐ Error boundaries set
    ☐ Pagination/infinite scroll working
    ☐ Deep linking working
    ☐ Mobile fully tested

Feature Criteria:
  All page DOD +
    ☐ End-to-end user flow complete
    ☐ Real API integration
    ☐ Performance benchmarks met
    ☐ Analytics tracking
    ☐ User documentation written
    ☐ Stakeholder approval
    ☐ Launch ready
```

---

# 🤖 ПРОМПТЫ ДЛЯ CURSOR AI

## Phase 1: Setup (Week 1)

```
"Create a new Vue 3 project structure with:
1. Vite as build tool
2. TypeScript strict mode
3. Tailwind CSS with these design tokens:
   - Primary: #0052CC, Secondary: #00875A
   - Neutral: #FFFFFF to #111827
   - Success: #10B981, Error: #EF4444
4. Pinia for state management
5. Vue Router for routing
6. Directory structure:
   src/components/, pages/, stores/, services/, styles/, types/
7. ESLint + Prettier configured
8. .env.example for configuration
9. Create README with setup instructions
10. Use TypeScript for all files"
```

## Phase 2: Components (Week 2-3)

```
"Create Header.vue component in Vue 3 + TypeScript + Tailwind:
- Fixed top positioning (z-index: 50)
- Height: exactly 64px
- Responsive: hamburger menu on mobile (640px)
- Left: Logo (200px) with router-link to home
- Center: Search input with Ctrl+K focus shortcut
- Right: Upload button (primary action), Filters, Notifications, User menu
- Dark mode support
- Keyboard shortcuts: Ctrl+K focus, Escape blur
- Accessibility: Proper ARIA labels, semantic HTML
- Unit tests: >= 80% coverage
- Storybook story with all states
- No inline styles, use @apply for custom classes
- TypeScript: Strict mode, full types for all props/emits"
```

## Phase 3: Gallery (Week 4)

```
"Create GalleryView.vue component showing asset cards in responsive grid:
- Grid layout: 4 columns (desktop), 2 (tablet md:), 1 (mobile sm:)
- Card size: 300x260px (300x200px image + 60px metadata)
- Responsive gap: 16px
- Connect to Pinia assetStore
- Fetch data from GET /api/v4/dam/assets/ with pagination
- Query params: limit=50, offset=0
- Implement pagination component
- Lazy load images with Intersection Observer
- Loading skeleton state while fetching
- Error boundary with retry button
- Empty state when no results
- Asset card hover: show checkbox, quick actions (trash, heart, more)
- Bulk select: shift+click for range, ctrl+click individual
- Click card to open detail page
- Dark mode support
- Performance: virtual scrolling for 1000+ items
- Accessibility: ARIA labels, keyboard navigation
- Unit tests: 50+ tests covering all scenarios
- Storybook stories for all states (loading, empty, error, data)
- No data in component, all from store"
```

---

# 🔧 РАСШИРЕННЫЕ СЦЕНАРИИ И EDGE CASES

## Security Considerations

```yaml
Authentication:
  - JWT token storage (secure cookie preferred)
  - Token refresh mechanism
  - XSS protection (sanitize user input)
  - CSRF token validation
  - Session timeout (15 min inactivity)

Authorization:
  - Role-based access control (RBAC)
  - Resource-level permissions
  - Verify access on every API call
  - Audit logging for sensitive actions

Data Protection:
  - HTTPS only
  - Sensitive data encrypted at rest
  - API rate limiting
  - Input validation on all endpoints
  - SQL injection prevention
```

## Performance Edge Cases

```yaml
Large File Uploads:
  - Chunked upload support
  - Resume interrupted uploads
  - Progress tracking per chunk
  - Disk space validation

Bulk Operations on Large Datasets:
  - Pagination for bulk operations
  - Background job processing
  - Async progress tracking
  - Timeout handling (> 10 min operations)

Search Scalability:
  - Indexed search (Elasticsearch recommended)
  - Faceted search optimization
  - Query caching
  - Result pagination

Memory Management:
  - Virtual scrolling for 1000+ items
  - Lazy component loading
  - Image thumbnail caching
  - Cleanup on component unmount
```

## Browser Compatibility

```yaml
Tested Browsers:
  - Chrome 90+
  - Firefox 88+
  - Safari 14+
  - Edge 90+
  - Mobile Safari 14+
  - Chrome Mobile 90+

Polyfills Required:
  - IntersectionObserver (for lazy loading)
  - Promise
  - Object.assign

Known Limitations:
  - IE11: Not supported
  - Safari < 14: Limited CSS support
  - Mobile browsers: 16px font min (zoom prevention)
```

---

# 📋 РЕЗЮМЕ

## Что включено в этот документ

✅ **Полный анализ проблемы** — текущее состояние системы  
✅ **Видение решения** — современный Vue.js + Tailwind фронтенд  
✅ **Complete Design System** — цвета, типография, spacing, анимации  
✅ **Детальная структура проекта** — 40+ файлов, компоненты, store, services  
✅ **Все критические страницы** — 15 страниц/подстраниц  
✅ **Все модальные окна** — 15 диалогов  
✅ **30+ компонентов** — Common, DAM, Modals, Layout  
✅ **API интеграция** — endpoints, client setup, error handling  
✅ **Требования по производительности** — метрики, оптимизация  
✅ **12-недельный детальный план** — phase-by-phase  
✅ **Definition of Done** — критерии для каждого компонента/страницы/фичи  
✅ **Готовые промпты для Cursor** — для генерации кода  
✅ **Edge cases & security** — best practices  

## Как использовать этот документ

1. **Для разработчиков:**
   - Копируй спецификации в Cursor
   - Используй промпты для кода
   - Ссылайся на Design System
   - Следуй Definition of Done

2. **Для архитекторов:**
   - Изучи техническую архитектуру
   - Проверь требования
   - Адаптируй план под команду
   - Review API design

3. **Для PM:**
   - 12-недельный timeline
   - Четкие deliverables
   - Метрики успеха
   - Risk identification

4. **Для QA:**
   - Тестовые сценарии (все указаны)
   - Accessibility requirements (WCAG AA)
   - Performance benchmarks
   - Edge case coverage

---

**ГОТОВО К РАЗРАБОТКЕ!** 🚀

*Этот документ — единый источник правды для всей команды*  
*Последнее обновление: Ноябрь 2025*  
*Версия: 2.0 (Complete)*  
*Статус: ✅ PRODUCTION-READY*