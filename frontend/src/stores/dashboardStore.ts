import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { dashboardService, type DashboardStats, type ActivityItem, type StorageMetrics } from '@/services/dashboardService'
import { formatApiError } from '@/utils/errors'

export const useDashboardStore = defineStore(
  'dashboard',
  () => {
    // State
    const stats = ref<DashboardStats | null>(null)
    const activityFeed = ref<ActivityItem[]>([])
    const storageMetrics = ref<StorageMetrics | null>(null)
    const isLoading = ref(false)
    const error = ref<string | null>(null)
    const lastUpdated = ref<Date | null>(null)

    // Getters
    const hasRecentActivity = computed(() => activityFeed.value.length > 0)
    const storageUsagePercentage = computed(() => {
      if (!storageMetrics.value) return 0
      return storageMetrics.value.usage_percentage
    })
    const formattedStorageUsed = computed(() => {
      if (!storageMetrics.value) return '0 B'
      return formatBytes(storageMetrics.value.used_size)
    })
    const formattedStorageTotal = computed(() => {
      if (!storageMetrics.value) return '0 B'
      return formatBytes(storageMetrics.value.total_size)
    })

    // Actions
    async function fetchDashboardStats() {
      isLoading.value = true
      error.value = null

      try {
        const data = await dashboardService.getDashboardStats()
        stats.value = data
        lastUpdated.value = new Date()
      } catch (err) {
        error.value = formatApiError(err)
        throw err
      } finally {
        isLoading.value = false
      }
    }

    async function fetchActivityFeed(limit = 20) {
      try {
        const data = await dashboardService.getActivityFeed(limit)
        activityFeed.value = data
      } catch (err) {
        // Activity feed is optional, don't throw
        console.warn('Failed to fetch activity feed:', err)
        activityFeed.value = []
      }
    }

    async function fetchStorageMetrics() {
      try {
        const data = await dashboardService.getStorageMetrics()
        storageMetrics.value = data
      } catch (err) {
        // Storage metrics are optional, don't throw
        console.warn('Failed to fetch storage metrics:', err)
        storageMetrics.value = null
      }
    }

    async function refresh() {
      await Promise.all([
        fetchDashboardStats(),
        fetchActivityFeed(),
        fetchStorageMetrics()
      ])
    }

    // Helper function
    function formatBytes(bytes: number): string {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return `${Math.round((bytes / Math.pow(k, i)) * 100) / 100} ${sizes[i]}`
    }

    return {
      // State
      stats,
      activityFeed,
      storageMetrics,
      isLoading,
      error,
      lastUpdated,
      // Getters
      hasRecentActivity,
      storageUsagePercentage,
      formattedStorageUsed,
      formattedStorageTotal,
      // Actions
      fetchDashboardStats,
      fetchActivityFeed,
      fetchStorageMetrics,
      refresh
    }
  },
  {
    persist: false // Don't persist dashboard data
  }
)

