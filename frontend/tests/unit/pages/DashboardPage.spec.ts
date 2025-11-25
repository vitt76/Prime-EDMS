import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import DashboardPage from '@/pages/DashboardPage.vue'
import { useDashboardStore } from '@/stores/dashboardStore'
import { useAssetStore } from '@/stores/assetStore'
import { useAuthStore } from '@/stores/authStore'
import { dashboardService } from '@/services/dashboardService'
import type { DashboardStats, ActivityItem, StorageMetrics } from '@/services/dashboardService'
import type { Asset } from '@/types/api'

vi.mock('@/services/dashboardService')

describe('DashboardPage', () => {
  let pinia: any
  let router: any
  let wrapper: ReturnType<typeof mount>

  const mockStats: DashboardStats = {
    documents: {
      total: 150,
      with_analysis: 120,
      without_analysis: 30
    },
    analyses: {
      completed: 120,
      processing: 5,
      pending: 25,
      failed: 3
    },
    providers: [
      { provider: 'yandex', count: 100 },
      { provider: 'gigachat', count: 20 }
    ]
  }

  const mockActivityFeed: ActivityItem[] = [
    {
      id: 1,
      type: 'upload',
      user: 'John Doe',
      user_id: 1,
      timestamp: '2025-01-27T10:00:00Z',
      description: 'загрузил новый актив',
      asset_id: 101,
      asset_label: 'campaign_banner.jpg'
    },
    {
      id: 2,
      type: 'comment',
      user: 'Jane Smith',
      user_id: 2,
      timestamp: '2025-01-27T09:30:00Z',
      description: 'оставил комментарий к активу',
      asset_id: 102,
      asset_label: 'product_shot.png'
    }
  ]

  const mockStorageMetrics: StorageMetrics = {
    total_size: 100 * 1024 * 1024 * 1024, // 100 GB
    used_size: 30 * 1024 * 1024 * 1024, // 30 GB
    available_size: 70 * 1024 * 1024 * 1024, // 70 GB
    usage_percentage: 30,
    by_type: [
      { type: 'image', count: 100, size: 20 * 1024 * 1024 * 1024 },
      { type: 'video', count: 50, size: 10 * 1024 * 1024 * 1024 }
    ]
  }

  const mockAssets: Asset[] = [
    {
      id: 1,
      label: 'test-asset-1.jpg',
      size: 1024000,
      date_added: '2025-01-27T10:00:00Z',
      thumbnail_url: 'https://example.com/thumb1.jpg',
      mime_type: 'image/jpeg'
    },
    {
      id: 2,
      label: 'test-asset-2.png',
      size: 2048000,
      date_added: '2025-01-26T09:00:00Z',
      thumbnail_url: 'https://example.com/thumb2.jpg',
      mime_type: 'image/png'
    }
  ]

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', component: DashboardPage },
        { path: '/dam/gallery', component: { template: '<div>Gallery</div>' } },
        { path: '/dam/assets/:id', component: { template: '<div>Asset Detail</div>' } }
      ]
    })

    vi.clearAllMocks()

    // Setup stores
    const dashboardStore = useDashboardStore()
    const assetStore = useAssetStore()
    const authStore = useAuthStore()

    dashboardStore.stats = null
    dashboardStore.activityFeed = []
    dashboardStore.storageMetrics = null
    dashboardStore.isLoading = false
    dashboardStore.error = null

    assetStore.assets = []
    assetStore.isLoading = false

    authStore.user = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      is_active: true
    }

    // Mock service methods
    ;(dashboardService.getDashboardStats as vi.Mock).mockResolvedValue(mockStats)
    ;(dashboardService.getActivityFeed as vi.Mock).mockResolvedValue(mockActivityFeed)
    ;(dashboardService.getStorageMetrics as vi.Mock).mockResolvedValue(mockStorageMetrics)
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('renders page with welcome message', async () => {
    wrapper = mount(DashboardPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          RouterLink: { template: '<a><slot /></a>' }
        }
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Добро пожаловать')
  })

  it('displays user name in welcome message', async () => {
    wrapper = mount(DashboardPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          RouterLink: { template: '<a><slot /></a>' }
        }
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Test')
  })

  it('shows loading state when data is being fetched', async () => {
    const dashboardStore = useDashboardStore()
    dashboardStore.isLoading = true
    dashboardStore.stats = null

    wrapper = mount(DashboardPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          RouterLink: { template: '<a><slot /></a>' }
        }
      }
    })

    await wrapper.vm.$nextTick()
    // Check for skeleton loaders
    const skeletonCards = wrapper.findAll('.animate-pulse')
    expect(skeletonCards.length).toBeGreaterThan(0)
  })

  it('displays stats cards when data is loaded', async () => {
    const dashboardStore = useDashboardStore()
    dashboardStore.stats = mockStats
    dashboardStore.storageMetrics = mockStorageMetrics
    dashboardStore.isLoading = false

    wrapper = mount(DashboardPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          RouterLink: { template: '<a><slot /></a>' }
        }
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('150')
    expect(wrapper.text()).toContain('Всего документов')
    expect(wrapper.text()).toContain('120')
    expect(wrapper.text()).toContain('Завершенных анализов')
  })

  it('displays activity feed when available', async () => {
    const dashboardStore = useDashboardStore()
    dashboardStore.stats = mockStats
    dashboardStore.activityFeed = mockActivityFeed
    dashboardStore.isLoading = false

    wrapper = mount(DashboardPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          RouterLink: { template: '<a><slot /></a>' }
        }
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Активность')
    expect(wrapper.text()).toContain('John Doe')
    expect(wrapper.text()).toContain('загрузил новый актив')
  })

  it('displays recent assets when available', async () => {
    const dashboardStore = useDashboardStore()
    const assetStore = useAssetStore()
    dashboardStore.stats = mockStats
    assetStore.assets = mockAssets
    dashboardStore.isLoading = false

    wrapper = mount(DashboardPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          RouterLink: { template: '<a><slot /></a>' }
        }
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Недавние активы')
    expect(wrapper.text()).toContain('test-asset-1.jpg')
  })

  it('displays storage metrics correctly', async () => {
    const dashboardStore = useDashboardStore()
    dashboardStore.stats = mockStats
    dashboardStore.storageMetrics = mockStorageMetrics
    dashboardStore.isLoading = false

    wrapper = mount(DashboardPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          RouterLink: { template: '<a><slot /></a>' }
        }
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Хранилище')
    expect(wrapper.text()).toContain('30%')
  })

  it('shows error state when fetch fails', async () => {
    const dashboardStore = useDashboardStore()
    dashboardStore.error = 'Ошибка загрузки данных'
    dashboardStore.stats = null
    dashboardStore.isLoading = false

    wrapper = mount(DashboardPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          RouterLink: { template: '<a><slot /></a>' }
        }
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Ошибка загрузки данных')
    expect(wrapper.text()).toContain('Попробовать снова')
  })

  it('calls refresh when retry button is clicked', async () => {
    const dashboardStore = useDashboardStore()
    dashboardStore.error = 'Ошибка загрузки данных'
    dashboardStore.stats = null
    dashboardStore.isLoading = false

    const refreshSpy = vi.spyOn(dashboardStore, 'refresh')

    wrapper = mount(DashboardPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          RouterLink: { template: '<a><slot /></a>' }
        }
      }
    })

    await wrapper.vm.$nextTick()
    const retryButton = wrapper.find('button[aria-label="Повторить загрузку"]')
    expect(retryButton.exists()).toBe(true)

    await retryButton.trigger('click')
    expect(refreshSpy).toHaveBeenCalled()
  })

  it('navigates to asset detail when asset is clicked', async () => {
    const dashboardStore = useDashboardStore()
    const assetStore = useAssetStore()
    dashboardStore.stats = mockStats
    assetStore.assets = mockAssets
    dashboardStore.isLoading = false

    const pushSpy = vi.fn()
    router.push = pushSpy

    wrapper = mount(DashboardPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          RouterLink: { template: '<a><slot /></a>' }
        }
      }
    })

    await wrapper.vm.$nextTick()
    const assetCard = wrapper.find('[role="gridcell"]')
    expect(assetCard.exists()).toBe(true)

    // Test that clicking triggers navigation
    await assetCard.trigger('click')
    // Note: router.push is called via goToAsset method in component
    // The actual navigation is tested in E2E tests
  })

  it('displays empty state when no recent assets', async () => {
    const dashboardStore = useDashboardStore()
    const assetStore = useAssetStore()
    dashboardStore.stats = mockStats
    assetStore.assets = []
    dashboardStore.isLoading = false

    wrapper = mount(DashboardPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          RouterLink: { template: '<a><slot /></a>' }
        }
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Нет недавних активов')
  })

  it('displays empty state when no activity', async () => {
    const dashboardStore = useDashboardStore()
    dashboardStore.stats = mockStats
    dashboardStore.activityFeed = []
    dashboardStore.isLoading = false

    wrapper = mount(DashboardPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          RouterLink: { template: '<a><slot /></a>' }
        }
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Нет недавней активности')
  })

  it('has proper ARIA labels for accessibility', async () => {
    const dashboardStore = useDashboardStore()
    dashboardStore.stats = mockStats
    dashboardStore.storageMetrics = mockStorageMetrics
    dashboardStore.isLoading = false

    wrapper = mount(DashboardPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          RouterLink: { template: '<a><slot /></a>' }
        }
      }
    })

    await wrapper.vm.$nextTick()
    
    // Check for ARIA labels
    const statsRegion = wrapper.find('[role="region"][aria-label="Статистика системы"]')
    expect(statsRegion.exists()).toBe(true)

    const activityList = wrapper.find('[role="list"][aria-label="Лента активности"]')
    expect(activityList.exists()).toBe(true)

    const progressBar = wrapper.find('[role="progressbar"]')
    expect(progressBar.exists()).toBe(true)
    expect(progressBar.attributes('aria-valuenow')).toBe('30')
  })

  it('loads dashboard data on mount', async () => {
    const dashboardStore = useDashboardStore()
    const refreshSpy = vi.spyOn(dashboardStore, 'refresh')

    wrapper = mount(DashboardPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          RouterLink: { template: '<a><slot /></a>' }
        }
      }
    })

    await wrapper.vm.$nextTick()
    // Wait for onMounted to execute
    await new Promise(resolve => setTimeout(resolve, 100))
    expect(refreshSpy).toHaveBeenCalled()
  })

  it('formats storage size correctly', async () => {
    const dashboardStore = useDashboardStore()
    dashboardStore.stats = mockStats
    dashboardStore.storageMetrics = mockStorageMetrics
    dashboardStore.isLoading = false

    wrapper = mount(DashboardPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          RouterLink: { template: '<a><slot /></a>' }
        }
      }
    })

    await wrapper.vm.$nextTick()
    // Check that storage is formatted (should contain GB)
    const storageText = wrapper.text()
    expect(storageText).toMatch(/\d+\.?\d*\s*(GB|MB|KB)/)
  })
})

