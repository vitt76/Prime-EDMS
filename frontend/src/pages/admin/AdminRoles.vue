<template>
  <div class="admin-roles space-y-4 sm:space-y-6">
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-semibold text-gray-900">Роли и права доступа</h1>
        <p class="text-sm text-gray-600 mt-1">Управление ролями пользователей и разрешениями</p>
      </div>
      <button
        type="button"
        class="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-violet-600 hover:bg-violet-700 text-white font-medium text-sm rounded-lg shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2"
        @click="openCreateModal"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
        <span class="hidden sm:inline">Создать роль</span>
        <span class="sm:hidden">Создать</span>
      </button>
    </div>

    <!-- Roles Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <div
        v-for="role in roles"
        :key="role.id"
        class="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md hover:border-violet-300 transition-all"
      >
        <div class="p-5">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-3">
              <div
                :class="[
                  'w-10 h-10 rounded-lg flex items-center justify-center',
                  role.color ? `bg-${role.color}-100` : 'bg-violet-100'
                ]"
                :style="{ backgroundColor: getRoleColor(role.id) + '20' }"
              >
                <svg
                  class="w-5 h-5"
                  :style="{ color: getRoleColor(role.id) }"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <h3 class="font-semibold text-gray-900">{{ role.label }}</h3>
                <p class="text-xs text-gray-500">{{ role.users_count || 0 }} пользователей</p>
              </div>
            </div>
            <div class="flex items-center gap-1">
              <button
                type="button"
                class="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                title="Редактировать"
                @click="editRole(role)"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              <button
                v-if="!role.is_system"
                type="button"
                class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="Удалить"
                @click="confirmDelete(role)"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Description -->
          <p v-if="role.description" class="mt-3 text-sm text-gray-600">
            {{ role.description }}
          </p>

          <!-- Permissions Preview -->
          <div class="mt-4">
            <p class="text-xs font-medium text-gray-500 mb-2">Разрешения ({{ role.permissions.length }})</p>
            <div class="flex flex-wrap gap-1">
              <span
                v-for="perm in role.permissions.slice(0, 4)"
                :key="perm"
                class="px-2 py-0.5 text-[10px] font-medium bg-gray-100 text-gray-600 rounded"
              >
                {{ getPermissionLabel(perm) }}
              </span>
              <span
                v-if="role.permissions.length > 4"
                class="px-2 py-0.5 text-[10px] font-medium bg-gray-100 text-gray-500 rounded"
              >
                +{{ role.permissions.length - 4 }}
              </span>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-5 py-3 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
          <span
            v-if="role.is_system"
            class="px-2 py-0.5 text-[10px] font-medium bg-amber-100 text-amber-700 rounded"
          >
            Системная роль
          </span>
          <span v-else class="text-xs text-gray-400">
            Создана {{ formatDate(role.created_at) }}
          </span>
          <button
            type="button"
            class="text-xs text-violet-600 hover:text-violet-700 font-medium"
            @click="editRole(role)"
          >
            Настроить →
          </button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Role Modal -->
    <Teleport to="body">
      <div
        v-if="showModal"
        class="fixed inset-0 z-50 flex items-center justify-center"
      >
        <div class="absolute inset-0 bg-black/50" @click="closeModal" />
        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-hidden flex flex-col">
          <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-900">
              {{ editingRole ? 'Редактировать роль' : 'Создать роль' }}
            </h2>
            <button
              type="button"
              class="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              @click="closeModal"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div class="flex-1 overflow-y-auto p-6 space-y-6">
            <!-- Basic Info -->
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Название роли</label>
                <input
                  v-model="roleForm.label"
                  type="text"
                  required
                  placeholder="Например: Редактор контента"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Описание</label>
                <textarea
                  v-model="roleForm.description"
                  rows="2"
                  placeholder="Краткое описание роли и её назначения..."
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent resize-none"
                />
              </div>
            </div>

            <!-- Permissions -->
            <div>
              <h3 class="text-sm font-semibold text-gray-900 mb-3">Разрешения</h3>
              <div class="space-y-4">
                <div
                  v-for="(perms, namespace) in groupedPermissions"
                  :key="namespace"
                  class="border border-gray-200 rounded-lg overflow-hidden"
                >
                  <div class="px-4 py-2 bg-gray-50 border-b border-gray-200 flex items-center justify-between">
                    <span class="text-sm font-medium text-gray-700 uppercase">{{ namespace }}</span>
                    <button
                      type="button"
                      class="text-xs text-violet-600 hover:text-violet-700"
                      @click="toggleNamespace(namespace)"
                    >
                      {{ isNamespaceSelected(namespace) ? 'Снять все' : 'Выбрать все' }}
                    </button>
                  </div>
                  <div class="p-3 grid grid-cols-2 gap-2">
                    <label
                      v-for="perm in perms"
                      :key="perm.name"
                      class="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-50 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        :checked="roleForm.permissions.includes(perm.name)"
                        @change="togglePermission(perm.name)"
                        class="w-4 h-4 text-violet-600 border-gray-300 rounded focus:ring-violet-500"
                      />
                      <span class="text-sm text-gray-700">{{ perm.label }}</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="px-6 py-4 border-t border-gray-100 flex gap-3">
            <button
              type="button"
              class="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
              @click="closeModal"
            >
              Отмена
            </button>
            <button
              type="button"
              class="flex-1 px-4 py-2.5 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700 transition-colors"
              @click="saveRole"
            >
              {{ editingRole ? 'Сохранить' : 'Создать' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Delete Confirmation Modal -->
    <Teleport to="body">
      <div
        v-if="showDeleteModal && deletingRole"
        class="fixed inset-0 z-50 flex items-center justify-center"
      >
        <div class="absolute inset-0 bg-black/50" @click="showDeleteModal = false" />
        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-md mx-4 p-6">
          <div class="flex items-center gap-4 mb-4">
            <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div>
              <h2 class="text-lg font-semibold text-gray-900">Удалить роль?</h2>
              <p class="text-sm text-gray-500">Это действие нельзя отменить</p>
            </div>
          </div>
          
          <div class="p-4 bg-gray-50 rounded-lg mb-6">
            <p class="text-sm font-medium text-gray-900">{{ deletingRole.label }}</p>
            <p class="text-sm text-gray-500">{{ deletingRole.users_count || 0 }} пользователей с этой ролью</p>
          </div>

          <div class="flex gap-3">
            <button
              type="button"
              class="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
              @click="showDeleteModal = false"
            >
              Отмена
            </button>
            <button
              type="button"
              class="flex-1 px-4 py-2.5 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
              @click="deleteRole"
            >
              Удалить
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Toast Notification -->
    <Teleport to="body">
      <Transition name="toast">
        <div
          v-if="toast.show"
          :class="[
            'fixed bottom-4 right-4 z-50 flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg',
            toast.type === 'success' ? 'bg-emerald-600 text-white' : 'bg-red-600 text-white'
          ]"
        >
          <svg v-if="toast.type === 'success'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="text-sm font-medium">{{ toast.message }}</span>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { adminService } from '@/services/adminService'

interface Permission {
  id: number
  namespace: string
  name: string
  label: string
}

interface Role {
  id: number
  label: string
  description?: string
  permissions: string[]
  users_count?: number
  is_system?: boolean
  created_at?: string
  color?: string
}

// ═══════════════════════════════════════════════════════════════════════════════
// State
// ═══════════════════════════════════════════════════════════════════════════════
const showModal = ref(false)
const showDeleteModal = ref(false)
const editingRole = ref<Role | null>(null)
const deletingRole = ref<Role | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)

