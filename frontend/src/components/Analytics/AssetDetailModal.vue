<template>
  <div v-if="open" class="fixed inset-0 z-50">
    <div class="absolute inset-0 bg-black/40" @click="close" />
    <div class="absolute inset-0 overflow-auto">
      <div class="max-w-5xl mx-auto p-4 md:p-8">
        <div class="bg-white rounded-xl shadow-lg border border-neutral-200">
          <div class="flex items-center justify-between gap-4 p-4 border-b border-neutral-200">
            <div>
              <div class="text-sm text-neutral-500">Детали файла</div>
              <div class="text-lg font-semibold text-neutral-900">
                {{ title }}
              </div>
            </div>
            <button
              class="px-3 py-2 text-sm rounded-md border border-neutral-300 hover:bg-neutral-50"
              @click="close"
            >
              Закрыть
            </button>
          </div>

          <div class="p-4">
            <div v-if="isLoading" class="text-sm text-neutral-500">Загрузка…</div>
            <div v-else-if="error" class="text-sm text-neutral-600">{{ error }}</div>

            <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div class="lg:col-span-2">
                <div class="text-sm font-semibold text-neutral-900 mb-2">Просмотры и скачивания (по дням)</div>
                <div class="h-64 border border-neutral-200 rounded-lg p-2">
                  <canvas ref="canvasRef" aria-label="Asset detail chart" />
                </div>
              </div>

              <div>
                <div class="text-sm font-semibold text-neutral-900 mb-2">Источники из поиска</div>
                <div class="border border-neutral-200 rounded-lg overflow-auto max-h-64">
                  <table class="min-w-full text-sm">
                    <thead class="bg-neutral-50">
                      <tr class="text-left">
                        <th class="px-3 py-2 font-semibold text-neutral-700">Запрос</th>
                        <th class="px-3 py-2 font-semibold text-neutral-700">Кол-во</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-if="detail?.search_referrers?.length === 0">
                        <td class="px-3 py-3 text-neutral-500" colspan="2">Нет данных за выбранный период</td>
                      </tr>
                      <tr
                        v-for="row in detail?.search_referrers || []"
                        :key="row.query_text"
                        class="border-t border-neutral-200"
                      >
                        <td class="px-3 py-2">{{ row.query_text }}</td>
                        <td class="px-3 py-2">{{ row.count }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <div class="text-sm font-semibold text-neutral-900 mt-6 mb-2">Каналы</div>
                <div class="border border-neutral-200 rounded-lg overflow-auto max-h-64">
                  <table class="min-w-full text-sm">
                    <thead class="bg-neutral-50">
                      <tr class="text-left">
                        <th class="px-3 py-2 font-semibold text-neutral-700">Канал</th>
                        <th class="px-3 py-2 font-semibold text-neutral-700">Событие</th>
                        <th class="px-3 py-2 font-semibold text-neutral-700">Кол-во</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-if="detail?.channels?.length === 0">
                        <td class="px-3 py-3 text-neutral-500" colspan="3">Нет данных за выбранный период</td>
                      </tr>
                      <tr
                        v-for="(row, idx) in detail?.channels || []"
                        :key="`${row.channel}-${row.event_type}-${idx}`"
                        class="border-t border-neutral-200"
                      >
                        <td class="px-3 py-2">{{ row.channel || '—' }}</td>
                        <td class="px-3 py-2">{{ row.event_type }}</td>
                        <td class="px-3 py-2">{{ row.count }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onUnmounted, ref, watch } from 'vue'

import { analyticsService } from '@/services/analyticsService'

const props = defineProps<{
  open: boolean
  documentId: number | null
  documentLabel?: string | null
  days?: number
}>()

const emit = defineEmits<{
  close: []
}>()

const isLoading = ref(false)
const error = ref<string | null>(null)
const detail = ref<any | null>(null)

const canvasRef = ref<HTMLCanvasElement | null>(null)
let chartInstance: import('chart.js').Chart | null = null

const title = computed(() => {
  if (props.documentLabel) return props.documentLabel
  if (props.documentId) return `Document #${props.documentId}`
  return '—'
})

function close(): void {
  emit('close')
}

async function renderChart(): Promise<void> {
  if (!canvasRef.value || !detail.value?.daily_series) return
  const ctx = canvasRef.value.getContext('2d')
  if (!ctx) return

  const Chart = (await import('chart.js/auto')).default

  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }

  const series = detail.value.daily_series as any[]
  const labels = series.map((p) => String(p.date))
  const views = series.map((p) => Number(p.views || 0))
  const downloads = series.map((p) => Number(p.downloads || 0))

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label: 'Views', data: views, borderColor: '#3b82f6', tension: 0.25, pointRadius: 0 },
        { label: 'Downloads', data: downloads, borderColor: '#10b981', tension: 0.25, pointRadius: 0 },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom' },
      },
    },
  })
}

async function fetchDetail(): Promise<void> {
  if (!props.open || !props.documentId) return
  isLoading.value = true
  error.value = null
  try {
    detail.value = await analyticsService.getAssetDetail({
      document_id: props.documentId,
      days: props.days ?? 30,
    })
    await nextTick()
    await renderChart()
  } catch (e: any) {
    error.value = e?.message || 'Не удалось загрузить детализацию'
  } finally {
    isLoading.value = false
  }
}

watch(
  () => [props.open, props.documentId],
  async () => {
    await fetchDetail()
  }
)

onUnmounted(() => {
  if (chartInstance) chartInstance.destroy()
})
</script>


