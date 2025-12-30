<template>
  <Card padding="lg">
    <div class="flex items-center justify-between gap-4 mb-4">
      <h3 class="text-base font-semibold text-neutral-900">Просмотры и скачивания</h3>
      <div class="text-xs text-neutral-500">две оси</div>
    </div>

    <div v-if="timeline.length === 0" class="text-sm text-neutral-500">Нет данных за выбранный период</div>
    <div v-else class="h-72">
      <canvas ref="canvasRef" aria-label="График просмотров и скачиваний" />
    </div>
  </Card>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch, nextTick } from 'vue'

import Card from '@/components/Common/Card.vue'

const props = defineProps<{
  timeline: Array<{ timestamp__date: string; views: number; downloads: number }>
  baseline?: { campaign: { id: string; label: string }; timeline: Array<{ timestamp__date: string; views: number; downloads: number }> } | null
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
let chartInstance: import('chart.js').Chart | null = null

async function renderChart(): Promise<void> {
  if (!canvasRef.value) return
  const Chart = (await import('chart.js/auto')).default
  const ctx = canvasRef.value.getContext('2d')
  if (!ctx) return

  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }

  const labels = (props.timeline || []).map((p) => p.timestamp__date)
  const views = (props.timeline || []).map((p) => p.views || 0)
  const downloads = (props.timeline || []).map((p) => p.downloads || 0)

  const baselineViews = (props.baseline?.timeline || []).map((p) => p.views || 0)
  const baselineDownloads = (props.baseline?.timeline || []).map((p) => p.downloads || 0)

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Просмотры',
          data: views,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.12)',
          yAxisID: 'y',
          tension: 0.25,
          pointRadius: 0,
        },
        ...(props.baseline
          ? [
              {
                label: `Просмотры (база: ${props.baseline.campaign.label})`,
                data: baselineViews,
                borderColor: 'rgba(59, 130, 246, 0.65)',
                backgroundColor: 'transparent',
                yAxisID: 'y',
                tension: 0.25,
                pointRadius: 0,
                borderDash: [6, 6],
              },
            ]
          : []),
        {
          label: 'Скачивания',
          data: downloads,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.12)',
          yAxisID: 'y1',
          tension: 0.25,
          pointRadius: 0,
        },
        ...(props.baseline
          ? [
              {
                label: `Скачивания (база: ${props.baseline.campaign.label})`,
                data: baselineDownloads,
                borderColor: 'rgba(16, 185, 129, 0.65)',
                backgroundColor: 'transparent',
                yAxisID: 'y1',
                tension: 0.25,
                pointRadius: 0,
                borderDash: [6, 6],
              },
            ]
          : []),
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: { legend: { position: 'bottom' } },
      scales: {
        y: { type: 'linear', position: 'left', beginAtZero: true },
        y1: {
          type: 'linear',
          position: 'right',
          beginAtZero: true,
          grid: { drawOnChartArea: false },
        },
      },
    },
  })
}

watch(
  () => props.timeline,
  async () => {
    await nextTick()
    await renderChart()
  },
  { deep: true }
)

onMounted(async () => {
  await nextTick()
  await renderChart()
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
})
</script>


