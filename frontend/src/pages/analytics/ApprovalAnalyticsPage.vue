<template>
  <div class="container mx-auto px-4 py-6">

      <Card padding="lg" class="mb-6">
        <div class="flex items-center justify-between gap-4">
          <div class="text-sm text-neutral-700">Сводка + рекомендации</div>
          <button
            class="px-3 py-2 text-sm rounded-md border border-neutral-300 hover:bg-neutral-50"
            :disabled="analyticsStore.isLoading"
            @click="refresh"
          >
            Обновить
          </button>
        </div>
      </Card>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card padding="lg">
          <div class="text-xs text-neutral-500">Approval cycle time</div>
          <div class="text-2xl font-semibold text-neutral-900 mt-1">
            {{ approvalCycleTime != null ? `${approvalCycleTime} дн` : '—' }}
          </div>
        </Card>
        <Card padding="lg">
          <div class="text-xs text-neutral-500">First-time-right</div>
          <div class="text-2xl font-semibold text-neutral-900 mt-1">
            {{ ftrRate != null ? `${ftrRate}%` : '—' }}
          </div>
        </Card>
        <Card padding="lg">
          <div class="text-xs text-neutral-500">Rejected</div>
          <div class="text-2xl font-semibold text-neutral-900 mt-1">
            {{ totalRejected }}
          </div>
        </Card>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <Card padding="lg">
          <div class="flex items-center justify-between gap-4 mb-4">
            <h3 class="text-base font-semibold text-neutral-900">Timeseries</h3>
            <div class="text-xs text-neutral-500">submitted/approved/rejected</div>
          </div>
          <div v-if="series.length === 0" class="text-sm text-neutral-500">Нет данных</div>
          <div v-else class="h-72">
            <canvas ref="canvasRef" aria-label="Approval timeseries chart" />
          </div>
        </Card>

        <Card padding="lg">
          <div class="flex items-center justify-between gap-4 mb-4">
            <h3 class="text-base font-semibold text-neutral-900">Рекомендации</h3>
            <div class="text-xs text-neutral-500">практические</div>
          </div>
          <div v-if="recommendations.length === 0" class="text-sm text-neutral-500">Нет рекомендаций</div>
          <div v-else class="space-y-3">
            <div
              v-for="rec in recommendations"
              :key="rec.title"
              class="p-3 border border-neutral-200 rounded-lg bg-white"
            >
              <div class="text-sm font-semibold text-neutral-900">{{ rec.title }}</div>
              <div class="text-sm text-neutral-700 mt-1">{{ rec.message }}</div>
            </div>
          </div>
        </Card>
      </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'

import Card from '@/components/Common/Card.vue'
import { useAnalyticsStore } from '@/stores/analyticsStore'

const analyticsStore = useAnalyticsStore()
const canvasRef = ref<HTMLCanvasElement | null>(null)
let chart: import('chart.js').Chart | null = null

const approvalCycleTime = computed(() => analyticsStore.approvalSummary?.approval_cycle_time_days ?? null)
const ftrRate = computed(() => analyticsStore.approvalSummary?.first_time_right_rate ?? null)
const totalRejected = computed(() => analyticsStore.approvalSummary?.total_rejected ?? 0)

const series = computed(() => analyticsStore.approvalTimeseries?.results || [])
const recommendations = computed(() => analyticsStore.approvalRecommendations?.recommendations || [])

async function renderChart(): Promise<void> {
  if (!canvasRef.value) return
  const Chart = (await import('chart.js/auto')).default
  const ctx = canvasRef.value.getContext('2d')
  if (!ctx) return

  if (chart) {
    chart.destroy()
    chart = null
  }

  const labels = series.value.map((p: any) => p.date)
  const submitted = series.value.map((p: any) => p.submitted || 0)
  const approved = series.value.map((p: any) => p.approved || 0)
  const rejected = series.value.map((p: any) => p.rejected || 0)

  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label: 'Submitted', data: submitted, borderColor: '#6366f1', tension: 0.25, pointRadius: 0 },
        { label: 'Approved', data: approved, borderColor: '#10b981', tension: 0.25, pointRadius: 0 },
        { label: 'Rejected', data: rejected, borderColor: '#ef4444', tension: 0.25, pointRadius: 0 },
      ],
    },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } },
  })
}

async function refresh(): Promise<void> {
  await Promise.all([
    analyticsStore.fetchApprovalSummary({ days: 30 }),
    analyticsStore.fetchApprovalTimeseries({ days: 90 }),
    analyticsStore.fetchApprovalRecommendations({ days: 30 }),
  ])
  await nextTick()
  await renderChart()
}

watch(
  () => analyticsStore.approvalTimeseries,
  async () => {
    await nextTick()
    await renderChart()
  }
)

onMounted(async () => {
  await refresh()
})

onUnmounted(() => {
  if (chart) chart.destroy()
})
</script>


