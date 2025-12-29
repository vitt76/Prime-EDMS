<template>
  <div class="min-h-screen bg-neutral-50">
    <div class="container mx-auto px-4 py-8">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-neutral-900">Analytics</h1>
        <p class="text-neutral-600">Asset Bank (Phase 1)</p>
      </div>

      <TopMetricsCard
        :metrics="analyticsStore.assetBankTopMetrics"
        :last-updated="analyticsStore.lastUpdated"
        :is-loading="analyticsStore.isLoading"
        :error="analyticsStore.error"
        @refresh="refreshAll"
      />

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <AssetDistributionChart :distribution="analyticsStore.assetDistribution" />
        <MostDownloadedAssetsTable :rows="analyticsStore.mostDownloadedAssets" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

import AssetDistributionChart from '@/components/Analytics/AssetDistributionChart.vue'
import MostDownloadedAssetsTable from '@/components/Analytics/MostDownloadedAssetsTable.vue'
import TopMetricsCard from '@/components/Analytics/TopMetricsCard.vue'
import { useAnalyticsStore } from '@/stores/analyticsStore'

const analyticsStore = useAnalyticsStore()

async function refreshAll(): Promise<void> {
  await analyticsStore.fetchAssetBankAll()
}

onMounted(async () => {
  await refreshAll()
})
</script>


