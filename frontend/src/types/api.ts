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
  description?: string
  filename: string
  size: number
  mime_type: string
  date_added: string
  thumbnail_url?: string
  preview_url?: string
  download_url?: string
  file_latest_id?: number
  tags?: string[]
  metadata?: Record<string, unknown>
  file_details?: FileDetails
  ai_analysis?: AIAnalysis
  comments?: Comment[]
  version_history?: Version[]
  access_level?: string
  is_favorite?: boolean
  isFavorite?: boolean
  description?: string
}

export interface UsageStats {
  views?: number
  downloads?: number
  shares?: number
  usedInLinks?: number
  usedInPublications?: number
  lastViewedAt?: string
  lastDownloadedAt?: string
}

export interface ExtendedAsset extends Asset {
  isFavorite?: boolean
  uploadedBy?: {
    id?: number
    username?: string
    email?: string
    first_name?: string
    last_name?: string
    avatar_url?: string
  }
  lastAccessedAt?: string
  sharedWithMe?: boolean
  sharedBy?: {
    id?: number
    username?: string
    email?: string
    first_name?: string
    last_name?: string
    avatar_url?: string
  }
  sharedAt?: string
  exif?: Record<string, unknown>
  usage?: UsageStats
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
  author_id?: number
  author_avatar?: string
  text: string
  created_date: string
  updated_date?: string
  edited?: boolean
}

export interface Version {
  id: number
  filename: string
  uploaded_date: string
  uploaded_by?: string
  uploaded_by_id?: number
  size: number
  is_current?: boolean
  download_url?: string
  restore_url?: string
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

// Comment API types
export interface CreateCommentRequest {
  text: string
}

export interface UpdateCommentRequest {
  text: string
}

// Publication/Distribution API types
export interface Publication {
  id: number
  title: string
  description?: string
  status: 'draft' | 'scheduled' | 'published' | 'archived'
  created_date: string
  updated_date: string
  published_date?: string
  created_by: string
  created_by_id: number
  assets: Asset[]
  channels: PublicationChannel[]
  schedule?: PublicationSchedule
  permissions?: PublicationPermissions
  analytics?: PublicationAnalytics
  share_links?: ShareLink[]
}

export interface PublicationChannel {
  id: number
  name: string
  type: 'website' | 'social' | 'email' | 'api'
  status: 'active' | 'inactive'
  icon?: string
}

export interface PublicationSchedule {
  start_date?: string
  end_date?: string
  timezone?: string
}

export interface PublicationPermissions {
  view: string[] // Array of user IDs or roles
  download: string[]
  edit: string[]
}

export interface PublicationAnalytics {
  views: number
  downloads: number
  shares: number
  last_viewed?: string
}

export interface ShareLink {
  id: number
  url: string
  expires_at?: string
  password_protected: boolean
  permissions: {
    view: boolean
    download: boolean
  }
  created_date: string
}

export interface CreatePublicationRequest {
  title: string
  description?: string
  asset_ids: number[]
  channel_ids: number[]
  schedule?: PublicationSchedule
  permissions?: PublicationPermissions
}

export interface UpdatePublicationRequest {
  title?: string
  description?: string
  asset_ids?: number[]
  channel_ids?: number[]
  schedule?: PublicationSchedule
  permissions?: PublicationPermissions
  status?: Publication['status']
}

