<template>
  <Card padding="lg">
    <div class="flex items-center justify-between gap-4 mb-4">
      <h3 class="text-base font-semibold text-neutral-900">Asset Reuse</h3>
      <div class="text-xs text-neutral-500">за 12 месяцев</div>
    </div>

    <div v-if="!monthlyData.length" class="text-sm text-neutral-500">
      Нет данных
    </div>
    <div v-else class="h-72">
      <canvas ref="canvasRef" aria-label="Asset reuse metrics chart" />
    </div>
  </Card>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch, nextTick } from 'vue'

import Card from '@/components/Common/Card.vue'
import type { AssetReuseMonthlyPoint } from '@/stores/analyticsStore'

const props = defineProps<{
  monthlyData: AssetReuseMonthlyPoint[]
  targetRate?: number
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

  const labels = (props.monthlyData || []).map((p) => p.month)
  const data = (props.monthlyData || []).map((p) => p.reuse_rate)
  const target = Number.isFinite(props.targetRate) ? (props.targetRate as number) : 62
  const targetSeries = labels.map(() => target)

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Reuse rate (%)',
          data,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.15)',
          fill: true,
          tension: 0.25,
          pointRadius: 2,
        },
        {
          label: 'Target (%)',
          data: targetSeries,
          borderColor: '#6b7280',
          borderDash: [6, 6],
          pointRadius: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'bottom' },
        tooltip: {
          callbacks: {
            label: (context: any) => {
              const value = context?.raw ?? 0
              return `${context.dataset.label}: ${Number(value).toFixed(2)}%`
            },
          },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          suggestedMax: 100,
          ticks: {
            callback: (v: any) => `${v}%`,
          },
        },
      },
    },
  })
}

watch(
  () => props.monthlyData,
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


