import { apiService } from './apiService'
import type {
  Report,
  ReportTimeRange,
  UsageMetrics,
  DownloadMetric,
  UserActivity,
  StorageBreakdown,
  ExportFormat,
  GetReportsParams
} from '@/types/reports'

/**
 * Reports Service
 * 
 * Service class for reports and analytics-related API operations.
 * Handles fetching metrics, generating charts, and exporting reports.
 */
class ReportsService {
  /**
   * Get usage report with overall metrics
   */
  async getUsageReport(timeRange: ReportTimeRange): Promise<UsageMetrics> {
    const queryParams: Record<string, string> = {
      start: timeRange.startDate,
      end: timeRange.endDate
    }

    return apiService.get<UsageMetrics>(
      '/v4/reports/usage/',
      { params: queryParams },
      true // Cache usage reports for 5 minutes
    )
  }

  /**
   * Get download report with time-series data
   */
  async getDownloadReport(
    timeRange: ReportTimeRange
  ): Promise<DownloadMetric[]> {
    const queryParams: Record<string, string> = {
      start: timeRange.startDate,
      end: timeRange.endDate
    }

    return apiService.get<DownloadMetric[]>(
      '/v4/reports/downloads/',
      { params: queryParams },
      true // Cache download reports for 5 minutes
    )
  }

  /**
   * Get activity report with user actions
   */
  async getActivityReport(
    timeRange: ReportTimeRange,
    limit?: number
  ): Promise<UserActivity[]> {
    const queryParams: Record<string, string | number> = {
      start: timeRange.startDate,
      end: timeRange.endDate
    }

    if (limit) {
      queryParams.limit = limit
    }

    return apiService.get<UserActivity[]>(
      '/v4/reports/activity/',
      { params: queryParams },
      false // Don't cache activity reports (real-time data)
    )
  }

  /**
   * Get storage report with breakdown by category
   */
  async getStorageReport(
    timeRange: ReportTimeRange
  ): Promise<StorageBreakdown[]> {
    const queryParams: Record<string, string> = {
      start: timeRange.startDate,
      end: timeRange.endDate
    }

    return apiService.get<StorageBreakdown[]>(
      '/v4/reports/storage/',
      { params: queryParams },
      true // Cache storage reports for 5 minutes
    )
  }

  /**
   * Export report as CSV or PDF
   */
  async exportReport(reportId: number, format: ExportFormat): Promise<Blob> {
    // Use axios directly for blob responses
    const axios = (await import('axios')).default
    const token = localStorage.getItem('auth_token')
    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

    const response = await axios.get<Blob>(
      `${API_BASE_URL}/v4/reports/${reportId}/export/`,
      {
        params: { format },
        responseType: 'blob',
        headers: {
          Authorization: token ? `Bearer ${token}` : ''
        }
      }
    )

    return response.data
  }

  /**
   * Get all reports (saved or generated)
   */
  async getAllReports(params?: GetReportsParams): Promise<Report[]> {
    const queryParams: Record<string, string | number> = {}

    if (params?.type) {
      queryParams.type = params.type
    }
    if (params?.timeRange) {
      queryParams.start = params.timeRange.startDate
      queryParams.end = params.timeRange.endDate
    }
    if (params?.sort_by) {
      queryParams.sort_by = params.sort_by
    }
    if (params?.page) {
      queryParams.page = params.page
    }
    if (params?.page_size) {
      queryParams.page_size = params.page_size
    }

    return apiService.get<Report[]>(
      '/v4/reports/',
      { params: queryParams },
      true // Cache reports list for 5 minutes
    )
  }

  /**
   * Save a report for later use
   */
  async saveReport(report: Report): Promise<Report> {
    // Validate report
    if (!report.name || report.name.trim().length === 0) {
      throw new Error('Report name is required')
    }
    if (report.name.length > 255) {
      throw new Error('Report name must be 255 characters or less')
    }

    return apiService.post<Report>('/v4/reports/', report)
  }

  /**
   * Get report by ID
   */
  async getReport(id: number): Promise<Report> {
    return apiService.get<Report>(`/v4/reports/${id}/`, undefined, true)
  }

  /**
   * Delete saved report
   */
  async deleteReport(id: number): Promise<void> {
    return apiService.delete<void>(`/v4/reports/${id}/`)
  }
}

export const reportsService = new ReportsService()

