/**
 * Mock data for shared links / publications
 * Used for development and testing without backend
 */

import type { Asset } from '@/types/api'

export interface SharedLink {
  id: number
  name: string
  slug: string  // URL slug (e.g., 'abc-123')
  url: string   // Full URL
  asset_ids: number[]
  assets?: Asset[]  // Populated when needed
  
  // Settings
  is_public: boolean
  password_protected: boolean
  password?: string  // Not exposed in responses
  
  // Dates
  created_date: string
  expires_date: string | null
  
  // Creator
  created_by: string
  created_by_id: number
  
  // Analytics
  views: number
  downloads: number
  unique_visitors: number
  
  // Status
  status: 'active' | 'expired' | 'revoked'
  
  // Permissions
  allow_download: boolean
  allow_comment: boolean
}

export interface CreateSharedLinkParams {
  name: string
  asset_ids: number[]
  is_public: boolean
  expires_date?: string | null
  password?: string
  allow_download: boolean
  allow_comment: boolean
}

// Generate random slug
function generateSlug(): string {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < 8; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

// Base URL for share links
const SHARE_BASE_URL = 'https://dam.local/s'

// Mock shared links data
export const MOCK_SHARED_LINKS: SharedLink[] = [
  {
    id: 1,
    name: 'Маркетинговые материалы Q4 2025',
    slug: 'mkt-q4-2025',
    url: `${SHARE_BASE_URL}/mkt-q4-2025`,
    asset_ids: [1, 2, 3, 5, 8],
    is_public: true,
    password_protected: false,
    created_date: new Date(Date.now() - 86400000 * 2).toISOString(),
    expires_date: new Date(Date.now() + 86400000 * 30).toISOString(),
    created_by: 'Алексей Иванов',
    created_by_id: 1,
    views: 245,
    downloads: 67,
    unique_visitors: 89,
    status: 'active',
    allow_download: true,
    allow_comment: false
  },
  {
    id: 2,
    name: 'Пресс-кит для СМИ',
    slug: 'press-kit-2025',
    url: `${SHARE_BASE_URL}/press-kit-2025`,
    asset_ids: [4, 6, 7, 12, 15, 18],
    is_public: true,
    password_protected: true,
    created_date: new Date(Date.now() - 86400000 * 5).toISOString(),
    expires_date: new Date(Date.now() + 86400000 * 60).toISOString(),
    created_by: 'Мария Петрова',
    created_by_id: 2,
    views: 1250,
    downloads: 432,
    unique_visitors: 567,
    status: 'active',
    allow_download: true,
    allow_comment: true
  },
  {
    id: 3,
    name: 'Фото с корпоратива',
    slug: 'corp-party-nov',
    url: `${SHARE_BASE_URL}/corp-party-nov`,
    asset_ids: [9, 10, 11, 13, 14],
    is_public: true,
    password_protected: false,
    created_date: new Date(Date.now() - 86400000 * 10).toISOString(),
    expires_date: new Date(Date.now() - 86400000 * 3).toISOString(), // Expired
    created_by: 'Дмитрий Козлов',
    created_by_id: 3,
    views: 89,
    downloads: 23,
    unique_visitors: 34,
    status: 'expired',
    allow_download: true,
    allow_comment: false
  },
  {
    id: 4,
    name: 'Логотипы и брендбук',
    slug: 'brand-assets',
    url: `${SHARE_BASE_URL}/brand-assets`,
    asset_ids: [16, 17, 19, 20],
    is_public: true,
    password_protected: true,
    created_date: new Date(Date.now() - 86400000 * 15).toISOString(),
    expires_date: null, // No expiration
    created_by: 'Елена Смирнова',
    created_by_id: 4,
    views: 3456,
    downloads: 1234,
    unique_visitors: 890,
    status: 'active',
    allow_download: true,
    allow_comment: false
  },
  {
    id: 5,
    name: 'Презентация для инвесторов',
    slug: 'inv-pitch-dec',
    url: `${SHARE_BASE_URL}/inv-pitch-dec`,
    asset_ids: [21, 22, 23],
    is_public: false,
    password_protected: true,
    created_date: new Date(Date.now() - 86400000 * 7).toISOString(),
    expires_date: new Date(Date.now() + 86400000 * 14).toISOString(),
    created_by: 'Алексей Иванов',
    created_by_id: 1,
    views: 12,
    downloads: 5,
    unique_visitors: 8,
    status: 'active',
    allow_download: false,
    allow_comment: false
  },
  {
    id: 6,
    name: 'Каталог продукции 2025',
    slug: 'catalog-2025',
    url: `${SHARE_BASE_URL}/catalog-2025`,
    asset_ids: [24, 25, 26, 27, 28, 29, 30],
    is_public: true,
    password_protected: false,
    created_date: new Date(Date.now() - 86400000 * 20).toISOString(),
    expires_date: new Date(Date.now() + 86400000 * 90).toISOString(),
    created_by: 'Мария Петрова',
    created_by_id: 2,
    views: 5678,
    downloads: 2345,
    unique_visitors: 1890,
    status: 'active',
    allow_download: true,
    allow_comment: true
  },
  {
    id: 7,
    name: 'Отчёт для партнёров',
    slug: 'partner-report',
    url: `${SHARE_BASE_URL}/partner-report`,
    asset_ids: [31, 32],
    is_public: false,
    password_protected: true,
    created_date: new Date(Date.now() - 86400000 * 30).toISOString(),
    expires_date: new Date(Date.now() - 86400000 * 15).toISOString(),
    created_by: 'Дмитрий Козлов',
    created_by_id: 3,
    views: 45,
    downloads: 12,
    unique_visitors: 23,
    status: 'expired',
    allow_download: true,
    allow_comment: false
  },
  {
    id: 8,
    name: 'Видеоролик для соцсетей',
    slug: 'social-video',
    url: `${SHARE_BASE_URL}/social-video`,
    asset_ids: [33, 34, 35],
    is_public: true,
    password_protected: false,
    created_date: new Date(Date.now() - 86400000 * 3).toISOString(),
    expires_date: new Date(Date.now() + 86400000 * 7).toISOString(),
    created_by: 'Елена Смирнова',
    created_by_id: 4,
    views: 890,
    downloads: 234,
    unique_visitors: 456,
    status: 'active',
    allow_download: true,
    allow_comment: true
  },
  {
    id: 9,
    name: 'Архив фотографий 2024',
    slug: 'photos-2024',
    url: `${SHARE_BASE_URL}/photos-2024`,
    asset_ids: [36, 37, 38, 39, 40, 41, 42, 43, 44, 45],
    is_public: true,
    password_protected: false,
    created_date: new Date(Date.now() - 86400000 * 60).toISOString(),
    expires_date: null,
    created_by: 'Алексей Иванов',
    created_by_id: 1,
    views: 12345,
    downloads: 5678,
    unique_visitors: 4567,
    status: 'active',
    allow_download: true,
    allow_comment: true
  },
  {
    id: 10,
    name: 'Удалённая ссылка',
    slug: 'deleted-link',
    url: `${SHARE_BASE_URL}/deleted-link`,
    asset_ids: [46],
    is_public: true,
    password_protected: false,
    created_date: new Date(Date.now() - 86400000 * 45).toISOString(),
    expires_date: null,
    created_by: 'Мария Петрова',
    created_by_id: 2,
    views: 23,
    downloads: 5,
    unique_visitors: 12,
    status: 'revoked',
    allow_download: true,
    allow_comment: false
  },
  {
    id: 11,
    name: 'Баннеры для рекламы',
    slug: 'ad-banners',
    url: `${SHARE_BASE_URL}/ad-banners`,
    asset_ids: [47, 48, 49, 50],
    is_public: true,
    password_protected: false,
    created_date: new Date(Date.now() - 86400000 * 1).toISOString(),
    expires_date: new Date(Date.now() + 86400000 * 14).toISOString(),
    created_by: 'Дмитрий Козлов',
    created_by_id: 3,
    views: 156,
    downloads: 45,
    unique_visitors: 78,
    status: 'active',
    allow_download: true,
    allow_comment: false
  },
  {
    id: 12,
    name: 'Материалы для блога',
    slug: 'blog-assets',
    url: `${SHARE_BASE_URL}/blog-assets`,
    asset_ids: [51, 52, 53],
    is_public: true,
    password_protected: false,
    created_date: new Date(Date.now() - 86400000 * 4).toISOString(),
    expires_date: new Date(Date.now() + 86400000 * 21).toISOString(),
    created_by: 'Елена Смирнова',
    created_by_id: 4,
    views: 234,
    downloads: 89,
    unique_visitors: 123,
    status: 'active',
    allow_download: true,
    allow_comment: true
  }
]

// Store for dynamically added shared links
let dynamicSharedLinks: SharedLink[] = []
let nextId = MOCK_SHARED_LINKS.length + 1

// Thumbnail URLs for assets (mock)
const THUMBNAIL_URLS = [
  'https://images.unsplash.com/photo-1682687220742-aba13b6e50ba?w=100&h=100&fit=crop',
  'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=100&h=100&fit=crop',
  'https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=100&h=100&fit=crop',
  'https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?w=100&h=100&fit=crop',
  'https://images.unsplash.com/photo-1433086966358-54859d0ed716?w=100&h=100&fit=crop',
  'https://images.unsplash.com/photo-1501854140801-50d01698950b?w=100&h=100&fit=crop',
  'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=100&h=100&fit=crop',
  'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=100&h=100&fit=crop',
  'https://images.unsplash.com/photo-1518173946687-a4c036bc4f9a?w=100&h=100&fit=crop',
  'https://images.unsplash.com/photo-1475924156734-496f6cac6ec1?w=100&h=100&fit=crop',
  'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop',
  'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop',
]

/**
 * Generate mock assets for a shared link
 */
function generateMockAssets(assetIds: number[]): Asset[] {
  return assetIds.map((id, index) => ({
    id,
    label: `Asset ${id}`,
    filename: `asset-${id}.jpg`,
    size: 1024 * 1024 * (Math.random() * 5 + 1),
    mime_type: 'image/jpeg',
    date_added: new Date(Date.now() - 86400000 * Math.random() * 30).toISOString(),
    thumbnail_url: THUMBNAIL_URLS[index % THUMBNAIL_URLS.length],
    preview_url: THUMBNAIL_URLS[index % THUMBNAIL_URLS.length].replace('w=100&h=100', 'w=800&h=600'),
  }))
}

/**
 * Get all shared links (mock + dynamic)
 */
export function getMockSharedLinks(
  filters?: {
    status?: SharedLink['status']
    search?: string
  }
): SharedLink[] {
  let allLinks = [...MOCK_SHARED_LINKS, ...dynamicSharedLinks]
  
  // Update status based on expiration and populate assets
  allLinks = allLinks.map(link => {
    const updatedLink = { ...link }
    
    // Update status
    if (link.status !== 'revoked' && link.expires_date && new Date(link.expires_date) < new Date()) {
      updatedLink.status = 'expired' as const
    }
    
    // Populate assets with mock data if not already present
    if (!updatedLink.assets || updatedLink.assets.length === 0) {
      updatedLink.assets = generateMockAssets(updatedLink.asset_ids)
    }
    
    return updatedLink
  })
  
  // Apply filters
  if (filters?.status) {
    allLinks = allLinks.filter(link => link.status === filters.status)
  }
  
  if (filters?.search) {
    const searchLower = filters.search.toLowerCase()
    allLinks = allLinks.filter(link => 
      link.name.toLowerCase().includes(searchLower) ||
      link.slug.toLowerCase().includes(searchLower)
    )
  }
  
  // Sort by created_date desc
  allLinks.sort((a, b) => 
    new Date(b.created_date).getTime() - new Date(a.created_date).getTime()
  )
  
  return allLinks
}

/**
 * Get a single shared link by ID
 */
export function getMockSharedLinkById(id: number): SharedLink | undefined {
  return [...MOCK_SHARED_LINKS, ...dynamicSharedLinks].find(link => link.id === id)
}

/**
 * Get a single shared link by slug
 */
export function getMockSharedLinkBySlug(slug: string): SharedLink | undefined {
  return [...MOCK_SHARED_LINKS, ...dynamicSharedLinks].find(link => link.slug === slug)
}

/**
 * Create a new shared link
 */
export function createMockSharedLink(params: CreateSharedLinkParams): SharedLink {
  const slug = generateSlug()
  const newLink: SharedLink = {
    id: nextId++,
    name: params.name,
    slug,
    url: `${SHARE_BASE_URL}/${slug}`,
    asset_ids: params.asset_ids,
    is_public: params.is_public,
    password_protected: !!params.password,
    created_date: new Date().toISOString(),
    expires_date: params.expires_date || null,
    created_by: 'Текущий пользователь',
    created_by_id: 1,
    views: 0,
    downloads: 0,
    unique_visitors: 0,
    status: 'active',
    allow_download: params.allow_download,
    allow_comment: params.allow_comment
  }
  
  dynamicSharedLinks.unshift(newLink)
  return newLink
}

/**
 * Revoke (delete) a shared link
 */
export function revokeMockSharedLink(id: number): boolean {
  // Check in dynamic links first
  const dynamicIndex = dynamicSharedLinks.findIndex(link => link.id === id)
  if (dynamicIndex !== -1) {
    dynamicSharedLinks[dynamicIndex].status = 'revoked'
    return true
  }
  
  // Check in static links (just mark as revoked, don't actually delete)
  const staticLink = MOCK_SHARED_LINKS.find(link => link.id === id)
  if (staticLink) {
    staticLink.status = 'revoked'
    return true
  }
  
  return false
}

/**
 * Update a shared link
 */
export function updateMockSharedLink(
  id: number, 
  updates: Partial<Pick<SharedLink, 'name' | 'expires_date' | 'allow_download' | 'allow_comment'>>
): SharedLink | undefined {
  // Check in dynamic links
  const dynamicLink = dynamicSharedLinks.find(link => link.id === id)
  if (dynamicLink) {
    Object.assign(dynamicLink, updates)
    return dynamicLink
  }
  
  // Check in static links
  const staticLink = MOCK_SHARED_LINKS.find(link => link.id === id)
  if (staticLink) {
    Object.assign(staticLink, updates)
    return staticLink
  }
  
  return undefined
}

/**
 * Get asset IDs that are currently shared (active links only)
 */
export function getSharedAssetIds(): Set<number> {
  const allLinks = [...MOCK_SHARED_LINKS, ...dynamicSharedLinks]
  const activeLinks = allLinks.filter(link => link.status === 'active')
  const assetIds = new Set<number>()
  
  activeLinks.forEach(link => {
    link.asset_ids.forEach(id => assetIds.add(id))
  })
  
  return assetIds
}

/**
 * Check if a specific asset is shared
 */
export function isAssetShared(assetId: number): boolean {
  return getSharedAssetIds().has(assetId)
}

/**
 * Reset dynamic shared links (for testing)
 */
export function resetDynamicSharedLinks(): void {
  dynamicSharedLinks = []
  nextId = MOCK_SHARED_LINKS.length + 1
}

