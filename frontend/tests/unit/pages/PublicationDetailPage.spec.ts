import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import flushPromises from 'flush-promises'
import PublicationDetailPage from '@/pages/PublicationDetailPage.vue'
import { useAuthStore } from '@/stores/authStore'
import { useDistributionStore } from '@/stores/distributionStore'
import { useUIStore } from '@/stores/uiStore'
import { distributionService } from '@/services/distributionService'

vi.mock('@/stores/authStore')
vi.mock('@/stores/distributionStore')
vi.mock('@/stores/uiStore')
vi.mock('@/services/distributionService')

const mockPublication = {
  id: 42,
  title: 'Annual Report',
  description: 'Summary of 2025 results',
  status: 'published',
  created_date: '2025-01-01T00:00:00Z',
  updated_date: '2025-01-05T00:00:00Z',
  created_by_id: 1,
  analytics: {
    views: 12,
    downloads: 5,
    shares: 3
  },
  schedule: {
    start_date: '2025-02-01T00:00:00Z',
    end_date: '2025-02-07T00:00:00Z'
  },
  channels: [
    {
      id: 1,
      name: 'Email',
      type: 'email',
      status: 'active'
    }
  ],
  assets: [
    {
      id: 100,
      label: 'Cover Image',
      filename: 'cover.jpg',
      size: 1024 * 1024,
      mime_type: 'image/jpeg',
      thumbnail_url: 'https://cdn/cover-thumb.jpg',
      preview_url: 'https://cdn/cover-preview.jpg'
    }
  ]
} as const

