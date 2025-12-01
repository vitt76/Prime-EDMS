import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useSearchStore } from '@/stores/searchStore'
import { assetService } from '@/services/assetService'
import type { SearchResponse } from '@/types/api'

// Mock assetService
vi.mock('@/services/assetService', () => ({
  assetService: {
    searchAssets: vi.fn()
  }
}))

// Mock formatApiError
vi.mock('@/utils/errors', () => ({
  formatApiError: (err: any) => err.message || 'Unknown error'
}))

describe('searchStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('initializes with empty state', () => {
    const store = useSearchStore()

    expect(store.query).toBe('')
    expect(store.results).toEqual([])
    expect(store.totalCount).toBe(0)
    expect(store.isLoading).toBe(false)
    expect(store.error).toBeNull()
    expect(store.recentSearches).toEqual([])
    expect(store.savedSearches).toEqual([])
  })

  it('performs search successfully', async () => {
    const mockResponse: SearchResponse = {
      count: 2,
      results: [
        { id: 1, label: 'Asset 1', size: 1024, date_added: '2023-01-01', mime_type: 'image/jpeg' },
        { id: 2, label: 'Asset 2', size: 2048, date_added: '2023-01-02', mime_type: 'image/png' }
      ],
      facets: {}
    }

    ;(assetService.searchAssets as any).mockResolvedValue(mockResponse)

    const store = useSearchStore()
    await store.performSearch('test query', 8)

    expect(store.query).toBe('test query')
    expect(store.results).toEqual(mockResponse.results)
    expect(store.totalCount).toBe(2)
    expect(store.isLoading).toBe(false)
    expect(store.error).toBeNull()
    expect(store.hasResults).toBe(true)
  })

  it('does not perform search when query length < 2', async () => {
    const store = useSearchStore()
    await store.performSearch('t', 8)

    expect(store.results).toEqual([])
    expect(store.totalCount).toBe(0)
    expect(assetService.searchAssets).not.toHaveBeenCalled()
  })

  it('handles search errors', async () => {
    const error = new Error('Search failed')
    ;(assetService.searchAssets as any).mockRejectedValue(error)

    const store = useSearchStore()
    await store.performSearch('test query', 8)

    expect(store.error).toBe('Search failed')
    expect(store.results).toEqual([])
    expect(store.totalCount).toBe(0)
    expect(store.isLoading).toBe(false)
  })

  it('adds query to recent searches', async () => {
    const mockResponse: SearchResponse = {
      count: 0,
      results: [],
      facets: {}
    }
    ;(assetService.searchAssets as any).mockResolvedValue(mockResponse)

    const store = useSearchStore()
    await store.performSearch('test query', 8)

    expect(store.recentSearches).toContain('test query')
    expect(store.recentSearches.length).toBe(1)
  })

  it('limits recent searches to 5 items', async () => {
    const mockResponse: SearchResponse = {
      count: 0,
      results: [],
      facets: {}
    }
    ;(assetService.searchAssets as any).mockResolvedValue(mockResponse)

    const store = useSearchStore()

    for (let i = 1; i <= 7; i++) {
      await store.performSearch(`query ${i}`, 8)
    }

    expect(store.recentSearches.length).toBe(5)
    expect(store.recentSearches[0]).toBe('query 7')
    expect(store.recentSearches[4]).toBe('query 3')
  })

  it('removes duplicate from recent searches', async () => {
    const mockResponse: SearchResponse = {
      count: 0,
      results: [],
      facets: {}
    }
    ;(assetService.searchAssets as any).mockResolvedValue(mockResponse)

    const store = useSearchStore()
    await store.performSearch('query 1', 8)
    await store.performSearch('query 2', 8)
    await store.performSearch('query 1', 8) // Duplicate

    expect(store.recentSearches.length).toBe(2)
    expect(store.recentSearches[0]).toBe('query 1')
    expect(store.recentSearches[1]).toBe('query 2')
  })

  it('clears search results', () => {
    const store = useSearchStore()
    store.query = 'test'
    store.results = [{ id: 1, label: 'Test', size: 1024, date_added: '2023-01-01', mime_type: 'image/jpeg' }] as any
    store.totalCount = 1

    store.clearSearch()

    expect(store.query).toBe('')
    expect(store.results).toEqual([])
    expect(store.totalCount).toBe(0)
    expect(store.error).toBeNull()
  })

  it('performs advanced search with filters', async () => {
    const mockResponse: SearchResponse = {
      count: 5,
      results: [],
      facets: {
        type: { image: 3, video: 2 },
        tags: { nature: 4, city: 1 }
      }
    }
    ;(assetService.searchAssets as any).mockResolvedValue(mockResponse)

    const store = useSearchStore()
    await store.advancedSearch({
      q: 'test',
      filters: { type: ['image'] },
      sort: 'relevance',
      limit: 50,
      offset: 0
    })

    expect(store.results).toEqual([])
    expect(store.totalCount).toBe(5)
    expect(store.facets).toEqual(mockResponse.facets)
  })

  it('saves search to saved searches', () => {
    const store = useSearchStore()
    const searchId = store.saveSearch('My Search', 'test query', { type: ['image'] })

    expect(store.savedSearches.length).toBe(1)
    expect(store.savedSearches[0].name).toBe('My Search')
    expect(store.savedSearches[0].query).toBe('test query')
    expect(store.savedSearches[0].id).toBe(searchId)
  })

  it('deletes saved search', () => {
    const store = useSearchStore()
    const searchId = store.saveSearch('My Search', 'test query')

    expect(store.savedSearches.length).toBe(1)

    store.deleteSavedSearch(searchId)

    expect(store.savedSearches.length).toBe(0)
  })

  it('loads recent searches from localStorage', () => {
    localStorage.setItem('recent_searches', JSON.stringify(['query1', 'query2']))

    const store = useSearchStore()

    expect(store.recentSearches).toEqual(['query1', 'query2'])
  })

  it('loads saved searches from localStorage', () => {
    const savedSearches = [
      {
        id: 'saved-1',
        name: 'My Search',
        query: 'test',
        created_at: '2023-01-01T10:00:00Z'
      }
    ]
    localStorage.setItem('saved_searches', JSON.stringify(savedSearches))

    const store = useSearchStore()

    expect(store.savedSearches.length).toBe(1)
    expect(store.savedSearches[0].name).toBe('My Search')
  })

  it('computes facets summary correctly', () => {
    const store = useSearchStore()
    store.facets = {
      type: { image: 10, video: 5 },
      tags: { nature: 8, city: 7 }
    }

    const summary = store.facetsSummary

    expect(summary.type).toBe(15)
    expect(summary.tags).toBe(15)
  })

  it('returns correct result count', () => {
    const store = useSearchStore()
    store.totalCount = 42

    expect(store.resultCount).toBe(42)
  })

  it('returns hasResults correctly', () => {
    const store = useSearchStore()

    expect(store.hasResults).toBe(false)

    store.results = [{ id: 1, label: 'Test', size: 1024, date_added: '2023-01-01', mime_type: 'image/jpeg' }] as any

    expect(store.hasResults).toBe(true)
  })
})

