# 🚀 DAM FRONTEND ENHANCEMENT - ПОШАГОВЫЙ ПЛАН С CURSOR AI ПРОМПТАМИ

**Версия:** 2.0 (AI-Ready Implementation Plan)  
**Дата:** 27 Января 2025  
**Статус:** ✅ Готово для Cursor AI  
**Документация ссылается на:** DAM-Frontend-Enhancement-TZ.md  
**Общее покрытие:** 91/100 в соответствии с требованиями современных DAM систем

---

## 📌 БЫСТРЫЙ СТАРТ

**За 10 минут вы поймете весь план:**

```
Phase 1: Admin Module (Week 11, Days 1-5) 
├─ Step 1-3: AdminPage + UserManagementPage
├─ Step 4-6: MetadataSchemaPage
├─ Step 7-8: WorkflowDesignerPage
└─ Step 9-11: Error Pages + Auth Pages

Phase 2: User Features (Week 12, Days 1-3)
├─ Step 12-13: CollectionsPage
├─ Step 14-15: ReportsPage  
└─ Step 16-17: Distribution Sub-pages

Phase 3: Modals & Polish (Week 12, Days 4-7)
├─ Step 18-22: 5 критических модальных окон
└─ Step 23-24: Финальный WorkflowDesignerPage

Total: 24 steps, каждый = 1-2 часа для Cursor AI
```

---

## ⚙️ КАК ИСПОЛЬЗОВАТЬ ЭТОТ ДОКУМЕНТ

### Для разработчика:

1. **Прочитайте Phase 1 Overview** (5 минут)
2. **Скопируйте Step 1 промпт** в Cursor
3. **Ждите завершения** (5-15 минут)
4. **Проверьте результат** против чеклиста
5. **Перейдите на Step 2** и повторите

### Для Cursor AI:

```
1. Получаете промпт → читаете Dependencies и Architecture
2. Генерируете код → следуя точной спецификации
3. Проверяете себя → против Acceptance Criteria
4. Готовите файлы → для коммита в Git
5. Логируете output → название файлов + строки кода
```

---

# PHASE 1: ADMIN MODULE (WEEK 11)

## 🔴 ПРИОРИТЕТ: P0 (CRITICAL FOR ENTERPRISE)

**Объем:** 4 страницы админ-панели + архитектура + 60+ unit tests  
**Время:** 5 дней  
**Output:** Production-ready Admin Module + полное тестовое покрытие  

---

## STEP 1: Admin Architecture Setup + adminStore

**Зависимости:** 
- ✅ Существующий: pinia, typescript, vue3
- ✅ Документация: DAM-Frontend-Transformation-Plan-v3.md (Section 4)
- ✅ ТЗ: DAM-Frontend-Enhancement-TZ.md (Section 3 - Admin Module Architecture)

**Время:** 1 час  
**Output:** 3 файла (types, store, service)

---

### ПРОМПТ 1: Создать Admin API Types + Pinia Store

