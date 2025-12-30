<template>
  <Card padding="lg">
    <div class="flex items-center justify-between gap-4 mb-2">
      <h3 class="text-base font-semibold text-neutral-900">Audience Geography</h3>
      <div class="text-xs text-neutral-500">top countries</div>
    </div>

    <div v-if="isLoading" class="text-sm text-neutral-500">Загрузка…</div>
    <div v-else-if="error" class="text-sm text-red-600">{{ error }}</div>

    <div v-else>
      <div class="h-64 border border-neutral-200 rounded-lg p-2">
        <canvas ref="canvasRef" aria-label="Campaign audience geography chart" />
      </div>

      <div class="mt-4 border border-neutral-200 rounded-lg overflow-auto max-h-64">
        <table class="min-w-full text-sm">
          <thead class="bg-neutral-50">
            <tr class="text-left">
              <th class="px-3 py-2 font-semibold text-neutral-700">Country</th>
              <th class="px-3 py-2 font-semibold text-neutral-700">MAU</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="countries.length === 0">
              <td class="px-3 py-3 text-neutral-500" colspan="2">Нет данных</td>
            </tr>
            <tr v-for="row in countries" :key="row.geo_country" class="border-t border-neutral-200">
              <td class="px-3 py-2">{{ row.geo_country }}</td>
              <td class="px-3 py-2">{{ row.mau }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </Card>
</template>

<script setup lang="ts">
import Card from '@/components/Common/Card.vue'
import { onMounted, onUnmounted, ref, watch, nextTick } from 'vue'

import { analyticsService } from '@/services/analyticsService'
import { useAnalyticsStore } from '@/stores/analyticsStore'

const analyticsStore = useAnalyticsStore()

const isLoading = ref(false)
const error = ref<string | null>(null)
const countries = ref<Array<{ geo_country: string; mau: number }>>([])

const canvasRef = ref<HTMLCanvasElement | null>(null)
let chartInstance: import('chart.js').Chart | null = null

async function renderChart(): Promise<void> {
  if (!canvasRef.value) return
  const ctx = canvasRef.value.getContext('2d')
  if (!ctx) return

  const Chart = (await import('chart.js/auto')).default

  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }

  const labels = countries.value.map((c) => c.geo_country)
  const data = countries.value.map((c) => c.mau)

  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'MAU',
          data,
          backgroundColor: '#3b82f6',
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
    },
  })
}

async function fetchGeography(): Promise<void> {
  isLoading.value = true
  error.value = null
  try {
    const data = await analyticsService.getCampaignGeography({
      campaign_id: analyticsStore.selectedCampaignId || undefined,
      days: 30,
    })
    countries.value = (data?.countries || []).slice(0, 20)
    await nextTick()
    await renderChart()
  } catch (e: any) {
    error.value = e?.message || 'Не удалось загрузить гео-данные'
  } finally {
    isLoading.value = false
  }
}

watch(
  () => analyticsStore.selectedCampaignId,
  async () => {
    await fetchGeography()
  }
)

onMounted(async () => {
  await fetchGeography()
})

onUnmounted(() => {
  if (chartInstance) chartInstance.destroy()
})
</script>


