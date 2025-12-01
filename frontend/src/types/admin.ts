/**
 * Admin Panel TypeScript Interfaces
 * Based on Mayan EDMS admin capabilities + DAM extensions
 */

// ═══════════════════════════════════════════════════════════════════════════════
// Base Types
// ═══════════════════════════════════════════════════════════════════════════════

export type UUID = string
export type ISODateTime = string

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// ═══════════════════════════════════════════════════════════════════════════════
// User & Access Management
// ═══════════════════════════════════════════════════════════════════════════════

export type UserStatus = 'active' | 'invited' | 'suspended' | 'inactive'

export interface AdminUser {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  is_staff: boolean
  is_superuser: boolean
  date_joined: ISODateTime
  last_login: ISODateTime | null
  status: UserStatus
  avatar_url?: string
  groups: AdminGroup[]
  roles: AdminRole[]
  two_factor_enabled: boolean
}

export interface AdminGroup {
  id: number
  name: string
  users_count: number
  permissions_count: number
}

export interface AdminRole {
  id: number
  label: string
  permissions: StoredPermission[]
  groups: AdminGroup[]
}

export interface StoredPermission {
  id: number
  namespace: string
  name: string
  label: string
}

export interface PermissionMatrix {
  role_id: number
  role_label: string
  permissions: Record<string, boolean> // permission_name -> granted
}

export interface InviteUserPayload {
  email: string
  role_ids: number[]
  group_ids: number[]
  send_invitation: boolean
}

// ═══════════════════════════════════════════════════════════════════════════════
// Documents & Types
// ═══════════════════════════════════════════════════════════════════════════════

export interface DocumentType {
  id: number
  label: string
  delete_time_period: number | null
  delete_time_unit: 'days' | 'hours' | 'minutes' | null
  trash_time_period: number | null
  trash_time_unit: 'days' | 'hours' | 'minutes' | null
  documents_count: number
  filename_templates: FilenameTemplate[]
  metadata_types: MetadataTypeBinding[]
}

export interface FilenameTemplate {
  id: number
  template: string
  document_type_id: number
}

export interface MetadataTypeBinding {
  id: number
  metadata_type: MetadataType
  required: boolean
  default_value: string
}

// ═══════════════════════════════════════════════════════════════════════════════
// Metadata Schema
// ═══════════════════════════════════════════════════════════════════════════════

export type MetadataFieldType = 
  | 'text' 
  | 'textarea' 
  | 'number' 
  | 'date' 
  | 'datetime' 
  | 'select' 
  | 'multiselect' 
  | 'boolean' 
  | 'url' 
  | 'email'

export interface MetadataType {
  id: number
  name: string        // internal key (snake_case)
  label: string       // display name
  default: string
  lookup: string      // comma-separated lookup values
  validation: string  // Python path or regex
  parser: string      // Python path
  // UI extensions
  field_type: MetadataFieldType
  placeholder?: string
  helper_text?: string
  options?: MetadataOption[]
  required?: boolean
  order?: number
}

export interface MetadataOption {
  value: string
  label: string
}

export interface MetadataSchema {
  id: string
  name: string
  description: string
  document_types: number[]
  fields: MetadataType[]
  created_at: ISODateTime
  updated_at: ISODateTime
}

// ═══════════════════════════════════════════════════════════════════════════════
// Workflows
// ═══════════════════════════════════════════════════════════════════════════════

export type WorkflowActionType = 
  | 'http_request' 
  | 'send_email' 
  | 'update_metadata' 
  | 'move_to_cabinet' 
  | 'add_tag' 
  | 'trigger_ai_analysis'

export interface Workflow {
  id: number
  label: string
  internal_name: string
  auto_launch: boolean
  document_types: DocumentType[]
  states: WorkflowState[]
  transitions: WorkflowTransition[]
  instances_count: number
}

export interface WorkflowState {
  id: number
  workflow_id: number
  label: string
  initial: boolean
  completion: boolean
  actions: WorkflowStateAction[]
  color?: string
  order: number
}

export interface WorkflowStateAction {
  id: number
  state_id: number
  label: string
  enabled: boolean
  when: 'on_entry' | 'on_exit'
  condition: string // Python expression
  action_path: string
  action_data: Record<string, unknown>
}

export interface WorkflowTransition {
  id: number
  workflow_id: number
  label: string
  origin_state_id: number
  destination_state_id: number
  condition: string
  triggers: WorkflowTrigger[]
}

export interface WorkflowTrigger {
  id: number
  transition_id: number
  event_type: string
  condition: string
  action: WorkflowActionType
  action_config: Record<string, unknown>
}

export interface WorkflowInstance {
  id: number
  workflow: Workflow
  document_id: number
  document_label: string
  current_state: WorkflowState
  last_transition: ISODateTime | null
  log_entries: WorkflowLogEntry[]
}

export interface WorkflowLogEntry {
  id: number
  datetime: ISODateTime
  transition_label: string
  user: string
  comment: string
}

// ═══════════════════════════════════════════════════════════════════════════════
// AI & Processing
// ═══════════════════════════════════════════════════════════════════════════════

export type AITaskType = 
  | 'image_analysis' 
  | 'ocr' 
  | 'tag_extraction' 
  | 'color_analysis' 
  | 'face_detection' 
  | 'content_moderation'

