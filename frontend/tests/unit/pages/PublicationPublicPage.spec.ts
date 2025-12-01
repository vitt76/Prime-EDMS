import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import PublicationPublicPage from '@/pages/PublicationPublicPage.vue'
import { distributionService } from '@/services/distributionService'
import type { Asset, Publication, PublicationChannel } from '@/types/api'

vi.mock('@/services/distributionService')

const mockAsset: Asset = {
  id: 101,
  label: 'Landscape',
  filename: 'landscape.png',
  size: 2_097_152,
  mime_type: 'image/png',
  thumbnail_url: 'https://cdn/landscape-thumb.png',
  preview_url: 'https://cdn/landscape-preview.png',
  date_added: '2025-05-01T00:00:00Z'
}

const mockPublication: Publication = {
  id: 900,
  title: 'Public Collection',
  description: 'Open access assets',
  status: 'published',
  analytics: {
    views: 420,
    downloads: 210,
    shares: 32
  },
  created_date: '2025-01-01T00:00:00Z',
  updated_date: '2025-01-05T00:00:00Z',
  created_by: 'admin',
  created_by_id: 1,
  channels: [] as PublicationChannel[],
  assets: [mockAsset]
}

const flushPromises = (): Promise<void> =>
  new Promise((resolve) => {
    setTimeout(resolve, 0)
  })

