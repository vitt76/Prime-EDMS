# 🎨 ТЕХНИЧЕСКОЕ ЗАДАНИЕ НА ДОРАБОТКУ UI/UX ФРОНТЕНДА DAM-СИСТЕМЫ
## Дополнительные страницы и компоненты для полной функциональности

**Дата:** 27 Января 2025  
**Версия:** 1.0 (Enhancement Specification)  
**Статус:** ✅ Готово к разработке  
**Аудитория:** Cursor AI, Frontend команда, UI/UX дизайнеры  
**Язык:** Русский  
**Базируется на:** DAM-Frontend-TZ-v2.0-FULL.md, DAM-Frontend-Transformation-Plan-v3.md, DAM-Frontend-User-Paths.md

---

## 📑 ОГЛАВЛЕНИЕ

1. [Резюме доработок](#резюме-доработок)
2. [Анализ текущего состояния](#анализ-текущего-состояния)
3. [Архитектурные решения и интеграция](#архитектурные-решения-и-интеграция)
4. [Admin Module (4 страницы)](#admin-module-4-страницы)
5. [Collections Management](#collections-management)
6. [Reports & Analytics](#reports--analytics)
7. [Auth Pages Enhancement](#auth-pages-enhancement)
8. [Error Pages](#error-pages)
9. [Distribution Sub-pages](#distribution-sub-pages)
10. [Дополнительные модальные окна](#дополнительные-модальные-окна)
11. [Улучшения существующих компонентов](#улучшения-существующих-компонентов)
12. [Приоритизация и план реализации](#приоритизация-и-план-реализации)
13. [Критерии готовности](#критерии-готовности)

---

# 🎯 РЕЗЮМЕ ДОРАБОТОК

## Контекст

После анализа текущего состояния фронтенда (Phase 1-3 завершены) выявлены отсутствующие критические страницы и компоненты, необходимые для полной функциональности DAM-системы уровня Bynder/Canto.

## Объем доработок

| Категория | Количество | Приоритет | Статус |
|-----------|------------|-----------|--------|
| **Admin страницы** | 4 | 🔴 P0 | ❌ Отсутствуют |
| **User страницы** | 2 | 🟡 P1 | ❌ Отсутствуют |
| **Auth страницы** | 2 | 🟡 P1 | ❌ Отсутствуют |
| **Error страницы** | 3 | 🟡 P1 | ⚠️ Частично (только 404) |
| **Distribution sub-pages** | 2 | 🟡 P1 | ❌ Отсутствуют |
| **Модальные окна** | 5 | 🟡 P1-P2 | ❌ Отсутствуют |
| **ИТОГО** | **18** | - | - |

## Метрики успеха

| Метрика | Текущее | Целевое |
|---------|---------|---------|
| **Покрытие функциональности** | 70% | 100% |
| **Admin функциональность** | 0% | 100% |
| **Error handling** | 33% (только 404) | 100% |
| **User onboarding** | 50% | 100% |

---

# 📊 АНАЛИЗ ТЕКУЩЕГО СОСТОЯНИЯ

## Реализованные страницы (9 из 15 основных)

✅ **Основные страницы:**
- DashboardPage.vue ✅
- DAMPage.vue ✅
- AssetDetailPage.vue ✅
- DistributionPage.vue ✅
- LoginPage.vue ✅
- SettingsPage.vue ✅ (включает Profile функциональность)
- AdvancedSearchPage.vue ✅
- NotFoundPage.vue ✅ (404)
- HomePage.vue ✅

## Отсутствующие страницы

❌ **Admin Module (0% готовности):**
- AdminPage.vue
- UserManagementPage.vue
- MetadataSchemaPage.vue
- WorkflowDesignerPage.vue

❌ **User страницы:**
- CollectionsPage.vue
- ReportsPage.vue

❌ **Auth страницы:**
- ForgotPasswordPage.vue
- ResetPasswordPage.vue

❌ **Error страницы:**
- Error500Page.vue
- UnauthorizedPage.vue (401)
- ForbiddenPage.vue (403)

❌ **Distribution sub-pages:**
- PublicationDetailPage.vue
- PublicationPublicPage.vue

---

# 🏗️ АРХИТЕКТУРНЫЕ РЕШЕНИЯ И ИНТЕГРАЦИЯ

## Приоритет: 🔴 P0 (Критично для архитектурной целостности)

> **Примечание архитектора:** Этот раздел описывает архитектурные решения для интеграции новых страниц и компонентов с существующей кодовой базой. Все решения основаны на анализе текущей реализации и следуют принципам, описанным в DAM-Frontend-Transformation-Plan-v3.md и DAM-Frontend-User-Paths.md.

---

## 📐 Архитектурные принципы интеграции

### 1. Соответствие существующей архитектуре

**Текущая архитектура фронтенда:**
```typescript
frontend/src/
├── components/          # Переиспользуемые компоненты
│   ├── Common/         # Базовые компоненты (Button, Input, Modal, Card, Badge)
│   ├── DAM/            # DAM-специфичные компоненты (GalleryView, FiltersPanel)
│   ├── Distribution/   # Distribution компоненты
│   └── Layout/         # Layout компоненты (Header, Sidebar, MainContent)
├── pages/              # Страницы (роуты)
├── stores/             # Pinia stores (assetStore, authStore, uiStore, etc.)
├── services/           # API services (apiService, assetService, etc.)
├── types/              # TypeScript типы
├── router/             # Vue Router конфигурация
└── utils/              # Утилиты
```

**Принцип:** Все новые страницы и компоненты должны следовать этой структуре и переиспользовать существующие компоненты.

---

### 2. State Management Architecture

#### 2.1 Новые Pinia Stores

**adminStore.ts** (новый)
```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { adminService } from '@/services/adminService'
import type { User, MetadataSchema, Workflow } from '@/types'

export const useAdminStore = defineStore('admin', () => {
  // Users state
  const users = ref<User[]>([])
  const totalUsersCount = ref(0)
  const selectedUsers = ref<number[]>([])
  const usersFilters = ref({ role: '', status: '', search: '' })
  
  // Metadata Schemas state
  const schemas = ref<MetadataSchema[]>([])
  const currentSchema = ref<MetadataSchema | null>(null)
  const currentField = ref<Field | null>(null)
  
  // Workflows state
  const workflows = ref<Workflow[]>([])
  const currentWorkflow = ref<Workflow | null>(null)
  const selectedNode = ref<Node | null>(null)
  
  // Actions
  async function fetchUsers(params?: GetUsersParams) {
    // Использует adminService.getUsers()
  }
  
  async function createUser(userData: CreateUserRequest) {
    // Использует adminService.createUser()
  }
  
  // ... другие actions
  
  return {
    // State
    users, totalUsersCount, selectedUsers, usersFilters,
    schemas, currentSchema, currentField,
    workflows, currentWorkflow, selectedNode,
    // Actions
    fetchUsers, createUser, updateUser, deleteUser,
    fetchSchemas, createSchema, updateSchema, deleteSchema,
    fetchWorkflows, createWorkflow, updateWorkflow, deleteWorkflow
  }
}, {
  persist: {
    paths: ['usersFilters'] // Только фильтры персистятся
  }
})
```

**reportsStore.ts** (новый)
```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { reportsService } from '@/services/reportsService'
import type { ReportData, ReportType } from '@/types'

export const useReportsStore = defineStore('reports', () => {
  const currentReport = ref<ReportType>('usage')
  const dateRange = ref({ start: new Date(), end: new Date() })
  const reportData = ref<ReportData | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  
  // Actions
  async function fetchReportData(reportType: ReportType, dateRange: DateRange) {
    isLoading.value = true
    try {
      const data = await reportsService.getReportData(reportType, dateRange)
      reportData.value = data
    } catch (err) {
      error.value = formatApiError(err)
    } finally {
      isLoading.value = false
    }
  }
  
  return {
    currentReport, dateRange, reportData, isLoading, error,
    fetchReportData, setDateRange, exportReport, scheduleReport
  }
})
```

**collectionStore.ts** (расширение assetStore или отдельный)
```typescript
// Вариант 1: Расширить существующий assetStore
// Вариант 2: Создать отдельный collectionStore

// Рекомендация: Расширить assetStore для сохранения консистентности
// Коллекции тесно связаны с активами

export const useAssetStore = defineStore('asset', () => {
  // ... существующий код ...
  
  // Collections state (новое)
  const collections = ref<Collection[]>([])
  const currentCollection = ref<Collection | null>(null)
  const collectionTree = ref<TreeNode[]>([])
  
  // Collections actions (новые)
  async function fetchCollections() {
    // Использует collectionService.getCollections()
  }
  
  async function createCollection(data: CreateCollectionRequest) {
    // Использует collectionService.createCollection()
  }
  
  // ... остальной код ...
})
```

#### 2.2 Интеграция с существующими stores

**Связи между stores:**
```typescript
// adminStore → authStore (для проверки прав)
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()
if (!authStore.hasPermission('admin.user_manage')) {
  throw new Error('Access denied')
}

// reportsStore → assetStore (для drill-down)
import { useAssetStore } from '@/stores/assetStore'

function navigateToAsset(assetId: number) {
  assetStore.getAssetDetail(assetId)
  router.push(`/dam/assets/${assetId}`)
}

// collectionStore → assetStore (для фильтрации активов)
function filterAssetsByCollection(collectionId: number) {
  assetStore.setFilters({ collection_id: collectionId })
  assetStore.fetchAssets()
}
```

---

### 3. API Services Architecture

#### 3.1 Новые API Services

**adminService.ts** (новый)
```typescript
import { apiService } from './apiService'
import type {
  User,
  CreateUserRequest,
  UpdateUserRequest,
  MetadataSchema,
  Workflow,
  PaginatedResponse
} from '@/types/api'

class AdminService {
  // Users API
  async getUsers(params?: GetUsersParams): Promise<PaginatedResponse<User>> {
    return apiService.get<PaginatedResponse<User>>('/v4/admin/users/', { params })
  }
  
  async createUser(data: CreateUserRequest): Promise<User> {
    return apiService.post<User>('/v4/admin/users/', data)
  }
  
  async updateUser(id: number, data: UpdateUserRequest): Promise<User> {
    return apiService.put<User>(`/v4/admin/users/${id}/`, data)
  }
  
  async deleteUser(id: number): Promise<void> {
    return apiService.delete<void>(`/v4/admin/users/${id}/`)
  }
  
  async bulkUserOperation(operation: BulkUserOperationRequest): Promise<BulkUserOperationResponse> {
    return apiService.post<BulkUserOperationResponse>('/v4/admin/users/bulk/', operation)
  }
  
  // Metadata Schemas API
  async getSchemas(): Promise<MetadataSchema[]> {
    return apiService.get<MetadataSchema[]>('/v4/admin/metadata-schemas/')
  }
  
  async createSchema(data: CreateSchemaRequest): Promise<MetadataSchema> {
    return apiService.post<MetadataSchema>('/v4/admin/metadata-schemas/', data)
  }
  
  // Workflows API
  async getWorkflows(): Promise<Workflow[]> {
    return apiService.get<Workflow[]>('/v4/admin/workflows/')
  }
  
  async validateWorkflow(id: number): Promise<WorkflowValidationResult> {
    return apiService.post<WorkflowValidationResult>(`/v4/admin/workflows/${id}/validate/`)
  }
}

export const adminService = new AdminService()
```

**reportsService.ts** (новый)
```typescript
import { apiService } from './apiService'
import type { ReportData, ReportType, DateRange } from '@/types/api'

class ReportsService {
  async getReportData(
    reportType: ReportType,
    dateRange: DateRange
  ): Promise<ReportData> {
    return apiService.get<ReportData>(`/v4/analytics/${reportType}/`, {
      params: {
        start_date: dateRange.start.toISOString(),
        end_date: dateRange.end.toISOString()
      }
    })
  }
  
  async exportReport(
    reportType: ReportType,
    format: 'csv' | 'pdf',
    dateRange: DateRange
  ): Promise<Blob> {
    return apiService.get<Blob>(`/v4/analytics/export/`, {
      params: {
        report_type: reportType,
        format,
        start_date: dateRange.start.toISOString(),
        end_date: dateRange.end.toISOString()
      },
      responseType: 'blob'
    })
  }
}

export const reportsService = new ReportsService()
```

**collectionService.ts** (новый или расширение assetService)
```typescript
import { apiService } from './apiService'
import type { Collection, CreateCollectionRequest } from '@/types/api'

class CollectionService {
  async getCollections(): Promise<Collection[]> {
    return apiService.get<Collection[]>('/v4/dam/collections/')
  }
  
  async getCollection(id: number): Promise<Collection> {
    return apiService.get<Collection>(`/v4/dam/collections/${id}/`)
  }
  
  async getCollectionAssets(
    id: number,
    params?: GetAssetsParams
  ): Promise<PaginatedResponse<Asset>> {
    return apiService.get<PaginatedResponse<Asset>>(
      `/v4/dam/collections/${id}/items/`,
      { params }
    )
  }
  
  async createCollection(data: CreateCollectionRequest): Promise<Collection> {
    return apiService.post<Collection>('/v4/dam/collections/', data)
  }
  
  async addAssetsToCollection(
    collectionId: number,
    assetIds: number[]
  ): Promise<void> {
    return apiService.post<void>(
      `/v4/dam/collections/${collectionId}/items/`,
      { asset_ids: assetIds }
    )
  }
}

export const collectionService = new CollectionService()
```

#### 3.2 Интеграция с существующим apiService

**Все новые services используют существующий apiService:**
- ✅ Автоматическая обработка CSRF токенов
- ✅ Автоматическая обработка ошибок (401, 403, 500)
- ✅ Автоматический retry на сетевых ошибках
- ✅ Кеширование (где применимо)
- ✅ Type-safe responses

---

### 4. Routing Architecture

#### 4.1 Структура роутов

**Новые роуты в `router/index.ts`:**
```typescript
const routes: RouteRecordRaw[] = [
  // ... существующие роуты ...
  
  // Admin routes (nested)
  {
    path: '/admin',
    component: () => import('@/pages/AdminPage.vue'),
    meta: { 
      requiresAuth: true,
      requiresPermission: 'admin.access' // Новое: permission check
    },
    children: [
      {
        path: 'users',
        name: 'admin-users',
        component: () => import('@/pages/admin/UserManagementPage.vue'),
        meta: { requiresPermission: 'admin.user_manage' }
      },
      {
        path: 'metadata-schemas',
        name: 'admin-metadata-schemas',
        component: () => import('@/pages/admin/MetadataSchemaPage.vue'),
        meta: { requiresPermission: 'admin.schema_manage' }
      },
      {
        path: 'workflows',
        name: 'admin-workflows',
        component: () => import('@/pages/admin/WorkflowDesignerPage.vue'),
        meta: { requiresPermission: 'admin.workflow_manage' }
      },
      {
        path: 'reports',
        name: 'admin-reports',
        component: () => import('@/pages/admin/ReportsPage.vue'),
        meta: { requiresPermission: 'admin.reports_view' }
      }
    ]
  },
  
  // Collections routes
  {
    path: '/dam/collections',
    name: 'collections',
    component: () => import('@/pages/CollectionsPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/dam/collections/:id',
    name: 'collection-detail',
    component: () => import('@/pages/CollectionsPage.vue'),
    meta: { requiresAuth: true }
  },
  
  // Reports route (может быть в admin или отдельно)
  {
    path: '/reports',
    name: 'reports',
    component: () => import('@/pages/ReportsPage.vue'),
    meta: { 
      requiresAuth: true,
      requiresPermission: 'reports.view' // Может быть доступно не только админам
    }
  },
  
  // Auth routes
  {
    path: '/auth/forgot-password',
    name: 'forgot-password',
    component: () => import('@/pages/ForgotPasswordPage.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/auth/reset-password/:token',
    name: 'reset-password',
    component: () => import('@/pages/ResetPasswordPage.vue'),
    meta: { requiresAuth: false }
  },
  
  // Error routes
  {
    path: '/500',
    name: 'error-500',
    component: () => import('@/pages/Error500Page.vue')
  },
  {
    path: '/401',
    name: 'unauthorized',
    component: () => import('@/pages/UnauthorizedPage.vue')
  },
  {
    path: '/403',
    name: 'forbidden',
    component: () => import('@/pages/ForbiddenPage.vue')
  },
  
  // Distribution sub-pages
  {
    path: '/distribution/publications/:id',
    name: 'publication-detail',
    component: () => import('@/pages/PublicationDetailPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/distribution/public/:token',
    name: 'publication-public',
    component: () => import('@/pages/PublicationPublicPage.vue'),
    meta: { requiresAuth: false } // Публичный доступ
  }
]
```

#### 4.2 Permission-based Route Guards

**Расширение router guards:**
```typescript
// router/index.ts

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const uiStore = useUIStore()
  
  // ... существующая логика проверки аутентификации ...
  
  // НОВОЕ: Permission-based access control
  if (to.meta.requiresPermission) {
    const permission = to.meta.requiresPermission as string
    if (!authStore.hasPermission(permission)) {
      // Redirect to forbidden page
      next({
        name: 'forbidden',
        query: { 
          returnTo: to.fullPath,
          requiredPermission: permission
        }
      })
      return
    }
  }
  
  // ... остальная логика ...
})
```

---

### 5. Component Reusability Strategy

#### 5.1 Переиспользование существующих компонентов

**Все новые страницы должны использовать:**
- ✅ `Layout/Header.vue` - общий header
- ✅ `Layout/Sidebar.vue` - общий sidebar (с расширением для admin nav)
- ✅ `Layout/MainContent.vue` - общий контейнер контента
- ✅ `Common/Button.vue` - все кнопки
- ✅ `Common/Input.vue` - все input поля
- ✅ `Common/Modal.vue` - все модальные окна
- ✅ `Common/Card.vue` - все карточки
- ✅ `Common/Badge.vue` - все badges
- ✅ `Common/Pagination.vue` - пагинация
- ✅ `DAM/GalleryView.vue` - для отображения активов (в Collections, Distribution)

**Пример переиспользования:**
```vue
<!-- CollectionsPage.vue -->
<template>
  <div class="collections-page">
    <!-- Использует существующий GalleryView -->
    <GalleryView 
      :assets="collectionAssets"
      :isLoading="isLoading"
      @select-asset="handleSelectAsset"
    />
    
    <!-- Использует существующий Modal -->
    <Modal
      v-if="showCreateModal"
      title="Create Collection"
      @close="showCreateModal = false"
    >
      <CreateCollectionForm @submit="handleCreateCollection" />
    </Modal>
  </div>
</template>
```

#### 5.2 Новые переиспользуемые компоненты

**Компоненты, которые будут созданы и переиспользованы:**

1. **AdminNavigationTabs.vue** - табы для admin страниц
   - Используется в: AdminPage
   - Может быть переиспользован для других tabbed интерфейсов

2. **DataTable.vue** - универсальная таблица с сортировкой, фильтрацией
   - Используется в: UserManagementPage, ReportsPage
   - Переиспользуется везде, где нужна таблица

3. **TreeView.vue** - древовидный компонент
   - Используется в: CollectionsPage (collection tree)
   - Может быть переиспользован для других иерархических структур

4. **ChartContainer.vue** - обертка для графиков
   - Используется в: ReportsPage
   - Абстрагирует выбор chart library

---

### 6. TypeScript Types Architecture

#### 6.1 Новые типы в `types/api.ts`

```typescript
// Admin API types
export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  is_staff: boolean
  is_superuser: boolean
  role: 'admin' | 'editor' | 'viewer'
  date_joined: string
  last_login?: string
  avatar_url?: string
  permissions?: string[]
}

export interface CreateUserRequest {
  username: string
  email: string
  first_name: string
  last_name: string
  password?: string
  role: 'admin' | 'editor' | 'viewer'
  is_active: boolean
  send_invitation?: boolean
}

export interface MetadataSchema {
  id: number
  name: string
  description?: string
  applies_to: ('image' | 'video' | 'document' | 'all')[]
  fields: SchemaField[]
  created_date: string
  updated_date: string
}

export interface SchemaField {
  id?: number
  name: string
  type: FieldType
  required: boolean
  default_value?: unknown
  options?: FieldOption[]
  validation_rules?: ValidationRules
  help_text?: string
  order: number
}

export type FieldType = 
  | 'text' 
  | 'textarea' 
  | 'number' 
  | 'date' 
  | 'date_range'
  | 'select' 
  | 'multi_select'
  | 'checkbox'
  | 'file_upload'
  | 'url'

export interface Workflow {
  id: number
  name: string
  description?: string
  nodes: WorkflowNode[]
  transitions: WorkflowTransition[]
  is_active: boolean
  created_date: string
}

export interface WorkflowNode {
  id: string
  name: string
  type: 'start' | 'state' | 'end'
  position: { x: number; y: number }
  allowed_roles: string[]
  actions: string[]
  notifications?: NotificationConfig
}

export interface WorkflowTransition {
  id: string
  from_node: string
  to_node: string
  condition: TransitionCondition
  label?: string
}

// Collections API types
export interface Collection {
  id: number
  name: string
  description?: string
  parent_id?: number
  items_count: number
  total_size: number
  created_date: string
  created_by: number
  privacy: 'private' | 'shared' | 'public'
  shared_with?: number[]
}

// Reports API types
export interface ReportData {
  report_type: ReportType
  date_range: DateRange
  summary: ReportSummary
  charts: ChartData[]
  tables: TableData[]
}

export type ReportType = 'usage' | 'downloads' | 'users' | 'storage' | 'custom'
```

#### 6.2 Интеграция с существующими типами

**Все новые типы должны:**
- ✅ Расширять существующие базовые типы (`ApiResponse`, `PaginatedResponse`)
- ✅ Использовать общие типы (`User`, `Asset`) где возможно
- ✅ Следовать соглашениям именования (PascalCase для интерфейсов, camelCase для полей)

---

### 7. Permission & Security Architecture

#### 7.1 Permission Checks Pattern

**Все новые страницы должны проверять права:**

```vue
<!-- UserManagementPage.vue -->
<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useAdminStore } from '@/stores/adminStore'

const router = useRouter()
const authStore = useAuthStore()
const adminStore = useAdminStore()

onMounted(async () => {
  // Проверка прав доступа
  if (!authStore.hasPermission('admin.user_manage')) {
    router.push({ name: 'forbidden' })
    return
  }
  
  // Загрузка данных
  await adminStore.fetchUsers()
})
</script>
```

#### 7.2 Route-level Permission Guards

**В router/index.ts:**
```typescript
router.beforeEach(async (to, from, next) => {
  // ... существующая логика ...
  
  // Permission check для admin routes
  if (to.meta.requiresPermission) {
    const authStore = useAuthStore()
    const permission = to.meta.requiresPermission as string
    
    if (!authStore.hasPermission(permission)) {
      // Логирование попытки доступа для аудита
      console.warn(`Access denied: User ${authStore.user?.id} attempted to access ${to.path} (required: ${permission})`)
      
      next({
        name: 'forbidden',
        query: {
          returnTo: to.fullPath,
          requiredPermission: permission
        }
      })
      return
    }
  }
  
  next()
})
```

#### 7.3 Component-level Permission Checks

**Условный рендеринг на основе прав:**
```vue
<template>
  <div>
    <!-- Кнопка видна только админам -->
    <Button 
      v-if="canManageUsers"
      @click="openCreateUserModal"
    >
      Create User
    </Button>
    
    <!-- Таблица с условными действиями -->
    <DataTable :items="users">
      <template #actions="{ item }">
        <Button 
          v-if="canEditUser(item)"
          @click="editUser(item)"
        >
          Edit
        </Button>
        <Button 
          v-if="canDeleteUser(item)"
          variant="danger"
          @click="deleteUser(item)"
        >
          Delete
        </Button>
      </template>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
const authStore = useAuthStore()

const canManageUsers = computed(() => 
  authStore.hasPermission('admin.user_manage')
)

function canEditUser(user: User) {
  // Можно редактировать только если:
  // 1. Есть право admin.user_edit
  // 2. Не пытаемся редактировать суперпользователя (если сам не суперпользователь)
  return authStore.hasPermission('admin.user_edit') &&
         (user.is_superuser ? authStore.user?.is_superuser : true)
}
</script>
```

---

### 8. Performance Optimization Strategy

#### 8.1 Lazy Loading для новых страниц

**Все новые страницы должны быть lazy-loaded:**
```typescript
// router/index.ts
{
  path: '/admin',
  component: () => import('@/pages/AdminPage.vue'), // ✅ Lazy load
  children: [
    {
      path: 'users',
      component: () => import('@/pages/admin/UserManagementPage.vue') // ✅ Lazy load
    }
  ]
}
```

#### 8.2 Code Splitting для тяжелых компонентов

**WorkflowDesignerPage с canvas библиотекой:**
```typescript
// WorkflowDesignerPage.vue
<script setup lang="ts">
import { defineAsyncComponent } from 'vue'

// Lazy load тяжелой canvas библиотеки
const WorkflowCanvas = defineAsyncComponent(() => 
  import('@/components/admin/WorkflowCanvas.vue')
)
</script>
```

#### 8.3 Кеширование данных

**Стратегия кеширования:**
```typescript
// adminStore.ts
async function fetchUsers(params?: GetUsersParams) {
  // Кешируем список пользователей на 5 минут
  const cacheKey = `admin_users_${JSON.stringify(params)}`
  const cached = cacheService.get<User[]>(cacheKey)
  
  if (cached) {
    users.value = cached
    return
  }
  
  const response = await adminService.getUsers(params)
  users.value = response.results
  totalUsersCount.value = response.count
  
  // Кешируем на 5 минут
  cacheService.set(cacheKey, users.value, 5 * 60 * 1000)
}

// Metadata schemas кешируются дольше (редко меняются)
async function fetchSchemas() {
  const cacheKey = 'metadata_schemas'
  const cached = cacheService.get<MetadataSchema[]>(cacheKey)
  
  if (cached) {
    schemas.value = cached
    return
  }
  
  schemas.value = await adminService.getSchemas()
  
  // Кешируем на 30 минут
  cacheService.set(cacheKey, schemas.value, 30 * 60 * 1000)
}
```

#### 8.4 Virtual Scrolling для больших списков

**UserManagementPage с 1000+ пользователями:**
```vue
<template>
  <DataTable 
    :items="users"
    :virtual-scroll="true"
    :item-height="60"
  >
    <!-- ... -->
  </DataTable>
</template>
```

---

### 9. Error Handling Architecture

#### 9.1 Централизованная обработка ошибок

**Все новые страницы используют существующий error handling:**
```typescript
// services/apiService.ts уже имеет:
// - Автоматический retry
// - Структурированные error responses
// - Логирование в Sentry (если настроено)

// Новые страницы просто используют try/catch:
try {
  await adminStore.fetchUsers()
} catch (error) {
  // apiService уже обработал ошибку и вернул структурированный ApiError
  // Просто показываем пользователю
  uiStore.addNotification({
    type: 'error',
    message: formatApiError(error)
  })
}
```

#### 9.2 Error Boundary для новых страниц

**Автоматический redirect на error pages:**
```typescript
// services/apiService.ts (существующий interceptor)
responseInterceptor: (error) => {
  if (error.response) {
    switch (error.response.status) {
      case 401:
        router.push({ name: 'unauthorized' })
        break
      case 403:
        router.push({ name: 'forbidden' })
        break
      case 500:
        router.push({ name: 'error-500' })
        break
    }
  }
}
```

---

### 10. Testing Architecture

#### 10.1 Unit Tests Structure

**Все новые компоненты следуют существующей структуре тестов:**
```
tests/unit/
├── components/
│   ├── admin/
│   │   ├── UserManagementPage.spec.ts
│   │   ├── MetadataSchemaPage.spec.ts
│   │   └── WorkflowDesignerPage.spec.ts
│   └── collections/
│       └── CollectionsPage.spec.ts
├── stores/
│   ├── adminStore.spec.ts
│   ├── reportsStore.spec.ts
│   └── collectionStore.spec.ts
└── services/
    ├── adminService.spec.ts
    ├── reportsService.spec.ts
    └── collectionService.spec.ts
```

#### 10.2 E2E Tests Structure

**Все новые страницы имеют E2E тесты:**
```
tests/e2e/
├── admin/
│   ├── user-management.spec.ts
│   ├── metadata-schema-editor.spec.ts
│   └── workflow-designer.spec.ts
├── collections/
│   └── collections-management.spec.ts
└── reports/
    └── reports-analytics.spec.ts
```

#### 10.3 Test Coverage Requirements

**Минимальное покрытие:**
- Компоненты: 85%+
- Stores: 90%+
- Services: 95%+
- Utils: 100%

---

### 11. Integration Points

#### 11.1 Интеграция с существующим Sidebar

**Расширение Sidebar для Admin навигации:**
```vue
<!-- Sidebar.vue (существующий) -->
<template>
  <nav>
    <!-- Существующие пункты меню -->
    <NavItem to="/dashboard" icon="home">Dashboard</NavItem>
    <NavItem to="/dam" icon="image">DAM</NavItem>
    <NavItem to="/distribution" icon="share">Distribution</NavItem>
    
    <!-- НОВОЕ: Admin секция (только для админов) -->
    <NavSection 
      v-if="isAdmin"
      title="Administration"
      icon="cog"
    >
      <NavItem to="/admin/users">Users</NavItem>
      <NavItem to="/admin/metadata-schemas">Metadata Schemas</NavItem>
      <NavItem to="/admin/workflows">Workflows</NavItem>
      <NavItem to="/admin/reports">Reports</NavItem>
    </NavSection>
  </nav>
</template>

<script setup lang="ts">
const authStore = useAuthStore()

const isAdmin = computed(() => 
  authStore.hasPermission('admin.access')
)
</script>
```

#### 11.2 Интеграция с Header Search

**Header Search должен работать на всех новых страницах:**
```vue
<!-- Header.vue (существующий) -->
<script setup lang="ts">
function handleSearch(query: string) {
  // Поиск работает глобально
  // На admin страницах ищет пользователей
  // На collections страницах ищет коллекции
  // На reports страницах ищет активы для drill-down
  
  const route = useRoute()
  
  if (route.path.startsWith('/admin')) {
    // Поиск пользователей
    adminStore.searchUsers(query)
  } else if (route.path.startsWith('/dam/collections')) {
    // Поиск коллекций
    collectionStore.searchCollections(query)
  } else {
    // Обычный поиск активов
    searchStore.search(query)
  }
}
</script>
```

#### 11.3 Интеграция с Notification System

**Все новые страницы используют существующую систему уведомлений:**
```typescript
// В любом новом компоненте
import { useUIStore } from '@/stores/uiStore'

const uiStore = useUIStore()

async function createUser(userData: CreateUserRequest) {
  try {
    await adminStore.createUser(userData)
    
    // Используем существующую систему уведомлений
    uiStore.addNotification({
      type: 'success',
      message: 'User created successfully',
      duration: 3000
    })
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      message: formatApiError(error),
      duration: 5000
    })
  }
}
```

---

### 12. Migration Strategy

#### 12.1 Постепенное внедрение

**Фаза 1: Admin Module (Week 11)**
- Создать adminStore, adminService
- Создать AdminPage + подстраницы
- Интегрировать в router
- Добавить permission checks

**Фаза 2: User Pages (Week 12)**
- Создать collectionStore (расширить assetStore)
- Создать CollectionsPage
- Создать reportsStore, reportsService
- Создать ReportsPage

**Фаза 3: Error & Auth Pages (Week 12)**
- Создать error pages
- Интегрировать в error boundary
- Создать auth pages
- Обновить router guards

#### 12.2 Backward Compatibility

**Все новые страницы:**
- ✅ Не ломают существующие роуты
- ✅ Не изменяют существующие API endpoints
- ✅ Используют существующие компоненты без изменений
- ✅ Следуют существующим паттернам кода

---

### 13. Performance Benchmarks

#### 13.1 Целевые метрики для новых страниц

| Страница | Initial Load | Time to Interactive | Lighthouse Score |
|----------|--------------|---------------------|------------------|
| AdminPage | < 1.5s | < 2.5s | 90+ |
| UserManagementPage | < 2s | < 3s | 88+ |
| MetadataSchemaPage | < 1.8s | < 2.8s | 90+ |
| WorkflowDesignerPage | < 2.5s | < 4s | 85+ (canvas тяжелый) |
| CollectionsPage | < 1.5s | < 2.5s | 90+ |
| ReportsPage | < 2s | < 3s | 88+ |

#### 13.2 Оптимизации

**Для всех новых страниц:**
- ✅ Lazy loading компонентов
- ✅ Code splitting по роутам
- ✅ Виртуальный скроллинг для больших списков
- ✅ Кеширование данных (где применимо)
- ✅ Debouncing для поиска и фильтров
- ✅ Оптимизация изображений (lazy loading)

---

### 14. Accessibility Requirements

#### 14.1 WCAG 2.1 AA Compliance

**Все новые страницы должны:**
- ✅ Поддерживать keyboard navigation
- ✅ Иметь ARIA labels для всех интерактивных элементов
- ✅ Поддерживать screen readers
- ✅ Иметь достаточный color contrast (4.5:1)
- ✅ Иметь focus indicators
- ✅ Поддерживать zoom до 200% без потери функциональности

**Примеры:**
```vue
<!-- UserManagementPage.vue -->
<template>
  <div role="main" aria-label="User Management">
    <button
      @click="createUser"
      aria-label="Create new user"
      :aria-describedby="'create-user-hint'"
    >
      Create User
    </button>
    <span id="create-user-hint" class="sr-only">
      Opens modal to create a new user account
    </span>
    
    <table role="table" aria-label="Users list">
      <thead>
        <tr>
          <th scope="col">Name</th>
          <th scope="col">Email</th>
          <!-- ... -->
        </tr>
      </thead>
      <tbody>
        <tr 
          v-for="user in users" 
          :key="user.id"
          :aria-label="`User ${user.username}`"
        >
          <!-- ... -->
        </tr>
      </tbody>
    </table>
  </div>
</template>
```

---

### 15. Documentation Requirements

#### 15.1 Storybook Stories

**Все новые компоненты должны иметь Storybook stories:**
```typescript
// UserManagementPage.stories.ts
export default {
  title: 'Pages/Admin/UserManagementPage',
  component: UserManagementPage
} as Meta

export const Default: Story = {
  args: {
    // Mock data
  }
}

export const WithManyUsers: Story = {
  args: {
    users: Array.from({ length: 100 }, (_, i) => createMockUser(i))
  }
}

export const Loading: Story = {
  args: {
    isLoading: true
  }
}
```

#### 15.2 Code Documentation

**Все новые функции должны иметь JSDoc:**
```typescript
/**
 * Fetches users from the API with optional filtering and pagination.
 * 
 * @param params - Optional query parameters for filtering and pagination
 * @returns Promise that resolves to paginated user list
 * @throws {ApiError} If API request fails or user lacks permissions
 * 
 * @example
 * ```typescript
 * await adminStore.fetchUsers({ 
 *   page: 1, 
 *   page_size: 50,
 *   role: 'editor'
 * })
 * ```
 */
async function fetchUsers(params?: GetUsersParams): Promise<void> {
  // ...
}
```

---

## 🔄 Интеграция с существующими компонентами

### Переиспользование GalleryView

**CollectionsPage использует существующий GalleryView:**
```vue
<!-- CollectionsPage.vue -->
<template>
  <div class="collections-page">
    <CollectionTree 
      :collections="collections"
      @select="handleCollectionSelect"
    />
    
    <!-- Переиспользуем существующий GalleryView -->
    <GalleryView
      v-if="currentCollection"
      :assets="collectionAssets"
      :isLoading="isLoading"
      @select-asset="handleSelectAsset"
      @bulk-action="handleBulkAction"
    />
  </div>
</template>
```

### Переиспользование FiltersPanel

**ReportsPage может использовать существующий FiltersPanel для фильтрации:**
```vue
<!-- ReportsPage.vue -->
<template>
  <div class="reports-page">
    <!-- Используем существующий DateRangePicker -->
    <DateRangePicker
      v-model="dateRange"
      @change="handleDateRangeChange"
    />
    
    <!-- Используем существующий Select для выбора типа отчета -->
    <Select
      v-model="currentReport"
      :options="reportTypes"
      @change="handleReportChange"
    />
  </div>
</template>
```

---

## 📋 Checklist для разработчиков

**Перед созданием новой страницы/компонента:**

- [ ] Проверил существующие компоненты для переиспользования
- [ ] Определил необходимые новые stores/services
- [ ] Создал TypeScript типы в `types/api.ts`
- [ ] Добавил роуты в `router/index.ts` с permission checks
- [ ] Настроил lazy loading для страницы
- [ ] Добавил permission checks в компонент
- [ ] Интегрировал с существующими Layout компонентами
- [ ] Настроил error handling
- [ ] Добавил accessibility attributes
- [ ] Создал Storybook stories
- [ ] Написал unit tests (85%+ coverage)
- [ ] Написал E2E tests для основных flows
- [ ] Проверил производительность (Lighthouse)
- [ ] Проверил responsive design
- [ ] Обновил документацию

---

# 🔧 ADMIN MODULE (4 СТРАНИЦЫ)

## Приоритет: 🔴 P0 (Критично для администрирования)

### 1. AdminPage.vue

**Назначение:** Главная страница административной панели (роутер outlet для admin подстраниц)

**Route:** `/admin`

**Layout:**
```
┌─────────────────────────────────────────────────┐
│ Header (64px)                                   │
├──────────┬──────────────────────────────────────┤
│ Sidebar  │  Admin Content Area                  │
│ (280px)  │  ┌────────────────────────────────┐ │
│          │  │  Admin Navigation Tabs         │ │
│ Admin    │  │  [Users] [Schemas] [Workflows] │ │
│ Nav:     │  │  [Integrations] [Reports]      │ │
│ • Users  │  ├────────────────────────────────┤ │
│ • Schemas│  │  Router Outlet (sub-pages)      │ │
│ • Workfl │  │  • UserManagementPage           │ │
│ • Integr │  │  • MetadataSchemaPage           │ │
│ • Reports│  │  • WorkflowDesignerPage         │ │
│          │  │  • AdminIntegrationsPage        │ │
│          │  │  • AdminReportsPage             │ │
│          │  └────────────────────────────────┘ │
└──────────┴──────────────────────────────────────┘
```

**Компоненты:**
- AdminNavigationTabs.vue (табы для переключения между подстраницами)
- RouterView (для отображения подстраниц)

**Features:**
- Permission gating (только для admin роли)
- Breadcrumbs: Главная > Администрирование > [Tab Name]
- Active tab highlighting
- Responsive: на мобильных табы → dropdown

**Props:** None (layout component)

**Emits:**
- `tab-change: (tabName: string) => void`

**Accessibility:**
- ARIA: `role="navigation"` для табов
- Keyboard navigation: Tab для переключения между табами
- Focus indicators

**Тесты:**
- Unit tests: AdminPage.spec.ts (10+ тестов)
- E2E tests: admin-navigation.spec.ts

---

### 2. UserManagementPage.vue

**Назначение:** Управление пользователями системы (CRUD операции)

**Route:** `/admin/users`

**Layout:**
```
┌─────────────────────────────────────────────────┐
│ Toolbar                                         │
│ [+ Add User] [Search] [Filter: All/Active/...] │
├─────────────────────────────────────────────────┤
│ Table:                                          │
│ ┌────┬──────┬──────────┬──────┬────────┬──────┐│
│ │ ☑  │ Avatar│ Name    │ Email│ Role   │ Act.││
│ ├────┼──────┼──────────┼──────┼────────┼──────┤│
│ │ ☑  │ 👤   │ John Doe │ j@.. │ Admin  │ ✅  ││
│ │ ☑  │ 👤   │ Jane S.  │ j@.. │ Editor │ ✅  ││
│ └────┴──────┴──────────┴──────┴────────┴──────┘│
│                                                 │
│ Bulk Actions: [Delete] [Change Role] [Activate] │
│ Pagination: < 1 2 3 >  50 of 234               │
└─────────────────────────────────────────────────┘
```

**Функциональность:**

**1. Таблица пользователей:**
- Колонки:
  - Checkbox (multi-select)
  - Avatar (или initial)
  - Name (first + last)
  - Email
  - Role (dropdown для изменения)
  - Status (Active/Inactive/Pending) с badge
  - Created date
  - Last login
  - Actions (Edit, Delete, More menu)

**2. Toolbar:**
- [+ Add User] button → открывает AddUserModal
- Search input (поиск по name, email)
- Filter dropdown:
  - All users
  - Active only
  - Inactive only
  - Pending verification
  - By role (Admin, Editor, Viewer)

**3. Bulk Actions:**
- Delete selected
- Change role (bulk)
- Activate/Deactivate
- Send invitation email

**4. Add/Edit User Modal:**
- Fields:
  - First Name (required)
  - Last Name (required)
  - Email (required, validation)
  - Role selector (Admin, Editor, Viewer)
  - Status (Active/Inactive/Pending)
  - Permissions checkboxes (если нужно)
  - Send invitation email (checkbox)
- Validation:
  - Email format
  - Unique email
  - Required fields

**5. User Detail View (опционально, можно в модальном):**
- Profile info
- Activity log
- Permissions
- Sessions (active sessions list)
- API keys (если есть)

**API Integration:**
```typescript
// GET /api/v4/admin/users/?page=1&page_size=50&role=editor&status=active&search=john
// Response: PaginatedResponse<User>
//   {
//     count: 234,
//     next: "/api/v4/admin/users/?page=2",
//     previous: null,
//     results: User[]
//   }

// POST /api/v4/admin/users/
// Body: CreateUserRequest
// Response: User

// PUT /api/v4/admin/users/{id}/
// Body: UpdateUserRequest
// Response: User

// DELETE /api/v4/admin/users/{id}/
// Response: 204 No Content

// POST /api/v4/admin/users/bulk/
// Body: { ids: number[], action: 'delete' | 'activate' | 'deactivate' | 'change_role', data?: {} }
// Response: { success: boolean, updated: number, failed: number, errors?: [] }
```

**Архитектурные требования:**
- ✅ Все endpoints требуют permission `admin.user_manage`
- ✅ Все endpoints возвращают структурированные ошибки
- ✅ Bulk operations ограничены 100 пользователями за раз
- ✅ Пагинация обязательна (default: 50, max: 100)
- ✅ Оптимизация: `select_related('groups', 'user_permissions')` на бэкенде

**State Management:**
- `adminStore.ts` (новый store) - см. раздел "Архитектурные решения" для деталей:
  - `users: User[]` - список пользователей текущей страницы
  - `totalUsersCount: number` - общее количество для пагинации
  - `usersFilters: {role, status, search}` - активные фильтры
  - `selectedUsers: number[]` - выбранные пользователи для bulk операций
  - Actions: `fetchUsers()`, `createUser()`, `updateUser()`, `deleteUser()`, `bulkOperation()`
  - **Кеширование:** Список пользователей кешируется на 5 минут
  - **Оптимизация:** Использует `select_related` на бэкенде для избежания N+1 запросов

**Responsive:**
- Desktop: полная таблица
- Tablet: упрощенная таблица (скрыть некоторые колонки)
- Mobile: card view вместо таблицы

**Accessibility:**
- ARIA labels для всех действий
- Keyboard navigation по таблице
- Screen reader announcements для bulk operations

**Тесты:**
- Unit tests: UserManagementPage.spec.ts (25+ тестов)
- E2E tests: user-management.spec.ts

---

### 3. MetadataSchemaPage.vue

**Назначение:** Визуальный редактор схем метаданных для активов

**Route:** `/admin/metadata-schemas`

**Layout:**
```
┌─────────────────────────────────────────────────┐
│ Toolbar: [+ Create Schema] [Search]            │
├──────────┬──────────────┬──────────────────────┤
│ Schema   │  Schema      │  Field Editor        │
│ List     │  Preview      │  (Right Panel)       │
│ (Left)   │  (Center)     │                      │
│          │              │  Field Name: [____]   │
│ • Schema1│  ┌─────────┐ │  Type: [Select ▼]   │
│ • Schema2│  │ Field 1  │ │  Required: ☑         │
│ • Schema3│  │ Field 2  │ │  Default: [____]     │
│          │  │ Field 3  │ │  Options: [____]      │
│          │  └─────────┘ │  [Save Field]         │
│          │              │                       │
│          │  Drag-drop   │                       │
│          │  для порядка │                       │
└──────────┴──────────────┴──────────────────────┘
```

**Функциональность:**

**1. Schema List (Left Panel):**
- Список всех схем
- [+ Create Schema] button
- Search по названию
- Click на схему → загружает в редактор

**2. Schema Editor (Center):**
- Schema name input
- Description textarea
- Applies to: multi-select (Images, Videos, Documents, All)
- Fields list (drag-drop для изменения порядка):
  - Field card с:
    - Field name
    - Field type icon
    - Required badge
    - Drag handle
    - Edit button
    - Delete button
- [+ Add Field] button

**3. Field Editor (Right Panel):**
- Field Name (required)
- Field Type selector:
  - Text (single line)
  - Text Area (multi-line)
  - Number
  - Date
  - Date Range
  - Select (dropdown)
  - Multi-select
  - Checkbox
  - File Upload
  - URL
- Required checkbox
- Default Value input (зависит от типа)
- Options (для Select/Multi-select):
  - Dynamic list: [+ Add Option]
  - Each option: value + label
- Validation Rules:
  - Min/Max length (для Text)
  - Min/Max value (для Number)
  - Date range (для Date)
  - Pattern (regex для Text)
- Help Text (описание поля для пользователей)
- [Save Field] button
- [Cancel] button

**4. Schema Actions:**
- [Save Schema] (сохраняет всю схему)
- [Delete Schema] (с подтверждением)
- [Duplicate Schema] (создает копию)
- [Export Schema] (JSON)
- [Import Schema] (JSON file upload)

**5. Schema Preview:**
- Показывает форму как ее увидят пользователи
- Live preview при редактировании

**Drag & Drop:**
- Использовать `@vueuse/core` или `vuedraggable`
- Визуальная обратная связь при перетаскивании
- Сохранение порядка в схеме

**API Integration:**
```typescript
// GET /api/v4/admin/metadata-schemas/
// POST /api/v4/admin/metadata-schemas/
// PUT /api/v4/admin/metadata-schemas/{id}/
// DELETE /api/v4/admin/metadata-schemas/{id}/
```

**State Management:**
- `metadataSchemaStore.ts` (новый store):
  - `schemas: MetadataSchema[]`
  - `currentSchema: MetadataSchema | null`
  - `currentField: Field | null`
  - Actions: `fetchSchemas()`, `createSchema()`, `updateSchema()`, `deleteSchema()`, `addField()`, `updateField()`, `deleteField()`, `reorderFields()`

**Validation:**
- Schema name: required, unique
- Field name: required, unique в рамках схемы, valid identifier
- Field type: required
- Options: required для Select/Multi-select

**Тесты:**
- Unit tests: MetadataSchemaPage.spec.ts (30+ тестов)
- E2E tests: metadata-schema-editor.spec.ts

---

### 4. WorkflowDesignerPage.vue

**Назначение:** Визуальный редактор workflow (состояния и переходы)

**Route:** `/admin/workflows`

**Layout:**
```
┌─────────────────────────────────────────────────┐
│ Toolbar: [+ Create Workflow] [Zoom: 100%]      │
├─────────────────────────────────────────────────┤
│ Canvas (with zoom/pan):                         │
│                                                  │
│     ┌─────────┐                                 │
│     │  Draft  │                                 │
│     │ (Start) │                                 │
│     └────┬────┘                                 │
│          │                                      │
│          ▼                                      │
│     ┌─────────┐                                 │
│     │  Review │                                 │
│     │  (Mid)  │                                 │
│     └────┬────┘                                 │
│          │                                      │
│          ▼                                      │
│     ┌─────────┐                                 │
│     │Approved │                                 │
│     │  (End)  │                                 │
│     └─────────┘                                 │
│                                                  │
│ Right Panel: Node Properties                    │
│ - Node Name: [____]                             │
│ - Node Type: [State ▼]                          │
│ - Allowed Roles: [☑ Admin] [☑ Reviewer]         │
│ - Actions: [Approve] [Reject] [Comment]          │
│ - Notifications: [☑ Send email]                  │
└─────────────────────────────────────────────────┘
```

**Функциональность:**

**1. Canvas (визуальный редактор):**
- Zoom controls (50%, 75%, 100%, 125%, 150%)
- Pan (drag canvas)
- Grid background (опционально)
- Minimap (опционально, для больших workflow)

**2. Nodes (состояния):**
- Types:
  - Start (начальное состояние, только одно)
  - State (промежуточное состояние)
  - End (конечное состояние, может быть несколько)
- Node properties:
  - Name (required)
  - Description
  - Color (для визуального различия)
  - Icon (опционально)
  - Allowed Roles (кто может находиться в этом состоянии)
  - Actions available (Approve, Reject, Comment, Edit, etc.)
  - Notifications:
    - Send email on entry
    - Send email on exit
    - Email template selector
  - Lock asset (запретить редактирование)
  - Auto-transition (автоматический переход через X дней)

**3. Transitions (стрелки между состояниями):**
- From state → To state
- Conditions:
  - User role (Admin, Reviewer, Editor)
  - User action (Approve, Reject, etc.)
  - Time-based (через X дней)
  - Custom condition (JavaScript expression, опционально)
- Label на стрелке (показывает условие)
- Color (для визуального различия)

**4. Workflow Actions:**
- [+ Create Workflow] → создает новый workflow
- [Save Workflow] → сохраняет текущий workflow
- [Delete Workflow] → удаляет с подтверждением
- [Duplicate Workflow] → создает копию
- [Test Workflow] → запускает тестовый сценарий
- [Export Workflow] → JSON export
- [Import Workflow] → JSON import

**5. Node Editor (Right Panel):**
- Открывается при клике на node
- Все свойства node редактируемы
- [Save Node] button
- [Delete Node] button (с проверкой связей)

**6. Transition Editor:**
- Открывается при клике на стрелку
- From state (read-only)
- To state (read-only)
- Condition selector
- Condition parameters (зависит от типа условия)
- [Save Transition] button
- [Delete Transition] button

**Drag & Drop:**
- Перетаскивание nodes по canvas
- Создание transition: drag от одного node к другому
- Изменение позиции nodes

**Validation:**
- Минимум один Start node
- Минимум один End node
- Все nodes должны быть связаны (нет изолированных)
- Нет циклов (опционально, можно разрешить для некоторых workflow)

**API Integration:**
```typescript
// GET /api/v4/admin/workflows/
// POST /api/v4/admin/workflows/
// PUT /api/v4/admin/workflows/{id}/
// DELETE /api/v4/admin/workflows/{id}/
// POST /api/v4/admin/workflows/{id}/validate/
```

**State Management:**
- `workflowStore.ts` (новый store):
  - `workflows: Workflow[]`
  - `currentWorkflow: Workflow | null`
  - `selectedNode: Node | null`
  - `selectedTransition: Transition | null`
  - `canvasZoom: number`
  - `canvasPan: {x: number, y: number}`
  - Actions: `fetchWorkflows()`, `createWorkflow()`, `updateWorkflow()`, `deleteWorkflow()`, `addNode()`, `updateNode()`, `deleteNode()`, `addTransition()`, `updateTransition()`, `deleteTransition()`, `validateWorkflow()`

**Libraries:**
- Для canvas: `@vue-flow/core` или `vue-d3-network` или custom canvas
- Для drag-drop: `@vueuse/core` или `vuedraggable`

**Тесты:**
- Unit tests: WorkflowDesignerPage.spec.ts (35+ тестов)
- E2E tests: workflow-designer.spec.ts

---

# 📁 COLLECTIONS MANAGEMENT

## Приоритет: 🟡 P1 (Важно для пользователей)

### CollectionsPage.vue

**Назначение:** Управление коллекциями (папками) активов

**Route:** `/dam/collections` или `/dam/collections/:id`

**Layout:**
```
┌─────────────────────────────────────────────────┐
│ Toolbar: [+ New Collection] [Search]            │
├──────────┬──────────────────────────────────────┤
│ Tree     │  Gallery View                        │
│ View     │  (Selected Collection)               │
│ (Left)   │                                      │
│          │  ┌──────┬──────┬──────┬──────┐     │
│ 📁 Root  │  │ Img  │ Img  │ Img  │ Img  │     │
│  ├─ 📁   │  │      │      │      │      │     │
│  │  Coll1│  └──────┴──────┴──────┴──────┘     │
│  ├─ 📁   │                                      │
│  │  Coll2│  Pagination: < 1 2 3 >              │
│  └─ 📁   │                                      │
│     Coll3│  Right Panel (Collection Metadata):  │
│          │  • Name: Collection 1                 │
│          │  • Items: 45                         │
│          │  • Created: 2025-01-15                │
│          │  • Privacy: Private/Shared            │
│          │  • Actions: [Edit] [Share] [Delete]  │
└──────────┴──────────────────────────────────────┘
```

**Функциональность:**

**1. Tree View (Left Panel):**
- Древовидная структура коллекций
- Expand/collapse folders
- Context menu (right-click):
  - New Collection
  - Rename
  - Delete
  - Share
  - Properties
- Drag-drop для перемещения коллекций
- Search в tree (фильтрует видимые коллекции)
- Special collections:
  - "My Uploads" (автоматическая)
  - "Favorites" (автоматическая)
  - "Recent" (автоматическая)
  - "Shared with me" (автоматическая)

**2. Gallery View (Center):**
- Показывает активы выбранной коллекции
- Использует существующий GalleryView компонент
- Фильтры применяются к текущей коллекции
- Bulk operations работают в контексте коллекции

**3. Collection Metadata (Right Panel):**
- Collection name (editable)
- Description (editable)
- Items count
- Total size
- Created date
- Created by
- Privacy settings:
  - Private (только владелец)
  - Shared (с выбранными пользователями)
  - Public (все пользователи)
- Shared with (список пользователей с правами)
- Actions:
  - [Edit] → EditCollectionModal
  - [Share] → ShareCollectionModal
  - [Delete] → DeleteConfirmModal
  - [Export] → ExportCollectionModal

**4. Collection Actions:**
- [+ New Collection] → CreateCollectionModal
- Rename collection (inline или modal)
- Delete collection (с подтверждением и опцией переместить активы)
- Move collection (drag-drop в tree)
- Duplicate collection (с активами или без)

**5. Drag & Drop:**
- Перемещение активов между коллекциями (drag из gallery в tree)
- Перемещение коллекций (drag в tree)
- Визуальная обратная связь (highlight при hover)

**API Integration:**
```typescript
// GET /api/v4/dam/collections/
// Response: Collection[] (все коллекции пользователя с иерархией)

// POST /api/v4/dam/collections/
// Body: { name: string, description?: string, parent_id?: number, privacy: 'private' | 'shared' | 'public' }
// Response: Collection

// GET /api/v4/dam/collections/{id}/
// Response: Collection (с полной информацией, включая shared_with)

// PUT /api/v4/dam/collections/{id}/
// Body: { name?, description?, parent_id?, privacy? }
// Response: Collection

// DELETE /api/v4/dam/collections/{id}/
// Body: { move_assets_to?: number } // Опционально: куда переместить активы
// Response: 204 No Content

// GET /api/v4/dam/collections/{id}/items/?page=1&page_size=50
// Response: PaginatedResponse<Asset> (активы коллекции)

// POST /api/v4/dam/collections/{id}/items/
// Body: { asset_ids: number[] }
// Response: { added: number, skipped: number }

// DELETE /api/v4/dam/collections/{id}/items/{asset_id}/
// Response: 204 No Content
```

**Архитектурные требования:**
- ✅ Все endpoints требуют authentication
- ✅ Проверка прав доступа к коллекции (ACL)
- ✅ Пагинация для `/items/` (default: 50, max: 100)
- ✅ Оптимизация: `prefetch_related('assets')` для загрузки активов коллекции
- ✅ Bulk операции ограничены 500 активами за раз

**State Management:**
- **Рекомендация:** Расширить существующий `assetStore.ts` (не создавать отдельный collectionStore)
- **Причина:** Коллекции тесно связаны с активами, общий store упрощает синхронизацию
- Новые поля в `assetStore.ts`:
  - `collections: Collection[]` - список всех коллекций пользователя
  - `currentCollection: Collection | null` - выбранная коллекция
  - `collectionTree: TreeNode[]` - древовидная структура для TreeView
  - `collectionAssets: Asset[]` - активы текущей коллекции (кешируются отдельно)
- Новые actions:
  - `fetchCollections()` - загружает все коллекции пользователя
  - `createCollection(data)` - создает новую коллекцию
  - `updateCollection(id, data)` - обновляет коллекцию
  - `deleteCollection(id)` - удаляет коллекцию (с опцией перемещения активов)
  - `addAssetsToCollection(collectionId, assetIds)` - добавляет активы в коллекцию
  - `removeAssetFromCollection(collectionId, assetId)` - удаляет актив из коллекции
  - `moveCollection(collectionId, newParentId)` - перемещает коллекцию в дереве
  - `fetchCollectionAssets(collectionId)` - загружает активы коллекции (использует существующий `fetchAssets` с фильтром)
- **Кеширование:** 
  - Список коллекций кешируется на 10 минут
  - Активы коллекции кешируются на 5 минут
  - Tree структура кешируется на 15 минут (редко меняется)

**Components:**
- CollectionTree.vue (tree view с drag-drop)
- CollectionMetadataPanel.vue (right panel)
- CreateCollectionModal.vue (создание новой коллекции)
- EditCollectionModal.vue (редактирование)
- ShareCollectionModal.vue (настройка доступа)

**Responsive:**
- Desktop: 3-колоночный layout
- Tablet: tree скрывается, показывается по кнопке
- Mobile: tree → modal, gallery full-width

**Тесты:**
- Unit tests: CollectionsPage.spec.ts (20+ тестов)
- E2E tests: collections-management.spec.ts

---

# 📊 REPORTS & ANALYTICS

## Приоритет: 🟡 P1 (Важно для аналитики)

### ReportsPage.vue

**Назначение:** Аналитика и отчеты по использованию активов

**Route:** `/admin/reports` или `/reports` (зависит от прав доступа)

**Layout:**
```
┌─────────────────────────────────────────────────┐
│ Toolbar: [Date Range] [Export] [Refresh]        │
├─────────────────────────────────────────────────┤
│ Report Tabs:                                    │
│ [Usage] [Downloads] [Users] [Storage] [Custom]  │
├─────────────────────────────────────────────────┤
│ Selected Report: Usage Analytics                │
│                                                  │
│ ┌─────────────────────────────────────────────┐│
│ │ Chart: Asset Usage Over Time (Line Chart)   ││
│ │ [Last 7 days] [Last 30 days] [Last year]    ││
│ └─────────────────────────────────────────────┘│
│                                                  │
│ ┌──────────────┬──────────────────────────────┐│
│ │ Top Assets   │  User Activity               ││
│ │ 1. asset.jpg │  • User1: 45 views            ││
│ │ 2. asset.png │  • User2: 32 views            ││
│ │ 3. asset.gif │  • User3: 28 views            ││
│ └──────────────┴──────────────────────────────┘│
│                                                  │
│ [Export to CSV] [Export to PDF] [Schedule]      │
└─────────────────────────────────────────────────┘
```

**Функциональность:**

**1. Report Tabs:**
- **Usage Analytics:**
  - Asset views over time (line chart)
  - Top viewed assets (table)
  - Views by user (table)
  - Views by collection (pie chart)
- **Download Analytics:**
  - Downloads over time (line chart)
  - Top downloaded assets (table)
  - Downloads by user (table)
  - Download trends (comparison period over period)
- **User Activity:**
  - Active users over time
  - User engagement metrics
  - User activity heatmap
  - Top contributors (uploaders)
- **Storage Analytics:**
  - Storage usage over time
  - Storage by file type (pie chart)
  - Storage by collection (bar chart)
  - Storage growth projection
- **Custom Reports:**
  - Report builder (drag-drop fields)
  - Custom date ranges
  - Custom filters
  - Save custom reports

**2. Date Range Picker:**
- Quick presets: Today, Last 7 days, Last 30 days, Last 90 days, Last year, Custom
- Custom range: DateRangePicker component
- Comparison mode: Compare with previous period

**3. Charts:**
- Line charts (для временных рядов)
- Bar charts (для сравнений)
- Pie charts (для распределений)
- Heatmaps (для активности)
- Library: `chart.js` или `recharts` или `vue-chartjs`

**4. Export Options:**
- Export to CSV
- Export to PDF (с графиками)
- Schedule report (email delivery)
- Export settings:
  - Date range
  - Format (CSV/PDF)
  - Include charts
  - Include raw data

**5. Drill-down:**
- Click на chart element → детальный отчет
- Click на asset → переход к AssetDetailPage
- Click на user → переход к UserManagementPage (если admin)

**API Integration:**
```typescript
// GET /api/v4/analytics/usage/?start_date=2025-01-01&end_date=2025-01-31
// Response: {
//   summary: { total_views: 1234, unique_assets: 456, ... },
//   chart_data: { labels: [], datasets: [] },
//   top_assets: Asset[],
//   views_by_user: { user_id: number, views: number }[],
//   views_by_collection: { collection_id: number, views: number }[]
// }

// GET /api/v4/analytics/downloads/?start_date=&end_date=
// Response: { summary, chart_data, top_assets, downloads_by_user, trends }

// GET /api/v4/analytics/users/?start_date=&end_date=
// Response: { active_users: number, engagement_metrics, activity_heatmap, top_contributors }

// GET /api/v4/analytics/storage/?start_date=&end_date=
// Response: { total_usage: number, by_file_type: {}, by_collection: {}, growth_projection }

// POST /api/v4/analytics/custom-report/
// Body: { fields: string[], filters: {}, date_range: {} }
// Response: ReportData

// GET /api/v4/analytics/export/?format=csv&report_type=usage&start_date=&end_date=
// Response: Blob (CSV или PDF файл)
```

**Архитектурные требования:**
- ✅ Все endpoints требуют authentication
- ✅ Permission check: `reports.view` или `admin.reports_view`
- ✅ Кеширование на бэкенде: отчеты кешируются на 30 минут (Redis)
- ✅ Rate limiting: максимум 10 запросов в минуту на пользователя
- ✅ Оптимизация: агрегация данных на уровне БД (не в Python)
- ✅ Пагинация для таблиц (top_assets, views_by_user)

**State Management:**
- `reportsStore.ts` (новый store) - см. раздел "Архитектурные решения" для деталей:
  - `currentReport: ReportType` - текущий тип отчета ('usage' | 'downloads' | 'users' | 'storage' | 'custom')
  - `dateRange: {start: Date, end: Date}` - выбранный диапазон дат
  - `reportData: ReportData | null` - загруженные данные отчета
  - `isLoading: boolean` - состояние загрузки
  - `error: string | null` - ошибка загрузки
  - `cachedReports: Map<string, ReportData>` - кеш отчетов по ключу (reportType + dateRange)
- Actions:
  - `fetchReportData(reportType, dateRange)` - загружает данные отчета
  - `setDateRange(dateRange)` - устанавливает диапазон дат
  - `exportReport(format, reportType, dateRange)` - экспортирует отчет (CSV/PDF)
  - `scheduleReport(config)` - настраивает автоматическую отправку отчета
- **Кеширование:**
  - Отчеты кешируются на 15 минут (данные редко меняются)
  - Ключ кеша: `${reportType}_${startDate}_${endDate}`
  - При изменении dateRange кеш инвалидируется
- **Оптимизация:**
  - Debounce для изменения dateRange (500ms)
  - Lazy loading графиков (загружаются только видимые)
  - Виртуальный скроллинг для больших таблиц

**Components:**
- ReportTabs.vue (навигация по типам отчетов)
- UsageChart.vue (line chart компонент)
- TopAssetsTable.vue (таблица топ активов)
- UserActivityTable.vue (таблица активности пользователей)
- StorageChart.vue (pie/bar chart)
- ExportModal.vue (настройки экспорта)

**Responsive:**
- Charts адаптивные (responsive)
- Таблицы с горизонтальным скроллом на мобильных
- Export options в dropdown на мобильных

**Тесты:**
- Unit tests: ReportsPage.spec.ts (25+ тестов)
- E2E tests: reports-analytics.spec.ts

---

# 🔐 AUTH PAGES ENHANCEMENT

## Приоритет: 🟡 P1 (Важно для UX)

### 1. ForgotPasswordPage.vue

**Назначение:** Восстановление пароля (запрос на сброс)

**Route:** `/auth/forgot-password`

**Layout:**
```
┌─────────────────────────────────────────────────┐
│                                                  │
│         ┌──────────────────────────┐            │
│         │   Forgot Password?       │            │
│         │                          │            │
│         │  Enter your email and    │            │
│         │  we'll send you a link   │            │
│         │  to reset your password  │            │
│         │                          │            │
│         │  Email: [____________]    │            │
│         │                          │            │
│         │  [Send Reset Link]       │            │
│         │                          │            │
│         │  [Back to Login]         │            │
│         └──────────────────────────┘            │
│                                                  │
└─────────────────────────────────────────────────┘
```

**Функциональность:**
- Email input (required, validation)
- [Send Reset Link] button
- Success message: "Reset link sent to your email"
- Error handling:
  - Email not found
  - Too many requests (rate limiting)
  - Network error
- [Back to Login] link
- Auto-redirect после успеха (через 3 секунды)

**API Integration:**
```typescript
// POST /api/v4/auth/forgot-password/
// Body: { email: string }
// Response: { 
//   success: boolean, 
//   message: string,
//   // В production: всегда success=true (security: не раскрываем существование email)
// }
```

**Архитектурные требования:**
- ✅ Rate limiting: максимум 3 запроса в час на email
- ✅ Security: не раскрывать существование email в production
- ✅ Email отправляется асинхронно (Celery task)
- ✅ Token валиден 24 часа
- ✅ Token одноразовый (после использования удаляется)

**Validation:**
- Email format validation
- Rate limiting (max 3 requests per hour per email)

**Тесты:**
- Unit tests: ForgotPasswordPage.spec.ts (8+ тестов)
- E2E tests: forgot-password-flow.spec.ts

---

### 2. ResetPasswordPage.vue

**Назначение:** Установка нового пароля (по токену из email)

**Route:** `/auth/reset-password/:token`

**Layout:**
```
┌─────────────────────────────────────────────────┐
│                                                  │
│         ┌──────────────────────────┐            │
│         │   Reset Password         │            │
│         │                          │            │
│         │  New Password:           │            │
│         │  [________________]      │            │
│         │                          │            │
│         │  Confirm Password:        │            │
│         │  [________________]      │            │
│         │                          │            │
│         │  Password strength: ████░ │            │
│         │                          │            │
│         │  [Reset Password]        │            │
│         │                          │            │
│         │  Token expired?          │            │
│         │  [Request new link]      │            │
│         └──────────────────────────┘            │
│                                                  │
└─────────────────────────────────────────────────┘
```

**Функциональность:**
- Token validation (при загрузке страницы)
- New Password input (required, min 8 chars)
- Confirm Password input (required, must match)
- Password strength indicator:
  - Weak (red)
  - Medium (yellow)
  - Strong (green)
- Password requirements checklist:
  - At least 8 characters
  - Contains uppercase letter
  - Contains lowercase letter
  - Contains number
  - Contains special character
- [Reset Password] button
- Success: redirect to login с сообщением
- Error handling:
  - Token expired/invalid
  - Passwords don't match
  - Password too weak
  - Network error
- [Request new link] (если токен истек)

**API Integration:**
```typescript
// POST /api/v4/auth/reset-password/
// Body: { 
//   token: string, 
//   password: string, 
//   password_confirm: string 
// }
// Response: { 
//   success: boolean, 
//   message: string 
// }
```

**Архитектурные требования:**
- ✅ Token validation при загрузке страницы (GET `/api/v4/auth/reset-password/validate/?token=...`)
- ✅ Password validation: минимум 8 символов, сложность (uppercase, lowercase, number, special)
- ✅ Rate limiting: максимум 5 попыток в час на token
- ✅ Token одноразовый (удаляется после успешного сброса)
- ✅ Security: не раскрывать причину ошибки (token expired vs invalid)

**Validation:**
- Token format validation
- Password strength validation
- Password match validation

**Тесты:**
- Unit tests: ResetPasswordPage.spec.ts (10+ тестов)
- E2E tests: reset-password-flow.spec.ts

---

# ⚠️ ERROR PAGES

## Приоритет: 🟡 P1 (Важно для обработки ошибок)

### 1. Error500Page.vue

**Назначение:** Страница для серверных ошибок (500)

**Route:** `/500` или автоматически при 500 ошибке

**Layout:**
```
┌─────────────────────────────────────────────────┐
│                                                  │
│              ┌──────────────────┐               │
│              │   500            │               │
│              │   Server Error   │               │
│              │                  │               │
│              │  Something went  │               │
│              │  wrong on our    │               │
│              │  end.            │               │
│              │                  │               │
│              │  [Retry]         │               │
│              │  [Go Home]       │               │
│              │  [Report Issue] │               │
│              └──────────────────┘               │
│                                                  │
└─────────────────────────────────────────────────┘
```

**Функциональность:**
- Error code display (500)
- User-friendly message
- [Retry] button (повторяет последний запрос)
- [Go Home] button (redirect to /)
- [Report Issue] button (открывает форму обратной связи или email)
- Error ID (для поддержки, если доступен)
- Stack trace (только в development mode)

**Error Boundary Integration:**
- Автоматический redirect при 500 ошибке из API interceptor
- Логирование ошибки в Sentry (если настроено)
- Сохранение контекста ошибки (URL, user, timestamp) для отладки
- Error ID для связи с логами на сервере

**Архитектурные требования:**
- ✅ Error page не требует authentication (может быть показана до логина)
- ✅ Retry button повторяет последний запрос (если возможно)
- ✅ Stack trace показывается только в development mode
- ✅ Error ID генерируется на бэкенде и передается в response

**Тесты:**
- Unit tests: Error500Page.spec.ts (5+ тестов)

---

### 2. UnauthorizedPage.vue

**Назначение:** Страница для ошибок аутентификации (401)

**Route:** `/401` или автоматически при 401 ошибке

**Layout:**
```
┌─────────────────────────────────────────────────┐
│                                                  │
│         ┌──────────────────────────┐            │
│         │   401                    │            │
│         │   Unauthorized           │            │
│         │                          │            │
│         │  Your session has        │            │
│         │  expired. Please log in   │            │
│         │  again.                   │            │
│         │                          │            │
│         │  [Go to Login]           │            │
│         │  [Go Home]               │            │
│         └──────────────────────────┘            │
│                                                  │
└─────────────────────────────────────────────────┘
```

**Функциональность:**
- Error code display (401)
- User-friendly message
- [Go to Login] button (redirect to /login с returnTo)
- [Go Home] button (redirect to /)
- Auto-redirect to login (через 5 секунд, опционально)

**Integration:**
- Автоматический redirect при 401 из API interceptor (`apiService.ts`)
- Сохранение returnTo URL в query параметрах
- Очистка токена и logout из authStore
- Auto-redirect через 5 секунд (опционально, можно отключить)

**Архитектурные требования:**
- ✅ Страница не требует authentication (показывается до логина)
- ✅ Сохранение контекста: куда пользователь пытался попасть
- ✅ После успешного логина автоматический redirect на returnTo

**Тесты:**
- Unit tests: UnauthorizedPage.spec.ts (5+ тестов)

---

### 3. ForbiddenPage.vue

**Назначение:** Страница для ошибок доступа (403)

**Route:** `/403` или автоматически при 403 ошибке

**Layout:**
```
┌─────────────────────────────────────────────────┐
│                                                  │
│         ┌──────────────────────────┐            │
│         │   403                    │            │
│         │   Access Forbidden        │            │
│         │                          │            │
│         │  You don't have          │            │
│         │  permission to access   │            │
│         │  this resource.          │            │
│         │                          │            │
│         │  [Request Access]        │            │
│         │  [Go Home]               │            │
│         │  [Contact Admin]        │            │
│         └──────────────────────────┘            │
│                                                  │
└─────────────────────────────────────────────────┘
```

**Функциональность:**
- Error code display (403)
- User-friendly message
- Resource information (что пытались открыть, опционально)
- [Request Access] button (открывает форму запроса доступа)
- [Go Home] button (redirect to /)
- [Contact Admin] button (открывает email или форму обратной связи)

**Integration:**
- Автоматический redirect при 403 из API interceptor
- Логирование попытки доступа (для аудита) - отправка на бэкенд
- Отображение информации о требуемом permission (если доступно)

**Архитектурные требования:**
- ✅ Страница требует authentication (показывается только авторизованным)
- ✅ Логирование на бэкенде: кто, когда, к чему пытался получить доступ
- ✅ Request Access отправляет запрос администратору (email или notification)
- ✅ Contact Admin открывает форму обратной связи или email клиент

**Тесты:**
- Unit tests: ForbiddenPage.spec.ts (5+ тестов)

---

# 📤 DISTRIBUTION SUB-PAGES

## Приоритет: 🟡 P1 (Важно для полного функционала Distribution)

### 1. PublicationDetailPage.vue

**Назначение:** Детальный просмотр публикации

**Route:** `/distribution/publications/:id`

**Layout:**
```
┌─────────────────────────────────────────────────┐
│ Header: [← Back] [Edit] [Delete] [Share]        │
├─────────────────────────────────────────────────┤
│ Publication Info:                               │
│ • Title: Spring 2025 Campaign                   │
│ • Status: 🟢 Active                              │
│ • Schedule: Dec 1 - Dec 31                      │
│ • Channels: [Slack] [Email] [Public Link]       │
├─────────────────────────────────────────────────┤
│ Assets (20 items):                              │
│ ┌──────┬──────┬──────┬──────┐                 │
│ │ Img  │ Img  │ Img  │ Img  │                 │
│ └──────┴──────┴──────┴──────┘                 │
│                                                  │
│ [View All Assets]                               │
├─────────────────────────────────────────────────┤
│ Analytics:                                      │
│ • Views: 45                                     │
│ • Downloads: 120                                │
│ • Shares: 8                                     │
│ • Engagement: 85%                                │
│                                                  │
│ [View Full Analytics]                          │
├─────────────────────────────────────────────────┤
│ Share Links:                                    │
│ • https://dam.local/p/spring-2025-abc123        │
│   [Copy] [Revoke]                              │
│                                                  │
│ [+ Generate New Link]                           │
└─────────────────────────────────────────────────┘
```

**Функциональность:**
- Publication details display
- Assets grid (использует GalleryView)
- Analytics summary
- Share links management
- Actions: Edit, Delete, Share, Preview
- Status badge с цветовой индикацией
- Schedule information
- Channels display

**API Integration:**
```typescript
// GET /api/v4/distribution/publications/{id}/
// Response: Publication (с полной информацией, включая assets, analytics, share_links)

// PUT /api/v4/distribution/publications/{id}/
// Body: UpdatePublicationRequest
// Response: Publication

// DELETE /api/v4/distribution/publications/{id}/
// Response: 204 No Content

// GET /api/v4/distribution/publications/{id}/analytics/
// Response: PublicationAnalytics (расширенная аналитика)

// GET /api/v4/distribution/publications/{id}/links/
// Response: ShareLink[] (все публичные ссылки публикации)

// POST /api/v4/distribution/publications/{id}/links/
// Body: { expires_at?: string, password?: string, permissions: {} }
// Response: ShareLink

// DELETE /api/v4/distribution/publications/{id}/links/{link_id}/
// Response: 204 No Content
```

**Архитектурные требования:**
- ✅ Permission check: пользователь должен быть владельцем публикации или иметь право `distribution.publication_view`
- ✅ Оптимизация: `prefetch_related('assets', 'channels', 'share_links')` на бэкенде
- ✅ Кеширование: детали публикации кешируются на 5 минут
- ✅ Real-time updates: WebSocket для обновления analytics в реальном времени (опционально)

**Тесты:**
- Unit tests: PublicationDetailPage.spec.ts (15+ тестов)
- E2E tests: publication-detail.spec.ts

---

### 2. PublicationPublicPage.vue

**Назначение:** Публичный доступ к публикации (без авторизации)

**Route:** `/distribution/public/:token`

**Layout:**
```
┌─────────────────────────────────────────────────┐
│ Public Header (minimal): [Logo]                 │
├─────────────────────────────────────────────────┤
│ Publication:                                    │
│ • Title: Spring 2025 Campaign                   │
│ • Description: Assets for spring marketing       │
├─────────────────────────────────────────────────┤
│ Assets Gallery:                                 │
│ ┌──────┬──────┬──────┬──────┐                 │
│ │ Img  │ Img  │ Img  │ Img  │                 │
│ └──────┴──────┴──────┴──────┘                 │
│                                                  │
│ Click asset → Preview Modal                     │
│                                                  │
│ [Download] (if permitted)                        │
└─────────────────────────────────────────────────┘
```

**Функциональность:**
- No authentication required
- Public token validation
- Assets gallery (read-only)
- Asset preview (lightbox modal)
- Download (если разрешено в настройках публикации)
- Password protection (если установлен пароль)
- Expiration check (показывает сообщение если истек срок)
- Analytics tracking (views, downloads)

**API Integration:**
```typescript
// GET /api/v4/distribution/public/{token}/
// GET /api/v4/distribution/public/{token}/assets/
// POST /api/v4/distribution/public/{token}/download/{asset_id}/
```

**Security:**
- Token validation при загрузке страницы
- Rate limiting (защита от брутфорса): максимум 100 запросов в час на IP
- CORS настройки: разрешены запросы с любых доменов (публичный доступ)
- Password protection: если установлен пароль, показывается форма ввода
- Expiration check: проверка срока действия публикации
- Analytics tracking: логирование views и downloads (без персональных данных)

**Архитектурные требования:**
- ✅ Страница НЕ требует authentication (публичный доступ)
- ✅ Минимальный layout (без Header/Sidebar для неавторизованных)
- ✅ Token в URL: одноразовый, валидный ограниченное время
- ✅ Download tracking: каждый download логируется для аналитики
- ✅ Оптимизация: кеширование публичных данных на CDN (если используется)

**Тесты:**
- Unit tests: PublicationPublicPage.spec.ts (12+ тестов)
- E2E tests: publication-public-access.spec.ts

---

# 🪟 ДОПОЛНИТЕЛЬНЫЕ МОДАЛЬНЫЕ ОКНА

## Приоритет: 🟡 P1-P2

### 1. UploadModal.vue

**Назначение:** Загрузка файлов в систему

**Статус:** ⚠️ Упомянуто в ТЗ, но не реализовано

**Функциональность:**
- Drag-drop zone
- Click to select files
- File list с progress bars
- Cancel upload per file
- Metadata form (опционально, перед загрузкой)
- Collection selector (куда загружать)
- Validation:
  - File size limits
  - File type restrictions
  - Total upload size limit

**Components:**
- FileUploader.vue (drag-drop компонент)
- UploadProgress.vue (progress bar)
- MetadataForm.vue (опциональная форма)

**API Integration:**
```typescript
// POST /api/v4/dam/assets/upload/
// Content-Type: multipart/form-data
// Body: FormData {
//   file: File,
//   collection_id?: number,
//   metadata?: JSON string
// }
// Response: { 
//   asset: Asset,
//   upload_id: string,
//   status: 'completed' | 'processing'
// }

// Для больших файлов (>50MB) используется chunked upload:
// POST /api/v4/dam/assets/upload/chunk/
// Body: { upload_id: string, chunk: Blob, chunk_number: number, total_chunks: number }
// Response: { upload_id, uploaded_chunks: number, status: 'uploading' | 'completed' }
```

**Архитектурные требования:**
- ✅ File size limits: проверка на фронтенде и бэкенде
- ✅ File type validation: только разрешенные MIME types
- ✅ Progress tracking: через XMLHttpRequest.upload.onprogress
- ✅ Chunked upload для файлов >50MB
- ✅ Retry logic: автоматический retry при сетевых ошибках
- ✅ Concurrent uploads: максимум 5 файлов одновременно
- ✅ Metadata form: опционально перед загрузкой (можно пропустить)

**Тесты:**
- Unit tests: UploadModal.spec.ts (15+ тестов)
- E2E tests: upload-flow.spec.ts

---

### 2. ShareModal.vue

**Назначение:** Генерация публичных ссылок для активов

**Статус:** ⚠️ Упомянуто в ТЗ, но не реализовано

**Функциональность:**
- [Generate Link] button
- Link display с [Copy] button
- Permissions selector:
  - View
  - Download
  - Comment
  - Edit (опционально)
- Expiration date picker
- Password protection (опционально)
- Share with users (email input, multi-select)
- Share links list (управление существующими ссылками)
- [Revoke Link] button

**API Integration:**
```typescript
// POST /api/v4/dam/assets/{id}/share/
// Body: {
//   permissions: { view: boolean, download: boolean, comment?: boolean, edit?: boolean },
//   expires_at?: string,
//   password?: string,
//   share_with_users?: number[] // Email list для прямого шаринга
// }
// Response: ShareLink

// GET /api/v4/dam/assets/{id}/share-links/
// Response: ShareLink[] (все существующие ссылки)

// DELETE /api/v4/dam/assets/{id}/share-links/{link_id}/
// Response: 204 No Content

// PUT /api/v4/dam/assets/{id}/share-links/{link_id}/
// Body: { expires_at?, password?, permissions? }
// Response: ShareLink
```

**Архитектурные требования:**
- ✅ Permission check: пользователь должен иметь право `assets.share` или быть владельцем
- ✅ Link generation: уникальный токен генерируется на бэкенде
- ✅ Expiration: автоматическая инвалидация истекших ссылок
- ✅ Password protection: хеширование пароля на бэкенде
- ✅ Rate limiting: максимум 50 ссылок на актив

**Тесты:**
- Unit tests: ShareModal.spec.ts (12+ тестов)

---

### 3. AssetPreviewModal.vue (Lightbox)

**Назначение:** Быстрый просмотр актива в полноэкранном режиме

**Статус:** ⚠️ Упомянуто в ТЗ, но не реализовано

**Функциональность:**
- Full-screen preview
- Large image/video display
- Zoom controls (in/out, reset)
- Navigation arrows (prev/next asset)
- Keyboard navigation:
  - Arrow keys (prev/next)
  - ESC (close)
  - +/- (zoom)
- Download button
- Share button
- Metadata quick view (опционально, toggle)
- Close button (X)

**Components:**
- ImageViewer.vue (для изображений)
- VideoPlayer.vue (для видео)
- ZoomControls.vue
- NavigationArrows.vue

**Тесты:**
- Unit tests: AssetPreviewModal.spec.ts (10+ тестов)
- E2E tests: asset-preview.spec.ts

---

### 4. EditMetadataModal.vue

**Назначение:** Редактирование метаданных актива

**Статус:** ⚠️ Упомянуто в ТЗ, но не реализовано

**Функциональность:**
- Dynamic form на основе MetadataSchema
- Все типы полей из схемы
- Validation по правилам схемы
- Save/Cancel buttons
- AI suggestions (опционально, для тегов)
- Tag autocomplete

**API Integration:**
```typescript
// GET /api/v4/dam/assets/{id}/metadata-schema/
// Response: MetadataSchema (схема метаданных для данного типа актива)

// GET /api/v4/dam/assets/{id}/metadata/
// Response: { [field_name: string]: unknown } (текущие значения метаданных)

// PUT /api/v4/dam/assets/{id}/metadata/
// Body: { [field_name: string]: unknown } (новые значения)
// Response: { success: boolean, updated_fields: string[] }
```

**Архитектурные требования:**
- ✅ Permission check: пользователь должен иметь право `assets.edit`
- ✅ Validation: все поля валидируются по правилам схемы на бэкенде
- ✅ AI suggestions: опционально, через отдельный endpoint `/api/v4/dam/assets/{id}/ai-suggestions/`
- ✅ Tag autocomplete: через `/api/v4/dam/tags/autocomplete/?q=...`
- ✅ Optimistic updates: обновление UI до подтверждения от сервера (с rollback при ошибке)

**Тесты:**
- Unit tests: EditMetadataModal.spec.ts (15+ тестов)

---

### 5. ChangePasswordModal.vue

**Назначение:** Смена пароля пользователя

**Статус:** ⚠️ Упомянуто в SettingsPage (TODO)

**Функциональность:**
- Current password input
- New password input
- Confirm password input
- Password strength indicator
- Password requirements checklist
- [Change Password] button
- Success/error messages

**API Integration:**
```typescript
// POST /api/v4/auth/change-password/
// Body: { 
//   current_password: string,
//   new_password: string,
//   new_password_confirm: string
// }
// Response: { success: boolean, message: string }
```

**Архитектурные требования:**
- ✅ Permission check: пользователь может менять только свой пароль (или админ для любого)
- ✅ Password validation: те же правила, что и для reset password
- ✅ Rate limiting: максимум 5 попыток в час
- ✅ Security: после смены пароля все другие сессии инвалидируются (опционально)
- ✅ Success: автоматический logout и redirect на login (для безопасности)

**Тесты:**
- Unit tests: ChangePasswordModal.spec.ts (8+ тестов)

---

# 🔧 УЛУЧШЕНИЯ СУЩЕСТВУЮЩИХ КОМПОНЕНТОВ

## Приоритет: 🟡 P1-P2

### 1. SettingsPage.vue - Доработка Security секции

**Текущее состояние:** Кнопки есть, но функциональность TODO

**Требуется:**
- Реализовать ChangePasswordModal (см. выше)
- Реализовать APIKeysPage или APIKeysModal:
  - Список API ключей пользователя
  - [Generate New Key] button → открывает GenerateAPIKeyModal
  - [Revoke Key] button → подтверждение и удаление
  - Key display (masked: `sk-...****`, с [Show] toggle для полного ключа)
  - Created date, Last used date
  - Permissions/scopes (если поддерживается)
  - Key name/label (для идентификации)

**API Integration:**
```typescript
// GET /api/v4/auth/api-keys/
// Response: APIKey[] (все ключи текущего пользователя)

// POST /api/v4/auth/api-keys/
// Body: { name?: string, scopes?: string[] }
// Response: { key: string, id: number, created_date: string }
// ⚠️ ВАЖНО: Полный ключ показывается только один раз при создании!

// DELETE /api/v4/auth/api-keys/{id}/
// Response: 204 No Content
```

**Архитектурные требования:**
- ✅ Permission check: пользователь может управлять только своими ключами
- ✅ Security: полный ключ показывается только при создании (не хранится на фронтенде)
- ✅ Key masking: отображение только последних 4 символов (`sk-...abcd`)
- ✅ Scopes: ограничение прав доступа для каждого ключа (если поддерживается)

---

### 2. LoginPage.vue - Улучшения

**Текущее состояние:** Базовая реализация

**Требуется добавить:**
- [Forgot Password?] link → ForgotPasswordPage
- "Remember me" checkbox
- OAuth/SSO buttons (если настроено)
- Error messages display (улучшить UX)
- Loading state (уже есть)
- 2FA support (если пользователь включил 2FA)

---

### 3. Sidebar.vue - Collections Links

**Текущее состояние:** Ссылки есть, но роуты не работают

**Требуется:**
- **Архитектурное решение:** Реализовать через фильтры в DAMPage (не отдельные роуты)
- **Причина:** Эти "коллекции" - виртуальные фильтры, а не реальные коллекции в БД
- **Реализация:**
  ```typescript
  // В DAMPage.vue или через router query params
  router.push({
    name: 'dam',
    query: { filter: 'my-uploads' } // или 'favorites', 'recent', 'shared'
  })
  
  // В assetStore.ts
  function applySpecialFilter(filter: 'my-uploads' | 'favorites' | 'recent' | 'shared') {
    switch (filter) {
      case 'my-uploads':
        filters.value.uploaded_by = authStore.user?.id
        break
      case 'favorites':
        filters.value.is_favorite = true
        break
      case 'recent':
        filters.value.date_range = [getRecentDateRange(), new Date()]
        break
      case 'shared':
        filters.value.shared_with_me = true
        break
    }
    fetchAssets()
  }
  ```
- **Альтернатива:** Если нужны отдельные роуты для лучшего UX:
  - `/dam/my-uploads` → DAMPage с фильтром `uploaded_by=current_user`
  - `/dam/favorites` → DAMPage с фильтром `is_favorite=true`
  - `/dam/recent` → DAMPage с фильтром `date_range=last_30_days`
  - `/dam/shared` → DAMPage с фильтром `shared_with_me=true`

---

### 4. DashboardPage.vue - Расширение

**Текущее состояние:** Базовая реализация есть

**Требуется добавить (опционально):**
- Quick actions widget
- Recent searches
- Saved searches
- Activity timeline (расширенный)

---

# 📅 ПРИОРИТИЗАЦИЯ И ПЛАН РЕАЛИЗАЦИИ

## Phase 4: Critical Enhancements (Weeks 11-12)

### Week 11: Admin Module + Error Pages

**День 1-2: AdminPage + UserManagementPage**
- [ ] Создать AdminPage.vue (роутер outlet)
- [ ] Создать AdminNavigationTabs.vue
- [ ] Создать UserManagementPage.vue
- [ ] Создать adminStore.ts
- [ ] Создать userService.ts
- [ ] Добавить роуты в router
- [ ] Unit tests (25+ тестов)
- [ ] E2E tests

**День 3-4: MetadataSchemaPage**
- [ ] Создать MetadataSchemaPage.vue
- [ ] Создать FieldEditor компонент
- [ ] Реализовать drag-drop для полей
- [ ] Создать metadataSchemaStore.ts
- [ ] Unit tests (30+ тестов)
- [ ] E2E tests

**День 5: WorkflowDesignerPage (начало)**
- [ ] Создать WorkflowDesignerPage.vue
- [ ] Выбрать библиотеку для canvas (vue-flow или custom)
- [ ] Реализовать базовый canvas с nodes
- [ ] Создать workflowStore.ts

**День 6-7: Error Pages + Auth Pages**
- [ ] Создать Error500Page.vue
- [ ] Создать UnauthorizedPage.vue
- [ ] Создать ForbiddenPage.vue
- [ ] Интегрировать в error boundary
- [ ] Создать ForgotPasswordPage.vue
- [ ] Создать ResetPasswordPage.vue
- [ ] Добавить роуты
- [ ] Unit tests (20+ тестов)

---

### Week 12: User Pages + Distribution + Modals

**День 1-2: CollectionsPage**
- [ ] Создать CollectionsPage.vue
- [ ] Создать CollectionTree.vue
- [ ] Создать CollectionMetadataPanel.vue
- [ ] Реализовать drag-drop
- [ ] Создать CreateCollectionModal.vue
- [ ] Расширить assetStore для коллекций
- [ ] Unit tests (20+ тестов)
- [ ] E2E tests

**День 3: ReportsPage**
- [ ] Создать ReportsPage.vue
- [ ] Выбрать chart library (chart.js или recharts)
- [ ] Создать chart components
- [ ] Создать reportsStore.ts
- [ ] Реализовать export (CSV/PDF)
- [ ] Unit tests (25+ тестов)

**День 4: Distribution Sub-pages**
- [ ] Создать PublicationDetailPage.vue
- [ ] Создать PublicationPublicPage.vue
- [ ] Добавить роуты
- [ ] Unit tests (27+ тестов)
- [ ] E2E tests

**День 5-6: Модальные окна**
- [ ] Создать UploadModal.vue
- [ ] Создать ShareModal.vue
- [ ] Создать AssetPreviewModal.vue
- [ ] Создать EditMetadataModal.vue
- [ ] Создать ChangePasswordModal.vue
- [ ] Интегрировать в существующие страницы
- [ ] Unit tests (60+ тестов)

**День 7: WorkflowDesignerPage (завершение)**
- [ ] Завершить WorkflowDesignerPage
- [ ] Реализовать transitions
- [ ] Реализовать validation
- [ ] Unit tests (35+ тестов)
- [ ] E2E tests

---

## Phase 5: Polish & Launch (Post-Week 12)

### Опциональные доработки:

1. **AdminIntegrationsPage.vue** (P2)
   - Управление интеграциями
   - API keys для внешних сервисов
   - Webhook configuration

2. **VerifyEmailPage.vue** (P2)
   - Верификация email после регистрации

3. **2FASetupPage.vue** (P2)
   - Настройка двухфакторной аутентификации

4. **Settings Sub-pages** (P2)
   - Если решено разделить SettingsPage на подстраницы

---

# ✅ КРИТЕРИИ ГОТОВНОСТИ

## Definition of Done для каждой страницы

### Admin Pages:

```yaml
AdminPage:
  ☐ Роутер outlet работает
  ☐ Табы переключаются
  ☐ Permission gating работает
  ☐ Responsive design
  ☐ 10+ unit tests
  ☐ E2E tests

UserManagementPage:
  ☐ Таблица отображает пользователей
  ☐ CRUD операции работают
  ☐ Bulk operations работают
  ☐ Search и фильтры работают
  ☐ Pagination работает
  ☐ 25+ unit tests
  ☐ E2E tests

MetadataSchemaPage:
  ☐ Список схем отображается
  ☐ Редактор схем работает
  ☐ Drag-drop полей работает
  ☐ Field editor работает
  ☐ Preview работает
  ☐ 30+ unit tests
  ☐ E2E tests

WorkflowDesignerPage:
  ☐ Canvas отображается
  ☐ Nodes создаются/редактируются
  ☐ Transitions создаются
  ☐ Drag-drop nodes работает
  ☐ Validation работает
  ☐ 35+ unit tests
  ☐ E2E tests
```

### User Pages:

```yaml
CollectionsPage:
  ☐ Tree view отображается
  ☐ Gallery отображает активы коллекции
  ☐ CRUD операции работают
  ☐ Drag-drop работает
  ☐ 20+ unit tests
  ☐ E2E tests

ReportsPage:
  ☐ Все типы отчетов работают
  ☐ Charts отображаются
  ☐ Date range picker работает
  ☐ Export работает
  ☐ 25+ unit tests
  ☐ E2E tests
```

### Auth Pages:

```yaml
ForgotPasswordPage:
  ☐ Email validation работает
  ☐ API integration работает
  ☐ Success/error messages отображаются
  ☐ 8+ unit tests
  ☐ E2E tests

ResetPasswordPage:
  ☐ Token validation работает
  ☐ Password strength indicator работает
  ☐ Password match validation работает
  ☐ 10+ unit tests
  ☐ E2E tests
```

### Error Pages:

```yaml
Error500Page:
  ☐ Отображается при 500 ошибке
  ☐ Retry button работает
  ☐ 5+ unit tests

UnauthorizedPage:
  ☐ Отображается при 401 ошибке
  ☐ Redirect to login работает
  ☐ 5+ unit tests

ForbiddenPage:
  ☐ Отображается при 403 ошибке
  ☐ Request access работает
  ☐ 5+ unit tests
```

### Distribution Sub-pages:

```yaml
PublicationDetailPage:
  ☐ Детали публикации отображаются
  ☐ Assets grid работает
  ☐ Analytics отображаются
  ☐ Share links управляются
  ☐ 15+ unit tests
  ☐ E2E tests

PublicationPublicPage:
  ☐ Публичный доступ работает
  ☐ Token validation работает
  ☐ Password protection работает
  ☐ Download работает (если разрешено)
  ☐ 12+ unit tests
  ☐ E2E tests
```

### Модальные окна:

```yaml
UploadModal:
  ☐ Drag-drop работает
  ☐ File selection работает
  ☐ Progress tracking работает
  ☐ Validation работает
  ☐ 15+ unit tests
  ☐ E2E tests

ShareModal:
  ☐ Link generation работает
  ☐ Permissions настраиваются
  ☐ Expiration date работает
  ☐ 12+ unit tests

AssetPreviewModal:
  ☐ Full-screen preview работает
  ☐ Zoom работает
  ☐ Navigation работает
  ☐ Keyboard shortcuts работают
  ☐ 10+ unit tests

EditMetadataModal:
  ☐ Dynamic form работает
  ☐ Validation работает
  ☐ Save работает
  ☐ 15+ unit tests

ChangePasswordModal:
  ☐ Password strength работает
  ☐ Validation работает
  ☐ API integration работает
  ☐ 8+ unit tests
```

---

# 📊 МЕТРИКИ УСПЕХА

## После реализации всех доработок:

| Метрика | Текущее | Целевое |
|---------|---------|---------|
| **Покрытие функциональности** | 70% | 100% |
| **Admin функциональность** | 0% | 100% |
| **Error handling** | 33% | 100% |
| **Auth flows** | 50% | 100% |
| **Distribution функциональность** | 80% | 100% |
| **Модальные окна** | 60% | 100% |
| **Total pages** | 9 | 18+ |
| **Test coverage** | ~87% | 90%+ |

---

# 🎯 ЗАКЛЮЧЕНИЕ

## Итоговый список доработок

**Критично (P0):**
- ✅ AdminPage.vue
- ✅ UserManagementPage.vue
- ✅ MetadataSchemaPage.vue
- ✅ WorkflowDesignerPage.vue

**Важно (P1):**
- ✅ CollectionsPage.vue
- ✅ ReportsPage.vue
- ✅ ForgotPasswordPage.vue
- ✅ ResetPasswordPage.vue
- ✅ Error500Page.vue
- ✅ UnauthorizedPage.vue
- ✅ ForbiddenPage.vue
- ✅ PublicationDetailPage.vue
- ✅ PublicationPublicPage.vue
- ✅ UploadModal.vue
- ✅ ShareModal.vue
- ✅ AssetPreviewModal.vue
- ✅ EditMetadataModal.vue
- ✅ ChangePasswordModal.vue

**Опционально (P2):**
- ⚠️ AdminIntegrationsPage.vue
- ⚠️ VerifyEmailPage.vue
- ⚠️ 2FASetupPage.vue

**Итого:** 18 обязательных доработок + 3 опциональных

---

---

# 📐 АРХИТЕКТУРНОЕ РЕЗЮМЕ

## Ключевые архитектурные решения

### 1. State Management Strategy

**Принцип:** Модульные stores с четким разделением ответственности

- **adminStore.ts** - управление административными данными (users, schemas, workflows)
- **reportsStore.ts** - управление отчетами и аналитикой
- **assetStore.ts** (расширенный) - управление активами и коллекциями
- **authStore.ts** (существующий) - аутентификация и права доступа
- **uiStore.ts** (существующий) - UI состояние (модальные окна, темы, уведомления)

**Правило:** Каждый store отвечает за свою доменную область, минимум пересечений.

### 2. API Services Architecture

**Принцип:** Один service на доменную область, переиспользование apiService

- **adminService.ts** - все admin endpoints
- **reportsService.ts** - все analytics endpoints
- **collectionService.ts** - все collection endpoints (или расширение assetService)
- **authService.ts** (существующий) - все auth endpoints

**Правило:** Все services используют существующий `apiService` для единообразной обработки ошибок, retry, кеширования.

### 3. Component Reusability

**Принцип:** Максимальное переиспользование существующих компонентов

**Переиспользуемые компоненты:**
- Layout: Header, Sidebar, MainContent
- Common: Button, Input, Modal, Card, Badge, Pagination, Select, DateRangePicker
- DAM: GalleryView, FiltersPanel, SearchBar, BulkActions

**Новые переиспользуемые компоненты:**
- DataTable.vue - универсальная таблица
- TreeView.vue - древовидный компонент
- ChartContainer.vue - обертка для графиков
- AdminNavigationTabs.vue - табы для admin страниц

### 4. Routing & Navigation

**Принцип:** Nested routes для логической группировки, permission-based guards

- Admin routes: `/admin/*` (nested)
- Collections routes: `/dam/collections/*`
- Error routes: `/401`, `/403`, `/500`
- Auth routes: `/auth/*`

**Permission guards:** Все защищенные роуты проверяют права через `router.beforeEach`.

### 5. Performance Optimization

**Стратегия:**
- ✅ Lazy loading всех новых страниц
- ✅ Code splitting для тяжелых компонентов (WorkflowDesignerPage)
- ✅ Кеширование данных (5-30 минут в зависимости от типа)
- ✅ Virtual scrolling для больших списков (1000+ элементов)
- ✅ Debouncing для поиска и фильтров (300-500ms)
- ✅ Оптимизация изображений (lazy loading, WebP)

### 6. Security Architecture

**Принципы:**
- ✅ Permission checks на уровне роутов и компонентов
- ✅ Rate limiting для всех публичных endpoints
- ✅ Token validation для всех auth операций
- ✅ Input validation на фронтенде и бэкенде
- ✅ Secure error handling (не раскрывать sensitive информацию)
- ✅ Audit logging для всех admin операций

### 7. Error Handling

**Стратегия:**
- ✅ Централизованная обработка через apiService interceptors
- ✅ Автоматический redirect на error pages (401 → UnauthorizedPage, 403 → ForbiddenPage, 500 → Error500Page)
- ✅ Структурированные error responses
- ✅ Логирование в Sentry (если настроено)
- ✅ User-friendly error messages

### 8. Testing Strategy

**Покрытие:**
- Unit tests: 85%+ для компонентов, 90%+ для stores, 95%+ для services
- E2E tests: все основные user flows
- Storybook: все новые компоненты

**Структура:**
```
tests/
├── unit/
│   ├── components/
│   │   ├── admin/
│   │   ├── collections/
│   │   └── reports/
│   ├── stores/
│   └── services/
└── e2e/
    ├── admin/
    ├── collections/
    └── reports/
```

### 9. Accessibility

**Требования:**
- ✅ WCAG 2.1 AA compliance
- ✅ Keyboard navigation для всех интерактивных элементов
- ✅ ARIA labels для screen readers
- ✅ Color contrast 4.5:1 минимум
- ✅ Focus indicators
- ✅ Zoom support до 200%

### 10. Documentation

**Требования:**
- ✅ Storybook stories для всех новых компонентов
- ✅ JSDoc комментарии для всех public функций
- ✅ README для новых модулей
- ✅ API documentation (OpenAPI/Swagger)

---

## 🔄 Интеграционные точки

### С существующими компонентами

1. **Sidebar** - расширение для Admin навигации
2. **Header** - глобальный поиск работает на всех страницах
3. **GalleryView** - переиспользование в CollectionsPage, PublicationDetailPage
4. **FiltersPanel** - переиспользование в ReportsPage (для фильтрации)
5. **Notification System** - все новые страницы используют существующую систему

### С существующими stores

1. **authStore** - проверка прав доступа во всех новых страницах
2. **uiStore** - управление модальными окнами, уведомлениями, темой
3. **assetStore** - расширение для коллекций (не создавать отдельный store)

### С существующими services

1. **apiService** - все новые services используют существующий apiService
2. **cacheService** - кеширование данных новых страниц

---

## 📊 Метрики производительности

### Целевые показатели для новых страниц

| Страница | Initial Load | TTI | Lighthouse | Bundle Size |
|----------|--------------|-----|------------|-------------|
| AdminPage | < 1.5s | < 2.5s | 90+ | < 200KB |
| UserManagementPage | < 2s | < 3s | 88+ | < 150KB |
| MetadataSchemaPage | < 1.8s | < 2.8s | 90+ | < 180KB |
| WorkflowDesignerPage | < 2.5s | < 4s | 85+ | < 300KB (canvas) |
| CollectionsPage | < 1.5s | < 2.5s | 90+ | < 200KB |
| ReportsPage | < 2s | < 3s | 88+ | < 250KB (charts) |

### Оптимизации

- **Code splitting:** Каждая страница загружается отдельным chunk
- **Tree shaking:** Удаление неиспользуемого кода
- **Image optimization:** Lazy loading, WebP с fallback
- **Caching:** Агрессивное кеширование статических данных

---

## 🛡️ Security Checklist

### Для всех новых страниц

- [ ] Permission checks на уровне роута
- [ ] Permission checks на уровне компонента (условный рендеринг)
- [ ] Input validation на фронтенде
- [ ] Rate limiting на бэкенде
- [ ] Audit logging для всех admin операций
- [ ] Secure error handling (не раскрывать sensitive данные)
- [ ] CSRF protection (через apiService)
- [ ] XSS protection (санитизация всех user inputs)

### Для Admin страниц (дополнительно)

- [ ] Двойная проверка прав (route + component)
- [ ] Confirmation dialogs для деструктивных операций
- [ ] Undo/Redo для критических операций (опционально)
- [ ] Activity log для всех изменений

---

## 📝 Checklist для разработчиков

**Перед началом разработки новой страницы:**

### Подготовка
- [ ] Изучил раздел "Архитектурные решения" в этом документе
- [ ] Проверил существующие компоненты для переиспользования
- [ ] Определил необходимые новые stores/services
- [ ] Создал TypeScript типы в `types/api.ts`
- [ ] Изучил существующие паттерны кода

### Разработка
- [ ] Создал страницу/компонент с lazy loading
- [ ] Добавил роуты в `router/index.ts` с permission checks
- [ ] Создал/расширил необходимые stores
- [ ] Создал необходимые services
- [ ] Интегрировал с существующими Layout компонентами
- [ ] Добавил permission checks в компонент
- [ ] Настроил error handling
- [ ] Добавил accessibility attributes
- [ ] Реализовал responsive design

### Тестирование
- [ ] Написал unit tests (85%+ coverage)
- [ ] Написал E2E tests для основных flows
- [ ] Создал Storybook stories
- [ ] Проверил производительность (Lighthouse)
- [ ] Проверил accessibility (axe-core)
- [ ] Протестировал на разных браузерах
- [ ] Протестировал на мобильных устройствах

### Документация
- [ ] Обновил README (если нужно)
- [ ] Добавил JSDoc комментарии
- [ ] Обновил API documentation

---

## 🎯 Следующие шаги

1. **Week 11, Day 1:** Начать с AdminPage + UserManagementPage
   - Создать adminStore, adminService
   - Создать базовую структуру страниц
   - Интегрировать в router

2. **Week 11, Day 2-3:** Продолжить Admin модуль
   - MetadataSchemaPage
   - WorkflowDesignerPage (начало)

3. **Week 11, Day 4-5:** Error & Auth Pages
   - Создать error pages
   - Интегрировать в error boundary
   - Создать auth pages

4. **Week 12:** User Pages + Distribution + Modals
   - CollectionsPage
   - ReportsPage
   - Distribution sub-pages
   - Модальные окна

---

**Документ создан:** 27 Января 2025  
**Версия:** 2.0 (Architecture-Enhanced)  
**Статус:** ✅ Готово к разработке  
**Архитектор:** Senior DAM Architect (20+ years experience)  
**Следующий шаг:** Начать Phase 4 (Week 11-12) с учетом архитектурных решений

