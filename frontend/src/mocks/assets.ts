/**
 * Mock Assets Data Layer
 * 
 * Provides realistic DAM assets for frontend-first development.
 * Simulates pagination, filtering, and search without backend.
 * 
 * ENHANCED for Collection Pages:
 * - isFavorite: boolean (~20% true)
 * - uploadedBy: User object
 * - lastAccessedAt: Date (for Recent sorting)
 * - sharedWithMe: boolean
 * 
 * Backend Alignment (Mayan EDMS):
 * - Owner filtering → documents.owner
 * - Access logs → documents.recent_documents (RecentDocument model)
 * - Shared → acls.AccessControlList + permissions
 * - Favorites → User bookmarks (via tags or separate table)
 */

import type { Asset, AIAnalysis, PaginatedResponse } from '@/types/api'

// ============================================================================
// USER TYPES (for uploadedBy, sharedBy)
// ============================================================================

export interface MockUser {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  avatar_url?: string
}

// Current logged-in user (simulated)
export const CURRENT_USER: MockUser = {
  id: 1,
  username: 'current_user',
  email: 'me@company.com',
  first_name: 'Текущий',
  last_name: 'Пользователь',
  avatar_url: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
}

// Other users who can share assets
const OTHER_USERS: MockUser[] = [
  {
    id: 2,
    username: 'ivan.petrov',
    email: 'ivan.petrov@company.com',
    first_name: 'Иван',
    last_name: 'Петров',
    avatar_url: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face',
  },
  {
    id: 3,
    username: 'maria.sidorova',
    email: 'maria.sidorova@company.com',
    first_name: 'Мария',
    last_name: 'Сидорова',
    avatar_url: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop&crop=face',
  },
  {
    id: 4,
    username: 'alexey.kozlov',
    email: 'alexey.kozlov@company.com',
    first_name: 'Алексей',
    last_name: 'Козлов',
    avatar_url: 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=100&h=100&fit=crop&crop=face',
  },
  {
    id: 5,
    username: 'elena.novikova',
    email: 'elena.novikova@company.com',
    first_name: 'Елена',
    last_name: 'Новикова',
    avatar_url: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=100&h=100&fit=crop&crop=face',
  },
  {
    id: 6,
    username: 'dmitry.volkov',
    email: 'dmitry.volkov@company.com',
    first_name: 'Дмитрий',
    last_name: 'Волков',
    avatar_url: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&h=100&fit=crop&crop=face',
  },
]

// ============================================================================
// EXTENDED ASSET TYPE (with collection fields)
// ============================================================================

export interface ExtendedAsset extends Asset {
  // Collection-related fields
  isFavorite: boolean
  uploadedBy: MockUser
  lastAccessedAt: string // ISO date
  sharedWithMe: boolean
  sharedBy?: MockUser  // Who shared this with me (if sharedWithMe)
  sharedAt?: string    // When it was shared
}

// ============================================================================
// MOCK DATA GENERATORS
// ============================================================================

// Unsplash-style placeholder images (free to use)
const PLACEHOLDER_IMAGES = [
  'https://images.unsplash.com/photo-1682687220742-aba13b6e50ba?w=400&h=300&fit=crop',
  'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=300&fit=crop',
  'https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=400&h=300&fit=crop',
  'https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?w=400&h=300&fit=crop',
  'https://images.unsplash.com/photo-1433086966358-54859d0ed716?w=400&h=300&fit=crop',
  'https://images.unsplash.com/photo-1501854140801-50d01698950b?w=400&h=300&fit=crop',
  'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=400&h=300&fit=crop',
  'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&h=300&fit=crop',
  'https://images.unsplash.com/photo-1518173946687-a4c036bc4f9a?w=400&h=300&fit=crop',
  'https://images.unsplash.com/photo-1475924156734-496f6cac6ec1?w=400&h=300&fit=crop',
  // Vertical images
  'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=400&fit=crop',
  'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=300&h=400&fit=crop',
  'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=300&h=400&fit=crop',
  'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=300&h=400&fit=crop',
  'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=300&h=400&fit=crop',
]

