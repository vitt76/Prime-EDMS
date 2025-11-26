/**
 * Admin Module TypeScript Types
 * 
 * Enterprise-grade type definitions for DAM admin functionality.
 * All types follow strict TypeScript patterns with discriminated unions
 * where appropriate.
 */

import type { PaginatedResponse } from './api'

/**
 * User role type
 */
export type UserRole = 'admin' | 'editor' | 'viewer' | 'guest'

/**
 * User status type
 */
export type UserStatus = 'active' | 'inactive' | 'suspended' | 'pending'

/**
 * User interface
 * 
 * Represents a user in the DAM system with all necessary fields
 * for user management functionality.
 */
export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  is_staff: boolean
  is_superuser: boolean
  role: UserRole
  date_joined: string
  last_login: string | null
  avatar_url: string | null
  permissions: string[]
}

/**
 * Create User Request
 * 
 * Payload for creating a new user via API.
 * All required fields must be provided.
 */
export interface CreateUserRequest {
  username: string
  email: string
  password: string
  first_name?: string
  last_name?: string
  role?: UserRole
  is_active?: boolean
  is_staff?: boolean
  permissions?: string[]
}

/**
 * Update User Request
 * 
 * Partial update payload for user modification.
 * Only provided fields will be updated.
 */
export interface UpdateUserRequest {
  username?: string
  email?: string
  password?: string
  first_name?: string
  last_name?: string
  role?: UserRole
  is_active?: boolean
  is_staff?: boolean
  permissions?: string[]
}

/**
 * Field Type Discriminated Union
 * 
 * All supported metadata field types with type-specific properties.
 */
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

/**
 * Validation Rules
 * 
 * Common validation constraints for schema fields.
 */
export interface ValidationRules {
  min_length?: number
  max_length?: number
  min_value?: number
  max_value?: number
  pattern?: string
  required?: boolean
  custom_validator?: string
}

/**
 * Schema Field Interface
 * 
 * Represents a single field in a metadata schema.
 * Type-specific properties are handled via discriminated union pattern.
 */
export interface SchemaField {
  name: string
  type: FieldType
  label: string
  description?: string
  required: boolean
  default_value?: string | number | boolean | string[]
  options?: string[] // For select/multi_select types
  validation_rules?: ValidationRules
  placeholder?: string
  help_text?: string
}

/**
 * Asset Type for Schema Application
 */
export type AssetType = 'image' | 'video' | 'document' | 'audio' | 'all'

/**
 * Metadata Schema Interface
 * 
 * Complete metadata schema definition with fields and application rules.
 */
export interface MetadataSchema {
  id: number
  name: string
  description?: string
  applies_to: AssetType[]
  fields: SchemaField[]
  is_active: boolean
  created_at: string
  updated_at: string
  created_by: number
  created_by_username?: string
}

/**
 * Create Metadata Schema Request
 */
export interface CreateMetadataSchemaRequest {
  name: string
  description?: string
  applies_to: AssetType[]
  fields: SchemaField[]
  is_active?: boolean
}

/**
 * Update Metadata Schema Request
 */
export interface UpdateMetadataSchemaRequest {
  name?: string
  description?: string
  applies_to?: AssetType[]
  fields?: SchemaField[]
  is_active?: boolean
}

/**
 * Workflow Node Type
 */
export type WorkflowNodeType = 'start' | 'state' | 'end'

/**
 * Workflow Node Interface
 * 
 * Represents a single node in a workflow state machine.
 */
export interface WorkflowNode {
  id: string
  name: string
  type: WorkflowNodeType
  position: {
    x: number
    y: number
  }
  allowed_roles: UserRole[]
  actions: WorkflowAction[]
  description?: string
  color?: string
}

/**
 * Workflow Action Interface
 * 
 * Actions available at a workflow node.
 */
export interface WorkflowAction {
  id: string
  label: string
  action_type: 'approve' | 'reject' | 'request_changes' | 'publish' | 'archive'
  target_node_id: string
  conditions?: WorkflowCondition[]
}

/**
 * Workflow Condition Interface
 * 
 * Conditions that must be met for a transition to occur.
 */
export interface WorkflowCondition {
  field: string
  operator: 'equals' | 'not_equals' | 'contains' | 'greater_than' | 'less_than'
  value: string | number | boolean
}

/**
 * Workflow Transition Interface
 * 
 * Represents a transition between workflow nodes.
 */
export interface WorkflowTransition {
  id: string
  from_node: string
  to_node: string
  condition?: WorkflowCondition
  label: string
  description?: string
}

/**
 * Workflow Interface
 * 
 * Complete workflow definition with nodes and transitions.
 */
export interface Workflow {
  id: number
  name: string
  description?: string
  nodes: WorkflowNode[]
  transitions: WorkflowTransition[]
  is_active: boolean
  created_at: string
  updated_at: string
  created_by: number
  created_by_username?: string
}

/**
 * Create Workflow Request
 */
export interface CreateWorkflowRequest {
  name: string
  description?: string
  nodes: WorkflowNode[]
  transitions: WorkflowTransition[]
  is_active?: boolean
}

/**
 * Update Workflow Request
 */
export interface UpdateWorkflowRequest {
  name?: string
  description?: string
  nodes?: WorkflowNode[]
  transitions?: WorkflowTransition[]
  is_active?: boolean
}

/**
 * Get Users Parameters
 * 
 * Query parameters for fetching paginated user list.
 */
export interface GetUsersParams {
  page?: number
  page_size?: number
  role?: UserRole
  status?: UserStatus
  search?: string
}

/**
 * Bulk User Operation Request
 * 
 * Request payload for bulk user operations.
 * Maximum 100 users per operation.
 */
export interface BulkUserOperationRequest {
  ids: number[]
  action: 'activate' | 'deactivate' | 'delete' | 'assign_role' | 'remove_permission'
  data?: {
    role?: UserRole
    permission?: string
  }
}

/**
 * Bulk User Operation Response
 */
export interface BulkUserOperationResponse {
  success: boolean
  updated: number
  failed: number
  errors?: Array<{
    id: number
    error: string
  }>
}

/**
 * Get Schemas Parameters
 */
export interface GetSchemasParams {
  page?: number
  page_size?: number
  applies_to?: AssetType
  is_active?: boolean
  search?: string
}

/**
 * Get Workflows Parameters
 */
export interface GetWorkflowsParams {
  page?: number
  page_size?: number
  is_active?: boolean
  search?: string
}

/**
 * Admin Store State Interface
 * 
 * Type for admin store state (for reference)
 */
export interface AdminStoreState {
  users: User[]
  totalUsersCount: number
  selectedUsers: number[]
  usersFilters: {
    role: string
    status: string
    search: string
  }
  schemas: MetadataSchema[]
  currentSchema: MetadataSchema | null
  workflows: Workflow[]
  currentWorkflow: Workflow | null
  selectedNode: WorkflowNode | null
  isLoading: boolean
  error: string | null
  lastFetchTime: number | null
}

/**
 * Type guards for discriminated unions
 */
export function isSelectField(field: SchemaField): field is SchemaField & { type: 'select' | 'multi_select' } {
  return field.type === 'select' || field.type === 'multi_select'
}

export function isDateField(field: SchemaField): field is SchemaField & { type: 'date' | 'date_range' } {
  return field.type === 'date' || field.type === 'date_range'
}

export function isNumericField(field: SchemaField): field is SchemaField & { type: 'number' } {
  return field.type === 'number'
}

