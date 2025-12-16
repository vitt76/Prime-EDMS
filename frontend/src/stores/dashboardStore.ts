import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { dashboardService, type DashboardStats, type StorageMetrics } from '@/services/dashboardService'
import { getDashboardActivityNormalized, type ActivityItem } from '@/services/activityService'
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

    // Mock data for dev mode (matches DashboardStats interface)
    const mockStats: DashboardStats = {
      documents: {
        total: 1250,
        with_analysis: 890,
        without_analysis: 360
      },
      analyses: {
        completed: 890,
        processing: 15,
        pending: 47,
        failed: 3
      },
      providers: [
        { provider: 'yandexgpt', count: 650 },
        { provider: 'gigachat', count: 240 }
      ]
    }

    const mockStorage: StorageMetrics = {
      total_size: 107374182400,
      used_size: 16890000000,
      available_size: 90484182400,
      usage_percentage: 15.7,
      by_type: [
        { type: 'images', count: 890, size: 10000000000 },
        { type: 'videos', count: 245, size: 5000000000 },
        { type: 'documents', count: 115, size: 1890000000 }
      ]
    }

    // Actions
    async function fetchDashboardStats() {
      isLoading.value = true
      error.value = null

      try {
        // Always try to fetch real data from API
        const data = await dashboardService.getDashboardStats()
        stats.value = data
        lastUpdated.value = new Date()
      } catch (err) {
        // Fallback to mock data only if API fails
        console.warn('[DashboardStore] Failed to fetch dashboard stats, using fallback:', err)
        stats.value = mockStats
        lastUpdated.value = new Date()
        error.value = formatApiError(err)
      } finally {
        isLoading.value = false
      }
    }

    async function fetchActivityFeed(limit = 20) {
      try {
        activityFeed.value = await getDashboardActivityNormalized(limit)
      } catch (err) {
        console.warn('Failed to fetch activity feed:', err)
        activityFeed.value = []
      }
    }

    async function fetchStorageMetrics() {
      try {
        // Always try to fetch real data from API
        const data = await dashboardService.getStorageMetrics()
        storageMetrics.value = data
      } catch (err) {
        // Storage metrics are optional, return zeros if API fails
        // (dashboardService already handles errors and returns zeros)
        console.warn('Failed to fetch storage metrics:', err)
        storageMetrics.value = {
          total_size: 0,
          used_size: 0,
          available_size: 0,
          usage_percentage: 0,
          by_type: []
        }
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





