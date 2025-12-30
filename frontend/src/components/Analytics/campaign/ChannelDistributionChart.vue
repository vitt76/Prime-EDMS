<template>
  <Card padding="lg">
    <div class="flex items-center justify-between gap-4 mb-4">
      <h3 class="text-base font-semibold text-neutral-900">Distribution by Channel</h3>
      <div class="text-xs text-neutral-500">stacked</div>
    </div>

    <div v-if="channels.length === 0" class="text-sm text-neutral-500">Нет данных</div>
    <div v-else class="h-72">
      <canvas ref="canvasRef" aria-label="Channel distribution chart" />
    </div>
  </Card>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch, nextTick } from 'vue'

import Card from '@/components/Common/Card.vue'

const props = defineProps<{
  channels: Array<{ channel: string; views: number; downloads: number }>
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

  const labels = (props.channels || []).map((p) => p.channel || '—')
  const views = (props.channels || []).map((p) => p.views || 0)
  const downloads = (props.channels || []).map((p) => p.downloads || 0)

  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Views',
          data: views,
          backgroundColor: 'rgba(59, 130, 246, 0.65)',
          stack: 'stack',
        },
        {
          label: 'Downloads',
          data: downloads,
          backgroundColor: 'rgba(16, 185, 129, 0.65)',
          stack: 'stack',
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: {
        x: { stacked: true },
        y: { stacked: true, beginAtZero: true },
      },
    },
  })
}

watch(
  () => props.channels,
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


