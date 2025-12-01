/**
 * Mock Data for Distribution/Sharing Feature
 * 
 * BACKEND ALIGNMENT:
 * - Added UUID field (matches Django's UUIDField)
 * - created_at/updated_at instead of just created_date
 * - access_count renamed from views for Django convention
 * - creator_id for foreign key relationship
 * 
 * AUDIT FIX: More realistic data structure matching Mayan EDMS patterns
 */

import type { Asset } from '@/types/api'

// ============================================================================
// TYPES
// ============================================================================

export interface SharedLink {
  id: number
  uuid: string                    // Django UUID field
  name: string
  slug: string
  url: string
  asset_ids: number[]
  assets?: Asset[]
  is_public: boolean
  password_protected: boolean
  password?: string
  created_date: string           // ISO timestamp
  updated_date?: string          // ISO timestamp  
  expires_date: string | null
  created_by: string             // Username
  created_by_id: number          // Foreign key
  views: number                  // access_count
  downloads: number
  unique_visitors: number
  status: 'active' | 'expired' | 'revoked'
  allow_download: boolean
  allow_comment: boolean
  
  // Additional Django-compatible fields
  ip_whitelist?: string[]
  domain_whitelist?: string[]
  max_downloads?: number | null
  watermark_enabled?: boolean
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

// ============================================================================
// HELPERS
// ============================================================================

function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = Math.random() * 16 | 0
    const v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
}

function generateSlug(): string {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
  let slug = ''
  for (let i = 0; i < 8; i++) {
    slug += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return slug
}

const SHARE_BASE_URL = 'https://dam.example.com/s/'

// Realistic thumbnail URLs
const THUMBNAIL_URLS = [
  'https://images.unsplash.com/photo-1682687220742-aba13b6e50ba?w=100&h=100&fit=crop',
  'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=100&h=100&fit=crop',
  'https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=100&h=100&fit=crop',
  'https://images.unsplash.com/photo-1426604966848-d7adac402bff?w=100&h=100&fit=crop',
  'https://images.unsplash.com/photo-1472214103451-9374bd1c798e?w=100&h=100&fit=crop',
  'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=100&h=100&fit=crop',
  'https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?w=100&h=100&fit=crop',
  'https://images.unsplash.com/photo-1433086966358-54859d0ed716?w=100&h=100&fit=crop',
  'https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=100&h=100&fit=crop',
  'https://images.unsplash.com/photo-1418065460487-3e41a6c84dc5?w=100&h=100&fit=crop',
]

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
  })) as Asset[]
}

// ============================================================================
// MOCK DATA - Realistic shared links
// ============================================================================

