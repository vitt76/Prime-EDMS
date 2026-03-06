import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render } from '@testing-library/vue'
import { axe } from 'vitest-axe'
import { createPinia, setActivePinia } from 'pinia'
import GalleryView from '@/components/DAM/GalleryView.vue'
import { useAssetStore } from '@/stores/assetStore'
import { useDistributionStore } from '@/stores/distributionStore'
import { useFavoritesStore } from '@/stores/favoritesStore'

vi.mock('@/services/apiService', () => ({
  apiService: {
    get: vi.fn().mockResolvedValue({ results: [] })
  }
}))

vi.mock('@/services/aiAnalysisService', () => ({
  aiAnalysisService: {
    runBulkAIAnalysis: vi.fn(),
    runAIAnalysis: vi.fn(),
    getAIAnalysis: vi.fn()
  }
}))

vi.mock('@/composables/useGalleryHotkeys', () => ({
  useGalleryHotkeys: vi.fn()
}))

vi.mock('@/services/savedSearchesService', () => ({
  createSavedSearch: vi.fn(),
  updateSavedSearch: vi.fn(),
  deleteSavedSearch: vi.fn()
}))

function createAsset(overrides: Record<string, unknown> = {}) {
  return {
    id: 1,
    label: 'Test Asset',
    filename: 'test-asset.jpg',
    size: 1024,
    mime_type: 'image/jpeg',
    date_added: '2025-01-01T00:00:00Z',
    thumbnail_url: 'https://example.com/thumb.jpg',
    tags: [],
    ...overrides
  }
}

describe('GalleryView Accessibility', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    const assetStore = useAssetStore()
    assetStore.assets = []
    assetStore.isLoading = false
    assetStore.error = null
    assetStore.isLoadingMore = false
    assetStore.totalCount = 0
    assetStore.currentPage = 1
    assetStore.pageSize = 50
    assetStore.availableTags = []
    assetStore.tagCounts = {}
    assetStore.typeCounts = {}
    assetStore.selectedAssets = new Set()
    assetStore.fetchAssets = vi.fn()
    assetStore.loadMore = vi.fn()
    assetStore.selectAll = vi.fn()
    assetStore.clearSelection = vi.fn()
    assetStore.toggleSelection = vi.fn()

    const distributionStore = useDistributionStore()
    distributionStore.sharedLinks = []
    distributionStore.sharedLinksLoading = false
    distributionStore.fetchSharedLinks = vi.fn()

    const favoritesStore = useFavoritesStore()
    favoritesStore.toggleFavorite = vi.fn()
    favoritesStore.isFavorite = vi.fn().mockReturnValue(false)
  })

  it('should have no accessibility violations with empty state', async () => {
    const { container } = render(GalleryView, {
      global: {
        stubs: {
          RecentlyViewedBlock: true,
          SavedSearchesDropdown: true,
          GalleryHeaderActions: true,
          AssetGrid: true,
          ImmersiveGrid: true
        }
      }
    })

    const results = await axe(container)
    expect(results.violations).toHaveLength(0)
  })

  it('should have proper ARIA labels for gallery list', async () => {
    const assetStore = useAssetStore()
    assetStore.assets = [createAsset()] as any
    assetStore.totalCount = 1

    const { container } = render(GalleryView, {
      global: {
        stubs: {
          RecentlyViewedBlock: true,
          SavedSearchesDropdown: true,
          GalleryHeaderActions: true,
          ImmersiveGrid: true
        }
      }
    })

    const list = container.querySelector('[role="list"]')
    expect(list).toHaveAttribute('aria-label', 'Галерея активов (comfortable density)')
    expect(container.querySelectorAll('[role="list"]').length).toBe(1)
    expect(container.querySelector('[role="listitem"]')).toBeInTheDocument()
  })

  it('should have proper keyboard navigation support', async () => {
    const assetStore = useAssetStore()
    assetStore.assets = [createAsset()] as any
    assetStore.totalCount = 1

    const { container } = render(GalleryView, {
      global: {
        stubs: {
          RecentlyViewedBlock: true,
          SavedSearchesDropdown: true,
          GalleryHeaderActions: true,
          ImmersiveGrid: true
        }
      }
    })

    const selectAllButton = container.querySelector('button[aria-label*="Выбрать все"]')
    expect(selectAllButton).toBeInTheDocument()
    const listitem = container.querySelector('[role="listitem"]')
    expect(listitem).toBeInTheDocument()
  })
})