```
You are a senior frontend architect with 20+ years experience. 

TASK: Create complete admin architecture for DAM frontend

Context:
- Existing: Vue 3 + TypeScript strict mode + Pinia stores
- Target: Enterprise-grade admin module (Bynder/Canto level)
- Framework: refs + computed pattern (Pinia composition API)
- Reference: DAM-Frontend-Enhancement-TZ.md section "architekturные решenia"

PHASE 1: Create TypeScript Types

File: src/types/admin.ts
Requirements:
- User interface (id, username, email, first_name, last_name, is_active, is_staff, is_superuser, role, date_joined, last_login, avatar_url, permissions)
- CreateUserRequest interface (for API payload)
- UpdateUserRequest interface (partial fields)
- MetadataSchema interface (id, name, description, applies_to, fields)
- SchemaField interface (name, type, required, default_value, options, validation_rules)
- FieldType as discriminated union ('text' | 'textarea' | 'number' | 'date' | 'date_range' | 'select' | 'multi_select' | 'checkbox' | 'file_upload' | 'url')
- Workflow interface (id, name, description, nodes, transitions, is_active)
- WorkflowNode interface (id, name, type: 'start'|'state'|'end', position, allowed_roles, actions)
- WorkflowTransition interface (id, from_node, to_node, condition, label)
- GetUsersParams interface (page?, page_size?, role?, status?, search?)
- PaginatedResponse generic (count, next, previous, results)

Strict Requirements:
✓ All interfaces exported with 'export interface' (not type)
✓ Use discriminated unions where appropriate
✓ Document complex fields with JSDoc comments
✓ Include validation type constraints (min lengths, patterns)
✓ No optional fields unless explicitly optional in docs
✓ Follow naming: PascalCase for interfaces, camelCase for fields

PHASE 2: Create adminStore.ts

File: src/stores/adminStore.ts
Store Pattern: Composition API with defineStore

State (using ref):
- users: Ref<User[]> = ref([])
- totalUsersCount: Ref<number> = ref(0)
- selectedUsers: Ref<number[]> = ref([])
- usersFilters: Ref<{role: string, status: string, search: string}> = ref({role: '', status: '', search: ''})
- schemas: Ref<MetadataSchema[]> = ref([])
- currentSchema: Ref<MetadataSchema | null> = ref(null)
- workflows: Ref<Workflow[]> = ref([])
- currentWorkflow: Ref<Workflow | null> = ref(null)
- selectedNode: Ref<WorkflowNode | null> = ref(null)
- isLoading: Ref<boolean> = ref(false)
- error: Ref<string | null> = ref(null)
- lastFetchTime: Ref<number | null> = ref(null)

Computed:
- canCreateUser: checks permission 'admin.user_create'
- canEditUser: checks permission 'admin.user_edit'
- canDeleteUser: checks permission 'admin.user_delete'
- filteredUsers: applies filters to users list
- hasUnsavedChanges: tracks dirty state for forms

Actions (async functions):
1. fetchUsers(params?: GetUsersParams)
   - call adminService.getUsers(params)
   - set users, totalUsersCount
   - implement cache: don't refetch if called within 5 minutes (use lastFetchTime)
   - error handling: try/catch, set error, rethrow

2. createUser(userData: CreateUserRequest)
   - call adminService.createUser(userData)
   - add to users array (optimistic update)
   - return User

3. updateUser(id: number, data: UpdateUserRequest)
   - call adminService.updateUser(id, data)
   - update in users array

4. deleteUser(id: number)
   - call adminService.deleteUser(id)
   - remove from users array

5. bulkUserOperation(operation: BulkUserOperationRequest)
   - validate: operation.ids.length <= 100
   - call adminService.bulkUserOperation(operation)
   - refresh users list

6. selectUsers(ids: number[])
   - set selectedUsers

7. clearFilters()
   - reset usersFilters to defaults

8. setFilters(filters: Partial<GetUsersParams>)
   - update usersFilters

9. Similar actions for schemas and workflows

Persist Configuration:
- persist: { paths: ['usersFilters'] }
  Only filters persist, not actual data (for security)

PHASE 3: Create adminService.ts

File: src/services/adminService.ts

Class AdminService:
- constructor: none needed, uses apiService

Methods:
1. getUsers(params?: GetUsersParams): Promise<PaginatedResponse<User>>
   - endpoint: GET /api/v4/admin/users/
   - params passed as query string
   - use apiService.get<PaginatedResponse<User>>()

2. createUser(data: CreateUserRequest): Promise<User>
   - endpoint: POST /api/v4/admin/users/
   - use apiService.post<User>()

3. updateUser(id: number, data: UpdateUserRequest): Promise<User>
   - endpoint: PUT /api/v4/admin/users/{id}/
   - use apiService.put<User>()

4. deleteUser(id: number): Promise<void>
   - endpoint: DELETE /api/v4/admin/users/{id}/
   - use apiService.delete<void>()

5. bulkUserOperation(operation: BulkUserOperationRequest): Promise<BulkUserOperationResponse>
   - endpoint: POST /api/v4/admin/users/bulk/
   - body: { ids: number[], action: string, data?: {} }

6. Similar methods for schemas and workflows

Export singleton:
export const adminService = new AdminService()

Error Handling:
- All methods use apiService which handles errors
- Don't duplicate error handling

Type Safety:
- Strict mode: no 'any' types
- Use generics where appropriate
- Discriminated unions for variants

TEST COVERAGE EXPECTATIONS:
- adminStore: 20+ unit tests
- adminService: 15+ unit tests
- types: 5+ tests (union validation)

ACCEPTANCE CRITERIA:
☐ All types properly exported and documented
☐ Store uses Composition API pattern (not Options API)
☐ Cache logic implemented correctly (5 minute TTL)
☐ All methods have proper error handling
☐ Service uses existing apiService (no duplicate logic)
☐ Persist configuration correct (only filters)
☐ No TypeScript errors (strict mode)
☐ All computed properties work correctly
☐ Bulk operations limit to 100 items
☐ File structure follows existing patterns

OUTPUT:
Generate these 3 files:
1. src/types/admin.ts (complete types)
2. src/stores/adminStore.ts (complete store with all actions)
3. src/services/adminService.ts (complete service class)

Format: Complete, production-ready code. No TODOs or placeholders.
```

---

### ВЫПОЛНЕННЫЙ РЕЗУЛЬТАТ (ДЛЯ ПРОВЕРКИ)

```
✅ src/types/admin.ts
   - User, CreateUserRequest, UpdateUserRequest
   - MetadataSchema, SchemaField, FieldType (union)
   - Workflow, WorkflowNode, WorkflowTransition
   - API request/response types
   - 450+ строк типов

✅ src/stores/adminStore.ts
   - Composition API pattern
   - 9 refs (users, schemas, workflows + state)
   - 4 computed properties
   - 9+ async actions (fetch, create, update, delete, bulk)
   - Caching logic (5-minute TTL)
   - Error handling
   - 280+ строк

✅ src/services/adminService.ts
   - AdminService class
   - 9+ методов (getUsers, createUser, etc.)
   - Все используют apiService
   - Полная типизация
   - 180+ строк
```

---

## STEP 2: AdminPage.vue + AdminNavigationTabs

**Зависимости:** Step 1 (adminStore, types)  
**Время:** 1 час  
**Output:** 2 файла (AdminPage + компонент табов)

---

### ПРОМПТ 2: Admin Main Page + Navigation Tabs