const MOCK_SHARED_LINKS: SharedLink[] = [
  {
    id: 1,
    uuid: 'f47ac10b-58cc-4372-a567-0e02b2c3d479',
    name: 'Пресс-кит продукта Q1 2025',
    slug: 'presskit-q1',
    url: `${SHARE_BASE_URL}presskit-q1`,
    asset_ids: [101, 102, 103, 104, 105],
    is_public: true,
    password_protected: false,
    created_date: new Date(Date.now() - 86400000 * 15).toISOString(),
    updated_date: new Date(Date.now() - 86400000 * 2).toISOString(),
    expires_date: new Date(Date.now() + 86400000 * 30).toISOString(),
    created_by: 'Анна Петрова',
    created_by_id: 1,
    views: 1247,
    downloads: 89,
    unique_visitors: 456,
    status: 'active',
    allow_download: true,
    allow_comment: false,
    watermark_enabled: true,
  },
  {
    id: 2,
    uuid: '550e8400-e29b-41d4-a716-446655440000',
    name: 'Фотосессия офиса для HR',
    slug: 'hr-photos',
    url: `${SHARE_BASE_URL}hr-photos`,
    asset_ids: [201, 202, 203],
    is_public: true,
    password_protected: true,
    password: 'hr2024',
    created_date: new Date(Date.now() - 86400000 * 30).toISOString(),
    expires_date: new Date(Date.now() - 86400000 * 5).toISOString(), // Expired
    created_by: 'Михаил Сидоров',
    created_by_id: 2,
    views: 523,
    downloads: 34,
    unique_visitors: 89,
    status: 'expired',
    allow_download: true,
    allow_comment: true,
  },
  {
    id: 3,
    uuid: '6ba7b810-9dad-11d1-80b4-00c04fd430c8',
    name: 'Логотипы и брендбук',
    slug: 'brandbook',
    url: `${SHARE_BASE_URL}brandbook`,
    asset_ids: [301, 302, 303, 304, 305, 306, 307],
    is_public: true,
    password_protected: false,
    created_date: new Date(Date.now() - 86400000 * 60).toISOString(),
    expires_date: null, // No expiration
    created_by: 'Елена Козлова',
    created_by_id: 3,
    views: 3421,
    downloads: 567,
    unique_visitors: 1234,
    status: 'active',
    allow_download: true,
    allow_comment: false,
    max_downloads: null,
  },
  {
    id: 4,
    uuid: '6ba7b811-9dad-11d1-80b4-00c04fd430c8',
    name: 'Видео с конференции TechDay',
    slug: 'techday-vid',
    url: `${SHARE_BASE_URL}techday-vid`,
    asset_ids: [401, 402],
    is_public: false,
    password_protected: true,
    password: 'techday2024',
    created_date: new Date(Date.now() - 86400000 * 7).toISOString(),
    expires_date: new Date(Date.now() + 86400000 * 5).toISOString(), // Expiring soon
    created_by: 'Дмитрий Иванов',
    created_by_id: 4,
    views: 156,
    downloads: 12,
    unique_visitors: 45,
    status: 'active',
    allow_download: true,
    allow_comment: true,
  },
  {
    id: 5,
    uuid: '6ba7b812-9dad-11d1-80b4-00c04fd430c8',
    name: 'Архив маркетинговых материалов 2023',
    slug: 'mkt-2023',
    url: `${SHARE_BASE_URL}mkt-2023`,
    asset_ids: [501, 502, 503, 504, 505, 506, 507, 508, 509, 510],
    is_public: true,
    password_protected: false,
    created_date: new Date(Date.now() - 86400000 * 120).toISOString(),
    expires_date: new Date(Date.now() - 86400000 * 30).toISOString(),
    created_by: 'Ольга Смирнова',
    created_by_id: 5,
    views: 892,
    downloads: 234,
    unique_visitors: 345,
    status: 'expired',
    allow_download: true,
    allow_comment: false,
  },
  {
    id: 6,
    uuid: '6ba7b813-9dad-11d1-80b4-00c04fd430c8',
    name: 'Фотографии для партнёров',
    slug: 'partners',
    url: `${SHARE_BASE_URL}partners`,
    asset_ids: [601, 602, 603, 604],
    is_public: true,
    password_protected: false,
    created_date: new Date(Date.now() - 86400000 * 3).toISOString(),
    expires_date: new Date(Date.now() + 86400000 * 14).toISOString(),
    created_by: 'Анна Петрова',
    created_by_id: 1,
    views: 67,
    downloads: 8,
    unique_visitors: 23,
    status: 'active',
    allow_download: true,
    allow_comment: false,
  },
  {
    id: 7,
    uuid: '6ba7b814-9dad-11d1-80b4-00c04fd430c8',
    name: 'Презентация для инвесторов',
    slug: 'investor-pres',
    url: `${SHARE_BASE_URL}investor-pres`,
    asset_ids: [701],
    is_public: false,
    password_protected: true,
    password: 'investor2024',
    created_date: new Date(Date.now() - 86400000 * 10).toISOString(),
    expires_date: new Date(Date.now() + 86400000 * 7).toISOString(),
    created_by: 'CEO Александр Волков',
    created_by_id: 6,
    views: 23,
    downloads: 5,
    unique_visitors: 8,
    status: 'active',
    allow_download: false,
    allow_comment: false,
    domain_whitelist: ['investor-corp.com', 'fund.example.com'],
  },
  {
    id: 8,
    uuid: '6ba7b815-9dad-11d1-80b4-00c04fd430c8',
    name: 'Инфографика для блога',
    slug: 'blog-info',
    url: `${SHARE_BASE_URL}blog-info`,
    asset_ids: [801, 802, 803],
    is_public: true,
    password_protected: false,
    created_date: new Date(Date.now() - 86400000 * 1).toISOString(),
    expires_date: new Date(Date.now() + 86400000 * 60).toISOString(),
    created_by: 'Контент-менеджер Ирина',
    created_by_id: 7,
    views: 12,
    downloads: 2,
    unique_visitors: 5,
    status: 'active',
    allow_download: true,
    allow_comment: true,
  },
  {
    id: 9,
    uuid: '6ba7b816-9dad-11d1-80b4-00c04fd430c8',
    name: 'Отзывная ссылка - тест',
    slug: 'test-revoked',
    url: `${SHARE_BASE_URL}test-revoked`,
    asset_ids: [901],
    is_public: true,
    password_protected: false,
    created_date: new Date(Date.now() - 86400000 * 45).toISOString(),
    expires_date: new Date(Date.now() + 86400000 * 30).toISOString(),
    created_by: 'Системный администратор',
    created_by_id: 8,
    views: 45,
    downloads: 3,
    unique_visitors: 12,
    status: 'revoked',
    allow_download: true,
    allow_comment: false,
  },
  {
    id: 10,
    uuid: '6ba7b817-9dad-11d1-80b4-00c04fd430c8',
    name: 'Социальные сети - Q4 контент',
    slug: 'social-q4',
    url: `${SHARE_BASE_URL}social-q4`,
    asset_ids: [1001, 1002, 1003, 1004, 1005, 1006],
    is_public: true,
    password_protected: false,
    created_date: new Date(Date.now() - 86400000 * 5).toISOString(),
    expires_date: new Date(Date.now() + 86400000 * 90).toISOString(),
    created_by: 'SMM Manager Катя',
    created_by_id: 9,
    views: 234,
    downloads: 45,
    unique_visitors: 78,
    status: 'active',
    allow_download: true,
    allow_comment: true,
  },
  {
    id: 11,
    uuid: '6ba7b818-9dad-11d1-80b4-00c04fd430c8',
    name: 'Пресс-релиз Q3 2024',
    slug: 'pr-q3-24',
    url: `${SHARE_BASE_URL}pr-q3-24`,
    asset_ids: [1101, 1102],
    is_public: true,
    password_protected: false,
    created_date: new Date(Date.now() - 86400000 * 90).toISOString(),
    expires_date: new Date(Date.now() - 86400000 * 60).toISOString(),
    created_by: 'PR Director Виктория',
    created_by_id: 10,
    views: 1567,
    downloads: 342,
    unique_visitors: 567,
    status: 'expired',
    allow_download: true,
    allow_comment: false,
  },
  {
    id: 12,
    uuid: '6ba7b819-9dad-11d1-80b4-00c04fd430c8',
    name: 'Каталог продукции 2025',
    slug: 'catalog-2025',
    url: `${SHARE_BASE_URL}catalog-2025`,
    asset_ids: [1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208],
    is_public: true,
    password_protected: false,
    created_date: new Date(Date.now() - 86400000 * 2).toISOString(),
    expires_date: null,
    created_by: 'Продакт-менеджер Артём',
    created_by_id: 11,
    views: 89,
    downloads: 23,
    unique_visitors: 34,
    status: 'active',
    allow_download: true,
    allow_comment: false,
    watermark_enabled: true,
    max_downloads: 500,
  },
]

