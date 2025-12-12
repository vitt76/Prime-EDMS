// @ts-nocheck
/**
 * Mock Search Data Layer
 * 
 * Provides autocomplete suggestions, recent searches, and facets
 * for the SmartSearch component.
 */

export interface SearchSuggestion {
  id: string
  type: 'asset' | 'collection' | 'tag' | 'query' | 'filter'
  label: string
  subtitle?: string
  icon?: string
  thumbnail?: string
  count?: number
  filter?: {
    key: string
    value: string
    label: string
  }
}

export interface SearchFilter {
  key: string
  label: string
  type: 'select' | 'multiselect' | 'date' | 'range'
  options?: { value: string; label: string; count?: number }[]
}

export interface RecentSearch {
  id: string
  query: string
  timestamp: Date
  resultCount: number
}

// ============================================================================
// SEARCH FILTERS CONFIGURATION
// ============================================================================

export const SEARCH_FILTERS: SearchFilter[] = [
  {
    key: 'type',
    label: 'Тип файла',
    type: 'multiselect',
    options: [
      { value: 'image', label: 'Изображения', count: 1250 },
      { value: 'video', label: 'Видео', count: 87 },
      { value: 'document', label: 'Документы', count: 342 },
      { value: 'audio', label: 'Аудио', count: 23 },
    ]
  },
  {
    key: 'orientation',
    label: 'Ориентация',
    type: 'select',
    options: [
      { value: 'landscape', label: 'Альбомная' },
      { value: 'portrait', label: 'Портретная' },
      { value: 'square', label: 'Квадрат' },
    ]
  },
  {
    key: 'date',
    label: 'Дата',
    type: 'select',
    options: [
      { value: 'today', label: 'Сегодня' },
      { value: 'week', label: 'На этой неделе' },
      { value: 'month', label: 'В этом месяце' },
      { value: 'year', label: 'В этом году' },
      { value: 'custom', label: 'Указать период...' },
    ]
  },
  {
    key: 'status',
    label: 'Статус',
    type: 'select',
    options: [
      { value: 'approved', label: 'Одобрено' },
      { value: 'pending', label: 'На модерации' },
      { value: 'draft', label: 'Черновик' },
    ]
  },
  {
    key: 'ai_analyzed',
    label: 'AI-анализ',
    type: 'select',
    options: [
      { value: 'yes', label: 'Проанализировано' },
      { value: 'no', label: 'Не проанализировано' },
    ]
  }
]

// ============================================================================
// MOCK RECENT SEARCHES (per user session)
// ============================================================================

let RECENT_SEARCHES: RecentSearch[] = [
  {
    id: '1',
    query: 'marketing banner 2025',
    timestamp: new Date(Date.now() - 1000 * 60 * 30),
    resultCount: 47
  },
  {
    id: '2',
    query: 'product photos hero',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2),
    resultCount: 123
  },
  {
    id: '3',
    query: 'type:video landscape',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24),
    resultCount: 15
  }
]

// ============================================================================
// AUTOCOMPLETE SUGGESTIONS DATABASE
// ============================================================================

const SUGGESTION_DATABASE: SearchSuggestion[] = [
  // Popular searches
  { id: 'q1', type: 'query', label: 'marketing materials', subtitle: '245 результатов', count: 245 },
  { id: 'q2', type: 'query', label: 'marketing campaign 2025', subtitle: '87 результатов', count: 87 },
  { id: 'q3', type: 'query', label: 'marketing banner', subtitle: '156 результатов', count: 156 },
  { id: 'q4', type: 'query', label: 'product photos', subtitle: '512 результатов', count: 512 },
  { id: 'q5', type: 'query', label: 'product video', subtitle: '34 результата', count: 34 },
  { id: 'q6', type: 'query', label: 'team photos', subtitle: '89 результатов', count: 89 },
  { id: 'q7', type: 'query', label: 'brand assets', subtitle: '234 результата', count: 234 },
  { id: 'q8', type: 'query', label: 'brand logo', subtitle: '45 результатов', count: 45 },
  { id: 'q9', type: 'query', label: 'social media', subtitle: '678 результатов', count: 678 },
  { id: 'q10', type: 'query', label: 'presentation slides', subtitle: '123 результата', count: 123 },
  
  // Tags
  { id: 't1', type: 'tag', label: 'hero-image', subtitle: 'Тег', count: 67 },
  { id: 't2', type: 'tag', label: 'banner', subtitle: 'Тег', count: 189 },
  { id: 't3', type: 'tag', label: 'campaign-2025', subtitle: 'Тег', count: 234 },
  { id: 't4', type: 'tag', label: 'approved', subtitle: 'Тег', count: 890 },
  { id: 't5', type: 'tag', label: 'website', subtitle: 'Тег', count: 456 },
  { id: 't6', type: 'tag', label: 'print', subtitle: 'Тег', count: 123 },
  { id: 't7', type: 'tag', label: 'social-media', subtitle: 'Тег', count: 345 },
  { id: 't8', type: 'tag', label: 'instagram', subtitle: 'Тег', count: 156 },
  
  // Collections
  { id: 'c1', type: 'collection', label: 'Маркетинг Q4 2025', subtitle: 'Коллекция • 45 активов', count: 45 },
  { id: 'c2', type: 'collection', label: 'Пресс-кит', subtitle: 'Коллекция • 23 актива', count: 23 },
  { id: 'c3', type: 'collection', label: 'Продуктовые фото', subtitle: 'Коллекция • 156 активов', count: 156 },
  { id: 'c4', type: 'collection', label: 'Корпоративный стиль', subtitle: 'Коллекция • 78 активов', count: 78 },
  { id: 'c5', type: 'collection', label: 'Видеоматериалы', subtitle: 'Коллекция • 34 актива', count: 34 },
  
  // Filter suggestions
  { id: 'f1', type: 'filter', label: 'Только изображения', subtitle: 'Фильтр', filter: { key: 'type', value: 'image', label: 'type:image' } },
  { id: 'f2', type: 'filter', label: 'Только видео', subtitle: 'Фильтр', filter: { key: 'type', value: 'video', label: 'type:video' } },
  { id: 'f3', type: 'filter', label: 'Альбомная ориентация', subtitle: 'Фильтр', filter: { key: 'orientation', value: 'landscape', label: 'orientation:landscape' } },
  { id: 'f4', type: 'filter', label: 'За сегодня', subtitle: 'Фильтр', filter: { key: 'date', value: 'today', label: 'date:today' } },
  { id: 'f5', type: 'filter', label: 'За эту неделю', subtitle: 'Фильтр', filter: { key: 'date', value: 'week', label: 'date:week' } },
  
  // Asset matches (for more specific queries)
  { 
    id: 'a1', 
    type: 'asset', 
    label: 'hero-banner-main.jpg', 
    subtitle: 'Изображение • 2.4 MB',
    thumbnail: 'https://images.unsplash.com/photo-1682687220742-aba13b6e50ba?w=60&h=60&fit=crop'
  },
  { 
    id: 'a2', 
    type: 'asset', 
    label: 'product-showcase.mp4', 
    subtitle: 'Видео • 45.2 MB',
    thumbnail: 'https://images.unsplash.com/photo-1536240478700-b869070f9279?w=60&h=60&fit=crop'
  },
  { 
    id: 'a3', 
    type: 'asset', 
    label: 'brand-guidelines.pdf', 
    subtitle: 'Документ • 12.8 MB',
    thumbnail: 'https://images.unsplash.com/photo-1568667256549-094345857637?w=60&h=60&fit=crop'
  },
]