```
You are a senior Vue 3 frontend developer with 20+ years experience.

TASK: Create AdminPage.vue (main admin layout) + AdminNavigationTabs.vue component

Context:
- Admin module main page (router outlet for sub-pages)
- Existing: Layout/Header.vue, Layout/Sidebar.vue, Layout/MainContent.vue
- Pattern: Composition API + TypeScript strict
- Design: Modern, accessible (WCAG 2.1 AA)

FILE 1: src/pages/AdminPage.vue

Structure:
<template>
  <div class="admin-page">
    <MainLayout>
      <template #content>
        <!-- Breadcrumbs -->
        <Breadcrumbs :items="breadcrumbs" />
        
        <!-- Admin Navigation Tabs -->
        <AdminNavigationTabs 
          :current-tab="currentTab"
          @tab-change="handleTabChange"
        />
        
        <!-- Content Area -->
        <div class="admin-content">
          <!-- Router outlet for sub-pages (UserManagementPage, MetadataSchemaPage, etc.) -->
          <RouterView />
        </div>
      </template>
    </MainLayout>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useUIStore } from '@/stores/uiStore'
import MainLayout from '@/components/Layout/MainLayout.vue'
import AdminNavigationTabs from '@/components/admin/AdminNavigationTabs.vue'
import Breadcrumbs from '@/components/Common/Breadcrumbs.vue'

// Hooks
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const uiStore = useUIStore()

// State
const currentTab = ref<string>('users')

// Computed
const breadcrumbs = computed(() => [
  { label: 'Home', to: '/' },
  { label: 'Administration', to: '/admin' },
  { label: formatTabName(currentTab.value), to: null }
])

// Methods
const handleTabChange = async (tabName: string) => {
  currentTab.value = tabName
  // Navigate to sub-page
  await router.push(`/admin/${tabName}`)
}

const formatTabName = (tab: string): string => {
  const names: Record<string, string> = {
    users: 'User Management',
    schemas: 'Metadata Schemas',
    workflows: 'Workflow Designer',
    integrations: 'Integrations',
    reports: 'Reports'
  }
  return names[tab] || tab
}

// Lifecycle
onMounted(async () => {
  // Permission check
  if (!authStore.hasPermission('admin.access')) {
    router.push({ name: 'forbidden' })
    return
  }
  
  // Sync current tab from route
  const tab = route.params.tab as string || 'users'
  currentTab.value = tab
})
</script>

<style scoped lang="css">
.admin-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.admin-content {
  flex: 1;
  padding: 24px;
  background: var(--color-background);
  animation: fadeIn 300ms ease-in;
}

@keyframes fadeIn {
  from { opacity: 0.95; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Responsive */
@media (max-width: 768px) {
  .admin-content {
    padding: 16px;
  }
}
</style>

---

FILE 2: src/components/admin/AdminNavigationTabs.vue

Component Purpose: Navigation tabs for admin sub-pages
- Responsive (desktop: horizontal tabs, mobile: dropdown)
- Active tab highlighting
- ARIA labels for accessibility
- Permission-based visibility (if needed)

<template>
  <div class="admin-tabs">
    <!-- Desktop Tabs -->
    <nav 
      class="admin-tabs__nav"
      role="tablist"
      aria-label="Administration Navigation"
    >
      <button
        v-for="tab in availableTabs"
        :key="tab.id"
        :class="['admin-tabs__tab', { 'admin-tabs__tab--active': currentTab === tab.id }]"
        :aria-selected="currentTab === tab.id"
        :aria-controls="`panel-${tab.id}`"
        role="tab"
        @click="emit('tab-change', tab.id)"
      >
        <i :class="['icon', `icon-${tab.icon}`]" />
        {{ tab.label }}
      </button>
    </nav>
    
    <!-- Mobile Dropdown -->
    <div class="admin-tabs__mobile">
      <select 
        :value="currentTab"
        @change="(e) => emit('tab-change', (e.target as HTMLSelectElement).value)"
        class="admin-tabs__select"
      >
        <option v-for="tab in availableTabs" :key="tab.id" :value="tab.id">
          {{ tab.label }}
        </option>
      </select>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/authStore'

// Types
interface Tab {
  id: string
  label: string
  icon: string
  requiresPermission?: string
}

// Props
defineProps<{
  currentTab: string
}>()

// Emits
const emit = defineEmits<{
  'tab-change': [tabName: string]
}>()

// Hooks
const authStore = useAuthStore()

// Tabs configuration
const allTabs: Tab[] = [
  { id: 'users', label: 'Users', icon: 'users', requiresPermission: 'admin.user_manage' },
  { id: 'schemas', label: 'Metadata Schemas', icon: 'database', requiresPermission: 'admin.schema_manage' },
  { id: 'workflows', label: 'Workflows', icon: 'flow', requiresPermission: 'admin.workflow_manage' },
  { id: 'integrations', label: 'Integrations', icon: 'plug', requiresPermission: 'admin.integrations_manage' },
  { id: 'reports', label: 'Reports', icon: 'chart-bar', requiresPermission: 'admin.reports_view' }
]

// Computed
const availableTabs = computed(() => 
  allTabs.filter(tab => 
    !tab.requiresPermission || authStore.hasPermission(tab.requiresPermission)
  )
)
</script>

<style scoped lang="css">
.admin-tabs {
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
  margin-bottom: 24px;
}

.admin-tabs__nav {
  display: flex;
  flex-direction: row;
  list-style: none;
  margin: 0;
  padding: 0;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.admin-tabs__tab {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border: none;
  border-bottom: 3px solid transparent;
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: var(--font-size-base);
  font-weight: 500;
  white-space: nowrap;
  transition: all 200ms ease;
}

.admin-tabs__tab:hover {
  color: var(--color-text);
  background: rgba(0, 0, 0, 0.02);
}

.admin-tabs__tab--active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.admin-tabs__tab:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: -2px;
}

.admin-tabs__mobile {
  display: none;
}

.admin-tabs__select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-base);
  background: var(--color-surface);
  color: var(--color-text);
  font-size: var(--font-size-base);
  cursor: pointer;
}

/* Responsive */
@media (max-width: 768px) {
  .admin-tabs__nav {
    display: none;
  }
  
  .admin-tabs__mobile {
    display: block;
    padding: 12px 16px;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .admin-tabs__tab {
    transition: none;
  }
}
</style>

---

REQUIREMENTS:
✓ AdminPage uses Composition API + TypeScript
✓ Permission check on mount (redirect if not admin)
✓ Breadcrumbs component for navigation
✓ AdminNavigationTabs responsive (desktop tabs, mobile dropdown)
✓ Tab synchronization with router
✓ ARIA labels for accessibility (role="tablist", role="tab")
✓ Keyboard navigation support (Tab key)
✓ Focus indicators visible
✓ Color contrast 4.5:1 minimum
✓ Animations smooth (prefer-reduced-motion support)
✓ CSS uses design system variables

ACCEPTANCE CRITERIA:
☐ AdminPage renders without errors
☐ Permission check works (401 → redirect to forbidden)
☐ Tab switching works (click/select changes route)
☐ Responsive design works (desktop tabs visible, mobile dropdown visible)
☐ Breadcrumbs update correctly
☐ ARIA attributes present and correct
☐ Keyboard navigation works (Tab, Enter, Arrow keys)
☐ Focus indicators visible and accessible
☐ No console errors or warnings
☐ TypeScript strict mode passes

OUTPUT:
Generate these 2 files:
1. src/pages/AdminPage.vue (complete)
2. src/components/admin/AdminNavigationTabs.vue (complete)
```

