<template>
  <div class="min-h-screen bg-neutral-50">
    <div class="container mx-auto px-4 py-8">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-neutral-900">Analytics</h1>
        <p class="text-neutral-600">Asset Bank (Phase 1)</p>
      </div>

      <FilterBar
        class="mb-6"
        :date-range="analyticsStore.filters.dateRange"
        :asset-type="analyticsStore.filters.assetType"
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
          @select-type="handleSelectAssetType"
        />
        <MostDownloadedAssetsTable :rows="analyticsStore.mostDownloadedAssets" />
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
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

import AssetDistributionChart from '@/components/Analytics/AssetDistributionChart.vue'
import AssetReuseMetricsChart from '@/components/Analytics/AssetReuseMetricsChart.vue'
import AlertsList from '@/components/Analytics/AlertsList.vue'
import FilterBar from '@/components/Analytics/FilterBar.vue'
import MostDownloadedAssetsTable from '@/components/Analytics/MostDownloadedAssetsTable.vue'
import StorageTrendsChart from '@/components/Analytics/StorageTrendsChart.vue'
import TopMetricsCard from '@/components/Analytics/TopMetricsCard.vue'
import UserAdoptionHeatMap from '@/components/Analytics/UserAdoptionHeatMap.vue'
import { useAnalyticsStore } from '@/stores/analyticsStore'

const analyticsStore = useAnalyticsStore()

async function refreshAll(): Promise<void> {
  await analyticsStore.fetchAssetBankAll()
}

async function handleApplyFilters(payload: {
  dateRange: [string, string] | null
  assetType: 'images' | 'videos' | 'documents' | 'other' | null
}): Promise<void> {
  analyticsStore.setDateRange(payload.dateRange)
  analyticsStore.setAssetType(payload.assetType)
  await analyticsStore.applyFilters()
}

async function handleClearFilters(): Promise<void> {
  analyticsStore.setDateRange(null)
  analyticsStore.setAssetType(null)
  await analyticsStore.applyFilters()
}

async function handleSelectAssetType(type: 'images' | 'videos' | 'documents' | 'other'): Promise<void> {
  analyticsStore.setAssetType(type)
  await analyticsStore.applyFilters()
}

onMounted(async () => {
  await refreshAll()
})
</script>


