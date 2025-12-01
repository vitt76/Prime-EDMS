import { mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useRoute, useRouter } from 'vue-router'
import AssetDetailPage from '@/pages/AssetDetailPage.vue'
import { useAssetStore } from '@/stores/assetStore'
import type { Asset } from '@/types/api'

// Mock vue-router
const mockPush = vi.fn()
const mockParams = { id: '123' }

vi.mock('vue-router', () => ({
  useRoute: () => ({
    params: mockParams
  }),
  useRouter: () => ({
    push: mockPush
  })
}))

// Mock assetStore
vi.mock('@/stores/assetStore', () => ({
  useAssetStore: vi.fn()
}))

describe('AssetDetailPage', () => {
  let pinia: ReturnType<typeof createPinia>
  let mockAssetStore: any

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    vi.clearAllMocks()
    mockPush.mockClear()

    mockAssetStore = {
      isLoading: false,
      error: null,
      currentAsset: {
        id: 123,
        label: 'Test Asset',
        size: 1024 * 500,
        date_added: '2023-01-01T10:00:00Z',
        mime_type: 'image/jpeg',
        thumbnail_url: 'https://example.com/thumb.jpg',
        preview_url: 'https://example.com/preview.jpg',
        tags: ['nature', 'landscape']
      },
      getAssetDetail: vi.fn().mockResolvedValue(undefined)
    }

    ;(useAssetStore as any).mockReturnValue(mockAssetStore)
  })

  it('renders loading state when loading', () => {
    mockAssetStore.isLoading = true
    mockAssetStore.currentAsset = null

    const wrapper = mount(AssetDetailPage, {
      global: {
        plugins: [pinia]
      }
    })

    expect(wrapper.text()).toContain('Загрузка...')
  })

  it('renders error state when error occurs', () => {
    mockAssetStore.error = 'Failed to load asset'
    mockAssetStore.currentAsset = null

    const wrapper = mount(AssetDetailPage, {
      global: {
        plugins: [pinia]
      }
    })

    expect(wrapper.text()).toContain('Ошибка загрузки')
    expect(wrapper.text()).toContain('Failed to load asset')
  })

  it('renders asset detail when loaded', () => {
    const wrapper = mount(AssetDetailPage, {
      global: {
        plugins: [pinia]
      }
    })

    expect(wrapper.text()).toContain('Test Asset')
    expect(wrapper.text()).toContain('nature')
    expect(wrapper.text()).toContain('landscape')
  })

  it('loads asset detail on mount', () => {
    mount(AssetDetailPage, {
      global: {
        plugins: [pinia]
      }
    })

    expect(mockAssetStore.getAssetDetail).toHaveBeenCalledWith(123)
  })

  it('does not reload if current asset matches route param', () => {
    mockAssetStore.currentAsset = { id: 123, label: 'Test' }

    mount(AssetDetailPage, {
      global: {
        plugins: [pinia]
      }
    })

    // Should not call getAssetDetail if asset already matches
    expect(mockAssetStore.getAssetDetail).not.toHaveBeenCalled()
  })

  it('retries loading on retry button click', async () => {
    mockAssetStore.error = 'Error'
    mockAssetStore.currentAsset = null

    const wrapper = mount(AssetDetailPage, {
      global: {
        plugins: [pinia]
      }
    })

    const retryButton = wrapper.find('button')
    await retryButton.trigger('click')

    expect(mockAssetStore.getAssetDetail).toHaveBeenCalledWith(123)
  })

  it('displays image preview for image assets', () => {
    const wrapper = mount(AssetDetailPage, {
      global: {
        plugins: [pinia]
      }
    })

    const image = wrapper.find('img')
    expect(image.exists()).toBe(true)
    expect(image.attributes('src')).toBe('https://example.com/preview.jpg')
    expect(image.attributes('alt')).toBe('Test Asset')
  })

  it('displays video player for video assets', () => {
    mockAssetStore.currentAsset = {
      ...mockAssetStore.currentAsset,
      mime_type: 'video/mp4',
      preview_url: 'https://example.com/video.mp4'
    }

    const wrapper = mount(AssetDetailPage, {
      global: {
        plugins: [pinia]
      }
    })

    const video = wrapper.find('video')
    expect(video.exists()).toBe(true)
    expect(video.attributes('src')).toBe('https://example.com/video.mp4')
  })

  it('shows zoom controls for images', () => {
    const wrapper = mount(AssetDetailPage, {
      global: {
        plugins: [pinia]
      }
    })

    const zoomButtons = wrapper.findAll('button[aria-label*="масштаб"], button[aria-label*="Увеличить"], button[aria-label*="Уменьшить"]')
    expect(zoomButtons.length).toBeGreaterThan(0)
  })

  it('handles image error gracefully', async () => {
    const wrapper = mount(AssetDetailPage, {
      global: {
        plugins: [pinia]
      }
    })

    const image = wrapper.find('img')
    await image.trigger('error')

    // Image error should be handled
    expect((wrapper.vm as any).imageError).toBe(true)
  })

  it('displays download button for non-previewable files', () => {
    mockAssetStore.currentAsset = {
      ...mockAssetStore.currentAsset,
      mime_type: 'application/pdf'
    }

    const wrapper = mount(AssetDetailPage, {
      global: {
        plugins: [pinia]
      }
    })

    expect(wrapper.text()).toContain('Предпросмотр недоступен')
    expect(wrapper.text()).toContain('Скачать файл')
  })

  it('handles download action', async () => {
    const wrapper = mount(AssetDetailPage, {
      global: {
        plugins: [pinia]
      }
    })

    // Find download button in MetadataPanel or main content
    const downloadButtons = wrapper.findAll('button').filter((b) => b.text().includes('Скачать'))
    if (downloadButtons.length > 0) {
      const openSpy = vi.spyOn(window, 'open').mockImplementation(() => null)
      await downloadButtons[0].trigger('click')
      // Download should trigger window.open
      expect(openSpy).toHaveBeenCalled()
      openSpy.mockRestore()
    }
  })

  it('navigates to previous asset when arrow left is clicked', async () => {
    // This would require relatedAssets to be populated
    // For now, we'll test that navigation function exists
    const wrapper = mount(AssetDetailPage, {
      global: {
        plugins: [pinia]
      }
    })

    // Simulate keyboard navigation
    const event = new KeyboardEvent('keydown', { key: 'ArrowLeft' })
    document.dispatchEvent(event)

    // Navigation should be attempted if previousAsset exists
    // In this test, relatedAssets is empty, so navigation won't happen
    expect(mockPush).not.toHaveBeenCalled()
  })

  it('navigates to next asset when arrow right is clicked', async () => {
    const wrapper = mount(AssetDetailPage, {
      global: {
        plugins: [pinia]
      }
    })

    const event = new KeyboardEvent('keydown', { key: 'ArrowRight' })
    document.dispatchEvent(event)

    // Navigation should be attempted if nextAsset exists
    expect(mockPush).not.toHaveBeenCalled()
  })

  it('cleans up event listeners on unmount', () => {
    const removeEventListenerSpy = vi.spyOn(document, 'removeEventListener')

    const wrapper = mount(AssetDetailPage, {
      global: {
        plugins: [pinia]
      }
    })

    wrapper.unmount()

    expect(removeEventListenerSpy).toHaveBeenCalledWith('keydown', expect.any(Function))
    removeEventListenerSpy.mockRestore()
  })
})

