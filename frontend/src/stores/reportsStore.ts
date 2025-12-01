import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { reportsService } from '@/services/reportsService'
import { formatApiError } from '@/utils/errors'
import { extractErrorCode } from '@/utils/errorHandling'
import { useAuthStore } from './authStore'
import { useUIStore } from './uiStore'
import type {
  Report,
  ReportTimeRange,
  UsageMetrics,
  DownloadMetric,
  UserActivity,
  StorageBreakdown,
  ChartData,
  ExportFormat,
  SavedReport,
  ReportSummary
} from '@/types/reports'

const DEFAULT_TIME_RANGE: ReportTimeRange = {
  type: 'month',
  startDate: '',
  endDate: ''
}

export const useReportsStore = defineStore(
  'reports',
  () => {
    const authStore = useAuthStore()
    const uiStore = useUIStore()

    const reportRequestIds = ref({
      usage: 0,
      downloads: 0,
      activity: 0,
      storage: 0
    })

    const startReportRequest = (
      key: keyof typeof reportRequestIds.value
    ): number => {
      const nextId = (reportRequestIds.value[key] ?? 0) + 1
      reportRequestIds.value = {
        ...reportRequestIds.value,
        [key]: nextId
      }
      return nextId
    }

    const isLatestReportRequest = (
      key: keyof typeof reportRequestIds.value,
      id: number
    ): boolean => reportRequestIds.value[key] === id

    const logReportError = (context: string, error: unknown): string => {
      const message = formatApiError(error)
      const code = extractErrorCode(error)
      console.warn(`${context} failed`, { code, error })
      uiStore.addNotification({
        type: 'error',
        title: `${context} Error`,
        message,
        meta: code ? { code } : undefined
      })
      return message
    }

    // Reports state
    const reports = ref<Report[]>([])
    const currentReport = ref<Report | null>(null)
    const savedReports = ref<SavedReport[]>([])
    const reportSummary = ref<ReportSummary | null>(null)

    // Time range state
    const timeRange = ref<ReportTimeRange>({ ...DEFAULT_TIME_RANGE })

    // Metrics state
    const usageMetrics = ref<UsageMetrics | null>(null)
    const downloadHistory = ref<DownloadMetric[]>([])
    const recentActivity = ref<UserActivity[]>([])
    const storageBreakdown = ref<StorageBreakdown[]>([])

    // Chart data state
    const chartData = ref<ChartData | null>(null)

    // Global state
    const isLoading = ref(false)
    const error = ref<string | null>(null)

    // Computed properties
    const chartsReady = computed(() => {
      return chartData.value !== null && chartData.value.datasets.length > 0
    })

    const exportDisabled = computed(() => {
      return currentReport.value === null
    })

    const timeRangeDisplay = computed(() => {
      if (timeRange.value.type === 'custom') {
        if (timeRange.value.startDate && timeRange.value.endDate) {
          const start = new Date(timeRange.value.startDate)
          const end = new Date(timeRange.value.endDate)
          return `${formatDate(start)} - ${formatDate(end)}`
        }
        return 'Custom range'
      }

      const now = new Date()
      switch (timeRange.value.type) {
        case 'today':
          return formatDate(now)
        case 'week':
          const weekAgo = new Date(now)
          weekAgo.setDate(now.getDate() - 7)
          return `${formatDate(weekAgo)} - ${formatDate(now)}`
        case 'month':
          return formatMonth(now)
        case 'quarter':
          return formatQuarter(now)
        default:
          return 'Select range'
      }
    })

    // Helper functions
    const formatDate = (date: Date): string => {
      return date.toLocaleDateString('en-US', {
        month: 'long',
        day: 'numeric',
        year: 'numeric'
      })
    }

    const formatMonth = (date: Date): string => {
      return date.toLocaleDateString('en-US', {
        month: 'long',
        year: 'numeric'
      })
    }

    const formatQuarter = (date: Date): string => {
      const quarter = Math.floor(date.getMonth() / 3) + 1
      return `Q${quarter} ${date.getFullYear()}`
    }

    const calculateTimeRange = (range: ReportTimeRange): { start: string; end: string } => {
      const now = new Date()
      let start: Date
      let end: Date = new Date(now)

      switch (range.type) {
        case 'today':
          start = new Date(now)
          start.setHours(0, 0, 0, 0)
          end.setHours(23, 59, 59, 999)
          break
        case 'week':
          start = new Date(now)
          start.setDate(now.getDate() - 7)
          start.setHours(0, 0, 0, 0)
          break
        case 'month':
          start = new Date(now.getFullYear(), now.getMonth(), 1)
          start.setHours(0, 0, 0, 0)
          end = new Date(now.getFullYear(), now.getMonth() + 1, 0)
          end.setHours(23, 59, 59, 999)
          break
        case 'quarter':
          const quarter = Math.floor(now.getMonth() / 3)
          start = new Date(now.getFullYear(), quarter * 3, 1)
          start.setHours(0, 0, 0, 0)
          end = new Date(now.getFullYear(), (quarter + 1) * 3, 0)
          end.setHours(23, 59, 59, 999)
          break
        case 'custom':
          start = new Date(range.startDate)
          end = new Date(range.endDate)
          break
        default:
          start = new Date(now)
          start.setMonth(now.getMonth() - 1)
      }

      return {
        start: start.toISOString(),
        end: end.toISOString()
      }
    }

    // Actions - Fetch reports
    async function fetchUsageReport(range?: ReportTimeRange): Promise<void> {
      const key: keyof typeof reportRequestIds.value = 'usage'
      const requestId = startReportRequest(key)
      isLoading.value = true
      error.value = null

      try {
        const targetRange = range || timeRange.value
        const { start, end } = calculateTimeRange(targetRange)

        const metrics = await reportsService.getUsageReport({
          type: targetRange.type,
          startDate: start,
          endDate: end
        })

        if (!isLatestReportRequest(key, requestId)) {
          return
        }

        usageMetrics.value = metrics

        if (metrics.assetsByType) {
          storageBreakdown.value = [
            {
              category: 'images',
              size: 0,
              count: metrics.assetsByType.images,
              percentage: 0
            },
            {
              category: 'videos',
              size: 0,
              count: metrics.assetsByType.videos,
              percentage: 0
            },
            {
              category: 'documents',
              size: 0,
              count: metrics.assetsByType.documents,
              percentage: 0
            },
            {
              category: 'audio',
              size: 0,
              count: metrics.assetsByType.audio,
              percentage: 0
            },
            {
              category: 'other',
              size: 0,
              count: metrics.assetsByType.other,
              percentage: 0
            }
          ]
        }

        chartData.value = generateStorageChartData(storageBreakdown.value)
      } catch (err) {
        if (!isLatestReportRequest(key, requestId)) {
          return
        }
        const message = logReportError('Usage report fetch', err)
        error.value = message
        usageMetrics.value = null
        storageBreakdown.value = []
        chartData.value = null
        throw err
      } finally {
        if (isLatestReportRequest(key, requestId)) {
          isLoading.value = false
        }
      }
    }

    async function fetchDownloadReport(range?: ReportTimeRange): Promise<void> {
      const key: keyof typeof reportRequestIds.value = 'downloads'
      const requestId = startReportRequest(key)
      isLoading.value = true
      error.value = null

      try {
        const targetRange = range || timeRange.value
        const { start, end } = calculateTimeRange(targetRange)

        const metrics = await reportsService.getDownloadReport({
          type: targetRange.type,
          startDate: start,
          endDate: end
        })

        if (!isLatestReportRequest(key, requestId)) {
          return
        }

        downloadHistory.value = metrics
        chartData.value = generateDownloadChartData(metrics)
      } catch (err) {
        if (!isLatestReportRequest(key, requestId)) {
          return
        }
        const message = logReportError('Download report fetch', err)
        error.value = message
        downloadHistory.value = []
        chartData.value = null
        throw err
      } finally {
        if (isLatestReportRequest(key, requestId)) {
          isLoading.value = false
        }
      }
    }

    async function fetchActivityReport(
      range?: ReportTimeRange,
      limit: number = 50
    ): Promise<void> {
      const key: keyof typeof reportRequestIds.value = 'activity'
      const requestId = startReportRequest(key)
      isLoading.value = true
      error.value = null

      try {
        const targetRange = range || timeRange.value
        const { start, end } = calculateTimeRange(targetRange)

        const activities = await reportsService.getActivityReport(
          {
            type: targetRange.type,
            startDate: start,
            endDate: end
          },
          limit
        )

        if (!isLatestReportRequest(key, requestId)) {
          return
        }

        recentActivity.value = activities
      } catch (err) {
        if (!isLatestReportRequest(key, requestId)) {
          return
        }
        const message = logReportError('Activity report fetch', err)
        error.value = message
        recentActivity.value = []
        throw err
      } finally {
        if (isLatestReportRequest(key, requestId)) {
          isLoading.value = false
        }
      }
    }

    async function fetchStorageReport(range?: ReportTimeRange): Promise<void> {
      const key: keyof typeof reportRequestIds.value = 'storage'
      const requestId = startReportRequest(key)
      isLoading.value = true
      error.value = null

      try {
        const targetRange = range || timeRange.value
        const { start, end } = calculateTimeRange(targetRange)

        const breakdown = await reportsService.getStorageReport({
          type: targetRange.type,
          startDate: start,
          endDate: end
        })

        if (!isLatestReportRequest(key, requestId)) {
          return
        }

        storageBreakdown.value = breakdown
        chartData.value = generateStorageChartData(breakdown)
      } catch (err) {
        if (!isLatestReportRequest(key, requestId)) {
          return
        }
        const message = logReportError('Storage report fetch', err)
        error.value = message
        storageBreakdown.value = []
        chartData.value = null
        throw err
      } finally {
        if (isLatestReportRequest(key, requestId)) {
          isLoading.value = false
        }
      }
    }

    // Actions - Time range
    function setTimeRange(range: ReportTimeRange): void {
      timeRange.value = { ...range }
    }

    // Watch time range changes and auto-refetch
    watch(
      () => timeRange.value,
      async (newRange) => {
        if (currentReport.value) {
          // Auto-refetch current report with new time range
          switch (currentReport.value.type) {
            case 'usage':
              await fetchUsageReport(newRange)
              break
            case 'downloads':
              await fetchDownloadReport(newRange)
              break
            case 'activity':
              await fetchActivityReport(newRange)
              break
            case 'storage':
              await fetchStorageReport(newRange)
              break
          }
        }
      },
      { deep: true }
    )

    // Actions - Chart data generation
    function generateChartData(
      reportType: string,
      metrics: UsageMetrics | DownloadMetric[] | StorageBreakdown[]
    ): ChartData {
      switch (reportType) {
        case 'usage':
        case 'storage':
          return generateStorageChartData(metrics as StorageBreakdown[])
        case 'downloads':
          return generateDownloadChartData(metrics as DownloadMetric[])
        default:
          return { labels: [], datasets: [] }
      }
    }

    function generateStorageChartData(breakdown: StorageBreakdown[]): ChartData {
      const labels: string[] = breakdown.map((item) => item.category)
      const data = breakdown.map((item) => item.size)
      const backgroundColors: string[] = [
        'rgba(59, 130, 246, 0.8)', // blue - images
        'rgba(239, 68, 68, 0.8)', // red - videos
        'rgba(16, 185, 129, 0.8)', // green - documents
        'rgba(245, 158, 11, 0.8)', // yellow - audio
        'rgba(139, 92, 246, 0.8)' // purple - other
      ]

      const borderColors: string[] = backgroundColors.slice(0, labels.length).map((c) =>
        c.replace('0.8', '1')
      )

      return {
        labels,
        datasets: [
          {
            label: 'Storage by Category',
            data,
            backgroundColor: backgroundColors.slice(0, labels.length) as any,
            borderColor: borderColors as any
          }
        ]
      }
    }

    function generateDownloadChartData(metrics: DownloadMetric[]): ChartData {
      const labels: string[] = metrics.map((m) => {
        const date = new Date(m.date)
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      })
      const downloads = metrics.map((m) => m.downloads)
      const uniqueUsers = metrics.map((m) => m.uniqueUsers)

      return {
        labels,
        datasets: [
          {
            label: 'Downloads',
            data: downloads,
            borderColor: 'rgba(59, 130, 246, 1)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            fill: true
          },
          {
            label: 'Unique Users',
            data: uniqueUsers,
            borderColor: 'rgba(16, 185, 129, 1)',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            fill: true
          }
        ]
      }
    }

    // Actions - Export
    async function exportReport(format: ExportFormat): Promise<Blob> {
      if (!currentReport.value) {
        throw new Error('No report selected for export')
      }

      isLoading.value = true
      error.value = null

      try {
        const blob = await reportsService.exportReport(
          currentReport.value.id,
          format
        )
        return blob
      } catch (err) {
        error.value = formatApiError(err)
        throw err
      } finally {
        isLoading.value = false
      }
    }

    // Actions - Save report
    async function saveReport(name: string, type: string): Promise<Report> {
      isLoading.value = true
      error.value = null

      try {
        // Build report from current state
        let metrics: UsageMetrics | DownloadMetric[] | UserActivity[] | StorageBreakdown[]
        
        switch (type) {
          case 'usage':
            if (!usageMetrics.value) {
              throw new Error('No usage metrics to save. Please fetch usage report first.')
            }
            metrics = usageMetrics.value
            break
          case 'downloads':
            if (downloadHistory.value.length === 0) {
              throw new Error('No download data to save. Please fetch download report first.')
            }
            metrics = downloadHistory.value
            break
          case 'activity':
            if (recentActivity.value.length === 0) {
              throw new Error('No activity data to save. Please fetch activity report first.')
            }
            metrics = recentActivity.value
            break
          case 'storage':
            if (storageBreakdown.value.length === 0) {
              throw new Error('No storage data to save. Please fetch storage report first.')
            }
            metrics = storageBreakdown.value
            break
          default:
            throw new Error(`Invalid report type: ${type}`)
        }

        const report: Report = {
          id: 0, // Will be assigned by backend
          name,
          type: type as Report['type'],
          timeRange: timeRange.value,
          metrics,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          created_by: authStore.user?.id || 0
        }

        const savedReport = await reportsService.saveReport(report)
        savedReports.value.push(savedReport as SavedReport)
        return savedReport
      } catch (err) {
        error.value = formatApiError(err)
        throw err
      } finally {
        isLoading.value = false
      }
    }

    // Actions - Fetch saved reports
    async function fetchSavedReports(): Promise<void> {
      isLoading.value = true
      error.value = null

      try {
        const saved = await reportsService.getAllReports({ type: 'usage' }) // Filter saved reports
        savedReports.value = saved as SavedReport[]
      } catch (err) {
        error.value = formatApiError(err)
        savedReports.value = []
        throw err
      } finally {
        isLoading.value = false
      }
    }

    // Actions - Current report
    function setCurrentReport(report: Report | null): void {
      currentReport.value = report
      if (report) {
        timeRange.value = report.timeRange
      }
    }

    // Actions - Utility
    function clearError(): void {
      error.value = null
    }

    function reset(): void {
      reports.value = []
      currentReport.value = null
      savedReports.value = []
      reportSummary.value = null
      timeRange.value = { ...DEFAULT_TIME_RANGE }
      usageMetrics.value = null
      downloadHistory.value = []
      recentActivity.value = []
      storageBreakdown.value = []
      chartData.value = null
      error.value = null
    }

    return {
      // State - Reports
      reports,
      currentReport,
      savedReports,
      reportSummary,

      // State - Time range
      timeRange,

      // State - Metrics
      usageMetrics,
      downloadHistory,
      recentActivity,
      storageBreakdown,

      // State - Charts
      chartData,

      // Global state
      isLoading,
      error,

      // Computed
      chartsReady,
      exportDisabled,
      timeRangeDisplay,

      // Actions - Fetch reports
      fetchUsageReport,
      fetchDownloadReport,
      fetchActivityReport,
      fetchStorageReport,

      // Actions - Time range
      setTimeRange,

      // Actions - Chart generation
      generateChartData,
      generateStorageChartData,
      generateDownloadChartData,

      // Actions - Export
      exportReport,

      // Actions - Save
      saveReport,
      fetchSavedReports,

      // Actions - Current report
      setCurrentReport,

      // Actions - Utility
      clearError,
      reset
    }
  },
  {
    persist: {
      paths: ['timeRange'] // Only persist time range preference
    }
  }
)

