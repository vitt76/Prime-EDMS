import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAssetStore } from '@/stores/assetStore'
import { assetService } from '@/services/assetService'
import type { Asset, PaginatedResponse } from '@/types/api'

// Mock assetService
vi.mock('@/services/assetService', () => ({
  assetService: {
    getAssets: vi.fn(),
    getAsset: vi.fn()
  }
}))

const mockAssets: Asset[] = [
  {
    id: 1,
    label: 'Asset 1',
    filename: 'asset1.jpg',
    size: 1024,
    mime_type: 'image/jpeg',
    date_added: '2025-01-01T00:00:00Z'
  },
  {
    id: 2,
    label: 'Asset 2',
    filename: 'asset2.jpg',
    size: 2048,
    mime_type: 'image/jpeg',
    date_added: '2025-01-02T00:00:00Z'
  }
]

const mockPaginatedResponse: PaginatedResponse<Asset> = {
  count: 100,
  next: 'http://api.example.com/assets/?page=2',
  previous: null,
  results: mockAssets
}

describe('assetStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('initializes with default state', () => {
    const store = useAssetStore()
    
    expect(store.assets).toEqual([])
    expect(store.totalCount).toBe(0)
    expect(store.currentPage).toBe(1)
    expect(store.pageSize).toBe(50)
    expect(store.isLoading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('fetches assets successfully', async () => {
    vi.mocked(assetService.getAssets).mockResolvedValue(mockPaginatedResponse)
    
    const store = useAssetStore()
    await store.fetchAssets()
    
    expect(store.assets).toEqual(mockAssets)
    expect(store.totalCount).toBe(100)
    expect(store.isLoading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('handles fetch error', async () => {
    const error = { code: 'NETWORK_ERROR', message: 'Network error' }
    vi.mocked(assetService.getAssets).mockRejectedValue(error)
    
    const store = useAssetStore()
    
    try {
      await store.fetchAssets()
    } catch (e) {
      // Expected to throw
    }
    
    expect(store.assets).toEqual([])
    expect(store.error).toBeTruthy()
    expect(store.isLoading).toBe(false)
  })

  it('calculates hasNextPage correctly', async () => {
    vi.mocked(assetService.getAssets).mockResolvedValue(mockPaginatedResponse)
    
    const store = useAssetStore()
    await store.fetchAssets()
    
    expect(store.hasNextPage).toBe(true)
  })

  it('calculates hasPreviousPage correctly', () => {
    const store = useAssetStore()
    store.currentPage = 1
    
    expect(store.hasPreviousPage).toBe(false)
    
    store.currentPage = 2
    expect(store.hasPreviousPage).toBe(true)
  })

  it('navigates to next page', async () => {
    vi.mocked(assetService.getAssets).mockResolvedValue(mockPaginatedResponse)
    
    const store = useAssetStore()
    store.currentPage = 1
    store.totalCount = 100
    
    await store.nextPage()
    
    expect(store.currentPage).toBe(2)
    expect(assetService.getAssets).toHaveBeenCalled()
  })

  it('navigates to previous page', async () => {
    vi.mocked(assetService.getAssets).mockResolvedValue(mockPaginatedResponse)
    
    const store = useAssetStore()
    store.currentPage = 2
    
    await store.previousPage()
    
    expect(store.currentPage).toBe(1)
    expect(assetService.getAssets).toHaveBeenCalled()
  })

  it('selects asset correctly', () => {
    const store = useAssetStore()
    store.assets = mockAssets
    
    store.selectAsset(mockAssets[0], false)
    
    // Should contain the asset (check by id)
    const found = store.selectedAssets.find(a => a.id === mockAssets[0].id)
    expect(found).toBeTruthy()
    expect(store.selectedCount).toBe(1)
  })

  it('selects all assets', () => {
    const store = useAssetStore()
    store.assets = mockAssets
    
    store.selectAll()
    
    expect(store.selectedAssets.length).toBe(2)
  })

  it('clears selection', () => {
    const store = useAssetStore()
    store.selectedAssets = mockAssets
    
    store.clearSelection()
    
    expect(store.selectedAssets).toEqual([])
  })

  it('sets page size correctly', async () => {
    vi.mocked(assetService.getAssets).mockResolvedValue(mockPaginatedResponse)
    
    const store = useAssetStore()
    await store.setPageSize(25)
    
    expect(store.pageSize).toBe(25)
    expect(store.currentPage).toBe(1) // Should reset to first page
    expect(assetService.getAssets).toHaveBeenCalled()
  })

  it('applies filters correctly', async () => {
    vi.mocked(assetService.getAssets).mockResolvedValue(mockPaginatedResponse)
    
    const store = useAssetStore()
    await store.applyFilters({ type: 'image' })
    
    expect(store.filters.type).toBe('image')
    expect(store.currentPage).toBe(1) // Should reset to first page
    expect(assetService.getAssets).toHaveBeenCalled()
  })

  it('clears filters correctly', async () => {
    vi.mocked(assetService.getAssets).mockResolvedValue(mockPaginatedResponse)
    
    const store = useAssetStore()
    store.filters = { type: 'image' }
    
    await store.clearFilters()
    
    expect(store.filters).toEqual({})
    expect(store.currentPage).toBe(1)
  })
})

