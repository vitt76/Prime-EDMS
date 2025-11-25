// API Response types
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
  page_size?: number
  total_pages?: number
}

export interface ApiError {
  code: string
  message: string
  details?: Record<string, unknown>
}

// Asset API types
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
  file_details?: FileDetails
  ai_analysis?: AIAnalysis
  comments?: Comment[]
  version_history?: Version[]
  access_level?: string
}

export interface FileDetails {
  filename: string
  size: number
  mime_type: string
  uploaded_date: string
  checksum?: string
}

export interface AIAnalysis {
  tags?: string[]
  confidence?: number
  objects_detected?: DetectedObject[]
  colors?: string[]
  status: 'pending' | 'processing' | 'completed' | 'failed'
  ai_description?: string
  provider?: string
}

export interface DetectedObject {
  name: string
  confidence: number
  bbox?: {
    x: number
    y: number
    width: number
    height: number
  }
}

export interface Comment {
  id: number
  author: string
  text: string
  created_date: string
  replies?: Comment[]
}

export interface Version {
  id: number
  filename: string
  uploaded_date: string
  uploaded_by?: string
  size: number
}

// Search API types
export interface SearchQuery {
  q?: string
  filters?: SearchFilters
  sort?: string
  limit?: number
  offset?: number
}

export interface SearchFilters {
  type?: string[]
  tags?: string[]
  date_range?: [string, string] // [start, end]
  size?: {
    min?: number
    max?: number
  }
  custom_metadata?: Record<string, unknown>
}

export interface SearchResponse {
  count: number
  results: Asset[]
  facets: Facets
}

export interface Facets {
  type?: Record<string, number>
  tags?: Record<string, number>
  date?: Record<string, number>
  [key: string]: Record<string, number> | undefined
}

// Bulk operations types
export interface BulkOperationRequest {
  ids: number[]
  action: 'add_tags' | 'remove_tags' | 'move' | 'delete' | 'export'
  data?: Record<string, unknown>
}

export interface BulkOperationResponse {
  success: boolean
  updated: number
  failed: number
  errors?: Array<{
    id: number
    error: string
  }>
}

// Asset detail response
export interface AssetDetailResponse extends Asset {
  file_details: FileDetails
  ai_analysis?: AIAnalysis
  comments: Comment[]
  version_history: Version[]
}

// Request parameters
export interface GetAssetsParams {
  page?: number
  page_size?: number
  sort?: string
  type?: string
  tags?: string
  search?: string
}

// Cache entry
export interface CacheEntry<T> {
  data: T
  timestamp: number
  ttl: number
}