const toast = reactive({
  show: false,
  message: '',
  type: 'success' as 'success' | 'error'
})

const roleForm = ref({
  label: '',
  description: '',
  permissions: [] as string[]
})

const roleColors = ['#8B5CF6', '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#EC4899']

// Permissions (static list - Mayan permissions are managed separately)
const permissions = ref<Permission[]>([
  { id: 1, namespace: 'Документы', name: 'documents.view', label: 'Просмотр документов' },
  { id: 2, namespace: 'Документы', name: 'documents.create', label: 'Создание документов' },
  { id: 3, namespace: 'Документы', name: 'documents.edit', label: 'Редактирование документов' },
  { id: 4, namespace: 'Документы', name: 'documents.delete', label: 'Удаление документов' },
  { id: 5, namespace: 'Документы', name: 'documents.download', label: 'Скачивание документов' },
  { id: 6, namespace: 'Метаданные', name: 'metadata.view', label: 'Просмотр метаданных' },
  { id: 7, namespace: 'Метаданные', name: 'metadata.edit', label: 'Редактирование метаданных' },
  { id: 8, namespace: 'Метаданные', name: 'metadata.manage', label: 'Управление схемами' },
  { id: 9, namespace: 'Пользователи', name: 'users.view', label: 'Просмотр пользователей' },
  { id: 10, namespace: 'Пользователи', name: 'users.manage', label: 'Управление пользователями' },
  { id: 11, namespace: 'Пользователи', name: 'users.invite', label: 'Приглашение пользователей' },
  { id: 12, namespace: 'Распространение', name: 'sharing.create', label: 'Создание ссылок' },
  { id: 13, namespace: 'Распространение', name: 'sharing.manage', label: 'Управление публикациями' },
  { id: 14, namespace: 'Система', name: 'system.settings', label: 'Настройки системы' },
  { id: 15, namespace: 'Система', name: 'system.logs', label: 'Просмотр логов' }
])

