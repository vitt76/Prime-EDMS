<template>
  <div class="min-h-screen bg-neutral-50">
    <div class="container mx-auto px-4 py-8">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-neutral-900">Analytics</h1>
        <p class="text-neutral-600">Campaign Performance (Phase 2)</p>
      </div>

      <Card padding="lg" class="mb-6">
        <div class="flex flex-col md:flex-row md:items-center gap-3">
          <div class="text-sm text-neutral-700">Кампания</div>
          <select
            class="px-3 py-2 text-sm rounded-md border border-neutral-300 bg-white"
            :value="analyticsStore.selectedCampaignId || ''"
            @change="onSelectCampaign(($event.target as HTMLSelectElement).value || null)"
          >
            <option v-if="analyticsStore.campaigns.length === 0" value="">Нет кампаний</option>
            <option v-for="c in analyticsStore.campaigns" :key="c.id" :value="c.id">
              {{ c.label }} ({{ c.status }})
            </option>
          </select>

          <button
            class="md:ml-auto px-3 py-2 text-sm rounded-md border border-neutral-300 hover:bg-neutral-50"
            :disabled="analyticsStore.isLoading"
            @click="refresh"
          >
            Обновить
          </button>
        </div>

        <div v-if="analyticsStore.error" class="mt-3 text-sm text-red-600">
          {{ analyticsStore.error }}
        </div>
      </Card>

      <CampaignSummaryCards :campaign="analyticsStore.campaignDashboard?.campaign || null" />

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <ViewsDownloadsChart :timeline="analyticsStore.campaignDashboard?.timeline || []" />
        <ChannelDistributionChart :channels="analyticsStore.campaignDashboard?.channels || []" />
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <TopPerformingAssetsTable :rows="analyticsStore.campaignTopAssets" />
        <CampaignTimeline
          :milestones="analyticsStore.campaignTimeline?.milestones || []"
          :velocity="analyticsStore.campaignTimeline?.velocity || {}"
        />
      </div>

      <div class="mt-6">
        <AudienceGeographyMap />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

import Card from '@/components/Common/Card.vue'
import AudienceGeographyMap from '@/components/Analytics/campaign/AudienceGeographyMap.vue'
import CampaignSummaryCards from '@/components/Analytics/campaign/CampaignSummaryCards.vue'
import CampaignTimeline from '@/components/Analytics/campaign/CampaignTimeline.vue'
import ChannelDistributionChart from '@/components/Analytics/campaign/ChannelDistributionChart.vue'
import TopPerformingAssetsTable from '@/components/Analytics/campaign/TopPerformingAssetsTable.vue'
import ViewsDownloadsChart from '@/components/Analytics/campaign/ViewsDownloadsChart.vue'
import { useAnalyticsStore } from '@/stores/analyticsStore'

const analyticsStore = useAnalyticsStore()

async function refresh(): Promise<void> {
  await analyticsStore.fetchCampaigns()
  await analyticsStore.selectCampaign(analyticsStore.selectedCampaignId)
}

async function onSelectCampaign(id: string | null): Promise<void> {
  await analyticsStore.selectCampaign(id)
}

onMounted(async () => {
  await refresh()
})
</script>


