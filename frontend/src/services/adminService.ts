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

/**
 * Admin Service
 * 
 * Service class for admin-related API operations.
 * Handles user management, metadata schemas, and workflows.
 */
class AdminService {
  /**
   * Get paginated list of users
   */
  async getUsers(params?: GetUsersParams): Promise<PaginatedResponse<User>> {
    const queryParams: Record<string, string | number> = {}

    if (params?.page) {
      queryParams.page = params.page
    }
    if (params?.page_size) {
      queryParams.page_size = params.page_size
    }
    if (params?.role) {
      queryParams.role = params.role
    }
    if (params?.status) {
      queryParams.status = params.status
    }
    if (params?.search) {
      queryParams.search = params.search
    }

    return apiService.get<PaginatedResponse<User>>(
      '/v4/admin/users/',
      { params: queryParams },
      false // Don't cache user lists for security
    )
  }

  /**
   * Get single user by ID
   */
  async getUser(id: number): Promise<User> {
    return apiService.get<User>(`/v4/admin/users/${id}/`, undefined, true)
  }

  /**
   * Create new user
   */
  async createUser(data: CreateUserRequest): Promise<User> {
    return apiService.post<User>('/v4/admin/users/', data)
  }

  /**
   * Update user
   */
  async updateUser(id: number, data: UpdateUserRequest): Promise<User> {
    return apiService.put<User>(`/v4/admin/users/${id}/`, data)
  }

  /**
   * Delete user
   */
  async deleteUser(id: number): Promise<void> {
    return apiService.delete<void>(`/v4/admin/users/${id}/`)
  }

  /**
   * Bulk user operation
   * 
   * Maximum 100 users per operation (validated on backend)
   */
  async bulkUserOperation(
    operation: BulkUserOperationRequest
  ): Promise<BulkUserOperationResponse> {
    return apiService.post<BulkUserOperationResponse>(
      '/v4/admin/users/bulk/',
      operation
    )
  }

  /**
   * Get paginated list of metadata schemas
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
    if (params?.applies_to) {
      queryParams.applies_to = params.applies_to
    }
    if (params?.is_active !== undefined) {
      queryParams.is_active = params.is_active
    }
    if (params?.search) {
      queryParams.search = params.search
    }

    return apiService.get<PaginatedResponse<MetadataSchema>>(
      '/v4/admin/schemas/',
      { params: queryParams },
      true // Cache schemas for 5 minutes
    )
  }

  /**
   * Get single metadata schema by ID
   */
  async getSchema(id: number): Promise<MetadataSchema> {
    return apiService.get<MetadataSchema>(
      `/v4/admin/schemas/${id}/`,
      undefined,
      true
    )
  }

  /**
   * Create new metadata schema
   */
  async createSchema(
    data: CreateMetadataSchemaRequest
  ): Promise<MetadataSchema> {
    return apiService.post<MetadataSchema>('/v4/admin/schemas/', data)
  }

  /**
   * Update metadata schema
   */
  async updateSchema(
    id: number,
    data: UpdateMetadataSchemaRequest
  ): Promise<MetadataSchema> {
    return apiService.put<MetadataSchema>(`/v4/admin/schemas/${id}/`, data)
  }

  /**
   * Delete metadata schema
   */
  async deleteSchema(id: number): Promise<void> {
    return apiService.delete<void>(`/v4/admin/schemas/${id}/`)
  }

  /**
   * Get paginated list of workflows
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
    if (params?.is_active !== undefined) {
      queryParams.is_active = params.is_active
    }
    if (params?.search) {
      queryParams.search = params.search
    }

    return apiService.get<PaginatedResponse<Workflow>>(
      '/v4/admin/workflows/',
      { params: queryParams },
      true // Cache workflows for 5 minutes
    )
  }

  /**
   * Get single workflow by ID
   */
  async getWorkflow(id: number): Promise<Workflow> {
    return apiService.get<Workflow>(
      `/v4/admin/workflows/${id}/`,
      undefined,
      true
    )
  }

  /**
   * Create new workflow
   */
  async createWorkflow(data: CreateWorkflowRequest): Promise<Workflow> {
    return apiService.post<Workflow>('/v4/admin/workflows/', data)
  }

  /**
   * Update workflow
   */
  async updateWorkflow(
    id: number,
    data: UpdateWorkflowRequest
  ): Promise<Workflow> {
    return apiService.put<Workflow>(`/v4/admin/workflows/${id}/`, data)
  }

  /**
   * Delete workflow
   */
  async deleteWorkflow(id: number): Promise<void> {
    return apiService.delete<void>(`/v4/admin/workflows/${id}/`)
  }
}

export const adminService = new AdminService()

