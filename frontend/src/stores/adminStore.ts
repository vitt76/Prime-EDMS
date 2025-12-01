import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { adminService } from '@/services/adminService'
import { formatApiError } from '@/utils/errors'
import type {
  User,
  CreateUserRequest,
  UpdateUserRequest,
  GetUsersParams,
  BulkUserOperationRequest,
  BulkUserOperationResponse,
  MetadataSchema,
  CreateMetadataSchemaRequest,
  UpdateMetadataSchemaRequest,
  GetSchemasParams,
  Workflow,
  CreateWorkflowRequest,
  UpdateWorkflowRequest,
  GetWorkflowsParams,
  WorkflowNode,
  PaginatedResponse
} from '@/types/admin'
import { useAuthStore } from './authStore'

const CACHE_TTL = 5 * 60 * 1000 // 5 minutes in milliseconds
const MAX_BULK_OPERATION_SIZE = 100

export const useAdminStore = defineStore(
  'admin',
  () => {
    const authStore = useAuthStore()

    // Users state
    const users = ref<User[]>([])
    const totalUsersCount = ref(0)
    const selectedUsers = ref<number[]>([])
    const usersFilters = ref<{
      role: string
      status: string
      search: string
    }>({
      role: '',
      status: '',
      search: ''
    })

    // Metadata Schemas state
    const schemas = ref<MetadataSchema[]>([])
    const totalSchemasCount = ref(0)
    const currentSchema = ref<MetadataSchema | null>(null)

    // Workflows state
    const workflows = ref<Workflow[]>([])
    const totalWorkflowsCount = ref(0)
    const currentWorkflow = ref<Workflow | null>(null)
    const selectedNode = ref<WorkflowNode | null>(null)

    // Global state
    const isLoading = ref(false)
    const error = ref<string | null>(null)
    const lastFetchTime = ref<number | null>(null)

    // Computed properties - Permissions
    const canCreateUser = computed(() => {
      return authStore.hasPermission.value('admin.user_create')
    })

    const canEditUser = computed(() => {
      return authStore.hasPermission.value('admin.user_edit')
    })

    const canDeleteUser = computed(() => {
      return authStore.hasPermission.value('admin.user_delete')
    })

    const canManageSchemas = computed(() => {
      return authStore.hasPermission.value('admin.schema_manage')
    })

    const canManageWorkflows = computed(() => {
      return authStore.hasPermission.value('admin.workflow_manage')
    })

    // Computed properties - Filtered data
    const filteredUsers = computed(() => {
      let result = users.value

      if (usersFilters.value.role) {
        result = result.filter((user) => user.role === usersFilters.value.role)
      }

      if (usersFilters.value.status) {
        if (usersFilters.value.status === 'active') {
          result = result.filter((user) => user.is_active)
        } else if (usersFilters.value.status === 'inactive') {
          result = result.filter((user) => !user.is_active)
        }
      }

      if (usersFilters.value.search) {
        const searchLower = usersFilters.value.search.toLowerCase()
        result = result.filter(
          (user) =>
            user.username.toLowerCase().includes(searchLower) ||
            user.email.toLowerCase().includes(searchLower) ||
            user.first_name.toLowerCase().includes(searchLower) ||
            user.last_name.toLowerCase().includes(searchLower)
        )
      }

      return result
    })

    const selectedUsersCount = computed(() => selectedUsers.value.length)

    const hasUnsavedChanges = computed(() => {
      // Track if any form has unsaved changes
      // This would be set by form components
      return false // Placeholder - implement based on form state
    })

    // Actions - Users
    async function fetchUsers(params?: GetUsersParams): Promise<void> {
      // Check cache
      const now = Date.now()
      if (
        lastFetchTime.value &&
        now - lastFetchTime.value < CACHE_TTL &&
        users.value.length > 0 &&
        !params
      ) {
        return // Use cached data
      }

      isLoading.value = true
      error.value = null

      try {
        const queryParams: GetUsersParams = {
          ...usersFilters.value,
          ...params
        }

        const response: PaginatedResponse<User> = await adminService.getUsers(queryParams)

        users.value = response.results
        totalUsersCount.value = response.count
        lastFetchTime.value = now
      } catch (err) {
        error.value = formatApiError(err)
        users.value = []
        totalUsersCount.value = 0
        throw err
      } finally {
        isLoading.value = false
      }
    }

    async function createUser(userData: CreateUserRequest): Promise<User> {
      isLoading.value = true
      error.value = null

      try {
        const newUser = await adminService.createUser(userData)
        // Optimistic update
        users.value.push(newUser)
        totalUsersCount.value++
        lastFetchTime.value = null // Invalidate cache
        return newUser
      } catch (err) {
        error.value = formatApiError(err)
        throw err
      } finally {
        isLoading.value = false
      }
    }

    async function updateUser(id: number, data: UpdateUserRequest): Promise<User> {
      isLoading.value = true
      error.value = null

      try {
        const updatedUser = await adminService.updateUser(id, data)
        // Update in array
        const index = users.value.findIndex((u) => u.id === id)
        if (index !== -1) {
          users.value[index] = updatedUser
        }
        lastFetchTime.value = null // Invalidate cache
        return updatedUser
      } catch (err) {
        error.value = formatApiError(err)
        throw err
      } finally {
        isLoading.value = false
      }
    }

    async function deleteUser(id: number): Promise<void> {
      isLoading.value = true
      error.value = null

      try {
        await adminService.deleteUser(id)
        // Remove from array
        users.value = users.value.filter((u) => u.id !== id)
        totalUsersCount.value--
        selectedUsers.value = selectedUsers.value.filter((uid) => uid !== id)
        lastFetchTime.value = null // Invalidate cache
      } catch (err) {
        error.value = formatApiError(err)
        throw err
      } finally {
        isLoading.value = false
      }
    }

    async function bulkUserOperation(
      operation: BulkUserOperationRequest
    ): Promise<BulkUserOperationResponse> {
      // Validate max size
      if (operation.ids.length > MAX_BULK_OPERATION_SIZE) {
        throw new Error(
          `Maximum ${MAX_BULK_OPERATION_SIZE} users allowed per bulk operation`
        )
      }

      isLoading.value = true
      error.value = null

      try {
        const response = await adminService.bulkUserOperation(operation)
        // Refresh users list
        await fetchUsers()
        return response
      } catch (err) {
        error.value = formatApiError(err)
        throw err
      } finally {
        isLoading.value = false
      }
    }

    function selectUsers(ids: number[]): void {
      selectedUsers.value = ids
    }

    function clearUserSelection(): void {
      selectedUsers.value = []
    }

    function setUsersFilters(filters: Partial<GetUsersParams>): void {
      usersFilters.value = {
        ...usersFilters.value,
        ...filters
      }
    }

    function clearUsersFilters(): void {
      usersFilters.value = {
        role: '',
        status: '',
        search: ''
      }
    }

    // Actions - Metadata Schemas
    async function fetchSchemas(params?: GetSchemasParams): Promise<void> {
      isLoading.value = true
      error.value = null

      try {
        const response: PaginatedResponse<MetadataSchema> =
          await adminService.getSchemas(params)

        schemas.value = response.results
        totalSchemasCount.value = response.count
      } catch (err) {
        error.value = formatApiError(err)
        schemas.value = []
        totalSchemasCount.value = 0
        throw err
      } finally {
        isLoading.value = false
      }
    }

    async function getSchema(id: number): Promise<MetadataSchema> {
      isLoading.value = true
      error.value = null

      try {
        const schema = await adminService.getSchema(id)
        currentSchema.value = schema
        return schema
      } catch (err) {
        error.value = formatApiError(err)
        currentSchema.value = null
        throw err
      } finally {
        isLoading.value = false
      }
    }

    async function createSchema(
      data: CreateMetadataSchemaRequest
    ): Promise<MetadataSchema> {
      isLoading.value = true
      error.value = null

      try {
        const newSchema = await adminService.createSchema(data)
        schemas.value.push(newSchema)
        totalSchemasCount.value++
        return newSchema
      } catch (err) {
        error.value = formatApiError(err)
        throw err
      } finally {
        isLoading.value = false
      }
    }

    async function updateSchema(
      id: number,
      data: UpdateMetadataSchemaRequest
    ): Promise<MetadataSchema> {
      isLoading.value = true
      error.value = null

      try {
        const updatedSchema = await adminService.updateSchema(id, data)
        const index = schemas.value.findIndex((s) => s.id === id)
        if (index !== -1) {
          schemas.value[index] = updatedSchema
        }
        if (currentSchema.value?.id === id) {
          currentSchema.value = updatedSchema
        }
        return updatedSchema
      } catch (err) {
        error.value = formatApiError(err)
        throw err
      } finally {
        isLoading.value = false
      }
    }

    async function deleteSchema(id: number): Promise<void> {
      isLoading.value = true
      error.value = null

      try {
        await adminService.deleteSchema(id)
        schemas.value = schemas.value.filter((s) => s.id !== id)
        totalSchemasCount.value--
        if (currentSchema.value?.id === id) {
          currentSchema.value = null
        }
      } catch (err) {
        error.value = formatApiError(err)
        throw err
      } finally {
        isLoading.value = false
      }
    }

    function setCurrentSchema(schema: MetadataSchema | null): void {
      currentSchema.value = schema
    }

    // Actions - Workflows
    async function fetchWorkflows(params?: GetWorkflowsParams): Promise<void> {
      isLoading.value = true
      error.value = null

      try {
        const response: PaginatedResponse<Workflow> =
          await adminService.getWorkflows(params)

        workflows.value = response.results
        totalWorkflowsCount.value = response.count
      } catch (err) {
        error.value = formatApiError(err)
        workflows.value = []
        totalWorkflowsCount.value = 0
        throw err
      } finally {
        isLoading.value = false
      }
    }

    async function getWorkflow(id: number): Promise<Workflow> {
      isLoading.value = true
      error.value = null

      try {
        const workflow = await adminService.getWorkflow(id)
        currentWorkflow.value = workflow
        return workflow
      } catch (err) {
        error.value = formatApiError(err)
        currentWorkflow.value = null
        throw err
      } finally {
        isLoading.value = false
      }
    }

    async function createWorkflow(
      data: CreateWorkflowRequest
    ): Promise<Workflow> {
      isLoading.value = true
      error.value = null

      try {
        const newWorkflow = await adminService.createWorkflow(data)
        workflows.value.push(newWorkflow)
        totalWorkflowsCount.value++
        return newWorkflow
      } catch (err) {
        error.value = formatApiError(err)
        throw err
      } finally {
        isLoading.value = false
      }
    }

    async function updateWorkflow(
      id: number,
      data: UpdateWorkflowRequest
    ): Promise<Workflow> {
      isLoading.value = true
      error.value = null

      try {
        const updatedWorkflow = await adminService.updateWorkflow(id, data)
        const index = workflows.value.findIndex((w) => w.id === id)
        if (index !== -1) {
          workflows.value[index] = updatedWorkflow
        }
        if (currentWorkflow.value?.id === id) {
          currentWorkflow.value = updatedWorkflow
        }
        return updatedWorkflow
      } catch (err) {
        error.value = formatApiError(err)
        throw err
      } finally {
        isLoading.value = false
      }
    }

    async function deleteWorkflow(id: number): Promise<void> {
      isLoading.value = true
      error.value = null

      try {
        await adminService.deleteWorkflow(id)
        workflows.value = workflows.value.filter((w) => w.id !== id)
        totalWorkflowsCount.value--
        if (currentWorkflow.value?.id === id) {
          currentWorkflow.value = null
        }
      } catch (err) {
        error.value = formatApiError(err)
        throw err
      } finally {
        isLoading.value = false
      }
    }

    function setCurrentWorkflow(workflow: Workflow | null): void {
      currentWorkflow.value = workflow
    }

    function setSelectedNode(node: WorkflowNode | null): void {
      selectedNode.value = node
    }

    // Utility actions
    function clearError(): void {
      error.value = null
    }

    function invalidateCache(): void {
      lastFetchTime.value = null
    }

    return {
      // State - Users
      users,
      totalUsersCount,
      selectedUsers,
      usersFilters,

      // State - Schemas
      schemas,
      totalSchemasCount,
      currentSchema,

      // State - Workflows
      workflows,
      totalWorkflowsCount,
      currentWorkflow,
      selectedNode,

      // Global state
      isLoading,
      error,
      lastFetchTime,

      // Computed - Permissions
      canCreateUser,
      canEditUser,
      canDeleteUser,
      canManageSchemas,
      canManageWorkflows,

      // Computed - Data
      filteredUsers,
      selectedUsersCount,
      hasUnsavedChanges,

      // Actions - Users
      fetchUsers,
      createUser,
      updateUser,
      deleteUser,
      bulkUserOperation,
      selectUsers,
      clearUserSelection,
      setUsersFilters,
      clearUsersFilters,

      // Actions - Schemas
      fetchSchemas,
      getSchema,
      createSchema,
      updateSchema,
      deleteSchema,
      setCurrentSchema,

      // Actions - Workflows
      fetchWorkflows,
      getWorkflow,
      createWorkflow,
      updateWorkflow,
      deleteWorkflow,
      setCurrentWorkflow,
      setSelectedNode,

      // Utility actions
      clearError,
      invalidateCache
    }
  },
  {
    persist: {
      paths: ['usersFilters'] // Only persist filters, not actual data
    }
  }
)

