// Re-export API types
export type {
  ApiResponse,
  PaginatedResponse,
  ApiError,
  Asset,
  AssetDetailResponse,
  SearchQuery,
  SearchResponse,
  BulkOperationRequest,
  BulkOperationResponse,
  GetAssetsParams
} from './api'

// User types
export interface User {
  id: number
  username: string
  email: string
  first_name?: string
  last_name?: string
  is_active: boolean
  is_staff?: boolean
  is_superuser?: boolean
  groups?: Array<{ id: number; name: string }>
  permissions?: string[]
  role?: string
  two_factor_enabled?: boolean
}

// 2FA types
export interface TwoFactorStatus {
  enabled: boolean
  method?: 'totp' | 'backup_code'
  backup_codes_generated?: boolean
}

export interface TwoFactorSetup {
  secret: string
  qr_code_url: string
  backup_codes: string[]
}

export interface TwoFactorVerify {
  token: string
  method?: 'totp' | 'backup_code'
}

// Component prop types
export type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
export type ButtonSize = 'sm' | 'md' | 'lg'
export type BadgeVariant = 'success' | 'warning' | 'error' | 'info' | 'neutral'


