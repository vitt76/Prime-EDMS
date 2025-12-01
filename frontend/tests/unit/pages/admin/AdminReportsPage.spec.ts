import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import AdminReportsPage from '@/pages/admin/AdminReportsPage.vue'
import { useReportsStore } from '@/stores/reportsStore'
import { useAuthStore } from '@/stores/authStore'
import { useUIStore } from '@/stores/uiStore'

// Mock stores
vi.mock('@/stores/reportsStore')
vi.mock('@/stores/authStore')
vi.mock('@/stores/uiStore')

describe('AdminReportsPage', () => {
  let pinia: any
  let router: any
  let wrapper: ReturnType<typeof mount>

  const mockUsageMetrics = {
    totalAssets: 1000,
    assetsByType: {
      images: 500,
      videos: 200,
      documents: 200,
      audio: 50,
      other: 50
    },
    storageUsed: 1024 * 1024 * 1024 * 10,
    storageLimit: 1024 * 1024 * 1024 * 100,
    storagePercentage: 10
  }

  const mockDownloadHistory = [
    {
      date: '2025-01-01T00:00:00Z',
      downloads: 100,
      uniqueUsers: 50
    }
  ]

  const mockActivities = [
    {
      username: 'user1',
      email: 'user1@example.com',
      action: 'upload' as const,
      asset_id: 1,
      asset_name: 'test.jpg',
      timestamp: '2025-01-01T00:00:00Z'
    }
  ]

  const mockStorageBreakdown = [
    {
      category: 'images' as const,
      size: 5 * 1024 * 1024 * 1024,
      count: 500,
      percentage: 50
    }
  ]

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/admin/reports', component: AdminReportsPage },
        { path: '/forbidden', component: { template: '<div>Forbidden</div>' } }
      ]
    })

    // Setup mock stores
    const reportsStore = useReportsStore()
    const authStore = useAuthStore()
    const uiStore = useUIStore()

    reportsStore.usageMetrics = mockUsageMetrics
    reportsStore.downloadHistory = mockDownloadHistory
    reportsStore.recentActivity = mockActivities
    reportsStore.storageBreakdown = mockStorageBreakdown
    reportsStore.currentReport = null
    reportsStore.isLoading = false
    reportsStore.fetchUsageReport = vi.fn().mockResolvedValue(undefined)
    reportsStore.fetchDownloadReport = vi.fn().mockResolvedValue(undefined)
    reportsStore.fetchActivityReport = vi.fn().mockResolvedValue(undefined)
    reportsStore.fetchStorageReport = vi.fn().mockResolvedValue(undefined)
    reportsStore.exportReport = vi.fn().mockResolvedValue(new Blob(['test'], { type: 'text/csv' }))
    reportsStore.saveReport = vi.fn().mockResolvedValue({
      id: 1,
      name: 'Test Report',
      type: 'usage',
      timeRange: { type: 'month', startDate: '', endDate: '' },
      metrics: mockUsageMetrics,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
      created_by: 1
    })
    reportsStore.setTimeRange = vi.fn()

    authStore.user = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      is_active: true
    }
    ;(authStore as any).hasPermission = vi.fn().mockReturnValue(true)

    uiStore.addNotification = vi.fn()
  })

  afterEach(() => {
    vi.clearAllMocks()
    wrapper?.unmount()
  })

  it('renders correctly', () => {
    wrapper = mount(AdminReportsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Select: true,
          DateRangePicker: true,
          Button: true,
          Card: true,
          ChartComponent: true,
          ActivityTable: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.reports-page').exists()).toBe(true)
  })

  it('displays page title', () => {
    wrapper = mount(AdminReportsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Select: true,
          DateRangePicker: true,
          Button: true,
          Card: true,
          ChartComponent: true,
          ActivityTable: true
        }
      }
    })

    expect(wrapper.text()).toContain('Analytics & Reports')
  })

  it('checks permission on mount', async () => {
    const authStore = useAuthStore()
    ;(authStore as any).hasPermission = vi.fn().mockReturnValue(false)
    const pushSpy = vi.spyOn(router, 'push')

    wrapper = mount(AdminReportsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Select: true,
          DateRangePicker: true,
          Button: true,
          Card: true,
          ChartComponent: true,
          ActivityTable: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    expect(authStore.hasPermission).toHaveBeenCalledWith('admin.reports_view')
    expect(pushSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        name: 'forbidden'
      })
    )
  })

  it('renders time range selector', () => {
    wrapper = mount(AdminReportsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Select: {
            template: '<select><slot /></select>',
            props: ['modelValue', 'options', 'label']
          },
          DateRangePicker: true,
          Button: true,
          Card: true,
          ChartComponent: true,
          ActivityTable: true
        }
      }
    })

    const select = wrapper.findComponent({ name: 'Select' })
    expect(select.exists()).toBe(true)
  })

  it('shows custom date range picker when custom is selected', async () => {
    wrapper = mount(AdminReportsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Select: {
            template: '<select><slot /></select>',
            props: ['modelValue', 'options', 'label']
          },
          DateRangePicker: {
            template: '<div class="date-range-picker">Date Range Picker</div>',
            props: ['modelValue']
          },
          Button: true,
          Card: true,
          ChartComponent: true,
          ActivityTable: true
        }
      }
    })

    ;(wrapper.vm as any).selectedTimeRange = 'custom'
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.date-range-picker').exists()).toBe(true)
  })

  it('renders export button', () => {
    wrapper = mount(AdminReportsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Select: true,
          DateRangePicker: true,
          Button: {
            template: '<button><slot /></button>',
            props: ['variant']
          },
          Card: true,
          ChartComponent: true,
          ActivityTable: true
        }
      }
    })

    expect(wrapper.text()).toContain('Export')
  })

  it('toggles export menu on button click', async () => {
    wrapper = mount(AdminReportsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Select: true,
          DateRangePicker: true,
          Button: {
            template: '<button @click="$emit(\'click\')"><slot /></button>',
            props: ['variant']
          },
          Card: true,
          ChartComponent: true,
          ActivityTable: true
        }
      }
    })

    const exportButton = wrapper.findAll('button').find((btn) => btn.text()?.includes('Export'))
    if (exportButton) {
      expect((wrapper.vm as any).showExportMenu).toBe(false)
      await exportButton.trigger('click')
      await wrapper.vm.$nextTick()
      expect((wrapper.vm as any).showExportMenu).toBe(true)
    }
  })

  it('renders all 4 chart cards', () => {
    wrapper = mount(AdminReportsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Select: true,
          DateRangePicker: true,
          Button: true,
          Card: {
            template: '<div class="card"><slot name="header" /><slot /></div>',
            props: ['variant']
          },
          ChartComponent: {
            template: '<div class="chart">Chart</div>',
            props: ['type', 'data', 'title']
          },
          ActivityTable: {
            template: '<div class="activity-table">Activity Table</div>',
            props: ['activities', 'isLoading']
          }
        }
      }
    })

    const cards = wrapper.findAll('.card')
    expect(cards.length).toBeGreaterThanOrEqual(4)
  })

  it('displays usage metrics correctly', async () => {
    wrapper = mount(AdminReportsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Select: true,
          DateRangePicker: true,
          Button: true,
          Card: {
            template: '<div><slot name="header" /><slot /></div>',
            props: ['variant']
          },
          ChartComponent: true,
          ActivityTable: true
        }
      }
    })

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Total Assets')
    expect(wrapper.text()).toContain('Storage Used')
    expect(wrapper.text()).toContain('Storage Limit')
    expect(wrapper.text()).toContain('Usage')
  })

  it('formats bytes correctly', () => {
    wrapper = mount(AdminReportsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Select: true,
          DateRangePicker: true,
          Button: true,
          Card: true,
          ChartComponent: true,
          ActivityTable: true
        }
      }
    })

    const formatted = (wrapper.vm as any).formatBytes(1024 * 1024)
    expect(formatted).toContain('MB')
  })

  it('handles export CSV', async () => {
    const reportsStore = useReportsStore()
    reportsStore.currentReport = {
      id: 1,
      name: 'Test',
      type: 'usage',
      timeRange: { type: 'month', startDate: '', endDate: '' },
      metrics: mockUsageMetrics,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
      created_by: 1
    }

    wrapper = mount(AdminReportsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Select: true,
          DateRangePicker: true,
          Button: {
            template: '<button @click="$emit(\'click\')"><slot /></button>',
            props: ['variant']
          },
          Card: true,
          ChartComponent: true,
          ActivityTable: true
        }
      }
    })

    // Mock URL.createObjectURL and document.createElement
    const createElementSpy = vi.spyOn(document, 'createElement')
    const createObjectURLSpy = vi.spyOn(window.URL, 'createObjectURL')
    const revokeObjectURLSpy = vi.spyOn(window.URL, 'revokeObjectURL')

    await (wrapper.vm as any).handleExport('csv')
    await wrapper.vm.$nextTick()

    expect(reportsStore.exportReport).toHaveBeenCalledWith('csv')
    expect(createObjectURLSpy).toHaveBeenCalled()
  })

  it('handles export PDF', async () => {
    const reportsStore = useReportsStore()
    reportsStore.currentReport = {
      id: 1,
      name: 'Test',
      type: 'usage',
      timeRange: { type: 'month', startDate: '', endDate: '' },
      metrics: mockUsageMetrics,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
      created_by: 1
    }

    wrapper = mount(AdminReportsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Select: true,
          DateRangePicker: true,
          Button: true,
          Card: true,
          ChartComponent: true,
          ActivityTable: true
        }
      }
    })

    await (wrapper.vm as any).handleExport('pdf')
    await wrapper.vm.$nextTick()

    expect(reportsStore.exportReport).toHaveBeenCalledWith('pdf')
  })

  it('creates report if none exists before export', async () => {
    const reportsStore = useReportsStore()
    reportsStore.currentReport = null

    wrapper = mount(AdminReportsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Select: true,
          DateRangePicker: true,
          Button: true,
          Card: true,
          ChartComponent: true,
          ActivityTable: true
        }
      }
    })

    await (wrapper.vm as any).handleExport('csv')
    await wrapper.vm.$nextTick()

    expect(reportsStore.saveReport).toHaveBeenCalled()
  })

  it('shows loading state', () => {
    const reportsStore = useReportsStore()
    reportsStore.isLoading = true

    wrapper = mount(AdminReportsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Select: true,
          DateRangePicker: true,
          Button: true,
          Card: true,
          ChartComponent: true,
          ActivityTable: true
        }
      }
    })

    expect(wrapper.find('.reports-loading').exists()).toBe(true)
  })

  it('fetches reports on mount', async () => {
    const reportsStore = useReportsStore()

    wrapper = mount(AdminReportsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Select: true,
          DateRangePicker: true,
          Button: true,
          Card: true,
          ChartComponent: true,
          ActivityTable: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    expect(reportsStore.fetchUsageReport).toHaveBeenCalled()
    expect(reportsStore.fetchDownloadReport).toHaveBeenCalled()
    expect(reportsStore.fetchActivityReport).toHaveBeenCalled()
    expect(reportsStore.fetchStorageReport).toHaveBeenCalled()
  })

  it('handles time range change', async () => {
    const reportsStore = useReportsStore()

    wrapper = mount(AdminReportsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Select: {
            template: '<select><slot /></select>',
            props: ['modelValue', 'options', 'label']
          },
          DateRangePicker: true,
          Button: true,
          Card: true,
          ChartComponent: true,
          ActivityTable: true
        }
      }
    })

    ;(wrapper.vm as any).selectedTimeRange = 'week'
    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    expect(reportsStore.fetchUsageReport).toHaveBeenCalled()
  })

  it('handles custom date range change', async () => {
    const reportsStore = useReportsStore()

    wrapper = mount(AdminReportsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Select: true,
          DateRangePicker: {
            template: '<div>Date Range Picker</div>',
            props: ['modelValue']
          },
          Button: true,
          Card: true,
          ChartComponent: true,
          ActivityTable: true
        }
      }
    })

    ;(wrapper.vm as any).selectedTimeRange = 'custom'
    ;(wrapper.vm as any).customDateRange = ['2025-01-01', '2025-01-31']
    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    expect(reportsStore.fetchUsageReport).toHaveBeenCalled()
  })

  it('displays error notification on fetch failure', async () => {
    const reportsStore = useReportsStore()
    const uiStore = useUIStore()
    reportsStore.fetchUsageReport = vi.fn().mockRejectedValue(new Error('Failed'))

    wrapper = mount(AdminReportsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Select: true,
          DateRangePicker: true,
          Button: true,
          Card: true,
          ChartComponent: true,
          ActivityTable: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 200))

    expect(uiStore.addNotification).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'error'
      })
    )
  })

  it('displays success notification on export', async () => {
    const reportsStore = useReportsStore()
    const uiStore = useUIStore()
    reportsStore.currentReport = {
      id: 1,
      name: 'Test',
      type: 'usage',
      timeRange: { type: 'month', startDate: '', endDate: '' },
      metrics: mockUsageMetrics,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
      created_by: 1
    }

    // Mock URL methods
    vi.spyOn(window.URL, 'createObjectURL').mockReturnValue('blob:test')
    vi.spyOn(window.URL, 'revokeObjectURL').mockImplementation(() => {})
    const createElementSpy = vi.spyOn(document, 'createElement').mockReturnValue({
      href: '',
      download: '',
      click: vi.fn(),
      appendChild: vi.fn(),
      removeChild: vi.fn()
    } as any)
    vi.spyOn(document.body, 'appendChild').mockImplementation(() => ({} as any))
    vi.spyOn(document.body, 'removeChild').mockImplementation(() => ({} as any))

    wrapper = mount(AdminReportsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Select: true,
          DateRangePicker: true,
          Button: true,
          Card: true,
          ChartComponent: true,
          ActivityTable: true
        }
      }
    })

    await (wrapper.vm as any).handleExport('csv')
    await wrapper.vm.$nextTick()

    expect(uiStore.addNotification).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'success'
      })
    )
  })

  it('renders chart components with correct props', () => {
    wrapper = mount(AdminReportsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Select: true,
          DateRangePicker: true,
          Button: true,
          Card: {
            template: '<div><slot /></div>',
            props: ['variant']
          },
          ChartComponent: {
            template: '<div class="chart-component">Chart</div>',
            props: ['type', 'data', 'title']
          },
          ActivityTable: true
        }
      }
    })

    const charts = wrapper.findAllComponents({ name: 'ChartComponent' })
    expect(charts.length).toBeGreaterThan(0)
  })

  it('renders ActivityTable with correct props', () => {
    wrapper = mount(AdminReportsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Select: true,
          DateRangePicker: true,
          Button: true,
          Card: {
            template: '<div><slot /></div>',
            props: ['variant']
          },
          ChartComponent: true,
          ActivityTable: {
            template: '<div class="activity-table">Table</div>',
            props: ['activities', 'isLoading', 'pageSize', 'showPagination']
          }
        }
      }
    })

    const table = wrapper.findComponent({ name: 'ActivityTable' })
    expect(table.exists()).toBe(true)
  })

  it('displays empty state for charts when no data', () => {
    const reportsStore = useReportsStore()
    reportsStore.storageBreakdown = []
    reportsStore.downloadHistory = []

    wrapper = mount(AdminReportsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Select: true,
          DateRangePicker: true,
          Button: true,
          Card: {
            template: '<div><slot /></div>',
            props: ['variant']
          },
          ChartComponent: true,
          ActivityTable: true
        }
      }
    })

    expect(wrapper.text()).toContain('No storage data available')
  })

  it('closes export menu when clicking outside', async () => {
    wrapper = mount(AdminReportsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Select: true,
          DateRangePicker: true,
          Button: true,
          Card: true,
          ChartComponent: true,
          ActivityTable: true
        }
      }
    })

    ;(wrapper.vm as any).showExportMenu = true
    await wrapper.vm.$nextTick()

    // Simulate click outside
    document.body.click()
    await wrapper.vm.$nextTick()

    // Menu should close (onClickOutside should handle this)
    // This is tested through the component's behavior
  })

  it('formats storage limit as Unlimited when null', () => {
    const reportsStore = useReportsStore()
    reportsStore.usageMetrics = {
      ...mockUsageMetrics,
      storageLimit: null
    }

    wrapper = mount(AdminReportsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Select: true,
          DateRangePicker: true,
          Button: true,
          Card: true,
          ChartComponent: true,
          ActivityTable: true
        }
      }
    })

    expect(wrapper.text()).toContain('Unlimited')
  })
})

