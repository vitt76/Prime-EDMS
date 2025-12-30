<template>
  <Card padding="lg">
    <div class="flex items-center justify-between gap-4 mb-4">
      <h3 class="text-base font-semibold text-neutral-900">Views & Downloads</h3>
      <div class="text-xs text-neutral-500">dual-axis</div>
    </div>

    <div v-if="timeline.length === 0" class="text-sm text-neutral-500">Нет данных</div>
    <div v-else class="h-72">
      <canvas ref="canvasRef" aria-label="Views and downloads chart" />
    </div>
  </Card>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch, nextTick } from 'vue'

import Card from '@/components/Common/Card.vue'

const props = defineProps<{
  timeline: Array<{ timestamp__date: string; views: number; downloads: number }>
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

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Views',
          data: views,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.12)',
          yAxisID: 'y',
          tension: 0.25,
          pointRadius: 0,
        },
        {
          label: 'Downloads',
          data: downloads,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.12)',
          yAxisID: 'y1',
          tension: 0.25,
          pointRadius: 0,
        },
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