describe('PublicationDetailPage', () => {
  let pinia: ReturnType<typeof createPinia>
  let router: ReturnType<typeof createRouter>
  let wrapper: ReturnType<typeof mount>

  const setupRouter = () => {
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/distribution', name: 'distribution', component: { template: '<div />' } },
        {
          path: '/distribution/publications/:id',
          name: 'publication-detail',
          component: PublicationDetailPage
        },
        { path: '/distribution/publications/:id/analytics', name: 'publication-analytics', component: { template: '<div />' } },
        { path: '/distribution/publications/:id/edit', name: 'publication-edit', component: { template: '<div />' } },
        { path: '/dam/assets/:id', name: 'asset-detail', component: { template: '<div />' } },
        { path: '/forbidden', name: 'forbidden', component: { template: '<div>Forbidden</div>' } }
      ]
    })
  }

  const mountComponent = async () => {
    await router.push({
      name: 'publication-detail',
      params: { id: String(mockPublication.id) }
    })
    await router.isReady()

    wrapper = mount(PublicationDetailPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div><slot /></div>' },
          Button: {
            props: ['variant', 'size', 'type', 'ariaLabel'],
            emits: ['click'],
            template: '<button @click="$emit(\'click\')"><slot /></slot></button>'
          },
          Badge: { template: '<span><slot /></slot></span>' },
          DeleteConfirmModal: { template: '<div />' },
          ShareLinksModal: { template: '<div />' }
        }
      }
    })
    await flushPromises()
  }

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    setupRouter()

    const authStore = useAuthStore()
    authStore.user = { id: 1, username: 'editor', email: 'editor@example.com', is_active: true }
    authStore.hasPermission = vi.fn().mockReturnValue(true)
    authStore.isAuthenticated = true
    authStore.checkAuth = vi.fn().mockResolvedValue(true)

    const distributionStore = useDistributionStore()
    distributionStore.getPublication = vi.fn().mockResolvedValue(mockPublication)
    distributionStore.deletePublication = vi.fn().mockResolvedValue(undefined)
    distributionStore.currentPublication = mockPublication as any

    const uiStore = useUIStore()
    uiStore.addNotification = vi.fn()

    ;(distributionService.getPublicationAnalytics as vi.Mock) = vi.fn().mockResolvedValue(
      mockPublication.analytics
    )
    ;(distributionService.getShareLinks as vi.Mock) = vi.fn().mockResolvedValue([])
  })

  afterEach(() => {
    vi.clearAllMocks()
    wrapper?.unmount()
  })

  it('renders loading skeleton while fetching', async () => {
    let resolvePublication: (value: typeof mockPublication) => void
    ;(useDistributionStore().getPublication as vi.Mock).mockImplementation(
      () =>
        new Promise((resolve) => {
          resolvePublication = resolve
        })
    )

    setupRouter()
    await router.push({ name: 'publication-detail', params: { id: String(mockPublication.id) } })
    await router.isReady()

    wrapper = mount(PublicationDetailPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: true,
          Button: true,
          Badge: true,
          DeleteConfirmModal: true,
          ShareLinksModal: true
        }
      }
    })

    expect(wrapper.find('.publication-detail-page__loading').exists()).toBe(true)

    resolvePublication!(mockPublication)
    await flushPromises()

    expect(wrapper.find('.publication-detail-page__loading').exists()).toBe(false)
  })

  it('renders publication metadata when load succeeds', async () => {
    await mountComponent()

    expect(wrapper.text()).toContain(mockPublication.title)
    expect(wrapper.text()).toContain('Summary of 2025 results')
    expect(wrapper.text()).toContain('Views')
    expect(wrapper.text()).toContain('Downloads')
    expect(wrapper.find('.publication-detail-page__asset-card').exists()).toBe(true)
  })

  it('shows error message when load fails', async () => {
    ;(useDistributionStore().getPublication as vi.Mock).mockRejectedValue(new Error('boom'))
    await mountComponent()

    expect(wrapper.find('.publication-detail-page__error').exists()).toBe(true)
    expect(wrapper.find('.publication-detail-page__error-message').text()).toContain('boom')
    expect(useUIStore().addNotification).toHaveBeenCalledWith(
      expect.objectContaining({ type: 'error' })
    )
  })

  it('redirects to forbidden when missing permission', async () => {
    const authStore = useAuthStore()
    authStore.hasPermission = vi.fn().mockReturnValue(false)

    const pushSpy = vi.spyOn(router, 'push')
    await mountComponent()

    expect(pushSpy).toHaveBeenCalledWith(
      expect.objectContaining({ name: 'forbidden', query: expect.any(Object) })
    )
  })

  it('shows edit and delete buttons for owner with permissions', async () => {
    await mountComponent()

    expect(wrapper.find('[aria-label="Edit publication"]').exists()).toBe(true)
    expect(wrapper.find('[aria-label="Delete publication"]').exists()).toBe(true)
  })

  it('opens share modal when share button clicked', async () => {
    await mountComponent()

    const shareButton = wrapper.find('[aria-label="Share publication"]')
    await shareButton.trigger('click')

    expect(wrapper.vm.showShareLinksModal).toBe(true)
  })

  it('navigates to analytics on button click', async () => {
    await mountComponent()
    const pushSpy = vi.spyOn(router, 'push')
    await wrapper.find('[aria-label="View full analytics"]').trigger('click')

    expect(pushSpy).toHaveBeenCalledWith(
      expect.objectContaining({ name: 'publication-analytics', params: { id: mockPublication.id } })
    )
  })

  it('navigates to edit page', async () => {
    await mountComponent()
    const pushSpy = vi.spyOn(router, 'push')
    await wrapper.vm.handleEdit()

    expect(pushSpy).toHaveBeenCalledWith(
      expect.objectContaining({ name: 'publication-edit', params: { id: mockPublication.id } })
    )
  })

  it('navigates back to distribution when back clicked', async () => {
    await mountComponent()
    const pushSpy = vi.spyOn(router, 'push')
    await wrapper.find('[aria-label="Go back"]').trigger('click')

    expect(pushSpy).toHaveBeenCalledWith(expect.objectContaining({ name: 'distribution' }))
  })

  it('navigates to asset detail when asset clicked', async () => {
    await mountComponent()
    const pushSpy = vi.spyOn(router, 'push')
    await wrapper.find('.publication-detail-page__asset-name').trigger('click')

    expect(pushSpy).toHaveBeenCalledWith(
      expect.objectContaining({ name: 'asset-detail', params: { id: mockPublication.assets[0].id } })
    )
  })

  it('successfully deletes publication and notifies', async () => {
    await mountComponent()
    const pushSpy = vi.spyOn(router, 'push')
    const distributionStore = useDistributionStore()

    await wrapper.vm.handleDelete()

    expect(distributionStore.deletePublication).toHaveBeenCalledWith(mockPublication.id)
    expect(useUIStore().addNotification).toHaveBeenCalledWith(
      expect.objectContaining({ type: 'success' })
    )
    expect(pushSpy).toHaveBeenCalledWith(expect.objectContaining({ name: 'distribution' }))
  })

  it('shows error when delete fails', async () => {
    const distributionStore = useDistributionStore()
    distributionStore.deletePublication = vi.fn().mockRejectedValue(new Error('boom'))
    await mountComponent()

    await wrapper.vm.handleDelete()

    expect(useUIStore().addNotification).toHaveBeenCalledWith(
      expect.objectContaining({ type: 'error' })
    )
  })

  it('downloads asset and notifies success', async () => {
    await mountComponent()
    const appendSpy = vi.spyOn(document.body, 'appendChild')
    const removeSpy = vi.spyOn(document.body, 'removeChild')

    await wrapper.vm.handleAssetDownload(mockPublication.assets[0].id)

    expect(appendSpy).toHaveBeenCalled()
    expect(removeSpy).toHaveBeenCalled()
    expect(useUIStore().addNotification).toHaveBeenCalledWith(
      expect.objectContaining({ type: 'success' })
    )
    appendSpy.mockRestore()
    removeSpy.mockRestore()
  })

  it('shows error when asset download missing', async () => {
    await mountComponent()

    await wrapper.vm.handleAssetDownload(999)

    expect(useUIStore().addNotification).toHaveBeenCalledWith(
      expect.objectContaining({ type: 'error', message: 'Asset not found' })
    )
  })

  it('downloads all assets and notifies', async () => {
    await mountComponent()
    vi.useFakeTimers()

    await wrapper.vm.handleDownloadAll()
    vi.runAllTimers()
    await flushPromises()

    expect(useUIStore().addNotification).toHaveBeenCalledWith(
      expect.objectContaining({ type: 'success' })
    )

    vi.useRealTimers()
  })

  it('formats schedule range correctly', async () => {
    await mountComponent()

    const result = wrapper.vm.formatSchedule(mockPublication.schedule)
    expect(result).toContain('Feb')
    expect(result).toContain('-')
  })
})
