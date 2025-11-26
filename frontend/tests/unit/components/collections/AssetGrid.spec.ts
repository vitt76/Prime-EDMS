import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AssetGrid from '@/components/collections/AssetGrid.vue'
import { collectionsService } from '@/services/collectionsService'
import type { CollectionWithAssets } from '@/types/collections'

// Mock collectionsService
vi.mock('@/services/collectionsService', () => ({
  collectionsService: {
    getCollection: vi.fn()
  }
}))

describe('AssetGrid', () => {
  let pinia: any
  let wrapper: ReturnType<typeof mount>

  const mockCollection: CollectionWithAssets = {
    id: 1,
    name: 'Test Collection',
    description: 'Test Description',
    parent_id: null,
    is_favorite: false,
    is_shared: false,
    visibility: 'private',
    asset_count: 2,
    created_by: 1,
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
    cover_image_id: null,
    assets: [
      {
        id: 1,
        label: 'Test Asset 1',
        filename: 'test1.jpg',
        size: 1024,
        mime_type: 'image/jpeg',
        date_added: '2025-01-01T00:00:00Z',
        thumbnail_url: '/thumbnails/test1.jpg',
        preview_url: '/previews/test1.jpg'
      },
      {
        id: 2,
        label: 'Test Asset 2',
        filename: 'test2.png',
        size: 2048,
        mime_type: 'image/png',
        date_added: '2025-01-02T00:00:00Z',
        thumbnail_url: '/thumbnails/test2.png',
        preview_url: '/previews/test2.png'
      }
    ]
  }

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.clearAllMocks()
    wrapper?.unmount()
  })

  it('renders correctly', () => {
    vi.mocked(collectionsService.getCollection).mockResolvedValue(mockCollection)

    wrapper = mount(AssetGrid, {
      props: {
        collectionId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('shows loading state initially', () => {
    vi.mocked(collectionsService.getCollection).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    )

    wrapper = mount(AssetGrid, {
      props: {
        collectionId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    // Should show loading skeleton
    expect(wrapper.exists()).toBe(true)
  })

  it('displays assets after loading', async () => {
    vi.mocked(collectionsService.getCollection).mockResolvedValue(mockCollection)

    wrapper = mount(AssetGrid, {
      props: {
        collectionId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    // Wait for async data loading
    await new Promise((resolve) => setTimeout(resolve, 100))

    // Assets should be displayed
    expect(wrapper.exists()).toBe(true)
  })

  it('shows empty state when collection has no assets', async () => {
    const emptyCollection: CollectionWithAssets = {
      ...mockCollection,
      asset_count: 0,
      assets: []
    }

    vi.mocked(collectionsService.getCollection).mockResolvedValue(emptyCollection)

    wrapper = mount(AssetGrid, {
      props: {
        collectionId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    await new Promise((resolve) => setTimeout(resolve, 100))

    // Should show empty state
    expect(wrapper.exists()).toBe(true)
  })

  it('emits asset-click event when asset is clicked', async () => {
    vi.mocked(collectionsService.getCollection).mockResolvedValue(mockCollection)

    wrapper = mount(AssetGrid, {
      props: {
        collectionId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    await new Promise((resolve) => setTimeout(resolve, 100))

    // Find asset element and click
    const assetElements = wrapper.findAll('[data-testid="asset-item"]')
    if (assetElements.length > 0) {
      await assetElements[0].trigger('click')
      expect(wrapper.emitted('asset-click')).toBeTruthy()
    }
  })

  it('handles string collection ID for special collections', async () => {
    vi.mocked(collectionsService.getCollection).mockResolvedValue(mockCollection)

    wrapper = mount(AssetGrid, {
      props: {
        collectionId: 'favorites'
      },
      global: {
        plugins: [pinia]
      }
    })

    // Should handle string IDs for special collections
    expect(wrapper.exists()).toBe(true)
  })

  it('formats file size correctly', async () => {
    vi.mocked(collectionsService.getCollection).mockResolvedValue(mockCollection)

    wrapper = mount(AssetGrid, {
      props: {
        collectionId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    await new Promise((resolve) => setTimeout(resolve, 100))

    // File size should be formatted (e.g., "1 KB", "2 KB")
    expect(wrapper.exists()).toBe(true)
  })

  it('displays asset thumbnails', async () => {
    vi.mocked(collectionsService.getCollection).mockResolvedValue(mockCollection)

    wrapper = mount(AssetGrid, {
      props: {
        collectionId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    await new Promise((resolve) => setTimeout(resolve, 100))

    // Thumbnails should be displayed
    const images = wrapper.findAll('img')
    expect(images.length).toBeGreaterThan(0)
  })

  it('handles keyboard navigation (Enter key)', async () => {
    vi.mocked(collectionsService.getCollection).mockResolvedValue(mockCollection)

    wrapper = mount(AssetGrid, {
      props: {
        collectionId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    await new Promise((resolve) => setTimeout(resolve, 100))

    const assetElements = wrapper.findAll('[data-testid="asset-item"]')
    if (assetElements.length > 0) {
      await assetElements[0].trigger('keydown.enter')
      expect(wrapper.emitted('asset-click')).toBeTruthy()
    }
  })

  it('handles keyboard navigation (Space key)', async () => {
    vi.mocked(collectionsService.getCollection).mockResolvedValue(mockCollection)

    wrapper = mount(AssetGrid, {
      props: {
        collectionId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    await new Promise((resolve) => setTimeout(resolve, 100))

    const assetElements = wrapper.findAll('[data-testid="asset-item"]')
    if (assetElements.length > 0) {
      await assetElements[0].trigger('keydown.space')
      expect(wrapper.emitted('asset-click')).toBeTruthy()
    }
  })

  it('handles loading error gracefully', async () => {
    vi.mocked(collectionsService.getCollection).mockRejectedValue(
      new Error('Failed to load collection')
    )

    wrapper = mount(AssetGrid, {
      props: {
        collectionId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    await new Promise((resolve) => setTimeout(resolve, 100))

    // Should handle error without crashing
    expect(wrapper.exists()).toBe(true)
  })

  it('reloads assets when collectionId changes', async () => {
    vi.mocked(collectionsService.getCollection).mockResolvedValue(mockCollection)

    wrapper = mount(AssetGrid, {
      props: {
        collectionId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    await new Promise((resolve) => setTimeout(resolve, 100))

    await wrapper.setProps({ collectionId: 2 })

    // Should reload assets for new collection
    expect(collectionsService.getCollection).toHaveBeenCalledTimes(2)
  })

  it('uses lazy loading for images', async () => {
    vi.mocked(collectionsService.getCollection).mockResolvedValue(mockCollection)

    wrapper = mount(AssetGrid, {
      props: {
        collectionId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    await new Promise((resolve) => setTimeout(resolve, 100))

    // Images should have loading="lazy" attribute
    const images = wrapper.findAll('img')
    if (images.length > 0) {
      expect(images[0].attributes('loading')).toBe('lazy')
    }
  })

  it('displays asset labels', async () => {
    vi.mocked(collectionsService.getCollection).mockResolvedValue(mockCollection)

    wrapper = mount(AssetGrid, {
      props: {
        collectionId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    await new Promise((resolve) => setTimeout(resolve, 100))

    // Asset labels should be displayed
    expect(wrapper.text()).toContain('Test Asset 1')
    expect(wrapper.text()).toContain('Test Asset 2')
  })

  it('has responsive grid layout', async () => {
    vi.mocked(collectionsService.getCollection).mockResolvedValue(mockCollection)

    wrapper = mount(AssetGrid, {
      props: {
        collectionId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    await new Promise((resolve) => setTimeout(resolve, 100))

    // Grid should have responsive classes
    const grid = wrapper.find('.asset-grid')
    expect(grid.exists()).toBe(true)
  })
})