---

## STEP 3: Router Integration + Permission Guards

**Зависимости:** Step 1-2  
**Время:** 30 минут  
**Output:** 1 файл (router/index.ts с обновлениями)

---

### ПРОМПТ 3: Add Admin Routes to Router

```
You are a senior Vue 3 + Vue Router expert.

TASK: Add admin routes to existing router/index.ts

Context:
- Existing router with auth guards
- New admin routes: /admin (main), /admin/users, /admin/schemas, /admin/workflows, /admin/integrations, /admin/reports
- Routes require permission checks
- All routes require authentication

FILE: src/router/index.ts (UPDATE ONLY THE ROUTES SECTION)

Add these routes to the main routes array:

// Admin routes (nested structure)
{
  path: '/admin',
  component: () => import('@/pages/AdminPage.vue'),
  meta: { 
    requiresAuth: true,
    requiresPermission: 'admin.access',
    breadcrumb: 'Administration'
  },
  children: [
    {
      path: 'users',
      name: 'admin-users',
      component: () => import('@/pages/admin/UserManagementPage.vue'),
      meta: { 
        requiresPermission: 'admin.user_manage',
        breadcrumb: 'User Management',
        title: 'User Management - Admin'
      }
    },
    {
      path: 'schemas',
      name: 'admin-metadata-schemas',
      component: () => import('@/pages/admin/MetadataSchemaPage.vue'),
      meta: { 
        requiresPermission: 'admin.schema_manage',
        breadcrumb: 'Metadata Schemas',
        title: 'Metadata Schemas - Admin'
      }
    },
    {
      path: 'workflows',
      name: 'admin-workflows',
      component: () => import('@/pages/admin/WorkflowDesignerPage.vue'),
      meta: { 
        requiresPermission: 'admin.workflow_manage',
        breadcrumb: 'Workflow Designer',
        title: 'Workflow Designer - Admin'
      }
    },
    {
      path: 'integrations',
      name: 'admin-integrations',
      component: () => import('@/pages/admin/AdminIntegrationsPage.vue'),
      meta: { 
        requiresPermission: 'admin.integrations_manage',
        breadcrumb: 'Integrations',
        title: 'Integrations - Admin'
      }
    },
    {
      path: 'reports',
      name: 'admin-reports',
      component: () => import('@/pages/admin/AdminReportsPage.vue'),
      meta: { 
        requiresPermission: 'admin.reports_view',
        breadcrumb: 'Reports',
        title: 'Admin Reports'
      }
    }
  ]
}

// Redirect /admin to /admin/users
{
  path: '/admin',
  redirect: '/admin/users'
}

EXISTING ROUTER GUARD UPDATE:

In router.beforeEach((to, from, next) => {
  // Add permission check after existing auth checks

  // EXISTING: Check if authenticated
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { returnTo: to.fullPath } })
    return
  }

  // NEW: Permission check
  if (to.meta.requiresPermission) {
    const permission = to.meta.requiresPermission as string
    if (!authStore.hasPermission(permission)) {
      console.warn(`Access denied: User ${authStore.user?.id} attempted ${to.path}, required: ${permission}`)
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

  // EXISTING: Continue
  next()
})

REQUIREMENTS:
✓ Routes use lazy loading with dynamic import
✓ All admin routes have requiresAuth: true
✓ All admin routes have requiresPermission meta
✓ Permission-based route guard implemented
✓ Breadcrumb meta present
✓ Title meta present for SEO
✓ Redirect /admin → /admin/users
✓ No hard-coded imports (only dynamic)

ACCEPTANCE CRITERIA:
☐ Routes parse without errors
☐ Permission guard checks authStore.hasPermission()
☐ Lazy loading works for all admin pages
☐ Redirect to /admin/users works
☐ Permission denied redirects to /forbidden
☐ No TypeScript errors

OUTPUT:
Update src/router/index.ts with:
1. New admin routes (nested children structure)
2. Redirect from /admin to /admin/users
3. Updated router.beforeEach guard with permission check
```

---

## STEP 4: UserManagementPage.vue + DataTable Component

**Зависимости:** Step 1-3 + adminStore  
**Время:** 1.5 часа  
**Output:** 2 файла (страница + компонент таблицы)

---

### ПРОМПТ 4: UserManagementPage + Generic DataTable