// Roles (groups) from real API
const roles = ref<Role[]>([])

// ═══════════════════════════════════════════════════════════════════════════════
// Data Loading
// ═══════════════════════════════════════════════════════════════════════════════
async function loadGroups() {
  isLoading.value = true
  error.value = null
  
  try {
    const response = await adminService.getGroups({ page_size: 100 })
    
    // Map Mayan groups to Role interface
    roles.value = response.results.map(group => ({
      id: group.id,
      label: group.name,
      description: '',
      permissions: [], // Mayan manages permissions separately
      users_count: 0,
      is_system: false
    }))
    
    console.log('[AdminRoles] Loaded groups:', roles.value.length)
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : 'Ошибка загрузки групп'
    showToast(error.value, 'error')
    console.error('[AdminRoles] Failed to load groups:', err)
  } finally {
    isLoading.value = false
  }
}

// Initial load
onMounted(() => {
  loadGroups()
})

// ═══════════════════════════════════════════════════════════════════════════════
// Computed
// ═══════════════════════════════════════════════════════════════════════════════
const groupedPermissions = computed(() => {
  const groups: Record<string, Permission[]> = {}
  permissions.value.forEach(perm => {
    if (!groups[perm.namespace]) {
      groups[perm.namespace] = []
    }
    groups[perm.namespace].push(perm)
  })
  return groups
})

// ═══════════════════════════════════════════════════════════════════════════════
// Methods
// ═══════════════════════════════════════════════════════════════════════════════
function showToast(message: string, type: 'success' | 'error' = 'success') {
  toast.message = message
  toast.type = type
  toast.show = true
  setTimeout(() => {
    toast.show = false
  }, 3000)
}

function getRoleColor(roleId: number): string {
  return roleColors[roleId % roleColors.length]
}

function getPermissionLabel(permName: string): string {
  const perm = permissions.value.find(p => p.name === permName)
  return perm?.label.split(' ')[0] || permName
}

function formatDate(iso?: string): string {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('ru-RU')
}

function openCreateModal(): void {
  editingRole.value = null
  roleForm.value = {
    label: '',
    description: '',
    permissions: []
  }
  showModal.value = true
}

function editRole(role: Role): void {
  editingRole.value = role
  roleForm.value = {
    label: role.label,
    description: role.description || '',
    permissions: [...role.permissions]
  }
  showModal.value = true
}

function closeModal(): void {
  showModal.value = false
  editingRole.value = null
}

function togglePermission(permName: string): void {
  const idx = roleForm.value.permissions.indexOf(permName)
  if (idx > -1) {
    roleForm.value.permissions.splice(idx, 1)
  } else {
    roleForm.value.permissions.push(permName)
  }
}

function isNamespaceSelected(namespace: string): boolean {
  const nsPerms = groupedPermissions.value[namespace]
  return nsPerms.every(p => roleForm.value.permissions.includes(p.name))
}

function toggleNamespace(namespace: string): void {
  const nsPerms = groupedPermissions.value[namespace]
  if (isNamespaceSelected(namespace)) {
    nsPerms.forEach(p => {
      const idx = roleForm.value.permissions.indexOf(p.name)
      if (idx > -1) roleForm.value.permissions.splice(idx, 1)
    })
  } else {
    nsPerms.forEach(p => {
      if (!roleForm.value.permissions.includes(p.name)) {
        roleForm.value.permissions.push(p.name)
      }
    })
  }
}

async function saveRole(): Promise<void> {
  try {
    if (editingRole.value) {
      // Update existing group
      await adminService.updateGroup(editingRole.value.id, {
        name: roleForm.value.label
      })
      showToast('Группа успешно обновлена')
    } else {
      // Create new group
      await adminService.createGroup({
        name: roleForm.value.label
      })
      showToast('Группа успешно создана')
    }
    
    closeModal()
    await loadGroups() // Reload list
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : 'Ошибка сохранения группы'
    showToast(errorMsg, 'error')
  }
}

function confirmDelete(role: Role): void {
  deletingRole.value = role
  showDeleteModal.value = true
}

async function deleteRole(): Promise<void> {
  if (!deletingRole.value) return
  
  try {
    await adminService.deleteGroup(deletingRole.value.id)
    
    showDeleteModal.value = false
    deletingRole.value = null
    showToast('Группа удалена')
    
    await loadGroups() // Reload list
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : 'Ошибка удаления группы'
    showToast(errorMsg, 'error')
  }
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(100px);
}
</style>
