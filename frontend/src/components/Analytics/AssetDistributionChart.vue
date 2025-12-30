<template>
  <Card padding="lg">
    <div class="flex items-center justify-between gap-4 mb-4">
      <h3 class="text-base font-semibold text-neutral-900">Распределение ассетов</h3>
      <div class="text-xs text-neutral-500">по типам файлов</div>
    </div>

    <div class="h-72">
      <canvas ref="canvasRef" aria-label="Asset distribution chart" />
    </div>

    <div class="h-40 mt-4">
      <canvas ref="trendCanvasRef" aria-label="Asset distribution trend chart" />
    </div>
  </Card>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch, nextTick } from 'vue'

import Card from '@/components/Common/Card.vue'
import type { AssetDistributionItem, AssetDistributionTrendMonth } from '@/stores/analyticsStore'

const props = defineProps<{
  distribution: AssetDistributionItem[]
  trend: AssetDistributionTrendMonth[]
}>()

const emit = defineEmits<{
  selectType: [type: AssetDistributionItem['type']]
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
const trendCanvasRef = ref<HTMLCanvasElement | null>(null)
let chartInstance: import('chart.js').Chart | null = null
let trendChartInstance: import('chart.js').Chart | null = null
let isUnmounted = false

const TYPE_LABELS: Record<string, string> = {
  images: 'Изображения',
  videos: 'Видео',
  documents: 'Документы',
  other: 'Другое',
}

const TYPE_COLORS: Record<string, string> = {
  images: '#3b82f6',
  videos: '#10b981',
  documents: '#f59e0b',
  other: '#ef4444',
}

async function renderChart(): Promise<void> {
  const canvas = canvasRef.value
  if (!canvas) return

  // Chart.js is loaded async; by the time it's ready the component might be unmounted.
  const Chart = (await import('chart.js/auto')).default
  if (isUnmounted) return
  if (canvasRef.value !== canvas) return

  const ctx = canvas.getContext('2d')
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
      onClick: (_event: any, elements: any[]) => {
        const first = elements?.[0]
        if (!first) return
        const index = first.index
        const selected = items[index]
        if (selected?.type) {
          emit('selectType', selected.type)
        }
      },
    },
  })

  // Trend chart (12 months), cumulative counts by type.
  const trendCanvas = trendCanvasRef.value
  if (!trendCanvas) return
  if (isUnmounted) return
  if (trendCanvasRef.value !== trendCanvas) return

  const trendCtx = trendCanvas.getContext('2d')
  if (!trendCtx) return

  if (trendChartInstance) {
    trendChartInstance.destroy()
    trendChartInstance = null
  }

  const trendMonths = (props.trend || []).map((t) => t.month)
  const byMonth = (props.trend || []).map((t) => {
    const map: Record<string, number> = {}
    for (const item of t.distribution || []) map[item.type] = item.count
    return map
  })

  const typeOrder: Array<AssetDistributionItem['type']> = ['images', 'videos', 'documents', 'other']
  const datasets = typeOrder.map((type) => {
    return {
      label: TYPE_LABELS[type] || type,
      data: byMonth.map((m) => m[type] || 0),
      borderColor: TYPE_COLORS[type] || '#6b7280',
      backgroundColor: 'transparent',
      tension: 0.25,
      pointRadius: 0,
      borderWidth: 2,
    }
  })

  trendChartInstance = new Chart(trendCtx, {
    type: 'line',
    data: {
      labels: trendMonths,
      datasets: datasets as any,
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
        },
      },
      scales: {
        x: {
          ticks: {
            maxRotation: 0,
            autoSkip: true,
            maxTicksLimit: 6,
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
  isUnmounted = true
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
  if (trendChartInstance) {
    trendChartInstance.destroy()
    trendChartInstance = null
  }
})
</script>