// Dynamic storage for created links during session
const dynamicSharedLinks: SharedLink[] = []
let nextId = 100

// ============================================================================
// EXPORTED FUNCTIONS
// ============================================================================

export function getMockSharedLinks(
  filters?: {
    status?: SharedLink['status']
    search?: string
  }
): SharedLink[] {
  // Combine static and dynamic links
  let allLinks = [...MOCK_SHARED_LINKS, ...dynamicSharedLinks]
  
  // Update status based on expiration (auto-expire check)
  allLinks = allLinks.map(link => {
    const updatedLink = { ...link }
    
    // Check if expired (but not revoked)
    if (link.status !== 'revoked' && link.expires_date && new Date(link.expires_date) < new Date()) {
      updatedLink.status = 'expired' as const
    }
    
    // Populate assets if not present
    if (!updatedLink.assets || updatedLink.assets.length === 0) {
      updatedLink.assets = generateMockAssets(updatedLink.asset_ids)
    }
    
    return updatedLink
  })
  
  // Apply filters
  if (filters) {
    if (filters.status) {
      allLinks = allLinks.filter(link => link.status === filters.status)
    }
    
    if (filters.search) {
      const query = filters.search.toLowerCase()
      allLinks = allLinks.filter(link => 
        link.name.toLowerCase().includes(query) ||
        link.slug.toLowerCase().includes(query) ||
        link.created_by.toLowerCase().includes(query)
      )
    }
  }
  
  // Sort by created_date descending (newest first)
  allLinks.sort((a, b) => new Date(b.created_date).getTime() - new Date(a.created_date).getTime())
  
  return allLinks
}

