import { apiService } from './apiService'

export interface DashboardStats {
  documents: {
    total: number
    with_analysis?: number  // Optional - not provided by headless endpoint
    without_analysis?: number  // Optional - not provided by headless endpoint
    last_30_days?: number
    prev_30_days?: number
    growth_percent?: number | null
    growth_label?: string
  }
  analyses?: {
    completed: number
    processing: number
    pending: number
    failed: number
  }
  providers?: Array<{
    provider: string
    count: number
  }>
  comments?: {
    last_7_days: number
    last_24_hours: number
  }
  users?: {
    total: number
    active_total: number
    last_30_days: number
    prev_30_days: number
    growth_percent: number | null
    growth_label: string
  }
  storage?: {
    used_bytes: number
    total_bytes: number
    unknown_size_files: number
  }
  generated_at?: string
  window_days?: number
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
    // Use headless dashboard stats endpoint (same as admin panel)
    const data = await apiService.get<any>(
      '/api/v4/headless/dashboard/stats/',
      undefined,
      false // Don't cache - data should be up-to-date
    )
    
    // Adapt the response to match DashboardStats interface
    return {
      documents: {
        total: data.documents?.total || 0,
        with_analysis: 0,  // Not provided by headless endpoint
        without_analysis: 0,  // Not provided by headless endpoint
        last_30_days: data.documents?.last_30_days,
        prev_30_days: data.documents?.prev_30_days,
        growth_percent: data.documents?.growth_percent,
        growth_label: data.documents?.growth_label
      },
      analyses: {
        completed: 0,  // Not provided by headless endpoint
        processing: 0,
        pending: 0,
        failed: 0
      },
      providers: [],  // Not provided by headless endpoint
      comments: {
        last_7_days: 0,  // Not provided by headless endpoint
        last_24_hours: 0
      },
      users: data.users,
      storage: data.storage,
      generated_at: data.generated_at,
      window_days: data.window_days
    }
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
    try {
      // Try to get storage data from headless dashboard stats (same as admin panel)
      const data = await apiService.get<any>(
        '/api/v4/headless/dashboard/stats/',
        undefined,
        false // Don't cache, as storage can change
      )
      
      // Extract storage metrics from response
      const used_bytes = data?.storage?.used_bytes || 0
      const total_bytes = data?.storage?.total_bytes || 0
      
      return {
        total_size: total_bytes,
        used_size: used_bytes,
        available_size: Math.max(0, total_bytes - used_bytes),
        usage_percentage: total_bytes > 0 
          ? Math.round((used_bytes / total_bytes) * 100 * 100) / 100 
          : 0,
        by_type: [] // Not provided by headless endpoint
      }
    } catch (err: any) {
      // For 403 (access denied for non-staff users) or other errors, return zeros
      // This is expected behavior - regular users don't have access to system-wide storage stats
      if (import.meta.env.DEV) {
        console.warn('[DashboardService] Storage metrics unavailable:', err?.response?.status === 403 
          ? 'Access denied (non-staff user)' 
          : err)
      }
      return {
        total_size: 0,
        used_size: 0,
        available_size: 0,
        usage_percentage: 0,
        by_type: []
      }
    }
  }
}

export const dashboardService = new DashboardService()

