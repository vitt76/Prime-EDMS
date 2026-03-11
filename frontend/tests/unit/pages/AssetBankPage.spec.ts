import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const analyticsStore = {
  filters: {
    dateRange: null,
    assetType: null,
    department: null
  },
  assetBankTopMetrics: null,
  lastUpdated: null,
  isLoading: false,
  error: null,
  assetDistribution: [],
  assetDistributionTrend: [],
  mostDownloadedAssets: [],
  assetReuseMetrics: null,
  storageTrends: null,
  dashboardGeography: [],
  dashboardGeographyError: null as string | null,
  userAdoptionHeatmap: null,
  assetBankAlerts: [],
  fetchAssetBankAll: vi.fn().mockResolvedValue(undefined),
  fetchDashboardGeography: vi.fn().mockResolvedValue(undefined),
  setDateRange: vi.fn(),
  setAssetType: vi.fn(),
  setDepartment: vi.fn(),
  applyFilters: vi.fn().mockResolvedValue(undefined)
}

const buildAnalyticsWebSocketUrl = vi.fn(
  () => 'ws://analytics.test/ws/analytics/?token=token-1&organization_id=org-1'
)

vi.mock('@/stores/analyticsStore', () => ({
  useAnalyticsStore: () => analyticsStore
}))

vi.mock('@/utils/constants', () => ({
  buildAnalyticsWebSocketUrl
}))

class MockWebSocket {
  static instances: MockWebSocket[] = []
  onmessage: ((event: { data: string }) => void | Promise<void>) | null = null
  close = vi.fn()

  constructor(public url: string) {
    MockWebSocket.instances.push(this)
  }
}

describe('AssetBankPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    MockWebSocket.instances = []
    vi.stubGlobal('WebSocket', MockWebSocket as unknown as typeof WebSocket)
    localStorage.clear()
    localStorage.setItem('auth_token', 'token-1')
    localStorage.setItem('current_organization_id', 'org-1')
    analyticsStore.dashboardGeographyError = null
  })

  it('opens analytics websocket with token and organization context', async () => {
    const AssetBankPage = (await import('@/pages/analytics/AssetBankPage.vue')).default

    mount(AssetBankPage, {
      global: {
        stubs: {
          FilterBar: true,
          TopMetricsCard: true,
          AssetDistributionChart: true,
          MostDownloadedAssetsTable: true,
          AssetReuseMetricsChart: true,
          StorageTrendsChart: true,
          GeoMap: true,
          UserAdoptionHeatMap: true,
          AlertsList: true,
          AssetDetailModal: true,
          ReportGenerateModal: true
        }
      }
    })

    await flushPromises()

    expect(analyticsStore.fetchAssetBankAll).toHaveBeenCalled()
    expect(analyticsStore.fetchDashboardGeography).toHaveBeenCalledWith({ days: 30 })
    expect(buildAnalyticsWebSocketUrl).toHaveBeenCalledWith('token-1', 'org-1')
    expect(MockWebSocket.instances[0]?.url).toBe(
      'ws://analytics.test/ws/analytics/?token=token-1&organization_id=org-1'
    )
  })

  it('shows geography error and refreshes on analytics_refresh event', async () => {
    analyticsStore.dashboardGeographyError = 'Не удалось загрузить географию аналитики'
    const AssetBankPage = (await import('@/pages/analytics/AssetBankPage.vue')).default

    const wrapper = mount(AssetBankPage, {
      global: {
        stubs: {
          FilterBar: true,
          TopMetricsCard: true,
          AssetDistributionChart: true,
          MostDownloadedAssetsTable: true,
          AssetReuseMetricsChart: true,
          StorageTrendsChart: true,
          GeoMap: true,
          UserAdoptionHeatMap: true,
          AlertsList: true,
          AssetDetailModal: true,
          ReportGenerateModal: true
        }
      }
    })

    await flushPromises()

    const socket = MockWebSocket.instances[0]
    await socket.onmessage?.({
      data: JSON.stringify({ type: 'analytics_refresh' })
    })
    await flushPromises()

    expect(wrapper.text()).toContain('Не удалось загрузить географию аналитики')
    expect(analyticsStore.fetchAssetBankAll).toHaveBeenCalledTimes(2)
    expect(analyticsStore.fetchDashboardGeography).toHaveBeenCalledTimes(2)
  })
})
