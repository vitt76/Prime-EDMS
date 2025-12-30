<template>
  <div class="container mx-auto px-4 py-6">

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
              {{ c.label }} ({{ formatCampaignStatus(c.status) }})
            </option>
          </select>

          <div class="md:ml-auto flex items-center gap-2">
            <button
              class="px-3 py-2 text-sm rounded-md border border-neutral-300 hover:bg-neutral-50"
              :disabled="analyticsStore.isLoading"
              @click="exportPdf"
            >
              PDF
            </button>
            <button
              class="px-3 py-2 text-sm rounded-md border border-neutral-300 hover:bg-neutral-50"
              :disabled="analyticsStore.isLoading"
              @click="refresh"
            >
              Обновить
            </button>
          </div>
        </div>

      </Card>

      <div ref="reportRef">
        <CampaignSummaryCards :campaign="analyticsStore.campaignDashboard?.campaign || null" />

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          <ViewsDownloadsChart
            :timeline="analyticsStore.campaignDashboard?.timeline || []"
            :baseline="analyticsStore.campaignDashboard?.baseline || null"
          />
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
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'

import Card from '@/components/Common/Card.vue'
import AudienceGeographyMap from '@/components/Analytics/campaign/AudienceGeographyMap.vue'
import CampaignSummaryCards from '@/components/Analytics/campaign/CampaignSummaryCards.vue'
import CampaignTimeline from '@/components/Analytics/campaign/CampaignTimeline.vue'
import ChannelDistributionChart from '@/components/Analytics/campaign/ChannelDistributionChart.vue'
import TopPerformingAssetsTable from '@/components/Analytics/campaign/TopPerformingAssetsTable.vue'
import ViewsDownloadsChart from '@/components/Analytics/campaign/ViewsDownloadsChart.vue'
import { analyticsService } from '@/services/analyticsService'
import { useAnalyticsStore } from '@/stores/analyticsStore'

const analyticsStore = useAnalyticsStore()
function formatCampaignStatus(status: string): string {
  const s = String(status || '').toLowerCase()
  if (s === 'draft') return 'Черновик'
  if (s === 'active') return 'Активна'
  if (s === 'completed') return 'Завершена'
  if (s === 'archived') return 'Архив'
  return status || '—'
}
const activeCampaignId = ref<string | null>(null)
const sessionStart = ref<Date | null>(null)
const reportRef = ref<HTMLElement | null>(null)

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

async function exportPdf(): Promise<void> {
  try {
    await nextTick()
    if (!reportRef.value) return
    const html2canvas = (await import('html2canvas')).default
    const { jsPDF } = await import('jspdf')

    const canvas = await html2canvas(reportRef.value, { scale: 2, useCORS: true })
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF({ orientation: 'portrait', unit: 'pt', format: 'a4' })

    const pageWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()

    const imgWidth = pageWidth
    const imgHeight = (canvas.height * imgWidth) / canvas.width

    let position = 0
    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
    position -= pageHeight

    while (imgHeight + position > 0) {
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      position -= pageHeight
    }

    const id = analyticsStore.campaignDashboard?.campaign?.id || 'campaign'
    pdf.save(`campaign-report-${id}.pdf`)
  } catch {
    // best-effort
  }
}

async function flushEngagement(): Promise<void> {
  if (!activeCampaignId.value || !sessionStart.value) return
  const end = new Date()
  const durationSeconds = Math.max(1, Math.floor((end.getTime() - sessionStart.value.getTime()) / 1000))
  try {
    await analyticsService.postCampaignEngagement(activeCampaignId.value, {
      duration_seconds: durationSeconds,
      session_start: sessionStart.value.toISOString(),
      session_end: end.toISOString(),
    })
  } catch {
    // best-effort
  }
}

watch(
  () => analyticsStore.selectedCampaignId,
  async (next, prev) => {
    if (prev && sessionStart.value) {
      await flushEngagement()
    }
    activeCampaignId.value = next
    sessionStart.value = next ? new Date() : null
  }
)

onUnmounted(async () => {
  await flushEngagement()
})
</script>