// ============================================================================
// SEARCH FUNCTIONS
// ============================================================================

/**
 * Get autocomplete suggestions based on query
 */
export function getSearchSuggestions(query: string, limit: number = 8): SearchSuggestion[] {
  if (!query || query.length < 2) {
    return []
  }
  
  const normalizedQuery = query.toLowerCase().trim()
  
  // Split query into words for better matching
  const queryWords = normalizedQuery.split(/\s+/)
  
  const results = SUGGESTION_DATABASE
    .filter(item => {
      const labelLower = item.label.toLowerCase()
      // Match if all query words are found in label
      return queryWords.every(word => labelLower.includes(word))
    })
    .sort((a, b) => {
      // Prioritize by type: queries > tags > collections > assets > filters
      const typeOrder = { query: 0, tag: 1, collection: 2, asset: 3, filter: 4 }
      const typeCompare = typeOrder[a.type] - typeOrder[b.type]
      if (typeCompare !== 0) return typeCompare
      
      // Then by count (popularity)
      return (b.count || 0) - (a.count || 0)
    })
    .slice(0, limit)
  
  return results
}

/**
 * Get recent searches
 */
export function getRecentSearches(limit: number = 3): RecentSearch[] {
  return RECENT_SEARCHES
    .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
    .slice(0, limit)
}

/**
 * Add a search to recent history
 */
export function addRecentSearch(query: string, resultCount: number = 0): void {
  // Remove existing if same query
  RECENT_SEARCHES = RECENT_SEARCHES.filter(s => s.query.toLowerCase() !== query.toLowerCase())
  
  // Add new search
  RECENT_SEARCHES.unshift({
    id: `recent_${Date.now()}`,
    query,
    timestamp: new Date(),
    resultCount
  })
  
  // Keep only last 10
  if (RECENT_SEARCHES.length > 10) {
    RECENT_SEARCHES = RECENT_SEARCHES.slice(0, 10)
  }
}

/**
 * Clear recent search history
 */
export function clearRecentSearches(): void {
  RECENT_SEARCHES = []
}

/**
 * Remove a specific recent search
 */
export function removeRecentSearch(id: string): void {
  RECENT_SEARCHES = RECENT_SEARCHES.filter(s => s.id !== id)
}

/**
 * Get popular/trending searches
 */
export function getTrendingSearches(): SearchSuggestion[] {
  return SUGGESTION_DATABASE
    .filter(s => s.type === 'query')
    .sort((a, b) => (b.count || 0) - (a.count || 0))
    .slice(0, 5)
}

/**
 * Parse search query for filters
 * Example: "marketing type:image orientation:landscape"
 * Returns: { query: "marketing", filters: { type: "image", orientation: "landscape" } }
 */
export function parseSearchQuery(input: string): {
  query: string
  filters: Record<string, string>
} {
  const filters: Record<string, string> = {}
  let query = input
  
  // Match filter patterns like key:value
  const filterPattern = /(\w+):(\w+)/g
  let match: RegExpExecArray | null
  
  while ((match = filterPattern.exec(input)) !== null) {
    const [fullMatch, key, value] = match
    filters[key] = value
    query = query.replace(fullMatch, '')
  }
  
  return {
    query: query.trim(),
    filters
  }
}

/**
 * Build search URL with filters
 */
export function buildSearchUrl(query: string, filters: Record<string, string> = {}): string {
  const params = new URLSearchParams()
  
  if (query) {
    params.set('q', query)
  }
  
  Object.entries(filters).forEach(([key, value]) => {
    if (value) {
      params.set(key, value)
    }
  })
  
  return `/dam/search?${params.toString()}`
}

