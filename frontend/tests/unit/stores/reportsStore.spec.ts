import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useReportsStore } from '@/stores/reportsStore'
import { reportsService } from '@/services/reportsService'
import { useAuthStore } from '@/stores/authStore'
import type {
  ReportTimeRange,
  UsageMetrics,
  DownloadMetric,
  UserActivity,
  StorageBreakdown,
  Report
} from '@/types/reports'

// Mock services
vi.mock('@/services/reportsService')
vi.mock('@/stores/authStore')

describe('ReportsStore', () => {
  let pinia: ReturnType<typeof createPinia>
  let store: ReturnType<typeof useReportsStore>
  let authStore: ReturnType<typeof useAuthStore>

  const mockUsageMetrics: UsageMetrics = {
    totalAssets: 1000,
    assetsByType: {
      images: 500,
      videos: 200,
      documents: 200,
      audio: 50,
      other: 50
    },
    storageUsed: 1024 * 1024 * 1024 * 10, // 10 GB
    storageLimit: 1024 * 1024 * 1024 * 100, // 100 GB
    storagePercentage: 10
  }

  const mockDownloadMetrics: DownloadMetric[] = [
    {
      date: '2025-01-01T00:00:00Z',
      downloads: 100,
      uniqueUsers: 50
    },
    {
      date: '2025-01-02T00:00:00Z',
      downloads: 150,
      uniqueUsers: 75
    }
  ]

  const mockActivities: UserActivity[] = [
    {
      username: 'user1',
      email: 'user1@example.com',
      action: 'upload',
      asset_id: 1,
      asset_name: 'test.jpg',
      timestamp: '2025-01-01T00:00:00Z'
    },
    {
      username: 'user2',
      email: 'user2@example.com',
      action: 'download',
      asset_id: 2,
      asset_name: 'test2.jpg',
      timestamp: '2025-01-02T00:00:00Z'
    }
  ]

  const mockStorageBreakdown: StorageBreakdown[] = [
    {
      category: 'images',
      size: 5 * 1024 * 1024 * 1024, // 5 GB
      count: 500,
      percentage: 50
    },
    {
      category: 'videos',
      size: 3 * 1024 * 1024 * 1024, // 3 GB
      count: 200,
      percentage: 30
    }
  ]

  const mockTimeRange: ReportTimeRange = {
    type: 'month',
    startDate: '2025-01-01T00:00:00Z',
    endDate: '2025-01-31T23:59:59Z'
  }

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    // Setup auth store mock
    authStore = useAuthStore()
    authStore.user = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      is_active: true
    }

    // Setup service mocks
    vi.mocked(reportsService.getUsageReport).mockResolvedValue(mockUsageMetrics)
    vi.mocked(reportsService.getDownloadReport).mockResolvedValue(mockDownloadMetrics)
    vi.mocked(reportsService.getActivityReport).mockResolvedValue(mockActivities)
    vi.mocked(reportsService.getStorageReport).mockResolvedValue(mockStorageBreakdown)
    vi.mocked(reportsService.exportReport).mockResolvedValue(new Blob(['test'], { type: 'text/csv' }))
    vi.mocked(reportsService.saveReport).mockResolvedValue({
      id: 1,
      name: 'Test Report',
      type: 'usage',
      timeRange: mockTimeRange,
      metrics: mockUsageMetrics,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
      created_by: 1
    } as Report)

    store = useReportsStore()
  })

  afterEach(() => {
    vi.clearAllMocks()
    store.reset()
  })

  describe('Initial State', () => {
    it('should initialize with default values', () => {
      expect(store.reports).toEqual([])
      expect(store.currentReport).toBeNull()
      expect(store.usageMetrics).toBeNull()
      expect(store.downloadHistory).toEqual([])
      expect(store.recentActivity).toEqual([])
      expect(store.storageBreakdown).toEqual([])
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('should have computed properties initialized', () => {
      expect(store.chartsReady).toBe(false)
      expect(store.exportDisabled).toBe(true)
      expect(store.timeRangeDisplay).toBe('Select range')
    })
  })

  describe('fetchUsageReport', () => {
    it('should fetch and set usage metrics', async () => {
      await store.fetchUsageReport(mockTimeRange)

      expect(reportsService.getUsageReport).toHaveBeenCalledWith(mockTimeRange)
      expect(store.usageMetrics).toEqual(mockUsageMetrics)
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('should calculate storage breakdown correctly', async () => {
      await store.fetchUsageReport(mockTimeRange)

      expect(store.storageBreakdown.length).toBe(5)
      expect(store.storageBreakdown.length).toBeGreaterThan(0)
      const imagesBreakdown = store.storageBreakdown.find((b) => b.category === 'images')
      expect(imagesBreakdown).toBeDefined()
      if (imagesBreakdown) {
        expect(imagesBreakdown.size).toBeGreaterThan(0)
        expect(imagesBreakdown.percentage).toBeGreaterThan(0)
        expect(imagesBreakdown.count).toBe(500)
      }
    })

    it('should handle errors correctly', async () => {
      const error = new Error('Failed to fetch usage report')
      vi.mocked(reportsService.getUsageReport).mockRejectedValue(error)

      await expect(store.fetchUsageReport(mockTimeRange)).rejects.toThrow()
      expect(store.error).toBeTruthy()
      expect(store.usageMetrics).toBeNull()
      expect(store.storageBreakdown).toEqual([])
    })

    it('should generate chart data for storage breakdown', async () => {
      await store.fetchUsageReport(mockTimeRange)

      expect(store.chartData).not.toBeNull()
      expect(store.chartData?.labels).toHaveLength(5)
      expect(store.chartData?.datasets).toHaveLength(1)
    })
  })

  describe('fetchDownloadReport', () => {
    it('should fetch and set download history', async () => {
      await store.fetchDownloadReport(mockTimeRange)

      expect(reportsService.getDownloadReport).toHaveBeenCalledWith(mockTimeRange)
      expect(store.downloadHistory).toEqual(mockDownloadMetrics)
      expect(store.isLoading).toBe(false)
    })

    it('should generate chart data for downloads', async () => {
      await store.fetchDownloadReport(mockTimeRange)

      expect(store.chartData).not.toBeNull()
      expect(store.chartData?.labels).toHaveLength(2)
      expect(store.chartData?.datasets).toHaveLength(2) // Downloads and Unique Users
    })

    it('should handle errors correctly', async () => {
      const error = new Error('Failed to fetch download report')
      vi.mocked(reportsService.getDownloadReport).mockRejectedValue(error)

      await expect(store.fetchDownloadReport(mockTimeRange)).rejects.toThrow()
      expect(store.error).toBeTruthy()
      expect(store.downloadHistory).toEqual([])
    })
  })

  describe('fetchActivityReport', () => {
    it('should fetch and set activity data', async () => {
      await store.fetchActivityReport(mockTimeRange, 50)

      expect(reportsService.getActivityReport).toHaveBeenCalledWith(mockTimeRange, 50)
      expect(store.recentActivity).toEqual(mockActivities)
      expect(store.isLoading).toBe(false)
    })

    it('should use default limit if not provided', async () => {
      await store.fetchActivityReport(mockTimeRange)

      expect(reportsService.getActivityReport).toHaveBeenCalledWith(mockTimeRange, 50)
    })

    it('should handle errors correctly', async () => {
      const error = new Error('Failed to fetch activity report')
      vi.mocked(reportsService.getActivityReport).mockRejectedValue(error)

      await expect(store.fetchActivityReport(mockTimeRange)).rejects.toThrow()
      expect(store.error).toBeTruthy()
      expect(store.recentActivity).toEqual([])
    })
  })

  describe('fetchStorageReport', () => {
    it('should fetch and set storage breakdown', async () => {
      await store.fetchStorageReport(mockTimeRange)

      expect(reportsService.getStorageReport).toHaveBeenCalledWith(mockTimeRange)
      expect(store.storageBreakdown).toEqual(mockStorageBreakdown)
      expect(store.isLoading).toBe(false)
    })

    it('should generate chart data for storage', async () => {
      await store.fetchStorageReport(mockTimeRange)

      expect(store.chartData).not.toBeNull()
      expect(store.chartData?.labels).toHaveLength(2)
    })

    it('should handle errors correctly', async () => {
      const error = new Error('Failed to fetch storage report')
      vi.mocked(reportsService.getStorageReport).mockRejectedValue(error)

      await expect(store.fetchStorageReport(mockTimeRange)).rejects.toThrow()
      expect(store.error).toBeTruthy()
      expect(store.storageBreakdown).toEqual([])
    })
  })

  describe('setTimeRange', () => {
    it('should update time range', () => {
      const newRange: ReportTimeRange = {
        type: 'week',
        startDate: '2025-01-01T00:00:00Z',
        endDate: '2025-01-07T23:59:59Z'
      }

      store.setTimeRange(newRange)

      expect(store.timeRange).toEqual(newRange)
    })
  })

  describe('exportReport', () => {
    it('should export report as CSV', async () => {
      store.setCurrentReport({
        id: 1,
        name: 'Test Report',
        type: 'usage',
        timeRange: mockTimeRange,
        metrics: mockUsageMetrics,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
        created_by: 1
      } as Report)

      const blob = await store.exportReport('csv')

      expect(reportsService.exportReport).toHaveBeenCalledWith(1, 'csv')
      expect(blob).toBeInstanceOf(Blob)
    })

    it('should export report as PDF', async () => {
      store.setCurrentReport({
        id: 1,
        name: 'Test Report',
        type: 'usage',
        timeRange: mockTimeRange,
        metrics: mockUsageMetrics,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
        created_by: 1
      } as Report)

      const blob = await store.exportReport('pdf')

      expect(reportsService.exportReport).toHaveBeenCalledWith(1, 'pdf')
      expect(blob).toBeInstanceOf(Blob)
    })

    it('should throw error if no current report', async () => {
      await expect(store.exportReport('csv')).rejects.toThrow('No report selected for export')
    })
  })

  describe('saveReport', () => {
    it('should save usage report', async () => {
      store.usageMetrics = mockUsageMetrics

      const report = await store.saveReport('Test Report', 'usage')

      expect(reportsService.saveReport).toHaveBeenCalled()
      expect(report.id).toBe(1)
      expect(store.savedReports.length).toBeGreaterThan(0)
    })

    it('should save download report', async () => {
      store.downloadHistory = mockDownloadMetrics

      const report = await store.saveReport('Test Report', 'downloads')

      expect(reportsService.saveReport).toHaveBeenCalled()
      expect(report.id).toBe(1)
    })

    it('should throw error if no data to save', async () => {
      await expect(store.saveReport('Test Report', 'usage')).rejects.toThrow()
    })
  })

  describe('Computed Properties', () => {
    it('should return chartsReady as true when chart data exists', async () => {
      await store.fetchUsageReport(mockTimeRange)

      expect(store.chartsReady).toBe(true)
    })

    it('should return exportDisabled as false when current report exists', () => {
      store.setCurrentReport({
        id: 1,
        name: 'Test',
        type: 'usage',
        timeRange: mockTimeRange,
        metrics: mockUsageMetrics,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
        created_by: 1
      } as Report)

      expect(store.exportDisabled).toBe(false)
    })

    it('should format time range display correctly', () => {
      store.setTimeRange({
        type: 'month',
        startDate: '2025-01-01T00:00:00Z',
        endDate: '2025-01-31T23:59:59Z'
      })

      expect(store.timeRangeDisplay).toContain('January')
    })
  })

  describe('reset', () => {
    it('should reset all state to initial values', async () => {
      await store.fetchUsageReport(mockTimeRange)
      store.setCurrentReport({
        id: 1,
        name: 'Test',
        type: 'usage',
        timeRange: mockTimeRange,
        metrics: mockUsageMetrics,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
        created_by: 1
      } as Report)

      store.reset()

      expect(store.reports).toEqual([])
      expect(store.currentReport).toBeNull()
      expect(store.usageMetrics).toBeNull()
      expect(store.downloadHistory).toEqual([])
      expect(store.recentActivity).toEqual([])
      expect(store.storageBreakdown).toEqual([])
      expect(store.chartData).toBeNull()
      expect(store.error).toBeNull()
    })
  })
})

