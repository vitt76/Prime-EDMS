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
  comments: {
    last_7_days: number
    last_24_hours: number
  }
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
    const [documents, aiStats, inboxStats] = await Promise.all([
      apiService.get<{
        total: number
      }>('/api/v4/headless/documents/stats/', undefined, false),
      apiService.get<{
        analyzed: number
        queued: number
        pending: number
        failed: number
      }>('/api/v4/headless/documents/ai-stats/', undefined, false),
      apiService.get<{
        comments_new: number
      }>('/api/v4/headless/user/inbox-stats/', undefined, false)
    ])

    const totalDocuments = documents?.total ?? 0
    const analyzedDocuments = aiStats?.analyzed ?? 0

    return {
      documents: {
        total: totalDocuments,
        with_analysis: analyzedDocuments,
        without_analysis: Math.max(totalDocuments - analyzedDocuments, 0)
      },
      analyses: {
        completed: analyzedDocuments,
        processing: aiStats?.queued ?? 0,
        pending: aiStats?.pending ?? 0,
        failed: aiStats?.failed ?? 0
      },
      providers: [],
      comments: {
        last_7_days: inboxStats?.comments_new ?? 0,
        last_24_hours: 0
      }
    }
  }

  /**
   * Get activity feed
   */
  async getActivityFeed(limit = 20): Promise<ActivityItem[]> {
    const response = await apiService.get<{
      results: Array<{
        id: number
        timestamp: string
        actor: { id: number | null; username: string } | null
        verb: string
        verb_code: string
        target: { id: number | null; label: string | null } | null
      }>
    }>(
      '/api/v4/headless/activity/feed/',
      { params: { filter: 'my_documents', important: 1, system: 0, page_size: limit } } as any,
      false
    )

    return (response?.results || []).map((item) => ({
      id: item.id,
      type: 'upload',
      user: item.actor?.username || 'system',
      user_id: item.actor?.id || null,
      asset_id: item.target?.id || undefined,
      asset_label: item.target?.label || undefined,
      timestamp: item.timestamp,
      description: item.verb || ''
    }))
  }

  /**
   * Get storage metrics
   */
  async getStorageMetrics(): Promise<StorageMetrics> {
    try {
      const data = await apiService.get<any>(
        '/api/v4/headless/organization/storage-stats/',
        undefined,
        false
      )

      const used_bytes = data?.used_bytes || 0
      const total_bytes = data?.limit_bytes || 0

      return {
        total_size: total_bytes,
        used_size: used_bytes,
        available_size: Math.max(0, total_bytes - used_bytes),
        usage_percentage: typeof data?.percentage === 'number' ? data.percentage : 0,
        by_type: []
      }
    } catch (err: any) {
      if (import.meta.env.DEV) {
        console.warn('[DashboardService] Storage metrics unavailable:', err)
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