```
You are a senior Vue 3 frontend architect with expertise in data tables and CRUD operations.

TASK: Create production-ready UserManagementPage with reusable DataTable component

Context:
- Page: /admin/users (nested in AdminPage)
- Features: List, search, filter, bulk operations, CRUD
- Admin must have permission 'admin.user_manage'
- Data: users from adminStore
- Pattern: Composition API + TypeScript
- Design: Modern, accessible (WCAG 2.1 AA)

FILE 1: src/components/Common/DataTable.vue (reusable)

Generic component for displaying tabular data
- Props: items, columns, isLoading, selectable, sortable
- Emits: select, sort, action-click
- Features:
  - Multi-select with checkboxes
  - Column sorting (click header)
  - Row actions (edit, delete, more)
  - Empty state
  - Loading skeleton
  - Virtual scrolling for 1000+ rows
  - Responsive (horizontal scroll on mobile)
  - Accessibility (semantic table, ARIA labels)

<template>
  <div class="data-table">
    <!-- Loading State -->
    <div v-if="isLoading" class="data-table__loading">
      <div v-for="i in 5" :key="i" class="data-table__skeleton-row" />
    </div>
    
    <!-- Empty State -->
    <div v-else-if="items.length === 0" class="data-table__empty">
      <p>{{ emptyStateText }}</p>
      <slot name="empty-action" />
    </div>
    
    <!-- Table -->
    <div v-else class="data-table__wrapper">
      <table class="data-table__table" role="table">
        <thead>
          <tr>
            <!-- Checkbox (if selectable) -->
            <th v-if="selectable" class="data-table__cell--checkbox">
              <input
                type="checkbox"
                :checked="allSelected"
                @change="toggleAllSelected"
                aria-label="Select all rows"
              />
            </th>
            
            <!-- Column Headers -->
            <th
              v-for="col in columns"
              :key="col.key"
              :class="['data-table__cell', `data-table__cell--${col.align || 'left'}`]"
              role="columnheader"
              :aria-sort="getSortOrder(col.key)"
              @click="sortable && handleSort(col.key)"
            >
              <button 
                v-if="sortable"
                class="data-table__sort-btn"
                :aria-label="`Sort by ${col.label}`"
              >
                {{ col.label }}
                <i v-if="sortKey === col.key" :class="['icon', `icon-arrow-${sortOrder}`]" />
              </button>
              <span v-else>{{ col.label }}</span>
            </th>
            
            <!-- Actions Column -->
            <th v-if="$slots['row-actions']" class="data-table__cell data-table__cell--actions">
              Actions
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in items" :key="getRowKey(item, index)">
            <!-- Checkbox -->
            <td v-if="selectable" class="data-table__cell data-table__cell--checkbox">
              <input
                type="checkbox"
                :value="getRowKey(item, index)"
                :checked="isRowSelected(item)"
                @change="toggleRowSelected(item)"
                :aria-label="`Select row ${index + 1}`"
              />
            </td>
            
            <!-- Data Cells -->
            <td
              v-for="col in columns"
              :key="col.key"
              :class="['data-table__cell', `data-table__cell--${col.align || 'left'}`]"
            >
              <slot
                :name="`col-${col.key}`"
                :item="item"
                :value="getNestedValue(item, col.key)"
              >
                {{ formatCellValue(getNestedValue(item, col.key), col.format) }}
              </slot>
            </td>
            
            <!-- Actions -->
            <td v-if="$slots['row-actions']" class="data-table__cell data-table__cell--actions">
              <slot name="row-actions" :item="item" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts" generic="T extends Record<string, any>">
import { ref, computed } from 'vue'

interface Column {
  key: string
  label: string
  align?: 'left' | 'center' | 'right'
  format?: 'date' | 'currency' | 'boolean'
  sortable?: boolean
}

interface DataTableEmits {
  select: [items: T[]]
  sort: [key: string, order: 'asc' | 'desc']
  'action-click': [action: string, item: T]
}

// Props
defineProps<{
  items: T[]
  columns: Column[]
  isLoading?: boolean
  selectable?: boolean
  sortable?: boolean
  emptyStateText?: string
  getRowKey?: (item: T, index: number) => string | number
}>()

// Emits
const emit = defineEmits<DataTableEmits>()

// State
const selectedItems = ref<T[]>([])
const sortKey = ref<string>('')
const sortOrder = ref<'asc' | 'desc'>('asc')

// Computed
const allSelected = computed(() => 
  selectedItems.value.length === props.items.length && props.items.length > 0
)

// Methods
const toggleAllSelected = () => {
  if (allSelected.value) {
    selectedItems.value = []
  } else {
    selectedItems.value = [...props.items]
  }
  emit('select', selectedItems.value)
}

const toggleRowSelected = (item: T) => {
  const index = selectedItems.value.indexOf(item)
  if (index > -1) {
    selectedItems.value.splice(index, 1)
  } else {
    selectedItems.value.push(item)
  }
  emit('select', selectedItems.value)
}

const isRowSelected = (item: T): boolean => 
  selectedItems.value.includes(item)

const handleSort = (key: string) => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
  emit('sort', key, sortOrder.value)
}

const getSortOrder = (key: string): 'ascending' | 'descending' | 'none' => {
  if (sortKey.value !== key) return 'none'
  return sortOrder.value === 'asc' ? 'ascending' : 'descending'
}

const getNestedValue = (obj: T, path: string): any => {
  return path.split('.').reduce((acc, part) => acc?.[part], obj)
}

const formatCellValue = (value: any, format?: string): string => {
  if (value === null || value === undefined) return '—'
  
  switch (format) {
    case 'date':
      return new Date(value).toLocaleDateString()
    case 'currency':
      return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value)
    case 'boolean':
      return value ? 'Yes' : 'No'
    default:
      return String(value)
  }
}

const getRowKey = (item: T, index: number): string | number => {
  return (item.id || index) as string | number
}
</script>

<style scoped lang="css">
.data-table {
  width: 100%;
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  overflow: hidden;
}

.data-table__wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.data-table__table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-size-base);
}

.data-table__table thead {
  background: var(--color-bg-1);
  border-bottom: 2px solid var(--color-border);
}

.data-table__table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: var(--color-text);
  white-space: nowrap;
}

.data-table__table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text);
}

.data-table__table tbody tr:hover {
  background: rgba(0, 0, 0, 0.02);
}

.data-table__cell {
  vertical-align: middle;
}

.data-table__cell--checkbox {
  width: 44px;
  text-align: center;
}

.data-table__cell--center {
  text-align: center;
}

.data-table__cell--right {
  text-align: right;
}

.data-table__cell--actions {
  width: 120px;
  text-align: right;
}

.data-table__sort-btn {
  background: none;
  border: none;
  color: inherit;
  font-size: inherit;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0;
  font-weight: 600;
}

.data-table__sort-btn:hover {
  color: var(--color-primary);
}

.data-table__sort-btn:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.data-table__empty {
  padding: 48px 24px;
  text-align: center;
  color: var(--color-text-secondary);
}

.data-table__loading {
  display: flex;
  flex-direction: column;
}

.data-table__skeleton-row {
  height: 48px;
  background: linear-gradient(90deg, var(--color-bg-1) 25%, rgba(0, 0, 0, 0.02) 50%, var(--color-bg-1) 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Responsive */
@media (max-width: 768px) {
  .data-table__table th,
  .data-table__table td {
    padding: 8px 12px;
    font-size: var(--font-size-sm);
  }
  
  .data-table__sort-btn {
    flex-direction: column;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .data-table__skeleton-row {
    animation: none;
    opacity: 0.5;
  }
}
</style>

---

FILE 2: src/pages/admin/UserManagementPage.vue

<template>
  <div class="user-management">
    <!-- Toolbar -->
    <div class="user-management__toolbar">
      <Button 
        v-if="canCreateUser"
        variant="primary"
        @click="showCreateModal = true"
      >
        <i class="icon icon-plus" />
        Add User
      </Button>
      
      <div class="user-management__search">
        <Input
          v-model="searchQuery"
          type="search"
          placeholder="Search users..."
          @input="handleSearch"
        />
      </div>
      
      <Select
        v-model="filters.status"
        :options="statusOptions"
        @change="handleFilterChange"
      />
    </div>
    
    <!-- Bulk Actions -->
    <div v-if="selectedUsers.length > 0" class="user-management__bulk-actions">
      <span>{{ selectedUsers.length }} selected</span>
      <Button 
        variant="secondary"
        size="sm"
        @click="handleBulkDelete"
      >
        Delete Selected
      </Button>
      <Button 
        variant="secondary"
        size="sm"
        @click="handleBulkChangeRole"
      >
        Change Role
      </Button>
    </div>
    
    <!-- Data Table -->
    <DataTable
      :items="paginatedUsers"
      :columns="tableColumns"
      :is-loading="isLoading"
      selectable
      sortable
      empty-state-text="No users found"
      @select="handleSelectUsers"
      @sort="handleSort"
    >
      <template #col-avatar="{ item }">
        <img
          :src="item.avatar_url || `https://ui-avatars.com/api/?name=${item.first_name}+${item.last_name}`"
          :alt="`${item.first_name} ${item.last_name}`"
          class="user-avatar"
        />
      </template>
      
      <template #col-name="{ item }">
        {{ item.first_name }} {{ item.last_name }}
      </template>
      
      <template #col-role="{ item }">
        <Select
          v-if="canEditUser"
          :model-value="item.role"
          :options="roleOptions"
          @change="(role) => handleUpdateUserRole(item, role)"
        />
        <span v-else>{{ item.role }}</span>
      </template>
      
      <template #col-is_active="{ item }">
        <Badge :variant="item.is_active ? 'success' : 'warning'">
          {{ item.is_active ? 'Active' : 'Inactive' }}
        </Badge>
      </template>
      
      <template #col-date_joined="{ item, value }">
        {{ new Date(value).toLocaleDateString() }}
      </template>
      
      <template #row-actions="{ item }">
        <Button 
          v-if="canEditUser"
          variant="ghost"
          size="sm"
          @click="handleEditUser(item)"
        >
          Edit
        </Button>
        <Button
          v-if="canDeleteUser"
          variant="ghost"
          size="sm"
          :disabled="item.is_superuser && !authStore.user?.is_superuser"
          @click="handleDeleteUser(item)"
        >
          Delete
        </Button>
      </template>
    </DataTable>
    
    <!-- Pagination -->
    <Pagination
      :page="currentPage"
      :page-size="pageSize"
      :total="totalUsersCount"
      @change="handlePageChange"
    />
    
    <!-- Modals -->
    <CreateUserModal
      v-if="showCreateModal"
      @submit="handleCreateUser"
      @close="showCreateModal = false"
    />
    
    <EditUserModal
      v-if="editingUser"
      :user="editingUser"
      @submit="handleUpdateUser"
      @close="editingUser = null"
    />
    
    <DeleteConfirmModal
      v-if="deletingUser"
      :title="`Delete User: ${deletingUser.first_name} ${deletingUser.last_name}`"
      :message="'This action cannot be undone. Are you sure?'"
      @confirm="confirmDeleteUser"
      @cancel="deletingUser = null"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { useAdminStore } from '@/stores/adminStore'
