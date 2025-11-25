// Common types
export interface ApiResponse<T> {
  data: T
  message?: string
  errors?: Record<string, string[]>
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface ApiError {
  code: string
  message: string
  details?: Record<string, unknown>
}

// Asset types
export interface Asset {
  id: number
  label: string
  filename: string
  size: number
  mime_type: string
  date_added: string
  thumbnail_url?: string
  preview_url?: string
  tags?: string[]
  metadata?: Record<string, unknown>
}

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


