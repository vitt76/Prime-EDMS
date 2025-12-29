import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { analyticsService } from '@/services/analyticsService'

export interface AssetBankTopMetrics {
  total_assets: number
  storage_used_bytes: number
  mau: number
  search_success_rate: number
  avg_find_time_minutes: number | null
}

export interface AssetDistributionItem {
  type: 'images' | 'videos' | 'documents' | 'other'
  count: number
  size_bytes: number
}

export interface MostDownloadedAssetRow {
  document_id: number
  document__label: string
  downloads: number
  views: number
  shares: number
}

export const useAnalyticsStore = defineStore('analytics', () => {
  // Asset Bank state
  const assetBankTopMetrics = ref<AssetBankTopMetrics | null>(null)
  const assetDistribution = ref<AssetDistributionItem[]>([])
  const mostDownloadedAssets = ref<MostDownloadedAssetRow[]>([])

  // Common state
  const isLoading = ref(false)
  const lastUpdated = ref<Date | null>(null)
  const error = ref<string | null>(null)

  const hasData = computed(() => {
    return (
      !!assetBankTopMetrics.value ||
      assetDistribution.value.length > 0 ||
      mostDownloadedAssets.value.length > 0
    )
  })

  async function fetchAssetBankTopMetrics(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      assetBankTopMetrics.value = await analyticsService.getAssetBankTopMetrics()
      lastUpdated.value = new Date()
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить метрики'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchAssetDistribution(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      assetDistribution.value = await analyticsService.getAssetDistribution()
      lastUpdated.value = new Date()
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить распределение ассетов'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchMostDownloadedAssets(params?: {
    date_from?: string
    date_to?: string
  }): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      mostDownloadedAssets.value = await analyticsService.getMostDownloadedAssets(params)
      lastUpdated.value = new Date()
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить топ скачиваний'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchAssetBankAll(): Promise<void> {
    await Promise.all([
      fetchAssetBankTopMetrics(),
      fetchAssetDistribution(),
      fetchMostDownloadedAssets(),
    ])
  }

  return {
    // state
    assetBankTopMetrics,
    assetDistribution,
    mostDownloadedAssets,
    isLoading,
    lastUpdated,
    error,
    // computed
    hasData,
    // actions
    fetchAssetBankTopMetrics,
    fetchAssetDistribution,
    fetchMostDownloadedAssets,
    fetchAssetBankAll,
  }
})


