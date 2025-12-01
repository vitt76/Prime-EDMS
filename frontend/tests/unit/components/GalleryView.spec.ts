import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import GalleryView from '@/components/DAM/GalleryView.vue'
import { useAssetStore } from '@/stores/assetStore'

// Mock assetService
vi.mock('@/services/assetService', () => ({
  assetService: {
    getAssets: vi.fn()
  }
}))

describe('GalleryView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders loading state', () => {
    const store = useAssetStore()
    store.isLoading = true
    store.assets = []

    const wrapper = mount(GalleryView)

    expect(wrapper.find('.animate-pulse').exists()).toBe(true)
  })

  it('renders error state', () => {
    const store = useAssetStore()
    store.error = 'Network error'
    store.assets = []

    const wrapper = mount(GalleryView)

    expect(wrapper.text()).toContain('Ошибка загрузки')
    expect(wrapper.text()).toContain('Network error')
  })

  it('renders empty state', () => {
    const store = useAssetStore()
    store.isLoading = false
    store.assets = []
    store.error = null

    const wrapper = mount(GalleryView)

    expect(wrapper.text()).toContain('Нет активов')
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

    const wrapper = mount(GalleryView)

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

    const wrapper = mount(GalleryView)

    const pagination = wrapper.findComponent({ name: 'Pagination' })
    expect(pagination.exists()).toBe(true)
  })
})