export function getMockSharedLinkById(id: number): SharedLink | undefined {
  const allLinks = [...MOCK_SHARED_LINKS, ...dynamicSharedLinks]
  const link = allLinks.find(l => l.id === id)
  
  if (link && (!link.assets || link.assets.length === 0)) {
    return { ...link, assets: generateMockAssets(link.asset_ids) }
  }
  
  return link
}

export function getMockSharedLinkBySlug(slug: string): SharedLink | undefined {
  const allLinks = [...MOCK_SHARED_LINKS, ...dynamicSharedLinks]
  const link = allLinks.find(l => l.slug === slug)
  
  if (link && (!link.assets || link.assets.length === 0)) {
    return { ...link, assets: generateMockAssets(link.asset_ids) }
  }
  
  return link
}

export function createMockSharedLink(params: CreateSharedLinkParams): SharedLink {
  const slug = generateSlug()
  const uuid = generateUUID()
  
  const newLink: SharedLink = {
    id: nextId++,
    uuid,
    name: params.name || `Shared Link ${nextId}`,
    slug,
    url: `${SHARE_BASE_URL}${slug}`,
    asset_ids: params.asset_ids,
    assets: generateMockAssets(params.asset_ids),
    is_public: params.is_public,
    password_protected: !!params.password,
    password: params.password,
    created_date: new Date().toISOString(),
    updated_date: new Date().toISOString(),
    expires_date: params.expires_date || null,
    created_by: 'Текущий пользователь',
    created_by_id: 1,
    views: 0,
    downloads: 0,
    unique_visitors: 0,
    status: 'active',
    allow_download: params.allow_download,
    allow_comment: params.allow_comment,
  }
  
  dynamicSharedLinks.unshift(newLink)
  
  return newLink
}

export function revokeMockSharedLink(id: number): boolean {
  // Check dynamic links first
  const dynamicIndex = dynamicSharedLinks.findIndex(l => l.id === id)
  if (dynamicIndex !== -1) {
    dynamicSharedLinks[dynamicIndex].status = 'revoked'
    return true
  }
  
  // Check static links (mark in a separate array or modify behavior)
  const staticIndex = MOCK_SHARED_LINKS.findIndex(l => l.id === id)
  if (staticIndex !== -1) {
    MOCK_SHARED_LINKS[staticIndex].status = 'revoked'
    return true
  }
  
  return false
}

export function updateMockSharedLink(
  id: number, 
  updates: Partial<Pick<SharedLink, 'name' | 'expires_date' | 'allow_download' | 'allow_comment'>>
): SharedLink | undefined {
  // Find in dynamic links
  const dynamicIndex = dynamicSharedLinks.findIndex(l => l.id === id)
  if (dynamicIndex !== -1) {
    dynamicSharedLinks[dynamicIndex] = {
      ...dynamicSharedLinks[dynamicIndex],
      ...updates,
      updated_date: new Date().toISOString()
    }
    return dynamicSharedLinks[dynamicIndex]
  }
  
  // Find in static links
  const staticIndex = MOCK_SHARED_LINKS.findIndex(l => l.id === id)
  if (staticIndex !== -1) {
    MOCK_SHARED_LINKS[staticIndex] = {
      ...MOCK_SHARED_LINKS[staticIndex],
      ...updates,
      updated_date: new Date().toISOString()
    }
    return MOCK_SHARED_LINKS[staticIndex]
  }
  
  return undefined
}

export function getSharedAssetIds(): number[] {
  const allLinks = [...MOCK_SHARED_LINKS, ...dynamicSharedLinks]
    .filter(l => l.status === 'active')
  
  const assetIds = new Set<number>()
  allLinks.forEach(link => {
    link.asset_ids.forEach(id => assetIds.add(id))
  })
  
  return Array.from(assetIds)
}

export function isAssetShared(assetId: number): boolean {
  return getSharedAssetIds().includes(assetId)
}

export function resetDynamicSharedLinks(): void {
  dynamicSharedLinks.length = 0
  nextId = 100
}
