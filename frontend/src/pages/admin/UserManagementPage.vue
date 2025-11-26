<template>
  <div class="user-management">
    <!-- Toolbar -->
    <div class="user-management__toolbar">
      <Button
        v-if="canCreateUser"
        variant="primary"
        @click="showCreateModal = true"
        aria-label="Create new user"
      >
        <svg
          class="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 4v16m8-8H4"
          />
        </svg>
        Add User
      </Button>

      <div class="user-management__search">
        <Input
          v-model="searchQuery"
          type="search"
          placeholder="Search users..."
          @input="handleSearchDebounced"
          aria-label="Search users"
        />
      </div>

      <Select
        v-model="filters.status"
        :options="statusOptions"
        placeholder="All statuses"
        @change="handleFilterChange"
        aria-label="Filter by status"
      />

      <Select
        v-model="filters.role"
        :options="roleOptions"
        placeholder="All roles"
        @change="handleFilterChange"
        aria-label="Filter by role"
      />
    </div>

    <!-- Bulk Actions -->
    <div
      v-if="selectedUsers.length > 0"
      class="user-management__bulk-actions"
      role="toolbar"
      aria-label="Bulk actions"
    >
      <span class="user-management__bulk-count">
        {{ selectedUsers.length }} selected
      </span>
      <Button
        variant="secondary"
        size="sm"
        @click="handleBulkDelete"
        :disabled="isLoading"
        aria-label="Delete selected users"
      >
        Delete Selected
      </Button>
      <Button
        variant="secondary"
        size="sm"
        @click="showBulkRoleModal = true"
        :disabled="isLoading"
        aria-label="Change role for selected users"
      >
        Change Role
      </Button>
      <Button
        variant="ghost"
        size="sm"
        @click="clearSelection"
        aria-label="Clear selection"
      >
        Clear
      </Button>
    </div>

    <!-- Data Table -->
    <DataTable
      :items="paginatedUsers"
      :columns="tableColumns"
      :is-loading="isLoading"
      :selectable="true"
      :sortable="true"
      empty-state-text="No users found"
      aria-label="Users management table"
      @select="handleSelectUsers"
      @sort="handleSort"
    >
      <template #col-avatar="{ item }">
        <img
          :src="
            item.avatar_url ||
            `https://ui-avatars.com/api/?name=${encodeURIComponent(
              `${item.first_name}+${item.last_name}`
            )}&size=32&background=random`
          "
          :alt="`${item.first_name} ${item.last_name}`"
          class="user-avatar"
          loading="lazy"
        />
      </template>

      <template #col-name="{ item }">
        <div class="user-name">
          <span class="user-name__full">
            {{ item.first_name }} {{ item.last_name }}
          </span>
          <span class="user-name__username">@{{ item.username }}</span>
        </div>
      </template>

      <template #col-role="{ item }">
        <Select
          v-if="canEditUser"
          :model-value="item.role"
          :options="roleOptions"
          size="sm"
          @change="(role) => handleUpdateUserRole(item, role)"
          :aria-label="`Change role for ${item.first_name} ${item.last_name}`"
        />
        <Badge v-else :variant="getRoleBadgeVariant(item.role)">
          {{ formatRole(item.role) }}
        </Badge>
      </template>

      <template #col-is_active="{ item }">
        <Badge :variant="item.is_active ? 'success' : 'warning'">
          {{ item.is_active ? 'Active' : 'Inactive' }}
        </Badge>
      </template>

      <template #col-date_joined="{ item, value }">
        {{ formatDate(value) }}
      </template>

      <template #col-last_login="{ item, value }">
        {{ value ? formatDate(value) : 'Never' }}
      </template>

      <template #row-actions="{ item }">
        <div class="user-management__actions">
          <Button
            v-if="canEditUser"
            variant="ghost"
            size="sm"
            @click="handleEditUser(item)"
            aria-label="Edit user"
          >
            <svg
              class="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
              />
            </svg>
            Edit
          </Button>
          <Button
            v-if="canDeleteUser"
            variant="ghost"
            size="sm"
            :disabled="item.is_superuser && !authStore.user?.is_superuser"
            @click="handleDeleteUser(item)"
            :aria-label="`Delete user ${item.first_name} ${item.last_name}`"
          >
            <svg
              class="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
            Delete
          </Button>
        </div>
      </template>
    </DataTable>

    <!-- Pagination -->
    <Pagination
      :current-page="currentPage"
      :total-items="totalUsersCount"
      :page-size="pageSize"
      @page-change="handlePageChange"
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
      :message="'This action cannot be undone. Are you sure you want to delete this user?'"
      @confirm="confirmDeleteUser"
      @cancel="deletingUser = null"
    />

    <BulkRoleModal
      v-if="showBulkRoleModal"
      :selected-count="selectedUsers.length"
      @submit="handleBulkChangeRole"
      @close="showBulkRoleModal = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useAdminStore } from '@/stores/adminStore'
