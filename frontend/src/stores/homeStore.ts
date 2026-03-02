import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiService } from '@/services/apiService'
import { formatApiError } from '@/utils/errors'
import { useAuthStore } from '@/stores/authStore'
import type { Asset } from '@/types/api'
import { adaptBackendAsset, type BackendOptimizedDocument } from '@/services/adapters/mayanAdapter'
import { getDashboardActivityNormalized, type ActivityItem } from '@/services/activityService'

export interface HomeDocumentsStats {
  total: number
  new_7days: number
  new_30days: number
}

export interface HomeAiStats {
  analyzed: number
  queued: number
  pending: number
  failed: number
}

export interface HomeInboxStats {
  unread_total: number
  comments_new: number
  approvals_pending: number
  collections_shared: number
  mentions: number
}

export interface HomeStorageStats {
  used_bytes: number
  limit_bytes: number
  percentage: number
}

export interface AIInsight {
  type: string
  count: number
  cta_label: string
  emoji: string
  message: string
}

export const useHomeStore = defineStore('home', () => {
  const documentsStats = ref<HomeDocumentsStats | null>(null)
  const aiStats = ref<HomeAiStats | null>(null)
  const inboxStats = ref<HomeInboxStats | null>(null)
  const storageStats = ref<HomeStorageStats | null>(null)
  const recentAssets = ref<Asset[]>([])
  const activityFeed = ref<ActivityItem[]>([])
  const insights = ref<AIInsight[]>([])
  
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const authStore = useAuthStore()

  async function fetchAll() {
    if (!authStore.isAuthenticated) return

    isLoading.value = true
    error.value = null

    try {
      const [docRes, aiRes, inboxStatsRes, storageRes, recentRes, activityRes, insightsRes] = await Promise.all([
        apiService.get<HomeDocumentsStats>('/api/v4/headless/documents/stats/').catch(() => ({ data: { total: 0, new_7days: 0, new_30days: 0 } })),
        apiService.get<HomeAiStats>('/api/v4/headless/documents/ai-stats/').catch(() => ({ data: { analyzed: 0, queued: 0, pending: 0, failed: 0 } })),
        apiService.get<HomeInboxStats>('/api/v4/headless/user/inbox-stats/').catch(() => ({ data: { unread_total: 0, comments_new: 0, approvals_pending: 0, collections_shared: 0, mentions: 0 } })),
        apiService.get<HomeStorageStats>('/api/v4/headless/organization/storage-stats/').catch(() => ({ data: { used_bytes: 0, limit_bytes: 0, percentage: 0 } })),
        apiService.get<{results: BackendOptimizedDocument[]}>('/api/v4/documents/optimized/', { params: { ordering: '-datetime_created', page_size: 8 } }).catch(() => ({ data: { results: [] } })),
        getDashboardActivityNormalized(10).catch(() => []),
        apiService.get<AIInsight[]>('/api/v4/headless/user/daily-insights/').catch(() => ({ data: [] }))
      ])

      documentsStats.value = docRes.data
      aiStats.value = aiRes.data
      inboxStats.value = inboxStatsRes.data
      storageStats.value = storageRes.data
      recentAssets.value = (recentRes.data.results || []).map((doc) => adaptBackendAsset(doc))
      activityFeed.value = activityRes
      insights.value = insightsRes.data
    } catch (err) {
      console.error('[HomeStore] Error fetching home data', err)
      error.value = formatApiError(err)
    } finally {
      isLoading.value = false
    }
  }

  return {
    documentsStats,
    aiStats,
    inboxStats,
    storageStats,
    recentAssets,
    activityFeed,
    insights,
    isLoading,
    error,
    fetchAll
  }
})