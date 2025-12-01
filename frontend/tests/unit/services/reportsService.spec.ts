import { describe, it, expect, beforeEach, vi } from 'vitest'
import { reportsService } from '@/services/reportsService'
import { apiService } from '@/services/apiService'
import type {
  ReportTimeRange,
  UsageMetrics,
  DownloadMetric,
  UserActivity,
  StorageBreakdown,
  Report,
  ExportFormat
} from '@/types/reports'

// Mock apiService
vi.mock('@/services/apiService', () => ({
  apiService: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

// Mock axios for export
vi.mock('axios', () => ({
  default: {
    get: vi.fn()
  }
}))

describe('ReportsService', () => {
  const mockTimeRange: ReportTimeRange = {
    type: 'month',
    startDate: '2025-01-01T00:00:00Z',
    endDate: '2025-01-31T23:59:59Z'
  }

  const mockUsageMetrics: UsageMetrics = {
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

  const mockDownloadMetrics: DownloadMetric[] = [
    {
      date: '2025-01-01T00:00:00Z',
      downloads: 100,
      uniqueUsers: 50
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
    }
  ]

  const mockStorageBreakdown: StorageBreakdown[] = [
    {
      category: 'images',
      size: 5 * 1024 * 1024 * 1024,
      count: 500,
      percentage: 50
    }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getUsageReport', () => {
    it('should fetch usage report with correct parameters', async () => {
      vi.mocked(apiService.get).mockResolvedValue(mockUsageMetrics)

      const result = await reportsService.getUsageReport(mockTimeRange)

      expect(apiService.get).toHaveBeenCalledWith(
        '/v4/reports/usage/',
        {
          params: {
            start: mockTimeRange.startDate,
            end: mockTimeRange.endDate
          }
        },
        true
      )
      expect(result).toEqual(mockUsageMetrics)
    })

    it('should handle errors correctly', async () => {
      const error = new Error('Failed to fetch usage report')
      vi.mocked(apiService.get).mockRejectedValue(error)

      await expect(reportsService.getUsageReport(mockTimeRange)).rejects.toThrow()
    })
  })

  describe('getDownloadReport', () => {
    it('should fetch download report with correct parameters', async () => {
      vi.mocked(apiService.get).mockResolvedValue(mockDownloadMetrics)

      const result = await reportsService.getDownloadReport(mockTimeRange)

      expect(apiService.get).toHaveBeenCalledWith(
        '/v4/reports/downloads/',
        {
          params: {
            start: mockTimeRange.startDate,
            end: mockTimeRange.endDate
          }
        },
        true
      )
      expect(result).toEqual(mockDownloadMetrics)
    })
  })

  describe('getActivityReport', () => {
    it('should fetch activity report without limit', async () => {
      vi.mocked(apiService.get).mockResolvedValue(mockActivities)

      const result = await reportsService.getActivityReport(mockTimeRange)

      expect(apiService.get).toHaveBeenCalledWith(
        '/v4/reports/activity/',
        {
          params: {
            start: mockTimeRange.startDate,
            end: mockTimeRange.endDate
          }
        },
        false
      )
      expect(result).toEqual(mockActivities)
    })

    it('should fetch activity report with limit', async () => {
      vi.mocked(apiService.get).mockResolvedValue(mockActivities)

      const result = await reportsService.getActivityReport(mockTimeRange, 50)

      expect(apiService.get).toHaveBeenCalledWith(
        '/v4/reports/activity/',
        {
          params: {
            start: mockTimeRange.startDate,
            end: mockTimeRange.endDate,
            limit: 50
          }
        },
        false
      )
      expect(result).toEqual(mockActivities)
    })
  })

  describe('getStorageReport', () => {
    it('should fetch storage report with correct parameters', async () => {
      vi.mocked(apiService.get).mockResolvedValue(mockStorageBreakdown)

      const result = await reportsService.getStorageReport(mockTimeRange)

      expect(apiService.get).toHaveBeenCalledWith(
        '/v4/reports/storage/',
        {
          params: {
            start: mockTimeRange.startDate,
            end: mockTimeRange.endDate
          }
        },
        true
      )
      expect(result).toEqual(mockStorageBreakdown)
    })
  })

  describe('exportReport', () => {
    it('should export report as CSV', async () => {
      const mockBlob = new Blob(['test'], { type: 'text/csv' })
      const axios = (await import('axios')).default
      vi.mocked(axios.get).mockResolvedValue({ data: mockBlob })

      // Mock localStorage
      const getItemSpy = vi.spyOn(Storage.prototype, 'getItem').mockReturnValue('test-token')

      const result = await reportsService.exportReport(1, 'csv')

      expect(axios.get).toHaveBeenCalled()
      expect(result).toBeInstanceOf(Blob)
      expect(getItemSpy).toHaveBeenCalledWith('auth_token')

      getItemSpy.mockRestore()
    })

    it('should export report as PDF', async () => {
      const mockBlob = new Blob(['test'], { type: 'application/pdf' })
      const axios = (await import('axios')).default
      vi.mocked(axios.get).mockResolvedValue({ data: mockBlob })

      const getItemSpy = vi.spyOn(Storage.prototype, 'getItem').mockReturnValue('test-token')

      const result = await reportsService.exportReport(1, 'pdf')

      expect(axios.get).toHaveBeenCalled()
      expect(result).toBeInstanceOf(Blob)

      getItemSpy.mockRestore()
    })
  })

  describe('getAllReports', () => {
    it('should fetch all reports without params', async () => {
      const mockReports: Report[] = [
        {
          id: 1,
          name: 'Test Report',
          type: 'usage',
          timeRange: mockTimeRange,
          metrics: mockUsageMetrics,
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z',
          created_by: 1
        }
      ]
      vi.mocked(apiService.get).mockResolvedValue(mockReports)

      const result = await reportsService.getAllReports()

      expect(apiService.get).toHaveBeenCalledWith('/v4/reports/', { params: undefined }, false)
      expect(result).toEqual(mockReports)
    })

    it('should fetch all reports with params', async () => {
      const mockReports: Report[] = []
      const params = { type: 'usage' as const, page: 1, page_size: 10 }
      vi.mocked(apiService.get).mockResolvedValue(mockReports)

      const result = await reportsService.getAllReports(params)

      expect(apiService.get).toHaveBeenCalledWith('/v4/reports/', { params }, false)
      expect(result).toEqual(mockReports)
    })
  })

  describe('saveReport', () => {
    it('should save report with valid data', async () => {
      const mockReport: Report = {
        id: 1,
        name: 'Test Report',
        type: 'usage',
        timeRange: mockTimeRange,
        metrics: mockUsageMetrics,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
        created_by: 1
      }
      vi.mocked(apiService.post).mockResolvedValue(mockReport)

      const result = await reportsService.saveReport(mockReport)

      expect(apiService.post).toHaveBeenCalledWith('/v4/reports/', mockReport)
      expect(result).toEqual(mockReport)
    })

    it('should validate report name length', async () => {
      const longName = 'a'.repeat(256)
      const mockReport: Report = {
        id: 1,
        name: longName,
        type: 'usage',
        timeRange: mockTimeRange,
        metrics: mockUsageMetrics,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
        created_by: 1
      }

      await expect(reportsService.saveReport(mockReport)).rejects.toThrow()
    })
  })

  describe('getReport', () => {
    it('should fetch single report by id', async () => {
      const mockReport: Report = {
        id: 1,
        name: 'Test Report',
        type: 'usage',
        timeRange: mockTimeRange,
        metrics: mockUsageMetrics,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
        created_by: 1
      }
      vi.mocked(apiService.get).mockResolvedValue(mockReport)

      const result = await reportsService.getReport(1)

      expect(apiService.get).toHaveBeenCalledWith('/v4/reports/1/', {}, false)
      expect(result).toEqual(mockReport)
    })
  })

  describe('deleteReport', () => {
    it('should delete report by id', async () => {
      vi.mocked(apiService.delete).mockResolvedValue(undefined)

      await reportsService.deleteReport(1)

      expect(apiService.delete).toHaveBeenCalledWith('/v4/reports/1/')
    })
  })
})