import { useNotificationStore } from '@/stores/notificationStore'
import { useDebounceFn } from '@vueuse/core'
import type {
  User,
  CreateUserRequest,
  UpdateUserRequest,
  GetUsersParams
} from '@/types/admin'
import Button from '@/components/Common/Button.vue'
import Input from '@/components/Common/Input.vue'
import Select from '@/components/Common/Select.vue'
import Badge from '@/components/Common/Badge.vue'
import DataTable from '@/components/Common/DataTable.vue'
import Pagination from '@/components/Common/Pagination.vue'
import Modal from '@/components/Common/Modal.vue'
import CreateUserModal from '@/components/admin/CreateUserModal.vue'
import EditUserModal from '@/components/admin/EditUserModal.vue'
import DeleteConfirmModal from '@/components/admin/DeleteConfirmModal.vue'
import BulkRoleModal from '@/components/admin/BulkRoleModal.vue'

// Hooks
const router = useRouter()
const authStore = useAuthStore()
const adminStore = useAdminStore()
const notificationStore = useNotificationStore()

// State
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(50)
const sortKey = ref<string>('')
const sortOrder = ref<'asc' | 'desc'>('asc')
const filters = ref<{ status: string; role: string }>({
  status: '',
  role: ''
})
const isLoading = ref(false)
const showCreateModal = ref(false)
const editingUser = ref<User | null>(null)
const deletingUser = ref<User | null>(null)
const showBulkRoleModal = ref(false)

// Computed
const canCreateUser = computed(() =>
  authStore.hasPermission.value('admin.user_create')
)
const canEditUser = computed(() =>
  authStore.hasPermission.value('admin.user_edit')
)
const canDeleteUser = computed(() =>
  authStore.hasPermission.value('admin.user_delete')
)

const selectedUsers = computed(() => {
  const ids = adminStore.selectedUsers
  return adminStore.users.filter((user) => ids.includes(user.id))
})

const paginatedUsers = computed(() => adminStore.users)
const totalUsersCount = computed(() => adminStore.totalUsersCount)

const tableColumns = [
  { key: 'avatar', label: '', width: 44, sortable: false },
  { key: 'name', label: 'Name', align: 'left', sortable: true },
  { key: 'email', label: 'Email', align: 'left', sortable: true },
  { key: 'role', label: 'Role', align: 'center', sortable: true },
  { key: 'is_active', label: 'Status', align: 'center', sortable: true },
  {
    key: 'date_joined',
    label: 'Created',
    align: 'left',
    sortable: true,
    format: 'date'
  },
  {
    key: 'last_login',
    label: 'Last Login',
    align: 'left',
    sortable: true,
    format: 'date'
  }
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
const fetchUsers = async (): Promise<void> => {
  isLoading.value = true
  try {
    const params: GetUsersParams = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value || undefined,
      status: filters.value.status || undefined,
      role: filters.value.role || undefined
    }
    await adminStore.fetchUsers(params)
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to load users. Please try again.'
    })
  } finally {
    isLoading.value = false
  }
}

const handleSearchDebounced = useDebounceFn(() => {
  currentPage.value = 1
  fetchUsers()
}, 300)

const handleFilterChange = (): void => {
  currentPage.value = 1
  fetchUsers()
}

const handleSort = (key: string, order: 'asc' | 'desc'): void => {
  sortKey.value = key
  sortOrder.value = order
  // Note: API-level sorting would need to be implemented
  // For now, this is handled on frontend
  currentPage.value = 1
  fetchUsers()
}

const handleSelectUsers = (users: User[]): void => {
  adminStore.selectUsers(users.map((u) => u.id))
}

const clearSelection = (): void => {
  adminStore.selectUsers([])
}

const handlePageChange = (page: number): void => {
  currentPage.value = page
  fetchUsers()
}

const handleCreateUser = async (data: CreateUserRequest): Promise<void> => {
  try {
    await adminStore.createUser(data)
    showCreateModal.value = false
    notificationStore.addNotification({
      type: 'success',
      title: 'Success',
      message: 'User created successfully'
    })
    await fetchUsers()
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to create user. Please try again.'
    })
  }
}

