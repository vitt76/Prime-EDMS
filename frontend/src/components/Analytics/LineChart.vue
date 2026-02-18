<template>
  <div class="h-full min-h-[200px]">
    <canvas
      v-if="labels.length > 0"
      ref="canvasRef"
      :aria-label="ariaLabel"
    />
    <div v-else class="flex items-center justify-center h-full text-sm text-neutral-500">
      Нет данных
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch, nextTick } from 'vue'

export interface LineChartDataset {
  label: string
  data: number[]
  borderColor?: string
  backgroundColor?: string
  fill?: boolean
  tension?: number
  pointRadius?: number
}

const props = withDefaults(
  defineProps<{
    labels: string[]
    datasets: LineChartDataset[]
    ariaLabel?: string
    yAxisSuffix?: string
    suggestedMax?: number
  }>(),
  { ariaLabel: 'Line chart', yAxisSuffix: '', suggestedMax: undefined }
)

const canvasRef = ref<HTMLCanvasElement | null>(null)
let chartInstance: import('chart.js').Chart | null = null

async function renderChart(): Promise<void> {
  if (!canvasRef.value || props.labels.length === 0) return
  const Chart = (await import('chart.js/auto')).default
  const ctx = canvasRef.value.getContext('2d')
  if (!ctx) return

  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }

  const chartDatasets = props.datasets.map((ds) => ({
    label: ds.label,
    data: ds.data,
    borderColor: ds.borderColor ?? '#3b82f6',
    backgroundColor: ds.backgroundColor ?? 'rgba(59, 130, 246, 0.1)',
    fill: ds.fill ?? false,
    tension: ds.tension ?? 0.25,
    pointRadius: ds.pointRadius ?? 2,
  }))

  const scaleOptions: Record<string, unknown> = {
    y: {
      beginAtZero: true,
      ticks: props.yAxisSuffix
        ? { callback: (v: unknown) => `${v}${props.yAxisSuffix}` }
        : {},
    },
  }
  if (props.suggestedMax != null) {
    (scaleOptions.y as Record<string, unknown>).suggestedMax = props.suggestedMax
  }

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: props.labels,
      datasets: chartDatasets,
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'bottom' },
      },
      scales: scaleOptions,
    },
  })
}

watch(
  () => [props.labels, props.datasets],
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