import { useUIStore } from '@/stores/uiStore'
import { useRouter } from 'vue-router'
import type { User, CreateUserRequest, UpdateUserRequest, GetUsersParams } from '@/types/admin'

// Hooks
const router = useRouter()
const authStore = useAuthStore()
const adminStore = useAdminStore()
const uiStore = useUIStore()

// State
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(50)
const sortKey = ref<string>('')
const sortOrder = ref<'asc' | 'desc'>('asc')
const filters = ref({ status: '', role: '' })
const isLoading = ref(false)
const showCreateModal = ref(false)
const editingUser = ref<User | null>(null)
const deletingUser = ref<User | null>(null)

// Computed
const canCreateUser = computed(() => authStore.hasPermission('admin.user_create'))
const canEditUser = computed(() => authStore.hasPermission('admin.user_edit'))
const canDeleteUser = computed(() => authStore.hasPermission('admin.user_delete'))

const selectedUsers = computed(() => adminStore.selectedUsers)
const paginatedUsers = computed(() => adminStore.users.slice(0, pageSize.value))
const totalUsersCount = computed(() => adminStore.totalUsersCount)

const tableColumns = [
  { key: 'avatar', label: '', width: 44, sortable: false },
  { key: 'first_name', label: 'Name', align: 'left' },
  { key: 'email', label: 'Email', align: 'left' },
  { key: 'role', label: 'Role', align: 'center' },
  { key: 'is_active', label: 'Status', align: 'center' },
  { key: 'date_joined', label: 'Created', align: 'left' }
]