export type AITaskStatus = 
  | 'pending' 
  | 'processing' 
  | 'completed' 
  | 'failed' 
  | 'cancelled'

export type AIProvider = 
  | 'qwenlocal' 
  | 'gigachat' 
  | 'openai' 
  | 'claude' 
  | 'gemini' 
  | 'yandexgpt' 
  | 'kieai'

export interface AITask {
  id: string
  document_id: number
  document_label: string
  thumbnail_url?: string
  task_type: AITaskType
  provider: AIProvider
  status: AITaskStatus
  created_at: ISODateTime
  started_at?: ISODateTime
  completed_at?: ISODateTime
  duration_ms?: number
  tokens_used?: number
  cost_estimate?: number
  error_message?: string
  result_summary?: string
  retries: number
  max_retries: number
}

export interface AIProviderStatus {
  provider: AIProvider
  label: string
  enabled: boolean
  healthy: boolean
  last_check: ISODateTime
  requests_today: number
  errors_today: number
  avg_response_ms: number
}

export interface DocumentAIAnalysis {
  id: number
  document_id: number
  copyright_notice: string | null
  usage_rights: string | null
  rights_expiry: string | null
  categories: string[]
  language: string | null
  people: string[]
  locations: string[]
  ai_description: string | null
  ai_tags: string[]
  dominant_colors: Array<{ hex: string; percentage: number }>
  alt_text: string | null
  ai_provider: AIProvider | null
  analysis_status: AITaskStatus
  created: ISODateTime
  updated: ISODateTime
  analysis_completed: ISODateTime | null
}

// ═══════════════════════════════════════════════════════════════════════════════
// System & Monitoring
// ═══════════════════════════════════════════════════════════════════════════════

export type ServiceStatus = 'healthy' | 'degraded' | 'down' | 'unknown'

export interface SystemHealth {
  database: ServiceHealth
  redis: ServiceHealth
  celery: CeleryHealth
  storage: StorageHealth
  search_index: ServiceHealth
}

export interface ServiceHealth {
  status: ServiceStatus
  latency_ms: number
  last_check: ISODateTime
  message?: string
}

export interface CeleryHealth {
  status: ServiceStatus
  workers: CeleryWorker[]
  queues: CeleryQueue[]
}

export interface CeleryWorker {
  name: string
  status: ServiceStatus
  active_tasks: number
  processed_total: number
  last_heartbeat: ISODateTime
}

export interface CeleryQueue {
  name: string
  pending: number
  active: number
  failed: number
}

export interface StorageHealth {
  status: ServiceStatus
  total_bytes: number
  used_bytes: number
  free_bytes: number
  usage_percent: number
}

// ═══════════════════════════════════════════════════════════════════════════════
// Activity & Audit
// ═══════════════════════════════════════════════════════════════════════════════

export type ActivityType = 
  | 'document_created' 
  | 'document_deleted' 
  | 'document_updated'
  | 'user_login' 
  | 'user_logout' 
  | 'user_created'
  | 'permission_changed'
  | 'workflow_transition'
  | 'import_started'
  | 'import_completed'
  | 'ai_analysis_completed'
  | 'bulk_operation'

export interface ActivityEvent {
  id: string
  type: ActivityType
  actor: string | {
    id: number
    username: string
    avatar_url?: string
  }
  target?: {
    type: string
    id: number | string
    label: string
  }
  description: string
  metadata?: Record<string, unknown>
  timestamp: ISODateTime
}

// ═══════════════════════════════════════════════════════════════════════════════
// Dashboard Stats
// ═══════════════════════════════════════════════════════════════════════════════

export interface AdminDashboardStats {
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
  recent_activity: ActivityEvent[]
  system_health: SystemHealth
}

// ═══════════════════════════════════════════════════════════════════════════════
// Sources
// ═══════════════════════════════════════════════════════════════════════════════

export type SourceType = 
  | 'web_form' 
  | 'email' 
  | 'staging_folder' 
  | 'watch_folder' 
  | 'yandex_disk'

export interface Source {
  id: number
  label: string
  enabled: boolean
  backend_path: string
  backend_data: Record<string, unknown>
  source_type: SourceType
  last_sync?: ISODateTime
  documents_imported: number
}

// ═══════════════════════════════════════════════════════════════════════════════
// Quotas
// ═══════════════════════════════════════════════════════════════════════════════

export interface Quota {
  id: number
  backend_path: string
  backend_data: Record<string, unknown>
  enabled: boolean
  label: string
  limit_value: number
  current_usage: number
}

// ═══════════════════════════════════════════════════════════════════════════════
// Tags & Cabinets
// ═══════════════════════════════════════════════════════════════════════════════

export interface AdminTag {
  id: number
  label: string
  color: string
  documents_count: number
}

export interface AdminCabinet {
  id: number
  label: string
  parent_id: number | null
  documents_count: number
  children: AdminCabinet[]
}

// ═══════════════════════════════════════════════════════════════════════════════
// Error Logs
// ═══════════════════════════════════════════════════════════════════════════════

export interface ErrorLogEntry {
  id: number
  datetime: ISODateTime
  app_label: string
  name: string
  level: 'debug' | 'info' | 'warning' | 'error' | 'critical'
  message: string
  traceback?: string
}