// Video placeholder thumbnails
const VIDEO_THUMBNAILS = [
  'https://images.unsplash.com/photo-1536240478700-b869070f9279?w=400&h=300&fit=crop',
  'https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?w=400&h=300&fit=crop',
  'https://images.unsplash.com/photo-1574717024653-61fd2cf4d44d?w=400&h=300&fit=crop',
]

// Document placeholder
const DOCUMENT_THUMBNAIL = 'https://images.unsplash.com/photo-1568667256549-094345857637?w=400&h=300&fit=crop'

// Tags pools
const AI_TAGS = ['Nature', 'Person', 'Portrait', 'Landscape', 'Architecture', 'Food', 'Travel', 'Business', 'Technology', 'Art', 'Fashion', 'Sports', 'Animals', 'City', 'Abstract']
const BUSINESS_TAGS = ['Invoice', 'Contract', 'Report', 'Presentation', 'Proposal', 'Marketing', 'HR', 'Legal', 'Finance', 'Sales']
const CUSTOM_TAGS = ['hero-image', 'banner', 'social-media', 'website', 'print', 'campaign-2025', 'approved', 'draft', 'archive']

// File extensions and MIME types
const FILE_TYPES = {
  image: [
    { ext: 'jpg', mime: 'image/jpeg' },
    { ext: 'png', mime: 'image/png' },
    { ext: 'webp', mime: 'image/webp' },
    { ext: 'gif', mime: 'image/gif' },
  ],
  video: [
    { ext: 'mp4', mime: 'video/mp4' },
    { ext: 'mov', mime: 'video/quicktime' },
    { ext: 'webm', mime: 'video/webm' },
  ],
  document: [
    { ext: 'pdf', mime: 'application/pdf' },
    { ext: 'docx', mime: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' },
    { ext: 'xlsx', mime: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' },
    { ext: 'pptx', mime: 'application/vnd.openxmlformats-officedocument.presentationml.presentation' },
  ],
  audio: [
    { ext: 'mp3', mime: 'audio/mpeg' },
    { ext: 'wav', mime: 'audio/wav' },
  ],
}

// Status options
const STATUSES = ['approved', 'pending', 'draft', 'rejected'] as const
type AssetStatus = typeof STATUSES[number]

// AI Providers
const AI_PROVIDERS = ['YandexGPT', 'GigaChat', 'Qwen'] as const

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function randomInt(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min
}

function randomElement<T>(arr: readonly T[]): T {
  return arr[Math.floor(Math.random() * arr.length)]!
}

function randomElements<T>(arr: T[], count: number): T[] {
  const shuffled = [...arr].sort(() => 0.5 - Math.random())
  return shuffled.slice(0, count)
}

function randomDate(daysBack: number = 365): string {
  const now = Date.now()
  const past = now - randomInt(0, daysBack * 24 * 60 * 60 * 1000)
  return new Date(past).toISOString()
}

function randomRecentDate(daysBack: number = 30): string {
  const now = Date.now()
  const past = now - randomInt(0, daysBack * 24 * 60 * 60 * 1000)
  return new Date(past).toISOString()
}

function generateFileSize(type: string): number {
  switch (type) {
    case 'image':
      return randomInt(500_000, 15_000_000) // 500KB - 15MB
    case 'video':
      return randomInt(10_000_000, 500_000_000) // 10MB - 500MB
    case 'document':
      return randomInt(100_000, 50_000_000) // 100KB - 50MB
    case 'audio':
      return randomInt(1_000_000, 100_000_000) // 1MB - 100MB
    default:
      return randomInt(100_000, 10_000_000)
  }
}

function generateFilename(type: string, index: number): string {
  const prefixes: Record<string, string[]> = {
    image: ['photo', 'image', 'screenshot', 'banner', 'hero', 'thumbnail', 'cover', 'bg'],
    video: ['video', 'clip', 'promo', 'interview', 'tutorial', 'demo', 'ad'],
    document: ['report', 'invoice', 'contract', 'proposal', 'presentation', 'guide', 'manual'],
    audio: ['podcast', 'interview', 'music', 'voiceover', 'sfx'],
  }
  
  const prefix = randomElement(prefixes[type] || ['file'])
  const fileType = FILE_TYPES[type as keyof typeof FILE_TYPES]
  const ext = randomElement(fileType).ext
  
  return `${prefix}_${String(index).padStart(4, '0')}.${ext}`
}

function generateLabel(filename: string): string {
  // Convert filename to human-readable label
  const name = filename.replace(/\.[^.]+$/, '') // Remove extension
  return name
    .replace(/_/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase())
}

function generateAIAnalysis(type: string): AIAnalysis | undefined {
  // 80% chance of having AI analysis
  if (Math.random() > 0.8) return undefined
  
  const status: AIAnalysis['status'] = Math.random() > 0.1 
    ? 'completed' 
    : randomElement(['pending', 'processing', 'failed'] as const)
  
  if (status !== 'completed') {
    return { status }
  }
  
  const tags = type === 'image' 
    ? randomElements(AI_TAGS, randomInt(2, 6))
    : type === 'document'
      ? randomElements(BUSINESS_TAGS, randomInt(1, 4))
      : randomElements(AI_TAGS, randomInt(1, 3))
  
  const colors = type === 'image' 
    ? ['#' + Math.floor(Math.random()*16777215).toString(16).padStart(6, '0'),
       '#' + Math.floor(Math.random()*16777215).toString(16).padStart(6, '0'),
       '#' + Math.floor(Math.random()*16777215).toString(16).padStart(6, '0')]
    : undefined
  
  const descriptions: Record<string, string[]> = {
    image: [
      'Живописный пейзаж с горами на закате',
      'Портрет молодого профессионала в офисной обстановке',
      'Современная архитектура городского центра',
      'Натюрморт с цветами и фруктами',
      'Абстрактная композиция в теплых тонах',
      'Групповое фото команды на корпоративном мероприятии',
      'Продуктовая фотография на белом фоне',
      'Панорамный вид на побережье океана',
    ],
    video: [
      'Промо-ролик нового продукта компании',
      'Интервью с руководителем отдела маркетинга',
      'Обучающее видео по использованию платформы',
      'Рекламный клип для социальных сетей',
    ],
    document: [
      'Финансовый отчет за Q4 2024',
      'Коммерческое предложение для клиента',
      'Договор на оказание услуг',
      'Маркетинговая презентация бренда',
    ],
  }
  
  return {
    status: 'completed',
    tags,
    confidence: Math.random() * 0.3 + 0.7, // 0.7 - 1.0
    colors,
    ai_description: randomElement(descriptions[type] ?? descriptions.image!),
    provider: randomElement([...AI_PROVIDERS]),
    objects_detected: type === 'image' ? tags.slice(0, 3).map(tag => ({
      name: tag,
      confidence: Math.random() * 0.3 + 0.7,
      bbox: {
        x: randomInt(0, 200),
        y: randomInt(0, 200),
        width: randomInt(50, 200),
        height: randomInt(50, 200),
      }
    })) : undefined,
  }
}

function generateThumbnail(type: string, index: number): string {
  switch (type) {
    case 'image':
      return PLACEHOLDER_IMAGES[index % PLACEHOLDER_IMAGES.length]!
    case 'video':
      return VIDEO_THUMBNAILS[index % VIDEO_THUMBNAILS.length]!
    default:
      return DOCUMENT_THUMBNAIL
  }
}

// ============================================================================
// MOCK ASSET GENERATOR (EXTENDED)
// ============================================================================

function generateMockAsset(id: number): ExtendedAsset {
  // Weighted random type selection: 60% images, 20% documents, 15% videos, 5% audio
  const typeRoll = Math.random()
  let type: string
  if (typeRoll < 0.6) type = 'image'
  else if (typeRoll < 0.8) type = 'document'
  else if (typeRoll < 0.95) type = 'video'
  else type = 'audio'
  
  const filename = generateFilename(type, id)
  const fileTypeInfo = FILE_TYPES[type as keyof typeof FILE_TYPES]
  const mimeType = fileTypeInfo.find(f => filename.endsWith(f.ext))?.mime || 'application/octet-stream'
  
  const status = randomElement(STATUSES)
  const customTags = randomElements(CUSTOM_TAGS, randomInt(0, 3))
  
  // ========================================
  // NEW: Collection-related fields
  // ========================================
  
  // ~20% are favorites
  const isFavorite = Math.random() < 0.20
  
  // ~40% uploaded by current user, ~60% by others
  const isMyUpload = Math.random() < 0.40
  const uploadedBy = isMyUpload ? CURRENT_USER : randomElement(OTHER_USERS)
  
  // Recent access: random time in last 30 days
  const lastAccessedAt = randomRecentDate(30)
  
  // ~30% shared with me (only if not my upload)
  const sharedWithMe = !isMyUpload && Math.random() < 0.30
  const sharedBy = sharedWithMe ? uploadedBy : undefined
  const sharedAt = sharedWithMe ? randomRecentDate(14) : undefined
  
  return {
    id,
    label: generateLabel(filename),
    filename,
    size: generateFileSize(type),
    mime_type: mimeType,
    date_added: randomDate(180), // Last 6 months
    thumbnail_url: generateThumbnail(type, id),
    preview_url: generateThumbnail(type, id),
    tags: customTags,
    metadata: {
      status,
      type,
      width: type === 'image' ? randomInt(800, 4000) : undefined,
      height: type === 'image' ? randomInt(600, 3000) : undefined,
      duration: type === 'video' ? randomInt(10, 600) : type === 'audio' ? randomInt(30, 3600) : undefined,
      pages: type === 'document' ? randomInt(1, 100) : undefined,
      author: uploadedBy.first_name + ' ' + uploadedBy.last_name,
      department: randomElement(['Marketing', 'Sales', 'HR', 'Legal', 'Finance', 'IT']),
    },
    ai_analysis: generateAIAnalysis(type),
    access_level: randomElement(['public', 'internal', 'confidential']),
    file_details: {
      filename,
      size: generateFileSize(type),
      mime_type: mimeType,
      uploaded_date: randomDate(180),
      checksum: 'sha256:' + Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join(''),
    },
    
    // Collection fields
    isFavorite,
    uploadedBy,
    lastAccessedAt,
    sharedWithMe,
    sharedBy,
    sharedAt,
  }
}

// ============================================================================
// MOCK DATA STORE
// ============================================================================

// Generate 75 mock assets on module load
const MOCK_ASSETS: ExtendedAsset[] = Array.from({ length: 75 }, (_, i) => generateMockAsset(i + 1))

// Sort by date_added descending by default
MOCK_ASSETS.sort((a, b) => new Date(b.date_added).getTime() - new Date(a.date_added).getTime())

// ============================================================================
// PUBLIC API - FILTERS & TYPES
// ============================================================================

export interface MockAssetFilters {
  type?: string[]
  tags?: string[]
  status?: string[]
  dateFrom?: string
  dateTo?: string
  sizeMin?: number
  sizeMax?: number
  search?: string
  // Collection-specific filters
  favoritesOnly?: boolean
  myUploadsOnly?: boolean
  sharedWithMeOnly?: boolean
}

export interface MockAssetSort {
  field: 'date_added' | 'name' | 'size' | 'type' | 'lastAccessedAt'
  direction: 'asc' | 'desc'
}

// ============================================================================
// PUBLIC API - MAIN FUNCTIONS
// ============================================================================

/**
 * Get paginated mock assets with filtering and sorting
 */
export function getMockAssets(
  page: number = 1,
  limit: number = 20,
  filters?: MockAssetFilters,
  sort?: MockAssetSort
): PaginatedResponse<ExtendedAsset> {
  let filtered = [...MOCK_ASSETS]
  
  // Apply filters
  if (filters) {
    // Type filter
    if (filters.type?.length) {
      filtered = filtered.filter(asset => {
        const assetType = asset.metadata?.type as string
        return filters.type!.includes(assetType)
      })
    }
    
    // Tags filter
    if (filters.tags?.length) {
      filtered = filtered.filter(asset => {
        const assetTags = [...(asset.tags || []), ...(asset.ai_analysis?.tags || [])]
        return filters.tags!.some(tag => assetTags.includes(tag))
      })
    }
    
    // Status filter
    if (filters.status?.length) {
      filtered = filtered.filter(asset => {
        const status = asset.metadata?.status as string
        return filters.status!.includes(status)
      })
    }
    
    // Date range filter
    if (filters.dateFrom) {
      const fromDate = new Date(filters.dateFrom).getTime()
      filtered = filtered.filter(asset => new Date(asset.date_added).getTime() >= fromDate)
    }
    if (filters.dateTo) {
      const toDate = new Date(filters.dateTo).getTime()
      filtered = filtered.filter(asset => new Date(asset.date_added).getTime() <= toDate)
    }
    
    // Size filter
    if (filters.sizeMin !== undefined) {
      filtered = filtered.filter(asset => asset.size >= filters.sizeMin!)
    }
    if (filters.sizeMax !== undefined) {
      filtered = filtered.filter(asset => asset.size <= filters.sizeMax!)
    }
    
    // Search filter (searches in label, filename, tags, AI description)
    if (filters.search?.trim()) {
      const searchLower = filters.search.toLowerCase().trim()
      filtered = filtered.filter(asset => {
        const searchableText = [
          asset.label,
          asset.filename,
          ...(asset.tags || []),
          ...(asset.ai_analysis?.tags || []),
          asset.ai_analysis?.ai_description,
          asset.metadata?.author,
          asset.metadata?.department,
        ].filter(Boolean).join(' ').toLowerCase()
        
        return searchableText.includes(searchLower)
      })
    }
    
    // ========================================
    // NEW: Collection-specific filters
    // ========================================
    
    if (filters.favoritesOnly) {
      filtered = filtered.filter(asset => asset.isFavorite)
    }
    
    if (filters.myUploadsOnly) {
      filtered = filtered.filter(asset => asset.uploadedBy.id === CURRENT_USER.id)
    }
    
    if (filters.sharedWithMeOnly) {
      filtered = filtered.filter(asset => asset.sharedWithMe)
    }
  }
  
  // Apply sorting
  if (sort) {
    filtered.sort((a, b) => {
      let comparison = 0
      
      switch (sort.field) {
        case 'date_added':
          comparison = new Date(a.date_added).getTime() - new Date(b.date_added).getTime()
          break
        case 'name':
          comparison = a.label.localeCompare(b.label)
          break
        case 'size':
          comparison = a.size - b.size
          break
        case 'type':
          comparison = (a.metadata?.type as string || '').localeCompare(b.metadata?.type as string || '')
          break
        case 'lastAccessedAt':
          comparison = new Date(a.lastAccessedAt).getTime() - new Date(b.lastAccessedAt).getTime()
          break
      }
      
      return sort.direction === 'desc' ? -comparison : comparison
    })
  }
  
  // Paginate
  const totalCount = filtered.length
  const totalPages = Math.ceil(totalCount / limit)
  const startIndex = (page - 1) * limit
  const endIndex = startIndex + limit
  const results = filtered.slice(startIndex, endIndex)
  
  return {
    count: totalCount,
    next: page < totalPages ? `/api/v4/dam/assets/?page=${page + 1}` : null,
    previous: page > 1 ? `/api/v4/dam/assets/?page=${page - 1}` : null,
    results,
    page_size: limit,
    total_pages: totalPages,
  }
}

// ============================================================================
// COLLECTION-SPECIFIC GETTERS
// ============================================================================

/**
 * Get favorites (isFavorite === true)
 */
export function getMockFavorites(
  page: number = 1,
  limit: number = 20,
  sort?: MockAssetSort
): PaginatedResponse<ExtendedAsset> {
  return getMockAssets(page, limit, { favoritesOnly: true }, sort)
}

/**
 * Get my uploads (uploadedBy === CURRENT_USER)
 */
export function getMockMyUploads(
  page: number = 1,
  limit: number = 20,
  sort?: MockAssetSort
): PaginatedResponse<ExtendedAsset> {
  return getMockAssets(page, limit, { myUploadsOnly: true }, sort)
}

/**
 * Get recent assets sorted by lastAccessedAt
 */
export function getMockRecent(
  page: number = 1,
  limit: number = 20
): PaginatedResponse<ExtendedAsset> {
  return getMockAssets(
    page, 
    limit, 
    undefined, 
    { field: 'lastAccessedAt', direction: 'desc' }
  )
}

/**
 * Get assets shared with me
 */
export function getMockSharedWithMe(
  page: number = 1,
  limit: number = 20,
  sort?: MockAssetSort
): PaginatedResponse<ExtendedAsset> {
  return getMockAssets(page, limit, { sharedWithMeOnly: true }, sort)
}

/**
 * Group recent assets by time period (for RecentsPage)
 */
export function getRecentAssetsGrouped(): {
  today: ExtendedAsset[]
  yesterday: ExtendedAsset[]
  thisWeek: ExtendedAsset[]
  earlier: ExtendedAsset[]
} {
  const now = new Date()
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterdayStart = new Date(todayStart.getTime() - 24 * 60 * 60 * 1000)
  const weekStart = new Date(todayStart.getTime() - 7 * 24 * 60 * 60 * 1000)
  
  const sorted = [...MOCK_ASSETS].sort(
    (a, b) => new Date(b.lastAccessedAt).getTime() - new Date(a.lastAccessedAt).getTime()
  )
  
  const today: ExtendedAsset[] = []
  const yesterday: ExtendedAsset[] = []
  const thisWeek: ExtendedAsset[] = []
  const earlier: ExtendedAsset[] = []
  
  for (const asset of sorted) {
    const accessDate = new Date(asset.lastAccessedAt)
    
    if (accessDate >= todayStart) {
      today.push(asset)
    } else if (accessDate >= yesterdayStart) {
      yesterday.push(asset)
    } else if (accessDate >= weekStart) {
      thisWeek.push(asset)
    } else {
      earlier.push(asset)
    }
  }
  
  return { today, yesterday, thisWeek, earlier }
}

// ============================================================================
// CRUD OPERATIONS
// ============================================================================

/**
 * Get a single mock asset by ID
 */
export function getMockAssetById(id: number): ExtendedAsset | undefined {
  return MOCK_ASSETS.find(asset => asset.id === id)
}

/**
 * Delete a mock asset (mutates the array)
 */
export function deleteMockAsset(id: number): boolean {
  const index = MOCK_ASSETS.findIndex(asset => asset.id === id)
  if (index !== -1) {
    MOCK_ASSETS.splice(index, 1)
    return true
  }
  return false
}

/**
 * Update a mock asset (mutates the array)
 */
export function updateMockAsset(id: number, data: Partial<ExtendedAsset>): ExtendedAsset | undefined {
  const index = MOCK_ASSETS.findIndex(asset => asset.id === id)
  if (index !== -1) {
    const existing = MOCK_ASSETS[index]!
    MOCK_ASSETS[index] = { ...existing, ...data } as ExtendedAsset
    return MOCK_ASSETS[index]
  }
  return undefined
}

/**
 * Add a new mock asset
 */
export function addMockAsset(asset: Partial<ExtendedAsset> & Pick<ExtendedAsset, 'label' | 'filename' | 'size' | 'mime_type' | 'date_added'>): ExtendedAsset {
  const maxId = Math.max(...MOCK_ASSETS.map(a => a.id), 0)
  const newAsset: ExtendedAsset = {
    id: maxId + 1,
    label: asset.label,
    filename: asset.filename,
    size: asset.size,
    mime_type: asset.mime_type,
    date_added: asset.date_added,
    thumbnail_url: asset.thumbnail_url,
    preview_url: asset.preview_url,
    tags: asset.tags,
    metadata: asset.metadata,
    ai_analysis: asset.ai_analysis,
    access_level: asset.access_level,
    file_details: asset.file_details,
    // Collection fields with defaults
    isFavorite: asset.isFavorite ?? false,
    uploadedBy: asset.uploadedBy ?? CURRENT_USER,
    lastAccessedAt: asset.lastAccessedAt ?? new Date().toISOString(),
    sharedWithMe: asset.sharedWithMe ?? false,
    sharedBy: asset.sharedBy,
    sharedAt: asset.sharedAt,
  }
  MOCK_ASSETS.unshift(newAsset)
  return newAsset
}

/**
 * Toggle favorite status
 */
export function toggleMockFavorite(id: number): ExtendedAsset | undefined {
  const asset = getMockAssetById(id)
  if (asset) {
    return updateMockAsset(id, { isFavorite: !asset.isFavorite })
  }
  return undefined
}

/**
 * Update last accessed time (for "Recent" tracking)
 */
export function touchMockAsset(id: number): ExtendedAsset | undefined {
  return updateMockAsset(id, { lastAccessedAt: new Date().toISOString() })
}

// ============================================================================
// FACET DATA
// ============================================================================

/**
 * Get all unique tags from mock assets
 */
export function getMockTags(): string[] {
  const tagsSet = new Set<string>()
  
  MOCK_ASSETS.forEach(asset => {
    asset.tags?.forEach(tag => tagsSet.add(tag))
    asset.ai_analysis?.tags?.forEach(tag => tagsSet.add(tag))
  })
  
  return Array.from(tagsSet).sort()
}

/**
 * Get asset type counts for faceted search
 */
export function getMockTypeCounts(): Record<string, number> {
  const counts: Record<string, number> = {}
  
  MOCK_ASSETS.forEach(asset => {
    const type = asset.metadata?.type as string || 'other'
    counts[type] = (counts[type] || 0) + 1
  })
  
  return counts
}

/**
 * Get status counts for faceted search
 */
export function getMockStatusCounts(): Record<string, number> {
  const counts: Record<string, number> = {}
  
  MOCK_ASSETS.forEach(asset => {
    const status = asset.metadata?.status as string || 'unknown'
    counts[status] = (counts[status] || 0) + 1
  })
  
  return counts
}

/**
 * Get collection counts
 */
export function getMockCollectionCounts(): {
  favorites: number
  myUploads: number
  recent: number
  sharedWithMe: number
} {
  return {
    favorites: MOCK_ASSETS.filter(a => a.isFavorite).length,
    myUploads: MOCK_ASSETS.filter(a => a.uploadedBy.id === CURRENT_USER.id).length,
    recent: MOCK_ASSETS.length, // All assets have lastAccessedAt
    sharedWithMe: MOCK_ASSETS.filter(a => a.sharedWithMe).length,
  }
}

// Export the raw mock assets for direct access if needed
// Note: CURRENT_USER is already exported at definition
export { MOCK_ASSETS, OTHER_USERS }
