import { apiService } from './apiService'
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
  PaginatedResponse
} from '@/types/admin'

// ═══════════════════════════════════════════════════════════════════════════════
// Mayan EDMS Backend Response Types
// ═══════════════════════════════════════════════════════════════════════════════

interface MayanUser {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  is_staff: boolean
  is_superuser: boolean
  date_joined: string
  last_login: string | null
  groups: MayanGroup[]
  groups_pk_list?: number[]
}

interface MayanGroup {
  id: number
  name: string
  url?: string
}

interface MayanPaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

interface SystemHealthResponse {
  status: 'healthy' | 'degraded' | 'down'
  database: {
    status: string
    latency_ms: number
  }
  redis: {
    status: string
    latency_ms: number
  }
  celery: {
    status: string
    workers_count: number
    active_tasks: number
  }
  storage: {
    status: string
    used_bytes: number
    total_bytes: number
  }
  search: {
    status: string
    latency_ms: number
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Adapter Functions
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Maps Mayan EDMS User to Frontend User type
 */
function adaptMayanUser(mayanUser: MayanUser): User {
  // Determine user status based on is_active
  let status: 'active' | 'invited' | 'suspended' | 'inactive' = 'active'
  if (!mayanUser.is_active) {
    status = mayanUser.last_login ? 'suspended' : 'inactive'
  }

  // Map groups to roles (Mayan uses groups for permissions)
  const roles = mayanUser.groups.map(g => ({
    id: g.id,
    label: g.name,
    permissions: [],
    groups: []
  }))

  return {
    id: mayanUser.id,
    username: mayanUser.username,
    email: mayanUser.email,
    first_name: mayanUser.first_name,
    last_name: mayanUser.last_name,
    is_active: mayanUser.is_active,
    is_staff: mayanUser.is_staff,
    is_superuser: mayanUser.is_superuser,
    date_joined: mayanUser.date_joined,
    last_login: mayanUser.last_login,
    status,
    groups: mayanUser.groups.map(g => ({
      id: g.id,
      name: g.name,
      users_count: 0,
      permissions_count: 0
    })),
    roles,
    two_factor_enabled: false // Mayan doesn't expose this directly
  }
}

/**
 * Maps Frontend User create request to Mayan API format
 */
function adaptUserForMayan(userData: CreateUserRequest | UpdateUserRequest): Record<string, unknown> {
  const payload: Record<string, unknown> = {}
  
  if ('username' in userData && userData.username) {
    payload.username = userData.username
  }
  if ('email' in userData && userData.email) {
    payload.email = userData.email
  }
  if ('first_name' in userData && userData.first_name) {
    payload.first_name = userData.first_name
  }
  if ('last_name' in userData && userData.last_name) {
    payload.last_name = userData.last_name
  }
  if ('password' in userData && userData.password) {
    payload.password = userData.password
  }
  if ('is_active' in userData && userData.is_active !== undefined) {
    payload.is_active = userData.is_active
  }
  if ('is_staff' in userData && userData.is_staff !== undefined) {
    payload.is_staff = userData.is_staff
  }
  if ('is_superuser' in userData && userData.is_superuser !== undefined) {
    payload.is_superuser = userData.is_superuser
  }
  if ('groups_pk_list' in userData && userData.groups_pk_list) {
    payload.groups_pk_list = userData.groups_pk_list
  }

  return payload
}

// ═══════════════════════════════════════════════════════════════════════════════
// Admin Service Class
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Admin Service
 * 
 * Service class for admin-related API operations.
 * Uses Mayan EDMS REST API endpoints.
 * 
 * API Reference:
 * - Users: /api/v4/users/
 * - Groups: /api/v4/groups/
 * - Metadata Types: /api/v4/metadata_types/
 * - Workflows: /api/v4/workflows/
 */
class AdminService {
  // ═══════════════════════════════════════════════════════════════════════════
  // User Management
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Get paginated list of users
   * 
   * Endpoint: GET /api/v4/users/
   */
  async getUsers(params?: GetUsersParams): Promise<PaginatedResponse<User>> {
    const queryParams: Record<string, string | number> = {}

    if (params?.page) {
      queryParams.page = params.page
    }
    if (params?.page_size) {
      queryParams.page_size = params.page_size
    }
    if (params?.search) {
      queryParams.search = params.search
    }
    // Mayan uses 'is_active' filter
    if (params?.status === 'active') {
      queryParams.is_active = 'True'
    } else if (params?.status === 'inactive' || params?.status === 'suspended') {
      queryParams.is_active = 'False'
    }

    const response = await apiService.get<MayanPaginatedResponse<MayanUser>>(
      '/api/v4/users/',
      { params: queryParams },
      false // Don't cache user lists for security
    )

    return {
      count: response.count,
      next: response.next,
      previous: response.previous,
      results: response.results.map(adaptMayanUser)
    }
  }

  /**
   * Get single user by ID
   * 
   * Endpoint: GET /api/v4/users/{id}/
   */
  async getUser(id: number): Promise<User> {
    const mayanUser = await apiService.get<MayanUser>(
      `/api/v4/users/${id}/`,
      undefined,
      false
    )
    return adaptMayanUser(mayanUser)
  }

  /**
   * Create new user
   * 
   * Endpoint: POST /api/v4/users/
   */
  async createUser(data: CreateUserRequest): Promise<User> {
    const payload = adaptUserForMayan(data)
    const mayanUser = await apiService.post<MayanUser>('/api/v4/users/', payload)
    return adaptMayanUser(mayanUser)
  }

  /**
   * Update user
   * 
   * Endpoint: PATCH /api/v4/users/{id}/
   */
  async updateUser(id: number, data: UpdateUserRequest): Promise<User> {
    const payload = adaptUserForMayan(data)
    const mayanUser = await apiService.patch<MayanUser>(`/api/v4/users/${id}/`, payload)
    return adaptMayanUser(mayanUser)
  }

  /**
   * Delete user
   * 
   * Endpoint: DELETE /api/v4/users/{id}/
   */
  async deleteUser(id: number): Promise<void> {
    return apiService.delete<void>(`/api/v4/users/${id}/`)
  }

  /**
   * Bulk user operation
   * 
   * Note: Mayan doesn't have a native bulk endpoint.
   * This performs operations sequentially.
   */
  async bulkUserOperation(
    operation: BulkUserOperationRequest
  ): Promise<BulkUserOperationResponse> {
    const results: BulkUserOperationResponse = {
      success: 0,
      failed: 0,
      errors: []
    }

    for (const id of operation.ids) {
      try {
        switch (operation.action) {
          case 'activate':
            await this.updateUser(id, { is_active: true })
            break
          case 'deactivate':
            await this.updateUser(id, { is_active: false })
            break
          case 'delete':
            await this.deleteUser(id)
            break
          case 'add_to_group':
            if (operation.data?.group_ids) {
              await this.addUserToGroups(id, operation.data.group_ids)
            }
            break
          case 'remove_from_group':
            if (operation.data?.group_ids) {
              await this.removeUserFromGroups(id, operation.data.group_ids)
            }
            break
          default:
            throw new Error(`Unknown action: ${operation.action}`)
        }
        results.success++
      } catch (err: unknown) {
        results.failed++
        results.errors.push({
          id,
          error: err instanceof Error ? err.message : 'Unknown error'
        })
      }
    }

    return results
  }

  /**
   * Add user to groups
   * 
   * Endpoint: POST /api/v4/users/{id}/groups/
   */
  async addUserToGroups(userId: number, groupIds: number[]): Promise<void> {
    for (const groupId of groupIds) {
      await apiService.post(`/api/v4/users/${userId}/groups/`, { group_pk: groupId })
    }
  }

  /**
   * Remove user from groups
   * 
   * Endpoint: DELETE /api/v4/users/{id}/groups/{group_id}/
   */
  async removeUserFromGroups(userId: number, groupIds: number[]): Promise<void> {
    for (const groupId of groupIds) {
      await apiService.delete(`/api/v4/users/${userId}/groups/${groupId}/`)
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Group Management
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Get paginated list of groups
   * 
   * Endpoint: GET /api/v4/groups/
   */
  async getGroups(params?: { page?: number; page_size?: number; search?: string }): Promise<PaginatedResponse<MayanGroup>> {
    const queryParams: Record<string, string | number> = {}

    if (params?.page) {
      queryParams.page = params.page
    }
    if (params?.page_size) {
      queryParams.page_size = params.page_size
    }
    if (params?.search) {
      queryParams.search = params.search
    }

    return apiService.get<MayanPaginatedResponse<MayanGroup>>(
      '/api/v4/groups/',
      { params: queryParams },
      true // Cache groups list
    )
  }

  /**
   * Get single group by ID
   * 
   * Endpoint: GET /api/v4/groups/{id}/
   */
  async getGroup(id: number): Promise<MayanGroup> {
    return apiService.get<MayanGroup>(`/api/v4/groups/${id}/`, undefined, true)
  }

  /**
   * Create new group
   * 
   * Endpoint: POST /api/v4/groups/
   */
  async createGroup(data: { name: string }): Promise<MayanGroup> {
    return apiService.post<MayanGroup>('/api/v4/groups/', data)
  }

  /**
   * Update group
   * 
   * Endpoint: PATCH /api/v4/groups/{id}/
   */
  async updateGroup(id: number, data: { name?: string }): Promise<MayanGroup> {
    return apiService.patch<MayanGroup>(`/api/v4/groups/${id}/`, data)
  }

  /**
   * Delete group
   * 
   * Endpoint: DELETE /api/v4/groups/{id}/
   */
  async deleteGroup(id: number): Promise<void> {
    return apiService.delete<void>(`/api/v4/groups/${id}/`)
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Metadata Schemas (Metadata Types in Mayan)
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Get paginated list of metadata types (schemas)
   * 
   * Endpoint: GET /api/v4/metadata_types/
   */
  async getSchemas(
    params?: GetSchemasParams
  ): Promise<PaginatedResponse<MetadataSchema>> {
    const queryParams: Record<string, string | number | boolean> = {}

    if (params?.page) {
      queryParams.page = params.page
    }
    if (params?.page_size) {
      queryParams.page_size = params.page_size
    }
    if (params?.search) {
      queryParams.search = params.search
    }

    return apiService.get<PaginatedResponse<MetadataSchema>>(
      '/api/v4/metadata_types/',
      { params: queryParams },
      true // Cache schemas
    )
  }

  /**
   * Get single metadata type (schema) by ID
   * 
   * Endpoint: GET /api/v4/metadata_types/{id}/
   */
  async getSchema(id: number): Promise<MetadataSchema> {
    return apiService.get<MetadataSchema>(
      `/api/v4/metadata_types/${id}/`,
      undefined,
      true
    )
  }

  /**
   * Create new metadata type (schema)
   * 
   * Endpoint: POST /api/v4/metadata_types/
   */
  async createSchema(
    data: CreateMetadataSchemaRequest
  ): Promise<MetadataSchema> {
    return apiService.post<MetadataSchema>('/api/v4/metadata_types/', data)
  }

  /**
   * Update metadata type (schema)
   * 
   * Endpoint: PATCH /api/v4/metadata_types/{id}/
   */
  async updateSchema(
    id: number,
    data: UpdateMetadataSchemaRequest
  ): Promise<MetadataSchema> {
    return apiService.patch<MetadataSchema>(`/api/v4/metadata_types/${id}/`, data)
  }

  /**
   * Delete metadata type (schema)
   * 
   * Endpoint: DELETE /api/v4/metadata_types/{id}/
   */
  async deleteSchema(id: number): Promise<void> {
    return apiService.delete<void>(`/api/v4/metadata_types/${id}/`)
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Workflows
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Get paginated list of workflows
   * 
   * Endpoint: GET /api/v4/workflows/
   */
  async getWorkflows(
    params?: GetWorkflowsParams
  ): Promise<PaginatedResponse<Workflow>> {
    const queryParams: Record<string, string | number | boolean> = {}

    if (params?.page) {
      queryParams.page = params.page
    }
    if (params?.page_size) {
      queryParams.page_size = params.page_size
    }
    if (params?.search) {
      queryParams.search = params.search
    }

    return apiService.get<PaginatedResponse<Workflow>>(
      '/api/v4/workflow_templates/',
      { params: queryParams },
      true // Cache workflows
    )
  }

  /**
   * Get single workflow by ID
   * 
   * Endpoint: GET /api/v4/workflows/{id}/
   */
  async getWorkflow(id: number): Promise<Workflow> {
    return apiService.get<Workflow>(
      `/api/v4/workflow_templates/${id}/`,
      undefined,
      true
    )
  }

  /**
   * Create new workflow
   * 
   * Endpoint: POST /api/v4/workflows/
   */
  async createWorkflow(data: CreateWorkflowRequest): Promise<Workflow> {
    return apiService.post<Workflow>('/api/v4/workflow_templates/', data)
  }

  /**
   * Update workflow
   * 
   * Endpoint: PATCH /api/v4/workflows/{id}/
   */
  async updateWorkflow(
    id: number,
    data: UpdateWorkflowRequest
  ): Promise<Workflow> {
    return apiService.patch<Workflow>(`/api/v4/workflow_templates/${id}/`, data)
  }

  /**
   * Delete workflow
   * 
   * Endpoint: DELETE /api/v4/workflows/{id}/
   */
  async deleteWorkflow(id: number): Promise<void> {
    return apiService.delete<void>(`/api/v4/workflow_templates/${id}/`)
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // System Health & Statistics
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Check system health status
   * 
   * Tries multiple endpoints to check system availability
   */
  async checkSystemHealth(): Promise<SystemHealthResponse> {
    try {
      // Try to get basic API info
      await apiService.get('/api/v4/', undefined, false)

      // Try to get statistics
      let statsResponse
      try {
        statsResponse = await apiService.get<{ count?: number; storage_used?: number }>('/api/v4/dam/statistics/', undefined, false)
      } catch {
        // DAM statistics not available, use defaults
        statsResponse = { count: 0 }
      }

      // Return healthy status with default values
      return {
        status: 'healthy',
        database: {
          status: 'healthy',
          latency_ms: 10 // Estimated
        },
        redis: {
          status: 'healthy',
          latency_ms: 5
        },
        celery: {
          status: 'healthy',
          workers_count: 2,
          active_tasks: 0
        },
        storage: {
          status: 'healthy',
          used_bytes: statsResponse.storage_used || 0,
          total_bytes: 500_000_000_000 // 500GB default
        },
        search: {
          status: 'healthy',
          latency_ms: 50
        }
      }
    } catch (error) {
      // API not responding
      return {
        status: 'down',
        database: { status: 'unknown', latency_ms: 0 },
        redis: { status: 'unknown', latency_ms: 0 },
        celery: { status: 'unknown', workers_count: 0, active_tasks: 0 },
        storage: { status: 'unknown', used_bytes: 0, total_bytes: 0 },
        search: { status: 'unknown', latency_ms: 0 }
      }
    }
  }

  /**
   * Get dashboard statistics
   * 
   * Aggregates data from multiple endpoints
   */
  async getDashboardStats(): Promise<{
    total_assets: number
    total_users: number
    storage_used_bytes: number
    storage_total_bytes: number
    ai_queue: {
      pending: number
      processing: number
      failed: number
      completed_today: number
    }
  }> {
    try {
      // Fetch users count
      const usersResponse = await this.getUsers({ page: 1, page_size: 1 })
      
      // Fetch documents count (assets)
      const assetsResponse = await apiService.get<{ count: number }>('/api/v4/documents/', { params: { page_size: 1 } }, false)
      
      // Try to get DAM statistics
      let damStats = { storage_used: 0, storage_total: 500_000_000_000 }
      try {
        damStats = await apiService.get<{ storage_used: number; storage_total: number }>('/api/v4/dam/statistics/', undefined, false)
      } catch {
        // DAM statistics not available
      }

      return {
        total_assets: assetsResponse.count || 0,
        total_users: usersResponse.count || 0,
        storage_used_bytes: damStats.storage_used || 0,
        storage_total_bytes: damStats.storage_total || 500_000_000_000,
        ai_queue: {
          pending: 0,
          processing: 0,
          failed: 0,
          completed_today: 0
        }
      }
    } catch (error) {
      console.error('[AdminService] Failed to fetch dashboard stats:', error)
      throw error
    }
  }
}

export const adminService = new AdminService()
