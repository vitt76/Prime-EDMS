<template>
  <Card padding="lg">
    <div class="flex items-center justify-between gap-4 mb-4">
      <div>
        <h3 class="text-base font-semibold text-neutral-900">Динамика хранилища</h3>
        <p class="text-xs text-neutral-500">история (12 мес) + прогноз (6 мес)</p>
      </div>
      <div
        v-if="isNearLimit"
        class="text-xs px-2 py-1 rounded-md bg-red-50 text-red-700 border border-red-200"
      >
        Риск: приближение к лимиту
      </div>
    </div>

    <div v-if="labels.length === 0" class="py-10 text-center text-neutral-500">
      <svg class="w-10 h-10 mx-auto text-neutral-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-6m4 6V7m4 10v-4M5 21h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v14a2 2 0 002 2z" />
      </svg>
      <div class="mt-3 text-sm">Нет данных за выбранный период</div>
    </div>
    <div v-else class="h-72">
      <canvas ref="canvasRef" aria-label="Storage trends chart" />
    </div>
  </Card>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch, nextTick } from 'vue'

import Card from '@/components/Common/Card.vue'
import type { StorageTrendsPoint } from '@/stores/analyticsStore'

const props = defineProps<{
  historical: StorageTrendsPoint[]
  forecast: StorageTrendsPoint[]
  storageLimitGb?: number
  alertThreshold?: number
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
let chartInstance: import('chart.js').Chart | null = null

const labels = computed(() => {
  return [...(props.historical || []), ...(props.forecast || [])].map((p) => p.month)
})

const currentStorageGb = computed(() => {
  const list = props.historical || []
  const last = list.length ? list[list.length - 1] : null
  return last?.total_gb ?? 0
})

const isNearLimit = computed(() => {
  const threshold = props.alertThreshold ?? (props.storageLimitGb ? props.storageLimitGb * 0.9 : 0)
  return threshold > 0 && currentStorageGb.value >= threshold
})

async function renderChart(): Promise<void> {
  if (!canvasRef.value) return
  const Chart = (await import('chart.js/auto')).default
  const ctx = canvasRef.value.getContext('2d')
  if (!ctx) return

  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }

  const types: Array<'images' | 'videos' | 'documents' | 'other'> = [
    'images',
    'videos',
    'documents',
    'other',
  ]
  const typeLabels: Record<string, string> = {
    images: 'Изображения',
    videos: 'Видео',
    documents: 'Документы',
    other: 'Другое',
  }
  const colors: Record<string, string> = {
    images: 'rgba(59, 130, 246, 0.35)',
    videos: 'rgba(16, 185, 129, 0.35)',
    documents: 'rgba(245, 158, 11, 0.35)',
    other: 'rgba(239, 68, 68, 0.35)',
  }

  const histLen = (props.historical || []).length
  const foreLen = (props.forecast || []).length
  const totalLen = histLen + foreLen

  const datasets: any[] = []
  for (const t of types) {
    const color = colors[t] || 'rgba(107, 114, 128, 0.35)'
    const borderColor = color.replace('0.35', '0.9')
    const forecastFill = color.replace('0.35', '0.18')

    const histData = (props.historical || []).map((p) => p.by_type[t] ?? 0)
    const foreData = (props.forecast || []).map((p) => p.by_type[t] ?? 0)

    datasets.push({
      label: `${typeLabels[t] || t} (история)`,
      data: [...histData, ...new Array(foreLen).fill(null)],
      backgroundColor: color,
      borderColor,
      fill: true,
      tension: 0.2,
      pointRadius: 0,
      stack: 'storage',
    })

    datasets.push({
      label: `${typeLabels[t] || t} (прогноз)`,
      data: [...new Array(histLen).fill(null), ...foreData],
      backgroundColor: forecastFill,
      borderColor,
      borderDash: [6, 6],
      fill: true,
      tension: 0.2,
      pointRadius: 0,
      stack: 'storage',
    })
  }

  // Total overlay line (optional, helps readability).
  const totalHist = (props.historical || []).map((p) => p.total_gb ?? 0)
  const totalFore = (props.forecast || []).map((p) => p.total_gb ?? 0)
  datasets.push({
    label: 'Итого (история)',
    data: [...totalHist, ...new Array(foreLen).fill(null)],
    borderColor: '#111827',
    backgroundColor: 'transparent',
    tension: 0.2,
    pointRadius: 0,
    fill: false,
    yAxisID: 'y',
  })
  datasets.push({
    label: 'Итого (прогноз)',
    data: [...new Array(histLen).fill(null), ...totalFore],
    borderColor: '#111827',
    borderDash: [6, 6],
    backgroundColor: 'transparent',
    tension: 0.2,
    pointRadius: 0,
    fill: false,
    yAxisID: 'y',
  })

  // Ensure arrays match labels length
  for (const ds of datasets) {
    if ((ds.data || []).length !== totalLen) {
      ds.data = (ds.data || []).slice(0, totalLen)
    }
  }

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: { labels: labels.value, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            title: (items: any) => items?.[0]?.label ?? '',
          },
        },
      },
      scales: {
        y: {
          stacked: true,
          beginAtZero: true,
          ticks: {
            callback: (v: any) => `${v} GB`,
          },
        },
        x: {
          ticks: {
            maxRotation: 0,
            autoSkip: true,
            maxTicksLimit: 10,
          },
        },
      },
    },
  })
}

watch(
  () => [props.historical, props.forecast],
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


