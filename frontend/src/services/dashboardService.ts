import { apiService } from './apiService'

export interface DashboardStats {
  documents: {
    total: number
    with_analysis: number
    without_analysis: number
  }
  analyses: {
    completed: number
    processing: number
    pending: number
    failed: number
  }
  providers: Array<{
    provider: string
    count: number
  }>
}

export interface ActivityItem {
  id: number
  type: 'upload' | 'download' | 'share' | 'comment' | 'tag' | 'delete'
  user: string
  user_id: number
  asset_id?: number
  asset_label?: string
  timestamp: string
  description: string
}

export interface StorageMetrics {
  total_size: number
  used_size: number
  available_size: number
  usage_percentage: number
  by_type: Array<{
    type: string
    count: number
    size: number
  }>
}

class DashboardService {
  /**
   * Get dashboard statistics
   */
  async getDashboardStats(): Promise<DashboardStats> {
    return apiService.get<DashboardStats>(
      '/v4/dam/dashboard-stats/',
      undefined,
      true // Cache for 5 minutes
    )
  }

  /**
   * Get activity feed
   */
  async getActivityFeed(limit = 20): Promise<ActivityItem[]> {
    // TODO: Replace with actual activity endpoint when available
    // For now, return empty array (endpoint doesn't exist yet)
    try {
      return await apiService.get<ActivityItem[]>(
        '/v4/dam/activity/',
        { params: { limit } } as any,
        false
      )
    } catch {
      // Fallback to empty array if endpoint doesn't exist
      return []
    }
  }

  /**
   * Get storage metrics
   */
  async getStorageMetrics(): Promise<StorageMetrics> {
    // TODO: Replace with actual storage endpoint when available
    return apiService.get<StorageMetrics>(
      '/v4/dam/storage-metrics/',
      undefined,
      true // Cache for 5 minutes
    ).catch(() => {
      // Fallback to calculated metrics from assets
      return {
        total_size: 0,
        used_size: 0,
        available_size: 0,
        usage_percentage: 0,
        by_type: []
      }
    })
  }
}

export const dashboardService = new DashboardService()

