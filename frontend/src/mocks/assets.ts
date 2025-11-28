/**
 * Mock Assets Data Layer
 * 
 * Provides realistic DAM assets for frontend-first development.
 * Simulates pagination, filtering, and search without backend.
 */

import type { Asset, AIAnalysis, PaginatedResponse } from '@/types/api'

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

function randomElement<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)]
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
  
  const status = Math.random() > 0.1 ? 'completed' : randomElement(['pending', 'processing', 'failed'])
  
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
    ai_description: randomElement(descriptions[type] || descriptions.image),
    provider: randomElement(AI_PROVIDERS),
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
      return PLACEHOLDER_IMAGES[index % PLACEHOLDER_IMAGES.length]
    case 'video':
      return VIDEO_THUMBNAILS[index % VIDEO_THUMBNAILS.length]
    default:
      return DOCUMENT_THUMBNAIL
  }
}

// ============================================================================
// MOCK ASSET GENERATOR
// ============================================================================

function generateMockAsset(id: number): Asset {
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
      author: randomElement(['Иван Петров', 'Мария Сидорова', 'Алексей Козлов', 'Елена Новикова', 'admin']),
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
  }
}

// ============================================================================
// MOCK DATA STORE
// ============================================================================

// Generate 75 mock assets on module load
const MOCK_ASSETS: Asset[] = Array.from({ length: 75 }, (_, i) => generateMockAsset(i + 1))

// Sort by date_added descending by default
MOCK_ASSETS.sort((a, b) => new Date(b.date_added).getTime() - new Date(a.date_added).getTime())

// ============================================================================
// PUBLIC API
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
}

export interface MockAssetSort {
  field: 'date_added' | 'name' | 'size' | 'type'
  direction: 'asc' | 'desc'
}

/**
 * Get paginated mock assets with filtering and sorting
 */
export function getMockAssets(
  page: number = 1,
  limit: number = 20,
  filters?: MockAssetFilters,
  sort?: MockAssetSort
): PaginatedResponse<Asset> {
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

/**
 * Get a single mock asset by ID
 */
export function getMockAssetById(id: number): Asset | undefined {
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
export function updateMockAsset(id: number, data: Partial<Asset>): Asset | undefined {
  const index = MOCK_ASSETS.findIndex(asset => asset.id === id)
  if (index !== -1) {
    MOCK_ASSETS[index] = { ...MOCK_ASSETS[index], ...data }
    return MOCK_ASSETS[index]
  }
  return undefined
}

/**
 * Add a new mock asset
 */
export function addMockAsset(asset: Omit<Asset, 'id'>): Asset {
  const maxId = Math.max(...MOCK_ASSETS.map(a => a.id), 0)
  const newAsset: Asset = { ...asset, id: maxId + 1 } as Asset
  MOCK_ASSETS.unshift(newAsset)
  return newAsset
}

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

// Export the raw mock assets for direct access if needed
export { MOCK_ASSETS }

