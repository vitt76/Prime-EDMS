import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import GalleryView from '@/components/DAM/GalleryView.vue'
import { useAssetStore } from '@/stores/assetStore'

// Mock assetService
vi.mock('@/services/assetService', () => ({
  assetService: {
    getAssets: vi.fn()
  }
}))

const router = createRouter({
  history: createMemoryHistory('/'),
  routes: [{ path: '/', component: { template: '<div />' } }]
})

describe('GalleryView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    if (!document.getElementById('header-actions')) {
      const el = document.createElement('div')
      el.id = 'header-actions'
      document.body.appendChild(el)
    }
    if (!document.getElementById('header-search')) {
      const el = document.createElement('div')
      el.id = 'header-search'
      document.body.appendChild(el)
    }
  })

  function mountGalleryView() {
    return mount(GalleryView, {
      global: {
        plugins: [router],
        stubs: { RouterLink: true }
      }
    })
  }

  it('renders loading state', () => {
    const store = useAssetStore()
    store.isLoading = true
    store.assets = []

    const wrapper = mountGalleryView()

    expect(wrapper.find('.animate-pulse').exists()).toBe(true)
  })

  it('renders error state', () => {
    const store = useAssetStore()
    store.error = 'Network error'
    store.assets = []

    const wrapper = mountGalleryView()

    expect(wrapper.text()).toContain('Ошибка загрузки')
    expect(wrapper.text()).toContain('Network error')
  })

  it('renders empty state', () => {
    const store = useAssetStore()
    store.isLoading = false
    store.assets = []
    store.error = null

    const wrapper = mountGalleryView()

    expect(wrapper.text()).toContain('Библиотека пуста')
  })

  it('renders assets grid', () => {
    const store = useAssetStore()
    store.assets = [
      {
        id: 1,
        label: 'Asset 1',
        filename: 'asset1.jpg',
        size: 1024,
        mime_type: 'image/jpeg',
        date_added: '2025-01-01T00:00:00Z'
      }
    ]
    store.isLoading = false
    store.error = null

    const wrapper = mountGalleryView()

    expect(wrapper.find('.gallery-content').exists()).toBe(true)
  })

  it('renders pagination when assets exist', () => {
    const store = useAssetStore()
    store.assets = [
      {
        id: 1,
        label: 'Asset 1',
        filename: 'asset1.jpg',
        size: 1024,
        mime_type: 'image/jpeg',
        date_added: '2025-01-01T00:00:00Z'
      }
    ]
    store.totalCount = 100
    store.isLoading = false

    const wrapper = mountGalleryView()

    const hasPagination =
      wrapper.findComponent({ name: 'Pagination' }).exists() ||
      wrapper.find('[class*="pagination"]').exists()
    expect(hasPagination).toBe(true)
  })
})