describe('PublicationPublicPage', () => {
  let wrapper: VueWrapper<any>
  let router: ReturnType<typeof createRouter>

  const setupRouter = () => {
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/public/publications/:token',
          name: 'publication-public',
          component: PublicationPublicPage
        }
      ]
    })
  }

  const mountComponent = async (token = 'public-token') => {
    await router.push({ name: 'publication-public', params: { token } })
    await router.isReady()

    wrapper = mount(PublicationPublicPage, {
      global: {
        plugins: [router],
        stubs: {
          Button: {
            props: ['variant', 'size', 'type', 'ariaLabel', 'disabled'],
            emits: ['click'],
            template: '<button :disabled="disabled" @click="$emit(\'click\')"><slot /></slot></button>'
          }
        }
      }
    })

    await flushPromises()
  }

  beforeEach(() => {
    setupRouter()
    const getPublicationMock = vi.mocked(distributionService.getPublicationByToken)
    getPublicationMock.mockClear()
    getPublicationMock.mockResolvedValue(mockPublication)

    const trackViewMock = vi.mocked(distributionService.trackPublicView)
    trackViewMock.mockClear()
    trackViewMock.mockResolvedValue(undefined)

    const trackDownloadMock = vi.mocked(distributionService.trackPublicDownload)
    trackDownloadMock.mockClear()
    trackDownloadMock.mockResolvedValue(undefined)
  })

  afterEach(() => {
    vi.clearAllMocks()
    wrapper?.unmount()
  })

  it('shows loading skeleton until data arrives', async () => {
    let resolvePromise: (value: typeof mockPublication) => void
    vi.mocked(distributionService.getPublicationByToken).mockImplementation(
      () =>
        new Promise((resolve) => {
          resolvePromise = resolve
        })
    )

    await mountComponent()
    expect(wrapper.find('.publication-public-page__loading').exists()).toBe(true)

    resolvePromise!(mockPublication)
    await flushPromises()

    expect(wrapper.find('.publication-public-page__loading').exists()).toBe(false)
  })

  it('renders publication title, description and stats', async () => {
    await mountComponent()

    expect(wrapper.text()).toContain(mockPublication.title)
    expect(wrapper.text()).toContain(mockPublication.description)
    expect(wrapper.text()).toContain('Views')
    expect(wrapper.text()).toContain('Downloads')
    expect(wrapper.find('.publication-public-page__asset-card').exists()).toBe(true)
  })

  it('tracks public view once per load', async () => {
    await mountComponent()

    expect(distributionService.trackPublicView).toHaveBeenCalledTimes(1)
    expect(distributionService.trackPublicView).toHaveBeenCalledWith('public-token')
  })

  it('re-fetches when the token changes', async () => {
    await mountComponent()
    await router.push({ name: 'publication-public', params: { token: 'new-token' } })
    await flushPromises()

    expect(distributionService.getPublicationByToken).toHaveBeenCalledTimes(2)
    expect(distributionService.getPublicationByToken).toHaveBeenLastCalledWith('new-token')
  })

  it('displays hero thumbnail from first asset', async () => {
    await mountComponent()
    const img = wrapper.find('.publication-public-page__hero-thumbnail img')
    expect(img.attributes('src')).toContain(mockAsset.thumbnail_url)
  })

  it('shows empty state when no assets are available', async () => {
    vi.mocked(distributionService.getPublicationByToken).mockResolvedValue({
      ...mockPublication,
      assets: []
    })

    await mountComponent()

    expect(wrapper.find('.publication-public-page__empty').exists()).toBe(true)
  })

  it('handles invalid token gracefully', async () => {
    await router.push({ name: 'publication-public', params: { token: '' } })
    await router.isReady()

    wrapper = mount(PublicationPublicPage, {
      global: {
        plugins: [router],
        stubs: {
          Button: true
        }
      }
    })
    await flushPromises()

    expect(wrapper.find('.publication-public-page__error').exists()).toBe(true)
    expect(wrapper.text()).toContain('Invalid or missing access token.')
  })

  it('shows error message when fetching fails', async () => {
    vi.mocked(distributionService.getPublicationByToken).mockRejectedValue(
      new Error('Not found')
    )
    await mountComponent()

    expect(wrapper.find('.publication-public-page__error').exists()).toBe(true)
    expect(wrapper.text()).toContain('Not found')
  })

  it('renders multiple assets correctly', async () => {
    const extendedAssets = [...mockPublication.assets, { ...mockAsset, id: 202, label: 'Second' }]
    vi.mocked(distributionService.getPublicationByToken).mockResolvedValue({
      ...mockPublication,
      assets: extendedAssets
    })

    await mountComponent()

    expect(wrapper.findAll('.publication-public-page__asset-card').length).toBe(2)
  })

  it('disables download when asset has no URLs', async () => {
    vi.mocked(distributionService.getPublicationByToken).mockResolvedValue({
      ...mockPublication,
      assets: [
        {
          id: 999,
          label: 'No URL',
          filename: 'ghost.pdf',
          size: 0,
          mime_type: 'application/pdf',
          date_added: '2025-01-03T00:00:00Z'
        }
      ]
    })

    await mountComponent()

    const button = wrapper.find('button')
    expect(button.attributes('disabled')).toBe('disabled')
  })

  it('downloads asset and tracks download events', async () => {
    await mountComponent()

    const appendSpy = vi.spyOn(document.body, 'appendChild')
    const removeSpy = vi.spyOn(document.body, 'removeChild')

    await wrapper.find('button').trigger('click')

    expect(appendSpy).toHaveBeenCalled()
    expect(removeSpy).toHaveBeenCalled()
    expect(distributionService.trackPublicDownload).toHaveBeenCalledWith(
      'public-token',
      mockAsset.id
    )

    appendSpy.mockRestore()
    removeSpy.mockRestore()
  })

  it('does not track download when no URL found', async () => {
    vi.mocked(distributionService.getPublicationByToken).mockResolvedValue({
      ...mockPublication,
      assets: [
        {
          id: 1,
          label: 'No URL',
          filename: 'ghost.pdf',
          size: 0,
          mime_type: 'application/pdf',
          date_added: '2025-01-06T00:00:00Z'
        }
      ]
    })

    await mountComponent()
    await wrapper.find('button').trigger('click')

    expect(distributionService.trackPublicDownload).not.toHaveBeenCalled()
  })

  it('shows stats formatted via formatBytes helper', async () => {
    await mountComponent()
    expect(wrapper.text()).toContain('2.0 MB')
  })

  it('tracking view errors are swallowed', async () => {
    vi.mocked(distributionService.trackPublicView).mockRejectedValue(new Error('boom'))
    await mountComponent()

    expect(wrapper.find('.publication-public-page__error').exists()).toBe(false)
  })

  it('handleAssetDownload uses preview when download_url missing', async () => {
    const previewOnlyAsset = {
      ...mockAsset,
      download_url: undefined,
      preview_url: 'https://preview',
      date_added: mockAsset.date_added
    }
    vi.mocked(distributionService.getPublicationByToken).mockResolvedValue({
      ...mockPublication,
      assets: [previewOnlyAsset]
    })

    await mountComponent()
    await wrapper.find('button').trigger('click')

    expect(distributionService.trackPublicDownload).toHaveBeenCalled()
  })

  it('formats bytes with fallback when value falsy', async () => {
    await mountComponent()

    const vm = wrapper.vm as any
    expect(vm.formatBytes(0)).toBe('—')
    expect(vm.formatBytes(undefined)).toBe('—')
  })
})

