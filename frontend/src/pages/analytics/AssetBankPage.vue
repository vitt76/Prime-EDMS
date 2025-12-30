<template>
  <div class="container mx-auto px-4 py-6">

      <FilterBar
        class="mb-6"
        :date-range="analyticsStore.filters.dateRange"
        :asset-type="analyticsStore.filters.assetType"
        :department="analyticsStore.filters.department"
        @apply="handleApplyFilters"
        @clear="handleClearFilters"
      />

      <TopMetricsCard
        :metrics="analyticsStore.assetBankTopMetrics"
        :last-updated="analyticsStore.lastUpdated"
        :is-loading="analyticsStore.isLoading"
        :error="analyticsStore.error"
        @refresh="refreshAll"
      />

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <AssetDistributionChart
          :distribution="analyticsStore.assetDistribution"
          :trend="analyticsStore.assetDistributionTrend"
          @select-type="handleSelectAssetType"
        />
        <MostDownloadedAssetsTable
          :rows="analyticsStore.mostDownloadedAssets"
          @select="handleSelectAsset"
        />
      </div>

      <div class="mt-6">
        <AssetReuseMetricsChart
          :monthly-data="analyticsStore.assetReuseMetrics?.monthly_data || []"
          :target-rate="analyticsStore.assetReuseMetrics?.target_rate || 62"
        />
      </div>

      <div class="mt-6">
        <StorageTrendsChart
          :historical="analyticsStore.storageTrends?.historical || []"
          :forecast="analyticsStore.storageTrends?.forecast || []"
          :storage-limit-gb="analyticsStore.storageTrends?.storage_limit_gb || 0"
          :alert-threshold="analyticsStore.storageTrends?.alert_threshold || 0"
        />
      </div>

      <div class="mt-6">
        <UserAdoptionHeatMap
          :heatmap-data="analyticsStore.userAdoptionHeatmap?.heatmap_data || []"
          :departments="analyticsStore.userAdoptionHeatmap?.departments || []"
          :regions="analyticsStore.userAdoptionHeatmap?.regions || []"
        />
      </div>

      <div class="mt-6">
        <AlertsList :rows="analyticsStore.assetBankAlerts" />
      </div>
  </div>

  <AssetDetailModal
    :open="assetDetailModalOpen"
    :document-id="selectedAsset?.document_id ?? null"
    :document-label="selectedAsset?.document__label ?? null"
    @close="assetDetailModalOpen = false"
  />
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

import AssetDistributionChart from '@/components/Analytics/AssetDistributionChart.vue'
import AssetDetailModal from '@/components/Analytics/AssetDetailModal.vue'
import AssetReuseMetricsChart from '@/components/Analytics/AssetReuseMetricsChart.vue'
import AlertsList from '@/components/Analytics/AlertsList.vue'
import FilterBar from '@/components/Analytics/FilterBar.vue'
import MostDownloadedAssetsTable from '@/components/Analytics/MostDownloadedAssetsTable.vue'
import StorageTrendsChart from '@/components/Analytics/StorageTrendsChart.vue'
import TopMetricsCard from '@/components/Analytics/TopMetricsCard.vue'
import UserAdoptionHeatMap from '@/components/Analytics/UserAdoptionHeatMap.vue'
import { useAnalyticsStore } from '@/stores/analyticsStore'
import type { MostDownloadedAssetRow } from '@/stores/analyticsStore'

const analyticsStore = useAnalyticsStore()
const selectedAsset = ref<MostDownloadedAssetRow | null>(null)
const assetDetailModalOpen = ref(false)
let ws: WebSocket | null = null

async function refreshAll(): Promise<void> {
  await analyticsStore.fetchAssetBankAll()
}

async function handleApplyFilters(payload: {
  dateRange: [string, string] | null
  assetType: 'images' | 'videos' | 'documents' | 'other' | null
  department: string | null
}): Promise<void> {
  analyticsStore.setDateRange(payload.dateRange)
  analyticsStore.setAssetType(payload.assetType)
  analyticsStore.setDepartment(payload.department)
  await analyticsStore.applyFilters()
}

async function handleClearFilters(): Promise<void> {
  analyticsStore.setDateRange(null)
  analyticsStore.setAssetType(null)
  analyticsStore.setDepartment(null)
  await analyticsStore.applyFilters()
}

async function handleSelectAssetType(type: 'images' | 'videos' | 'documents' | 'other'): Promise<void> {
  analyticsStore.setAssetType(type)
  await analyticsStore.applyFilters()
}

function handleSelectAsset(row: MostDownloadedAssetRow): void {
  selectedAsset.value = row
  assetDetailModalOpen.value = true
}

onMounted(async () => {
  await refreshAll()

  // Real-time updates (best-effort). Requires backend Channels route: /ws/analytics/
  try {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    ws = new WebSocket(`${protocol}://${window.location.host}/ws/analytics/`)
    ws.onmessage = async (event) => {
      try {
        const payload = JSON.parse(event.data || '{}')
        if (payload?.type === 'refresh' && !analyticsStore.isLoading) {
          await refreshAll()
        }
      } catch {
        // ignore
      }
    }
  } catch {
    ws = null
  }
})

onUnmounted(() => {
  try {
    ws?.close()
  } catch {
    // ignore
  }
  ws = null
})
</script>


