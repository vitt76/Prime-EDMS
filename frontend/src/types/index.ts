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
  permissions?: string[]
}

// Component prop types
export type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
export type ButtonSize = 'sm' | 'md' | 'lg'
export type BadgeVariant = 'success' | 'warning' | 'error' | 'info' | 'neutral'


