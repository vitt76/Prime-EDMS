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
  mentions: number | null
  mentions_supported: boolean
}

export interface HomeStorageStats {
  used_bytes: number
  limit_bytes: number | null
  percentage: number | null
  is_unlimited: boolean
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

    const results = await Promise.allSettled([
      apiService.get<HomeDocumentsStats>('/api/v4/headless/documents/stats/'),
      apiService.get<HomeAiStats>('/api/v4/headless/documents/ai-stats/'),
      apiService.get<HomeInboxStats>('/api/v4/headless/user/inbox-stats/'),
      apiService.get<HomeStorageStats>('/api/v4/headless/organization/storage-stats/'),
      apiService.get<{ results: BackendOptimizedDocument[] }>('/api/v4/documents/optimized/', {
        params: { ordering: '-datetime_created', page_size: 8 }
      }),
      getDashboardActivityNormalized(10),
      apiService.get<AIInsight[]>('/api/v4/headless/user/daily-insights/')
    ])

    const sectionErrors: string[] = []

    if (results[0].status === 'fulfilled') {
      documentsStats.value = results[0].value
    } else {
      documentsStats.value = null
      sectionErrors.push(`Документы: ${formatApiError(results[0].reason)}`)
    }

    if (results[1].status === 'fulfilled') {
      aiStats.value = results[1].value
    } else {
      aiStats.value = null
      sectionErrors.push(`AI: ${formatApiError(results[1].reason)}`)
    }

    if (results[2].status === 'fulfilled') {
      inboxStats.value = results[2].value
    } else {
      inboxStats.value = null
      sectionErrors.push(`Inbox: ${formatApiError(results[2].reason)}`)
    }

    if (results[3].status === 'fulfilled') {
      storageStats.value = results[3].value
    } else {
      storageStats.value = null
      sectionErrors.push(`Хранилище: ${formatApiError(results[3].reason)}`)
    }

    if (results[4].status === 'fulfilled') {
      recentAssets.value = (results[4].value.results || []).map((doc) => adaptBackendAsset(doc))
    } else {
      recentAssets.value = []
      sectionErrors.push(`Недавние активы: ${formatApiError(results[4].reason)}`)
    }

    if (results[5].status === 'fulfilled') {
      activityFeed.value = results[5].value
    } else {
      activityFeed.value = []
      sectionErrors.push(`Активность: ${formatApiError(results[5].reason)}`)
    }

    if (results[6].status === 'fulfilled') {
      insights.value = results[6].value
    } else {
      insights.value = []
      sectionErrors.push(`Инсайты: ${formatApiError(results[6].reason)}`)
    }

    error.value = sectionErrors.length ? sectionErrors.join(' | ') : null
    isLoading.value = false
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