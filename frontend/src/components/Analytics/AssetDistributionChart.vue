<template>
  <Card padding="lg">
    <div class="flex items-center justify-between gap-4 mb-4">
      <h3 class="text-base font-semibold text-neutral-900">Распределение ассетов</h3>
      <div class="text-xs text-neutral-500">по типам файлов</div>
    </div>

    <div class="h-72">
      <canvas ref="canvasRef" aria-label="Asset distribution chart" />
    </div>
  </Card>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch, nextTick } from 'vue'

import Card from '@/components/Common/Card.vue'
import type { AssetDistributionItem } from '@/stores/analyticsStore'

const props = defineProps<{
  distribution: AssetDistributionItem[]
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
let chartInstance: import('chart.js').Chart | null = null

const TYPE_LABELS: Record<string, string> = {
  images: 'Images',
  videos: 'Videos',
  documents: 'Documents',
  other: 'Other',
}

const TYPE_COLORS: Record<string, string> = {
  images: '#3b82f6',
  videos: '#10b981',
  documents: '#f59e0b',
  other: '#ef4444',
}

async function renderChart(): Promise<void> {
  if (!canvasRef.value) return

  const Chart = (await import('chart.js/auto')).default
  const ctx = canvasRef.value.getContext('2d')
  if (!ctx) return

  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }

  const items = props.distribution || []
  const labels = items.map((i) => TYPE_LABELS[i.type] || i.type)
  const data = items.map((i) => i.count)
  const backgroundColor = items.map((i) => TYPE_COLORS[i.type] || '#6b7280')

  chartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [
        {
          data,
          backgroundColor,
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            usePointStyle: true,
            boxWidth: 10,
          },
        },
        tooltip: {
          callbacks: {
            label: (context: any) => {
              const value = context?.raw ?? 0
              return `${context.label}: ${value}`
            },
          },
        },
      },
    },
  })
}

watch(
  () => props.distribution,
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