const handleEditUser = (user: User): void => {
  editingUser.value = user
}

const handleUpdateUser = async (data: UpdateUserRequest): Promise<void> => {
  if (!editingUser.value) return

  try {
    await adminStore.updateUser(editingUser.value.id, data)
    editingUser.value = null
    notificationStore.addNotification({
      type: 'success',
      title: 'Success',
      message: 'User updated successfully'
    })
    await fetchUsers()
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to update user. Please try again.'
    })
  }
}

const handleDeleteUser = (user: User): void => {
  deletingUser.value = user
}

const confirmDeleteUser = async (): Promise<void> => {
  if (!deletingUser.value) return

  try {
    await adminStore.deleteUser(deletingUser.value.id)
    deletingUser.value = null
    notificationStore.addNotification({
      type: 'success',
      title: 'Success',
      message: 'User deleted successfully'
    })
    await fetchUsers()
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to delete user. Please try again.'
    })
  }
}

const handleUpdateUserRole = async (
  user: User,
  role: string
): Promise<void> => {
  try {
    await adminStore.updateUser(user.id, { role: role as User['role'] })
    notificationStore.addNotification({
      type: 'success',
      title: 'Success',
      message: `User role updated to ${formatRole(role)}`
    })
    await fetchUsers()
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to update user role. Please try again.'
    })
  }
}

const handleBulkDelete = async (): Promise<void> => {
  if (
    !confirm(
      `Delete ${selectedUsers.value.length} users? This action cannot be undone.`
    )
  )
    return

  try {
    await adminStore.bulkUserOperation({
      ids: selectedUsers.value.map((u) => u.id),
      action: 'delete'
    })
    adminStore.selectUsers([])
    notificationStore.addNotification({
      type: 'success',
      title: 'Success',
      message: `${selectedUsers.value.length} users deleted successfully`
    })
    await fetchUsers()
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to delete users. Please try again.'
    })
  }
}

const handleBulkChangeRole = async (role: string): Promise<void> => {
  try {
    await adminStore.bulkUserOperation({
      ids: selectedUsers.value.map((u) => u.id),
      action: 'change_role',
      data: { role }
    })
    adminStore.selectUsers([])
    showBulkRoleModal.value = false
    notificationStore.addNotification({
      type: 'success',
      title: 'Success',
      message: `Role updated for ${selectedUsers.value.length} users`
    })
    await fetchUsers()
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to update user roles. Please try again.'
    })
  }
}

const formatRole = (role: string): string => {
  const roleMap: Record<string, string> = {
    admin: 'Administrator',
    editor: 'Editor',
    viewer: 'Viewer'
  }
  return roleMap[role] || role
}

const getRoleBadgeVariant = (role: string): 'success' | 'warning' | 'info' => {
  const variantMap: Record<string, 'success' | 'warning' | 'info'> = {
    admin: 'info',
    editor: 'success',
    viewer: 'warning'
  }
  return variantMap[role] || 'warning'
}

const formatDate = (date: string | null): string => {
  if (!date) return '—'
  return new Date(date).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// Lifecycle
onMounted(async () => {
  // Permission check
  if (!authStore.hasPermission.value('admin.user_manage')) {
    await router.push({ name: 'forbidden' })
    return
  }

  await fetchUsers()
})

// Watch for store changes
watch(
  () => adminStore.usersFilters,
  () => {
    filters.value = {
      status: adminStore.usersFilters.status,
      role: adminStore.usersFilters.role
    }
    searchQuery.value = adminStore.usersFilters.search
  },
  { immediate: true }
)
</script>

<style scoped lang="css">
.user-management {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
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
  background: var(--color-bg-1, #f9fafb);
  border-radius: var(--radius-base, 6px);
  border: 1px solid var(--color-border, #e5e7eb);
}

.user-management__bulk-count {
  font-weight: 500;
  color: var(--color-text, #111827);
  margin-right: auto;
}

.user-management__actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--color-border, #e5e7eb);
}

.user-name {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name__full {
  font-weight: 500;
  color: var(--color-text, #111827);
}

.user-name__username {
  font-size: var(--font-size-sm, 12px);
  color: var(--color-text-secondary, #6b7280);
}

/* Responsive */
@media (max-width: 768px) {
  .user-management {
    padding: 16px;
    gap: 16px;
  }

  .user-management__toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .user-management__search {
    width: 100%;
  }

  .user-management__bulk-actions {
    flex-wrap: wrap;
  }

  .user-management__actions {
    flex-direction: column;
  }
}
</style>



