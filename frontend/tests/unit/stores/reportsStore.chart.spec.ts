import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useReportsStore } from '@/stores/reportsStore'
import type { StorageBreakdown, DownloadMetric, ChartData } from '@/types/reports'

describe('ReportsStore - Chart Generation', () => {
  let pinia: ReturnType<typeof createPinia>
  let store: ReturnType<typeof useReportsStore>

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    store = useReportsStore()
  })

  describe('generateStorageChartData', () => {
    it('should generate pie chart data from storage breakdown', () => {
      const breakdown: StorageBreakdown[] = [
        {
          category: 'images',
          size: 5 * 1024 * 1024 * 1024,
          count: 500,
          percentage: 50
        },
        {
          category: 'videos',
          size: 3 * 1024 * 1024 * 1024,
          count: 200,
          percentage: 30
        },
        {
          category: 'documents',
          size: 2 * 1024 * 1024 * 1024,
          count: 200,
          percentage: 20
        }
      ]

      const chartData = store.generateStorageChartData(breakdown)

      expect(chartData).toBeDefined()
      expect(chartData.labels).toHaveLength(3)
      expect(chartData.labels).toEqual(['images', 'videos', 'documents'])
      expect(chartData.datasets).toHaveLength(1)
      expect(chartData.datasets[0].data).toEqual([
        5 * 1024 * 1024 * 1024,
        3 * 1024 * 1024 * 1024,
        2 * 1024 * 1024 * 1024
      ])
      expect(chartData.datasets[0].backgroundColor).toHaveLength(3)
    })

    it('should handle empty breakdown array', () => {
      const breakdown: StorageBreakdown[] = []

      const chartData = store.generateStorageChartData(breakdown)

      expect(chartData.labels).toHaveLength(0)
      expect(chartData.datasets[0].data).toHaveLength(0)
    })

    it('should use correct background colors for categories', () => {
      const breakdown: StorageBreakdown[] = [
        {
          category: 'images',
          size: 1000,
          count: 100,
          percentage: 100
        }
      ]

      const chartData = store.generateStorageChartData(breakdown)

      expect(chartData.datasets[0].backgroundColor).toBeDefined()
      expect(chartData.datasets[0].backgroundColor?.length).toBeGreaterThan(0)
    })
  })

  describe('generateDownloadChartData', () => {
    it('should generate line chart data from download metrics', () => {
      const metrics: DownloadMetric[] = [
        {
          date: '2025-01-01T00:00:00Z',
          downloads: 100,
          uniqueUsers: 50
        },
        {
          date: '2025-01-02T00:00:00Z',
          downloads: 150,
          uniqueUsers: 75
        },
        {
          date: '2025-01-03T00:00:00Z',
          downloads: 200,
          uniqueUsers: 100
        }
      ]

      const chartData = store.generateDownloadChartData(metrics)

      expect(chartData).toBeDefined()
      expect(chartData.labels).toHaveLength(3)
      expect(chartData.datasets).toHaveLength(2) // Downloads and Unique Users
      expect(chartData.datasets[0].label).toBe('Downloads')
      expect(chartData.datasets[0].data).toEqual([100, 150, 200])
      expect(chartData.datasets[1].label).toBe('Unique Users')
      expect(chartData.datasets[1].data).toEqual([50, 75, 100])
    })

    it('should handle empty metrics array', () => {
      const metrics: DownloadMetric[] = []

      const chartData = store.generateDownloadChartData(metrics)

      expect(chartData.labels).toHaveLength(0)
      expect(chartData.datasets[0].data).toHaveLength(0)
      expect(chartData.datasets[1].data).toHaveLength(0)
    })

    it('should format dates correctly in labels', () => {
      const metrics: DownloadMetric[] = [
        {
          date: '2025-01-15T00:00:00Z',
          downloads: 100,
          uniqueUsers: 50
        }
      ]

      const chartData = store.generateDownloadChartData(metrics)

      expect(chartData.labels[0]).toContain('Jan')
      expect(chartData.labels[0]).toContain('15')
    })
  })

  describe('generateChartData', () => {
    it('should generate storage chart data for storage report type', () => {
      const breakdown: StorageBreakdown[] = [
        {
          category: 'images',
          size: 1000,
          count: 100,
          percentage: 100
        }
      ]

      const chartData = store.generateChartData('storage', breakdown)

      expect(chartData).toBeDefined()
      expect(chartData.labels).toContain('images')
    })

    it('should generate download chart data for downloads report type', () => {
      const metrics: DownloadMetric[] = [
        {
          date: '2025-01-01T00:00:00Z',
          downloads: 100,
          uniqueUsers: 50
        }
      ]

      const chartData = store.generateChartData('downloads', metrics)

      expect(chartData).toBeDefined()
      expect(chartData.datasets).toHaveLength(2)
    })
  })
})



