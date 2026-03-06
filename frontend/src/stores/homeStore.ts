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

export interface HomeSectionErrors {
  documents: string | null
  ai: string | null
  inbox: string | null
  storage: string | null
  recentAssets: string | null
  activity: string | null
  insights: string | null
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
  const sectionErrors = ref<HomeSectionErrors>({
    documents: null,
    ai: null,
    inbox: null,
    storage: null,
    recentAssets: null,
    activity: null,
    insights: null
  })

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

    const aggregatedErrors: string[] = []

    if (results[0].status === 'fulfilled') {
      documentsStats.value = results[0].value
      sectionErrors.value.documents = null
    } else {
      documentsStats.value = null
      sectionErrors.value.documents = formatApiError(results[0].reason)
      aggregatedErrors.push(`Документы: ${sectionErrors.value.documents}`)
    }

    if (results[1].status === 'fulfilled') {
      aiStats.value = results[1].value
      sectionErrors.value.ai = null
    } else {
      aiStats.value = null
      sectionErrors.value.ai = formatApiError(results[1].reason)
      aggregatedErrors.push(`AI: ${sectionErrors.value.ai}`)
    }

    if (results[2].status === 'fulfilled') {
      inboxStats.value = results[2].value
      sectionErrors.value.inbox = null
    } else {
      inboxStats.value = null
      sectionErrors.value.inbox = formatApiError(results[2].reason)
      aggregatedErrors.push(`Inbox: ${sectionErrors.value.inbox}`)
    }

    if (results[3].status === 'fulfilled') {
      storageStats.value = results[3].value
      sectionErrors.value.storage = null
    } else {
      storageStats.value = null
      sectionErrors.value.storage = formatApiError(results[3].reason)
      aggregatedErrors.push(`Хранилище: ${sectionErrors.value.storage}`)
    }

    if (results[4].status === 'fulfilled') {
      recentAssets.value = (results[4].value.results || []).map((doc) => adaptBackendAsset(doc))
      sectionErrors.value.recentAssets = null
    } else {
      recentAssets.value = []
      sectionErrors.value.recentAssets = formatApiError(results[4].reason)
      aggregatedErrors.push(`Недавние активы: ${sectionErrors.value.recentAssets}`)
    }

    if (results[5].status === 'fulfilled') {
      activityFeed.value = results[5].value
      sectionErrors.value.activity = null
    } else {
      activityFeed.value = []
      sectionErrors.value.activity = formatApiError(results[5].reason)
      aggregatedErrors.push(`Активность: ${sectionErrors.value.activity}`)
    }

    if (results[6].status === 'fulfilled') {
      insights.value = results[6].value
      sectionErrors.value.insights = null
    } else {
      insights.value = []
      sectionErrors.value.insights = formatApiError(results[6].reason)
      aggregatedErrors.push(`Инсайты: ${sectionErrors.value.insights}`)
    }

    error.value = aggregatedErrors.length ? aggregatedErrors.join(' | ') : null
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
    sectionErrors,
    fetchAll
  }
})