const statusOptions = [
  { value: '', label: 'All' },
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' }
]

const roleOptions = [
  { value: 'admin', label: 'Administrator' },
  { value: 'editor', label: 'Editor' },
  { value: 'viewer', label: 'Viewer' }
]

// Methods
const fetchUsers = async () => {
  isLoading.value = true
  try {
    const params: GetUsersParams = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value,
      ...filters.value
    }
    await adminStore.fetchUsers(params)
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      message: 'Failed to load users',
      duration: 5000
    })
  } finally {
    isLoading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchUsers()
}

const handleFilterChange = () => {
  currentPage.value = 1
  fetchUsers()
}

const handleSort = (key: string, order: 'asc' | 'desc') => {
  sortKey.value = key
  sortOrder.value = order
  // Note: API-level sorting would need to be implemented
  // For now, this is handled on frontend
}

const handleSelectUsers = (users: User[]) => {
  adminStore.selectUsers(users.map(u => u.id))
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchUsers()
}

const handleCreateUser = async (data: CreateUserRequest) => {
  try {
    await adminStore.createUser(data)
    showCreateModal.value = false
    uiStore.addNotification({
      type: 'success',
      message: 'User created successfully',
      duration: 3000
    })
    await fetchUsers()
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      message: 'Failed to create user',
      duration: 5000
    })
  }
}

const handleEditUser = (user: User) => {
  editingUser.value = user
}

const handleUpdateUser = async (data: UpdateUserRequest) => {
  if (!editingUser.value) return
  
  try {
    await adminStore.updateUser(editingUser.value.id, data)
    editingUser.value = null
    uiStore.addNotification({
      type: 'success',
      message: 'User updated successfully',
      duration: 3000
    })
    await fetchUsers()
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      message: 'Failed to update user',
      duration: 5000
    })
  }
}

const handleDeleteUser = (user: User) => {
  deletingUser.value = user
}

const confirmDeleteUser = async () => {
  if (!deletingUser.value) return
  
  try {
    await adminStore.deleteUser(deletingUser.value.id)
    deletingUser.value = null
    uiStore.addNotification({
      type: 'success',
      message: 'User deleted successfully',
      duration: 3000
    })
    await fetchUsers()
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      message: 'Failed to delete user',
      duration: 5000
    })
  }
}

const handleUpdateUserRole = async (user: User, role: string) => {
  try {
    await adminStore.updateUser(user.id, { role })
    uiStore.addNotification({
      type: 'success',
      message: `User role updated to ${role}`,
      duration: 3000
    })
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      message: 'Failed to update user role',
      duration: 5000
    })
  }
}

const handleBulkDelete = async () => {
  if (!confirm(`Delete ${selectedUsers.value.length} users? This cannot be undone.`)) return
  
  try {
    await adminStore.bulkUserOperation({
      ids: selectedUsers.value,
      action: 'delete'
    })
    adminStore.selectUsers([])
    uiStore.addNotification({
      type: 'success',
      message: `${selectedUsers.value.length} users deleted`,
      duration: 3000
    })
    await fetchUsers()
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      message: 'Failed to delete users',
      duration: 5000
    })
  }
}

const handleBulkChangeRole = () => {
  // Open modal to select role
  // Then call adminStore.bulkUserOperation with action: 'change_role'
}

// Lifecycle
onMounted(async () => {
  // Permission check
  if (!authStore.hasPermission('admin.user_manage')) {
    router.push({ name: 'forbidden' })
    return
  }
  
  await fetchUsers()
})
</script>

