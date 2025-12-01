/**
 * Reports Module TypeScript Types
 * 
 * Enterprise-grade type definitions for DAM Reports and Analytics functionality.
 * Supports usage metrics, download tracking, user activity, and storage analytics
 * with time range filtering and data visualization.
 */

/**
 * Report Time Range Type
 * 
 * Predefined time ranges for report filtering:
 * - today: Current day
 * - week: Last 7 days
 * - month: Current month
 * - quarter: Current quarter (3 months)
 * - custom: User-defined date range
 */
export type ReportTimeRangeType = 'today' | 'week' | 'month' | 'quarter' | 'custom'

/**
 * Report Time Range
 * 
 * Defines the time period for report data.
 * For custom ranges, startDate and endDate must be provided.
 * 
 * @property type - Time range type
 * @property startDate - ISO 8601 date string (required for custom, optional for others)
 * @property endDate - ISO 8601 date string (required for custom, optional for others)
 */
export interface ReportTimeRange {
  type: ReportTimeRangeType
  startDate: string // ISO 8601 format
  endDate: string // ISO 8601 format
}

/**
 * Asset Type Breakdown
 * 
 * Count of assets by MIME type category.
 */
export interface AssetsByType {
  images: number
  videos: number
  documents: number
  audio: number
  other: number
}

/**
 * Usage Metrics
 * 
 * Overall usage statistics for the DAM system.
 * 
 * @property totalAssets - Total number of assets in the system
 * @property assetsByType - Breakdown by asset type
 * @property storageUsed - Total storage used in bytes
 * @property storageLimit - Storage limit in bytes (null if unlimited)
 * @property storagePercentage - Percentage of storage used (0-100)
 */
export interface UsageMetrics {
  totalAssets: number
  assetsByType: AssetsByType
  storageUsed: number // bytes
  storageLimit: number | null // bytes, null if unlimited
  storagePercentage: number // 0-100
}

/**
 * Download Metric
 * 
 * Time-series data point for download tracking.
 * Used for line charts showing download trends over time.
 * 
 * @property date - ISO 8601 date string
 * @property downloads - Total number of downloads on this date
 * @property uniqueUsers - Number of unique users who downloaded
 */
export interface DownloadMetric {
  date: string // ISO 8601 format
  downloads: number
  uniqueUsers: number
}

/**
 * User Activity Action Type
 * 
 * Types of actions that can be tracked in user activity reports.
 */
export type UserActivityAction =
  | 'upload'
  | 'download'
  | 'view'
  | 'delete'
  | 'share'
  | 'edit'
  | 'comment'
  | 'tag'

/**
 * User Activity
 * 
 * Single activity record for a user action.
 * 
 * @property username - User who performed the action
 * @property email - User email
 * @property action - Type of action performed
 * @property asset_id - ID of the asset (if applicable)
 * @property asset_name - Name of the asset (if applicable)
 * @property timestamp - ISO 8601 timestamp of the action
 * @property metadata - Additional metadata (optional)
 */
export interface UserActivity {
  username: string
  email: string
  action: UserActivityAction
  asset_id: number | null
  asset_name: string | null
  timestamp: string // ISO 8601 format
  metadata?: Record<string, unknown>
}

/**
 * Storage Category
 * 
 * Categories for storage breakdown.
 */
export type StorageCategory = 'images' | 'videos' | 'documents' | 'audio' | 'other'

/**
 * Storage Breakdown
 * 
 * Storage usage breakdown by category.
 * Used for pie charts showing storage distribution.
 * 
 * @property category - Storage category
 * @property size - Size in bytes
 * @property count - Number of assets in this category
 * @property percentage - Percentage of total storage (0-100)
 */
export interface StorageBreakdown {
  category: StorageCategory
  size: number // bytes
  count: number
  percentage: number // 0-100
}

/**
 * Report Type
 * 
 * Types of reports available in the system.
 */
export type ReportType = 'usage' | 'downloads' | 'activity' | 'storage'

/**
 * Report
 * 
 * Generic report interface with type-specific metrics.
 * 
 * @property id - Report ID
 * @property name - Report name
 * @property type - Report type
 * @property timeRange - Time range for the report
 * @property metrics - Report-specific metrics (varies by type)
 * @property created_at - ISO 8601 timestamp
 * @property updated_at - ISO 8601 timestamp
 * @property created_by - User ID who created the report
 */
export interface Report {
  id: number
  name: string
  type: ReportType
  timeRange: ReportTimeRange
  metrics: UsageMetrics | DownloadMetric[] | UserActivity[] | StorageBreakdown[]
  created_at: string // ISO 8601 format
  updated_at: string // ISO 8601 format
  created_by: number
}

/**
 * Export Format
 * 
 * Supported export formats for reports.
 */
export type ExportFormat = 'csv' | 'pdf'

/**
 * Export Request
 * 
 * Request payload for exporting a report.
 * 
 * @property reportId - ID of the report to export
 * @property format - Export format
 */
export interface ExportRequest {
  reportId: number
  format: ExportFormat
}

/**
 * Chart Dataset
 * 
 * Single dataset for chart visualization.
 * 
 * @property label - Dataset label
 * @property data - Array of numeric values
 * @property borderColor - Border color (hex or RGB)
 * @property backgroundColor - Background color (hex or RGB)
 * @property fill - Whether to fill the area under the line (for line charts)
 */
export interface ChartDataset {
  label: string
  data: number[]
  borderColor?: string
  backgroundColor?: string
  fill?: boolean
}

/**
 * Chart Data
 * 
 * Structured data for chart visualization.
 * Compatible with Chart.js and ApexCharts.
 * 
 * @property labels - Array of labels for X-axis or categories
 * @property datasets - Array of datasets
 */
export interface ChartData {
  labels: string[]
  datasets: ChartDataset[]
}

/**
 * Get Reports Parameters
 * 
 * Query parameters for fetching reports.
 * All fields are optional for flexible filtering.
 * 
 * @property type - Filter by report type
 * @property timeRange - Filter by time range
 * @property sort_by - Sort field ('created_at', 'updated_at', 'name')
 * @property page - Page number for pagination
 * @property page_size - Items per page
 */
export interface GetReportsParams {
  type?: ReportType
  timeRange?: ReportTimeRange
  sort_by?: 'created_at' | 'updated_at' | 'name'
  page?: number
  page_size?: number
}

/**
 * Saved Report
 * 
 * Report that has been saved for later use.
 * Extends base Report with saved-specific fields.
 */
export interface SavedReport extends Report {
  is_favorite: boolean
  last_viewed: string | null // ISO 8601 format
}

/**
 * Report Summary
 * 
 * Summary statistics for quick dashboard display.
 */
export interface ReportSummary {
  totalReports: number
  recentReports: Report[]
  favoriteReports: SavedReport[]
  lastGenerated: string | null // ISO 8601 format
}

/**
 * Type guard to check if report is usage report
 */
export function isUsageReport(
  report: Report
): report is Report & { metrics: UsageMetrics } {
  return report.type === 'usage'
}

/**
 * Type guard to check if report is downloads report
 */
export function isDownloadsReport(
  report: Report
): report is Report & { metrics: DownloadMetric[] } {
  return report.type === 'downloads'
}

/**
 * Type guard to check if report is activity report
 */
export function isActivityReport(
  report: Report
): report is Report & { metrics: UserActivity[] } {
  return report.type === 'activity'
}

/**
 * Type guard to check if report is storage report
 */
export function isStorageReport(
  report: Report
): report is Report & { metrics: StorageBreakdown[] } {
  return report.type === 'storage'
}



