# NEW_FRONTEND_ANALYSIS.md
## Комплексный реверс-инжиниринг фронтенд-системы DAM

**Дата анализа:** 28 ноября 2025  
**Версия проекта:** 1.0.0  
**Аналитик:** Senior Frontend Architect & Technical Writer

---

## 📋 Содержание

1. [Архитектурный обзор](#1-архитектурный-обзор)
2. [Модель данных (Core Entities)](#2-модель-данных-core-entities)
3. [Детальный функциональный анализ](#3-детальный-функциональный-анализ)
4. [API и интеграции](#4-api-и-интеграции)
5. [Скрытая логика (Automation)](#5-скрытая-логика-automation)
6. [Тестирование и качество кода](#6-тестирование-и-качество-кода)
7. [Проблемы и рекомендации](#7-проблемы-и-рекомендации)

---

## 1. Архитектурный обзор

### 1.1 Технологический стек

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
| **Иконки** | HeroIcons/Vue | 2.1.1 |
| **Графики** | Chart.js | 4.4.1 |
| **Утилиты** | VueUse | 10.7.2 |
| **Тестирование** | Vitest + Playwright | 4.0.14 / 1.41.2 |
| **Документация** | Storybook | 8.4.5 |

### 1.2 Структура приложения

```
frontend/src/
├── components/           # UI компоненты
│   ├── admin/           # [CUSTOM] Административные компоненты
│   ├── collections/     # [CUSTOM] Управление коллекциями
│   ├── Common/          # Базовые переиспользуемые компоненты
│   ├── DAM/             # [CUSTOM] Ключевые DAM-компоненты
│   ├── Distribution/    # [CUSTOM] Публикации и распространение
│   ├── gallery/         # Галерея активов
│   ├── Layout/          # Компоненты макета
│   ├── modals/          # Модальные окна
│   ├── reports/         # Отчеты и аналитика
│   └── workflow/        # Загрузка с workflow
├── composables/         # Vue 3 Composables (хуки)
├── pages/               # Страницы приложения
│   ├── admin/           # Административные страницы
│   └── auth/            # Страницы аутентификации
├── router/              # Конфигурация маршрутов
├── services/            # API-сервисы
├── stores/              # Pinia хранилища
├── types/               # TypeScript типы
├── utils/               # Утилиты
└── styles/              # Глобальные стили
```

### 1.3 Ключевые архитектурные решения

| Решение | Описание | Статус |
|---------|----------|--------|
| **Composition API** | Все компоненты используют Vue 3 Composition API с `<script setup>` | ✅ Реализовано |
| **Type-Safe State** | Полная типизация stores и services | ✅ Реализовано |
| **Session Auth** | Сессионная аутентификация (не JWT) | ✅ Реализовано |
| **Lazy Loading** | Динамическая загрузка страниц через `import()` | ✅ Реализовано |
| **Persisted State** | Сохранение состояния в localStorage через pinia-plugin-persistedstate | ✅ Реализовано |
| **Virtual Scrolling** | Виртуальная прокрутка для больших списков (100+ элементов) | ✅ Реализовано |
| **Chunked Upload** | Загрузка больших файлов чанками (5MB) | ✅ Реализовано |

---

## 2. Модель данных (Core Entities)

### 2.1 Диаграмма связей сущностей

```
┌─────────────────────────────────────────────────────────────────┐
│                         ASSET (Document)                         │
├─────────────────────────────────────────────────────────────────┤
│ id, label, filename, size, mime_type, date_added                │
│ thumbnail_url, preview_url, tags[], metadata{}                  │
│ access_level                                                     │
└───────────────┬─────────────────────┬───────────────────────────┘
                │                     │
                │ 1:1                 │ 1:N
                ▼                     ▼
┌───────────────────────┐   ┌─────────────────────────┐
│     AI ANALYSIS       │   │       VERSION           │
├───────────────────────┤   ├─────────────────────────┤
│ tags[], confidence    │   │ id, filename, size      │
│ objects_detected[]    │   │ uploaded_date           │
│ colors[], status      │   │ uploaded_by, is_current │
│ ai_description        │   │ download_url            │
│ provider              │   └─────────────────────────┘
└───────────────────────┘
                │
                │ 1:N
                ▼
┌───────────────────────┐   ┌─────────────────────────┐
│      COMMENT          │   │     COLLECTION          │
├───────────────────────┤   ├─────────────────────────┤
│ id, author, text      │   │ id, name, description   │
│ created_date, replies │   │ parent_id (hierarchy)   │
│ mentions[]            │   │ visibility, asset_count │
└───────────────────────┘   │ is_favorite, is_shared  │
                            └─────────────────────────┘
                                        │
                                        │ N:M
                                        ▼
                            ┌─────────────────────────┐
                            │     PUBLICATION         │
                            ├─────────────────────────┤
                            │ id, title, status       │
                            │ assets[], channels[]    │
                            │ schedule, permissions   │
                            │ analytics, share_links  │
                            └─────────────────────────┘
```

### 2.2 Основные сущности

#### Asset (Актив/Документ)
**Файл:** `src/types/api.ts`

```typescript
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
  file_details?: FileDetails
  ai_analysis?: AIAnalysis        // [CUSTOM] AI-анализ
  comments?: Comment[]            // [CUSTOM] Комментарии
  version_history?: Version[]     // [CUSTOM] История версий
  access_level?: string           // ACL уровень доступа
}
```

#### AIAnalysis [CUSTOM]
**Файл:** `src/types/api.ts`

```typescript
interface AIAnalysis {
  tags?: string[]                 // AI-сгенерированные теги
  confidence?: number             // Уровень уверенности
  objects_detected?: DetectedObject[]  // Обнаруженные объекты
  colors?: string[]               // Доминантные цвета
  status: 'pending' | 'processing' | 'completed' | 'failed'
  ai_description?: string         // AI-описание
  provider?: string               // Провайдер AI (Qwen, GigaChat, etc.)
}
```

#### Collection (Коллекция) [CUSTOM]
**Файл:** `src/types/collections.ts`

```typescript
interface Collection {
  id: number
  name: string
  description?: string
  parent_id: number | null        // Иерархическая структура
  is_favorite: boolean
  is_shared: boolean
  visibility: 'private' | 'shared' | 'public'
  asset_count: number
  cover_image_url?: string | null
}
```

#### Publication (Публикация) [CUSTOM]
**Файл:** `src/types/api.ts`

```typescript
interface Publication {
  id: number
  title: string
  description?: string
  status: 'draft' | 'scheduled' | 'published' | 'archived'
  assets: Asset[]
  channels: PublicationChannel[]  // Каналы распространения
  schedule?: PublicationSchedule  // Планирование публикации
  permissions?: PublicationPermissions
  analytics?: PublicationAnalytics  // Аналитика (views, downloads)
  share_links?: ShareLink[]       // Публичные ссылки
}
```

#### User (Пользователь)
**Файл:** `src/types/index.ts` и `src/types/admin.ts`

```typescript
interface User {
  id: number
  username: string
  email: string
  first_name?: string
  last_name?: string
  is_active: boolean
  permissions?: string[]
  role?: 'admin' | 'editor' | 'viewer' | 'guest'
  two_factor_enabled?: boolean    // [CUSTOM] 2FA поддержка
}
```

#### Workflow (Рабочий процесс) [CUSTOM]
**Файл:** `src/types/admin.ts`

```typescript
interface Workflow {
  id: number
  name: string
  description?: string
  nodes: WorkflowNode[]           // Узлы (состояния)
  transitions: WorkflowTransition[] // Переходы между состояниями
  is_active: boolean
}

interface WorkflowNode {
  id: string
  name: string
  type: 'start' | 'state' | 'end'
  position: { x: number; y: number }
  allowed_roles: UserRole[]
  actions: WorkflowAction[]
}
```

#### MetadataSchema (Схема метаданных) [CUSTOM]
**Файл:** `src/types/admin.ts`

```typescript
interface MetadataSchema {
  id: number
  name: string
  description?: string
  applies_to: ('image' | 'video' | 'document' | 'audio' | 'all')[]
  fields: SchemaField[]
  is_active: boolean
}

interface SchemaField {
  name: string
  type: 'text' | 'textarea' | 'number' | 'date' | 'select' | 'multi_select' | ...
  label: string
  required: boolean
  validation_rules?: ValidationRules
}
```

---

## 3. Детальный функциональный анализ

### 3.1 Ingestion (Загрузка) [CUSTOM]

#### Реализованные возможности:

| Функция | Компонент | Статус |
|---------|-----------|--------|
| **Web Upload** | `UploadModal.vue`, `UploadPage.vue` | ✅ Реализовано |
| **Drag & Drop** | `UploadStep.vue` | ✅ Реализовано |
| **Chunked Upload** | `uploadService.ts` | ✅ Реализовано |
| **Progress Tracking** | `uploadWorkflowStore.ts` | ✅ Реализовано |
| **File Validation** | `uploadService.ts` | ✅ Реализовано |
| **Resume Upload** | `uploadService.ts` | ✅ Реализовано |

**Ключевые файлы:**
- `src/services/uploadService.ts` — сервис загрузки с поддержкой чанков
- `src/stores/uploadWorkflowStore.ts` — состояние workflow загрузки
- `src/components/workflow/UploadStep.vue` — UI компонент загрузки

**Особенности реализации:**

```typescript
// uploadService.ts
private readonly DEFAULT_CHUNK_SIZE = 5 * 1024 * 1024  // 5MB
private readonly MAX_FILE_SIZE = 500 * 1024 * 1024     // 500MB
private readonly MAX_TOTAL_SIZE = 2 * 1024 * 1024 * 1024 // 2GB

// Chunked upload для файлов > 5MB
async uploadChunked(file, chunkSize, onProgress, signal, retryOptions)

// Возобновление прерванной загрузки
async resumeUpload(uploadId: string, file: File, options)
```

**Multi-step Workflow загрузки:**
1. **Upload Step** — загрузка файлов с прогрессом
2. **Metadata Step** — заполнение метаданных
3. **Collection Step** — выбор коллекции
4. **Share Step** — настройка публичного доступа

### 3.2 Processing & Transformation

#### Реализованные возможности:

| Функция | Компонент | Статус |
|---------|-----------|--------|
| **Preview Generation** | `AssetPreviewModal.vue` | ✅ UI готов |
| **Image Zoom/Pan** | `AssetPreviewModal.vue` | ✅ Реализовано |
| **Image Rotation** | `AssetPreviewModal.vue` | ✅ Реализовано |
| **Video Playback** | `AssetDetailPage.vue` | ✅ Реализовано |
| **PDF Preview** | `AssetPreviewModal.vue` | ✅ Реализовано |
| **Thumbnail Display** | `AssetCard.vue`, `GalleryItem.vue` | ✅ Реализовано |

**⚠️ ВАЖНО:** Реальная обработка (ресайз, конвертация, OCR, генерация тумбнейлов) выполняется на **бэкенде**. Фронтенд только отображает результаты и вызывает соответствующие API.

**Компоненты просмотра:**

```vue
<!-- AssetPreviewModal.vue -->
<div class="asset-preview-modal__media-transform" :style="mediaTransform">
  <img v-if="isImage" :src="mediaUrl" />
  <video v-else-if="isVideo" :src="mediaUrl" controls />
  <iframe v-else-if="isPdf" :src="mediaUrl" />
</div>

<!-- Toolbar с zoom/rotation -->
<button @click="zoomIn">Zoom In</button>
<button @click="zoomOut">Zoom Out</button>
<button @click="rotateLeft">Rotate Left</button>
<button @click="rotateRight">Rotate Right</button>
```

### 3.3 Metadata & AI [CUSTOM]

#### Реализованные возможности:

| Функция | Компонент | Статус |
|---------|-----------|--------|
| **AI Tags Display** | `MetadataPanel.vue` | ✅ Реализовано |
| **AI Description** | `AssetDetailPage.vue` | ✅ Реализовано |
| **AI Status Tracking** | `types/api.ts` | ✅ Типы определены |
| **EXIF Data Display** | `AssetPreviewModal.vue` | ✅ Реализовано |
| **Custom Metadata Schemas** | `MetadataSchemaPage.vue` | ✅ Реализовано |
| **Metadata Editing** | `EditMetadataModal.vue` | ✅ Реализовано |

**AI Analysis отображение:**

```vue
<!-- MetadataPanel.vue - отображение AI-результатов -->
<div v-if="asset.ai_analysis">
  <p>Status: {{ asset.ai_analysis.status }}</p>
  <p>Description: {{ asset.ai_analysis.ai_description }}</p>
  <div>Tags: <span v-for="tag in asset.ai_analysis.tags">{{ tag }}</span></div>
  <div>Colors: <span v-for="color in asset.ai_analysis.colors">{{ color }}</span></div>
  <p>Provider: {{ asset.ai_analysis.provider }}</p>
</div>
```

**EXIF данные:**

```vue
<!-- AssetPreviewModal.vue -->
<div v-if="exifEntries.length" class="asset-preview-modal__exif">
  <p class="asset-preview-modal__exif-title">EXIF data</p>
  <ul>
    <li v-for="entry in exifEntries" :key="entry.label">
      <span>{{ entry.label }}</span>
      <span>{{ entry.value }}</span>
    </li>
  </ul>
</div>
```

### 3.4 Search (Поиск) [CUSTOM]

#### Реализованные возможности:

| Функция | Компонент | Статус |
|---------|-----------|--------|
| **Quick Search** | `SearchBar.vue` | ✅ Реализовано |
| **Advanced Search** | `AdvancedSearchPage.vue` | ✅ Реализовано |
| **Faceted Search** | `FiltersPanel.vue` | ✅ Реализовано |
| **Search Results** | `SearchResults.vue` | ✅ Реализовано |
| **Recent Searches** | `searchStore.ts` | ✅ Реализовано |
| **Saved Searches** | `searchStore.ts` | ✅ Реализовано |

**Ключевые файлы:**
- `src/stores/searchStore.ts` — состояние поиска
- `src/components/DAM/SearchBar.vue` — панель поиска
- `src/components/DAM/FiltersPanel.vue` — фильтры
- `src/pages/AdvancedSearchPage.vue` — расширенный поиск

**Поисковый запрос:**

```typescript
// types/api.ts
interface SearchQuery {
  q?: string
  filters?: SearchFilters
  sort?: string
  limit?: number
  offset?: number
}

interface SearchFilters {
  type?: string[]           // Тип файла
  tags?: string[]           // Теги
  date_range?: [string, string]  // Диапазон дат
  size?: { min?: number; max?: number }  // Размер файла
  custom_metadata?: Record<string, unknown>  // Кастомные поля
}

interface SearchResponse {
  count: number
  results: Asset[]
  facets: Facets  // Фасеты для фильтрации
}
```

**Фасетный поиск:**

```typescript
interface Facets {
  type?: Record<string, number>   // { "image": 150, "video": 30 }
  tags?: Record<string, number>   // { "nature": 45, "portrait": 20 }
  date?: Record<string, number>   // { "2024": 100, "2025": 50 }
}
```

### 3.5 Permissions (ACL) [CUSTOM]

#### Реализованные возможности:

| Функция | Компонент | Статус |
|---------|-----------|--------|
| **Route Guards** | `router/index.ts` | ✅ Реализовано |
| **Permission Check** | `authStore.ts` | ✅ Реализовано |
| **Role-based Access** | `authStore.ts` | ✅ Реализовано |
| **2FA Support** | `Login2FAPage.vue` | ✅ Реализовано |
| **Collection Visibility** | `types/collections.ts` | ✅ Реализовано |
| **Publication Permissions** | `types/api.ts` | ✅ Реализовано |

**Route Guards:**

```typescript
// router/index.ts
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()
  
  // Проверка аутентификации
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { returnTo: to.fullPath } })
    return
  }
  
  // Проверка 2FA
  if (authStore.requiresTwoFactor && !authStore.isTwoFactorVerified) {
    next({ name: 'two-factor-auth', query: { returnTo: to.fullPath } })
    return
  }
  
  // Проверка permissions
  if (to.meta.requiresPermission) {
    if (!authStore.hasPermission(to.meta.requiresPermission)) {
      next({ name: 'forbidden' })
      return
    }
  }
  
  // Проверка роли
  if (to.meta.requiresRole) {
    if (!authStore.hasRole(to.meta.requiresRole)) {
      next({ name: 'forbidden' })
      return
    }
  }
})
```

**Проверка прав в компонентах:**

```typescript
// authStore.ts
const hasPermission = computed(() => {
  return (permission: string) => {
    return permissions.value.includes(permission) || 
           user.value?.permissions?.includes(permission) || false
  }
})

const hasRole = computed(() => {
  return (role: string) => user.value?.role === role
})
```

**Определенные permissions:**
- `admin.access` — доступ к админ-панели
- `admin.user_manage` — управление пользователями
- `admin.schema_manage` — управление схемами метаданных
- `admin.workflow_manage` — управление workflows
- `admin.reports_view` — просмотр отчетов
- `collections.create` — создание коллекций
- `collections.delete` — удаление коллекций
- `collections.edit` — редактирование коллекций
- `collections.share` — шаринг коллекций

### 3.6 Collections (Коллекции) [CUSTOM]

#### Реализованные возможности:

| Функция | Компонент | Статус |
|---------|-----------|--------|
| **Tree View** | `CollectionTree.vue` | ✅ Реализовано |
| **Drag & Drop** | `CollectionTree.vue` | ✅ Реализовано |
| **Create/Rename/Delete** | `CreateCollectionModal.vue`, `RenameCollectionModal.vue` | ✅ Реализовано |
| **Favorites** | `collectionsStore.ts` | ✅ Реализовано |
| **Special Collections** | `collectionsStore.ts` | ✅ Реализовано |
| **Bulk Operations** | `collectionsStore.ts` | ✅ Реализовано |
| **Visibility Control** | `types/collections.ts` | ✅ Реализовано |

**Иерархическая структура:**

```typescript
interface CollectionTree {
  collection: Collection
  children: CollectionTree[]
  level: number
}

// Построение дерева
function buildCollectionTree(collectionsList: Collection[]): CollectionTree[] {
  const buildTree = (parentId: number | null, level: number): CollectionTree[] => {
    const children = sorted.filter(c => c.parent_id === parentId)
    return children.map(collection => ({
      collection,
      children: buildTree(collection.id, level + 1),
      level
    }))
  }
  return buildTree(null, 0)
}
```

**Специальные коллекции:**

```typescript
type SpecialCollectionType =
  | 'favorites'        // Избранное
  | 'recent'           // Недавние
  | 'my_uploads'       // Мои загрузки
  | 'shared_with_me'   // Расшаренные мне
  | 'public_collections'  // Публичные
```

### 3.7 Distribution (Публикации) [CUSTOM]

#### Реализованные возможности:

| Функция | Компонент | Статус |
|---------|-----------|--------|
| **Publication List** | `DistributionPage.vue` | ✅ Реализовано |
| **Create Publication** | `CreatePublicationModal.vue` | ✅ Реализовано |
| **Edit Publication** | `EditPublicationModal.vue` | ✅ Реализовано |
| **Publication Detail** | `PublicationDetailPage.vue` | ✅ Реализовано |
| **Public Portal** | `PublicationPublicPage.vue` | ✅ Реализовано |
| **Share Links** | `ShareLinksModal.vue` | ✅ Реализовано |
| **Analytics** | `distributionService.ts` | ✅ Реализовано |
| **Scheduling** | `types/api.ts` | ✅ Типы определены |

**Статусы публикации:**
- `draft` — черновик
- `scheduled` — запланирована
- `published` — опубликована
- `archived` — в архиве

**Каналы распространения:**
- `website` — веб-сайт
- `social` — социальные сети
- `email` — email-рассылка
- `api` — API-интеграция

### 3.8 Bulk Operations [CUSTOM]

#### Реализованные возможности:

| Функция | Компонент | Статус |
|---------|-----------|--------|
| **Bulk Select** | `GalleryView.vue` | ✅ Реализовано |
| **Bulk Tag** | `BulkTagModal.vue` | ✅ Реализовано |
| **Bulk Move** | `BulkMoveModal.vue` | ✅ Реализовано |
| **Bulk Download** | `BulkDownloadModal.vue` | ✅ Реализовано |
| **Bulk Share** | `BulkShareModal.vue` | ✅ Реализовано |
| **Bulk Delete** | `BulkDeleteModal.vue` | ✅ Реализовано |

**BulkActions компонент:**

```vue
<!-- GalleryView.vue -->
<BulkActions
  :selected-count="assetStore.selectedCount"
  @tag="handleBulkTag"
  @move="handleBulkMove"
  @download="handleBulkDownload"
  @share="handleBulkShare"
  @delete="handleBulkDelete"
  @clear-selection="handleClearSelection"
/>
```

---

## 4. API и интеграции

### 4.1 REST API Endpoints

**Base URL:** `/api/v4/`

#### Assets API

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/v4/dam/assets/` | GET | Список активов (пагинация) |
| `/v4/dam/assets/{id}/` | GET | Детали актива |
| `/v4/dam/assets/{id}/` | PUT | Обновление актива |
| `/v4/dam/assets/{id}/` | DELETE | Удаление актива |
| `/v4/dam/assets/search/` | POST | Расширенный поиск |
| `/v4/dam/assets/bulk/` | POST | Массовые операции |
| `/v4/dam/assets/upload/` | POST | Загрузка файла |

#### Upload API (Chunked)

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/v4/assets/upload/` | POST | Простая загрузка |
| `/v4/assets/upload/init/` | POST | Инициализация chunked upload |
| `/v4/assets/upload/chunk/` | POST | Загрузка чанка |
| `/v4/assets/upload/finalize/` | POST | Завершение загрузки |
| `/v4/assets/upload/status/{id}/` | GET | Статус загрузки |

#### Collections API

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/v4/collections/` | GET | Список коллекций |
| `/v4/collections/{id}/` | GET | Детали коллекции |
| `/v4/collections/` | POST | Создание коллекции |
| `/v4/collections/{id}/` | PUT | Обновление коллекции |
| `/v4/collections/{id}/` | DELETE | Удаление коллекции |
| `/v4/collections/{id}/move/` | POST | Перемещение коллекции |
| `/v4/collections/special/` | GET | Специальные коллекции |
| `/v4/collections/bulk/` | POST | Массовые операции |

#### Distribution API

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/v4/distribution/publications/` | GET/POST | Публикации |
| `/v4/distribution/publications/{id}/` | GET/PUT/DELETE | Публикация |
| `/v4/distribution/publications/{id}/publish/` | POST | Публикация |
| `/v4/distribution/publications/{id}/links/` | GET/POST | Share links |
| `/v4/distribution/publications/{id}/analytics/` | GET | Аналитика |
| `/v4/distribution/publications/portal/{token}/` | GET | Публичный портал |
| `/v4/distribution/channels/` | GET | Каналы |

#### Admin API

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/v4/admin/users/` | GET/POST | Пользователи |
| `/v4/admin/users/{id}/` | GET/PUT/DELETE | Пользователь |
| `/v4/admin/users/bulk/` | POST | Массовые операции |
| `/v4/admin/schemas/` | GET/POST | Схемы метаданных |
| `/v4/admin/workflows/` | GET/POST | Workflows |

### 4.2 API Service Architecture

**Файл:** `src/services/apiService.ts`

```typescript
class ApiService {
  private client: AxiosInstance
  
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: { 'Content-Type': 'application/json' }
    })
    this.setupInterceptors()
  }
  
  // Interceptors:
  // - CSRF token injection
  // - Session-based auth (cookies)
  // - Retry logic (3 attempts, exponential backoff)
  // - Error handling (401 → redirect to login, 403 → forbidden)
  // - Request/Response logging (dev mode)
  
  // Caching:
  // - GET requests cached via cacheService
  // - Cache invalidation on mutations
}
```

### 4.3 Proxy Configuration

**Файл:** `vite.config.ts`

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8080',  // Django backend
    changeOrigin: true,
    secure: false,
    cookieDomainRewrite: 'localhost'
  },
  '/authentication': { ... },
  '/static': { ... },
  '/media': { ... }
}
```

---

## 5. Скрытая логика (Automation)

### 5.1 Workflows (UI)

**Файлы:**
- `src/pages/admin/WorkflowDesignerPage.vue` — визуальный редактор
- `src/components/admin/WorkflowCanvas.vue` — канвас для узлов
- `src/components/admin/NodeEditor.vue` — редактор узла
- `src/components/admin/TransitionEditor.vue` — редактор переходов

**Возможности:**
- Визуальное создание workflow с drag & drop узлов
- Определение состояний (start, state, end)
- Настройка переходов между состояниями
- Условия перехода (conditions)
- Привязка к ролям пользователей

### 5.2 Upload Workflow [CUSTOM]

**Файл:** `src/stores/uploadWorkflowStore.ts`

4-шаговый workflow загрузки:

```typescript
// Шаги workflow
const currentStep = ref(0)  // 0-3

// Шаг 0: Upload
async function uploadFiles() { ... }

// Шаг 1: Metadata
async function saveMetadata() { ... }

// Шаг 2: Collection
async function assignToCollection() { ... }

// Шаг 3: Share
async function createShare() { ... }

// Завершение
async function completeWorkflow() {
  await saveMetadata()
  await assignToCollection()
  await createShare()
  resetWorkflow()
}
```

### 5.3 Auto-refresh & Caching

**Caching Strategy:**
- `cacheService.ts` — in-memory кэш с TTL
- Persisted state в localStorage (user preferences, filters)
- Cache TTL: 5 минут для collections, schemas

**Auto-refresh:**
- `lastFetchTime` tracking в stores
- Cache invalidation после mutations

### 5.4 Error Handling & Retry

**Файл:** `src/utils/retry.ts`

```typescript
async function withRetry<T>(
  operation: () => Promise<T>,
  options: {
    maxAttempts: number
    initialDelay: number
    maxDelay?: number
    shouldRetry?: (error: unknown) => boolean
  }
): Promise<RetryResult<T>>
```

**API Error Handling:**
- Network errors → retry с exponential backoff
- 5xx errors → retry
- 401 → redirect to login
- 403 → forbidden page
- Structured error responses: `{ code, message, details }`

---

## 6. Тестирование и качество кода

### 6.1 Test Coverage

**Unit Tests:** `tests/unit/`

| Категория | Файлы | Покрытие |
|-----------|-------|----------|
| Components | 40+ spec файлов | ✅ Хорошее |
| Stores | 8 spec файлов | ✅ Хорошее |
| Services | 4 spec файлов | ✅ Базовое |
| Utils | 2 spec файлов | ✅ Базовое |
| Composables | 2 spec файлов | ✅ Базовое |

**E2E Tests:** `tests/e2e/`

| Тест | Описание |
|------|----------|
| `gallery.spec.ts` | Галерея активов |
| `home.spec.ts` | Главная страница |
| `collections-dnd.spec.ts` | Drag & Drop коллекций |
| `admin-reports-export.spec.ts` | Экспорт отчетов |

**Accessibility Tests:**
- `Button.accessibility.spec.ts`
- `GalleryView.accessibility.spec.ts`
- `DashboardPage.accessibility.spec.ts`
- `SettingsPage.accessibility.spec.ts`

### 6.2 Storybook

**Файлы:** `src/components/**/*.stories.ts`

Документированные компоненты:
- Badge
- Button
- Card
- Input
- Modal
- Select
- Header
- Sidebar

### 6.3 Code Quality Tools

| Инструмент | Назначение |
|------------|------------|
| ESLint | Линтинг TypeScript/Vue |
| Prettier | Форматирование кода |
| TypeScript | Статическая типизация |
| vue-tsc | Type checking Vue SFC |
| vitest-axe | Accessibility testing |

---

## 7. Проблемы и рекомендации

### 7.1 Выявленные проблемы

#### 🔴 Критические

| # | Проблема | Файл | Рекомендация |
|---|----------|------|--------------|
| 1 | **Дублирование типа Collection** | `uploadWorkflowStore.ts` vs `collections.ts` | Удалить локальное определение, использовать импорт из `types/collections.ts` |
| 2 | **Undefined variable `options`** | `uploadService.ts:242` | Исправить: `options.onChunkComplete` → параметр функции |
| 3 | **Undefined `collectionService`** | `uploadWorkflowStore.ts:258` | Исправить импорт: `collectionsService` |

#### 🟡 Средние

| # | Проблема | Файл | Рекомендация |
|---|----------|------|--------------|
| 4 | **Mock data в production коде** | `assetStore.ts:46-52` | Вынести mock data в отдельный файл или использовать MSW |
| 5 | **Hardcoded API endpoints** | Разные services | Централизовать endpoints в константы |
| 6 | **Отсутствие i18n** | Все компоненты | Добавить vue-i18n для интернационализации |
| 7 | **Смешанные языки в UI** | Templates | Стандартизировать (русский или английский) |

#### 🟢 Низкие

| # | Проблема | Файл | Рекомендация |
|---|----------|------|--------------|
| 8 | **Отсутствие JSDoc в некоторых services** | `assetService.ts` | Добавить документацию |
| 9 | **Неиспользуемые импорты** | Разные файлы | Запустить ESLint --fix |

### 7.2 Архитектурные рекомендации

#### Для масштабирования:

1. **Feature-based структура** — рассмотреть переход от type-based (`components/`, `stores/`) к feature-based (`features/dam/`, `features/admin/`)

2. **API Layer abstraction** — создать абстрактный слой для API, позволяющий легко переключаться между REST и GraphQL

3. **State normalization** — для больших списков рассмотреть нормализацию данных (entities pattern)

4. **Lazy loading stores** — загружать stores по требованию для уменьшения initial bundle

#### Для производительности:

1. **Image optimization** — добавить lazy loading для изображений в галерее (уже есть `loading="lazy"`)

2. **Bundle splitting** — настроить manual chunks в Vite для оптимального code splitting

3. **Service Worker** — добавить PWA поддержку для offline-first опыта

### 7.3 Готовность к интеграции с бэкендом

| Аспект | Статус | Комментарий |
|--------|--------|-------------|
| **API Types** | ✅ Готово | Полная типизация запросов/ответов |
| **Error Handling** | ✅ Готово | Retry, structured errors |
| **Auth Flow** | ✅ Готово | Session-based, 2FA |
| **CSRF Protection** | ✅ Готово | Token injection в interceptor |
| **Proxy Config** | ✅ Готово | Vite proxy для development |
| **Mock Data** | ⚠️ Частично | Есть mock для dev mode, но не MSW |

---

## Заключение

### Общая оценка проекта

| Критерий | Оценка | Комментарий |
|----------|--------|-------------|
| **Архитектура** | 8/10 | Современный стек, хорошая структура |
| **Типизация** | 9/10 | Полная TypeScript типизация |
| **UI/UX** | 8/10 | Tailwind + HeadlessUI, accessibility |
| **Тестирование** | 7/10 | Хорошее покрытие unit tests |
| **Документация** | 6/10 | Storybook есть, но JSDoc неполный |
| **Готовность к production** | 7/10 | Требуется исправление критических багов |

### Реализованный бизнес-функционал

✅ **Полностью реализовано:**
- Галерея активов с виртуальной прокруткой
- Многошаговый workflow загрузки
- Коллекции с иерархией и drag & drop
- Расширенный поиск с фасетами
- Публикации и распространение
- Административная панель (пользователи, схемы, workflows)
- Аутентификация с 2FA
- Массовые операции над активами

⚠️ **Требует интеграции с бэкендом:**
- AI-анализ (UI готов, ждет API)
- Генерация превью (отображение готово)
- Реальная обработка файлов

---

*Документ создан: 28 ноября 2025*  
*Версия анализа: 1.0*