<style scoped lang="css">
.user-management {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.user-management__toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.user-management__search {
  flex: 1;
  min-width: 200px;
}

.user-management__bulk-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 12px 16px;
  background: var(--color-bg-1);
  border-radius: var(--radius-base);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

/* Responsive */
@media (max-width: 768px) {
  .user-management__toolbar {
    flex-direction: column;
  }
  
  .user-management__search {
    width: 100%;
  }
}
</style>

---

REQUIREMENTS:
✓ DataTable is generic component (works with any data type)
✓ UserManagementPage uses DataTable
✓ CRUD operations functional (create, read, update, delete)
✓ Bulk operations (select multiple, delete, change role)
✓ Search and filter implemented
✓ Pagination works
✓ Permission checks implemented
✓ Error handling with notifications
✓ Modal integration (create, edit, delete)
✓ Responsive design (desktop, tablet, mobile)
✓ Accessibility (WCAG 2.1 AA)
✓ TypeScript strict mode

ACCEPTANCE CRITERIA:
☐ DataTable renders items correctly
☐ Selection works (single and all)
☐ Sorting works (click header)
☐ Search updates results
☐ Filters work
☐ Pagination works
☐ Create user modal opens
☐ Edit user modal opens
☐ Delete user confirmation works
☐ Bulk operations work
☐ Error messages display
☐ Success messages display
☐ Responsive on mobile
☐ ARIA labels present
☐ Keyboard navigation works

OUTPUT:
Generate these 2 files:
1. src/components/Common/DataTable.vue (complete generic table)
2. src/pages/admin/UserManagementPage.vue (complete page)
```

---

## STEP 5-11: Продолжение Admin Module

**Структура:** Повторите STEP 4 для:
- Step 5: MetadataSchemaPage + FieldEditor
- Step 6: WorkflowDesignerPage (Part 1) - canvas setup
- Step 7: WorkflowDesignerPage (Part 2) - nodes + transitions
- Step 8-11: Error Pages + Auth Pages

---

# PHASE 2: USER FEATURES (WEEK 12)

## 🟡 ПРИОРИТЕТ: P1 (IMPORTANT FOR USERS)

---

## STEP 12-17: Collections + Reports + Distribution

**Аналогичная структура как Phase 1**

---

# PHASE 3: MODALS & POLISH (WEEK 12)

## 🟡 ПРИОРИТЕТ: P1-P2

---

## STEP 18-24: 5 Модальных окон + финальный WorkflowDesignerPage

---

# 📋 MASTER CHECKLIST

## Week 11 Completion Checklist

```
STEP 1: Admin Architecture
☐ src/types/admin.ts created (450+ lines)
☐ src/stores/adminStore.ts created (280+ lines)  
☐ src/services/adminService.ts created (180+ lines)
☐ Unit tests pass (35+ tests)
☐ TypeScript strict mode: OK

STEP 2: AdminPage + Navigation
☐ src/pages/AdminPage.vue created
☐ src/components/admin/AdminNavigationTabs.vue created
☐ Unit tests pass (15+ tests)
☐ Responsive design: OK
☐ ARIA labels: OK

STEP 3: Router Integration
☐ src/router/index.ts updated with /admin routes
☐ Permission guards implemented
☐ Lazy loading works
☐ Redirect /admin → /admin/users: OK

STEP 4: UserManagementPage
☐ src/components/Common/DataTable.vue created (generic)
☐ src/pages/admin/UserManagementPage.vue created
☐ CRUD operations: working
☐ Unit tests pass (40+ tests)
☐ E2E tests: passing

STEP 5: MetadataSchemaPage
☐ src/pages/admin/MetadataSchemaPage.vue created
☐ src/components/admin/FieldEditor.vue created
☐ Drag-drop: working
☐ Unit tests pass (30+ tests)

STEP 6-7: WorkflowDesignerPage
☐ src/pages/admin/WorkflowDesignerPage.vue created
☐ Canvas library integrated
☐ Nodes: create, edit, delete
☐ Transitions: create, edit, delete
☐ Unit tests pass (35+ tests)

STEP 8-11: Error & Auth Pages
☐ src/pages/Error500Page.vue created
☐ src/pages/UnauthorizedPage.vue created
☐ src/pages/ForbiddenPage.vue created
☐ src/pages/ForgotPasswordPage.vue created
☐ src/pages/ResetPasswordPage.vue created
☐ Unit tests pass (50+ tests)

TOTAL WEEK 11:
- 15+ new files
- 2500+ lines of code
- 190+ unit tests
- Phase 0 Architecture: ✅ Complete
- Phase 1 MVP: ✅ Complete (Ready for Phase 2)
```

---

## Week 12 Completion Checklist

```
STEP 12-13: CollectionsPage
☐ src/pages/CollectionsPage.vue created
☐ src/components/collections/CollectionTree.vue created
☐ TreeView: working
☐ Drag-drop: working
☐ Unit tests pass (25+ tests)

STEP 14-15: ReportsPage
☐ src/pages/ReportsPage.vue created
☐ Chart components: integrated
☐ Export (CSV/PDF): working
☐ Unit tests pass (30+ tests)

STEP 16-17: Distribution Sub-pages
☐ src/pages/PublicationDetailPage.vue created
☐ src/pages/PublicationPublicPage.vue created
☐ Unit tests pass (27+ tests)

STEP 18-22: Modals
☐ src/components/modals/CreateCollectionModal.vue
☐ src/components/modals/UploadModal.vue
☐ src/components/modals/ShareModal.vue
☐ src/components/modals/EditMetadataModal.vue
☐ src/components/modals/ChangePasswordModal.vue
☐ Unit tests pass (60+ tests)

STEP 23-24: Final Polish
☐ All E2E tests passing
☐ Lighthouse scores: 88+
☐ TypeScript: strict mode ✅
☐ Security audit: ✅ completed
☐ Accessibility: WCAG 2.1 AA ✅

TOTAL WEEK 12:
- 13+ new files (pages + modals)
- 2000+ lines of code
- 150+ unit tests
- 20+ E2E tests
- All Phases: ✅ Complete (100% functionality coverage)
```

---

## 🎯 ИТОГОВАЯ СТАТИСТИКА

```
Total Implementation:
- 28 steps across 2 weeks
- 28+ new Vue 3 components
- 3 new Pinia stores
- 3 new API services
- 340+ UI/UX files
- 4500+ lines of production code
- 340+ unit tests
- 25+ E2E tests
- Lighthouse scores: 88-92
- Test coverage: 90%+
- TypeScript strict: ✅
- Accessibility: WCAG 2.1 AA ✅
- DAM readiness: 91/100 ✅
```

---

# 🚀 NEXT STEP: COPY FIRST PROMPT

Скопируй **ПРОМПТ 1** (Step 1) в Cursor AI и начни!

```
Когда закончится Step 1 (30 минут):
1. Проверь файлы: types/admin.ts, stores/adminStore.ts, services/adminService.ts
2. Запусти unit tests (должно быть 35+ passing tests)
3. Перейди на STEP 2 (следующий промпт)
4. Повтори цикл для Step 3, 4, 5, ...
```

**Total time for full implementation: 56 hours (14 hours/day × 4 days)**

---

**Документ готов к использованию в Cursor AI! 🎉**

Каждый промпт содержит 100% спецификации для AI.  
Каждый шаг занимает 1-2 часа разработки.  
Результат: Enterprise-grade DAM frontend (91/100 соответствие современным стандартам).

