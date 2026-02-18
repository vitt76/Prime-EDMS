<template>
  <Card padding="lg">
    <div class="flex items-center justify-between gap-4 mb-2">
      <h3 class="text-base font-semibold text-neutral-900">События по странам</h3>
      <div class="text-xs text-neutral-500">за {{ days }} дн.</div>
    </div>

    <div v-if="isLoading" class="text-sm text-neutral-500">Загрузка…</div>
    <div v-else-if="error" class="text-sm text-red-600">{{ error }}</div>
    <template v-else>
      <div v-if="rows.length === 0" class="text-sm text-neutral-500 py-8">Нет данных</div>
      <template v-else>
        <div class="h-64 border border-neutral-200 rounded-lg p-2">
          <canvas ref="canvasRef" aria-label="События по странам" />
        </div>
        <div class="mt-4 border border-neutral-200 rounded-lg overflow-auto max-h-64">
          <table class="min-w-full text-sm">
            <thead class="bg-neutral-50">
              <tr class="text-left">
                <th class="px-3 py-2 font-semibold text-neutral-700">Страна</th>
                <th class="px-3 py-2 font-semibold text-neutral-700">События</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in rows" :key="row.country_code" class="border-t border-neutral-200">
                <td class="px-3 py-2">{{ row.country_code || '—' }}</td>
                <td class="px-3 py-2">{{ row.event_count }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </template>
  </Card>
</template>

<script setup lang="ts">
import Card from '@/components/Common/Card.vue'
import { onMounted, onUnmounted, ref, watch, nextTick } from 'vue'

const props = withDefaults(
  defineProps<{
    rows: Array<{ country_code: string; event_count: number }>
    isLoading?: boolean
    error?: string | null
    days?: number
  }>(),
  { isLoading: false, error: null, days: 30 }
)

const canvasRef = ref<HTMLCanvasElement | null>(null)
let chartInstance: import('chart.js').Chart | null = null

async function renderChart(): Promise<void> {
  if (!canvasRef.value || props.rows.length === 0) return
  const Chart = (await import('chart.js/auto')).default
  const ctx = canvasRef.value.getContext('2d')
  if (!ctx) return

  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }

  const labels = props.rows.map((r) => r.country_code || '')
  const data = props.rows.map((r) => r.event_count)

  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'События',
          data,
          backgroundColor: '#3b82f6',
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true },
      },
    },
  })
}

watch(
  () => props.rows,
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
