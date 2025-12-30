<template>
  <div class="container mx-auto px-4 py-6">

      <Card padding="lg" class="mb-6">
        <div class="flex items-center justify-between gap-4">
          <div class="text-sm text-neutral-700">Активность и когортный анализ</div>
          <button
            class="px-3 py-2 text-sm rounded-md border border-neutral-300 hover:bg-neutral-50"
            :disabled="analyticsStore.isLoading"
            @click="refresh"
          >
            Обновить
          </button>
        </div>
      </Card>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card padding="lg">
          <div class="flex items-center justify-between gap-4 mb-4">
            <h3 class="text-base font-semibold text-neutral-900">DAU (30 дней)</h3>
            <div class="text-xs text-neutral-500">уникальные пользователи/день</div>
          </div>
          <div v-if="dauSeries.length === 0" class="text-sm text-neutral-500">Нет данных за выбранный период</div>
          <div v-else class="h-72">
            <canvas ref="dauCanvasRef" aria-label="DAU chart" />
          </div>
        </Card>

        <Card padding="lg">
          <div class="flex items-center justify-between gap-4 mb-4">
            <h3 class="text-base font-semibold text-neutral-900">Частота входов</h3>
            <div class="text-xs text-neutral-500">30 дней</div>
          </div>
          <div v-if="!buckets" class="text-sm text-neutral-500">Нет данных</div>
          <div v-else class="h-72">
            <canvas ref="bucketCanvasRef" aria-label="Login frequency chart" />
          </div>
        </Card>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <Card padding="lg">
          <div class="flex items-center justify-between gap-4 mb-4">
            <h3 class="text-base font-semibold text-neutral-900">Когортный анализ</h3>
            <div class="text-xs text-neutral-500">удержание по неделям</div>
          </div>

          <div v-if="cohorts.length === 0" class="text-sm text-neutral-500">Нет данных</div>
          <div v-else class="overflow-auto border border-neutral-200 rounded-lg">
            <table class="min-w-full text-sm">
              <thead class="bg-neutral-50">
                <tr class="text-left">
                  <th class="px-3 py-2 font-semibold text-neutral-700">Cohort week</th>
                  <th class="px-3 py-2 font-semibold text-neutral-700">Size</th>
                  <th
                    v-for="w in retentionWeeks"
                    :key="w"
                    class="px-3 py-2 font-semibold text-neutral-700"
                  >
                    W{{ w }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in cohorts" :key="row.cohort_week_start" class="border-t border-neutral-200">
                  <td class="px-3 py-2">{{ row.cohort_week_start }}</td>
                  <td class="px-3 py-2">{{ row.cohort_size }}</td>
                  <td v-for="cell in row.retention" :key="cell.week_index" class="px-3 py-2">
                    {{ cell.retention_rate.toFixed(0) }}%
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </Card>

        <Card padding="lg">
          <div class="flex items-center justify-between gap-4 mb-4">
            <h3 class="text-base font-semibold text-neutral-900">Использование функций</h3>
            <div class="text-xs text-neutral-500">события использования</div>
          </div>

          <div v-if="featureRows.length === 0" class="text-sm text-neutral-500">Нет данных</div>
          <div v-else class="overflow-auto border border-neutral-200 rounded-lg">
            <table class="min-w-full text-sm">
              <thead class="bg-neutral-50">
                <tr class="text-left">
                  <th class="px-3 py-2 font-semibold text-neutral-700">Feature</th>
                  <th class="px-3 py-2 font-semibold text-neutral-700">Events</th>
                  <th class="px-3 py-2 font-semibold text-neutral-700">Unique users</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in featureRows" :key="row.feature_name" class="border-t border-neutral-200">
                  <td class="px-3 py-2">{{ row.feature_name }}</td>
                  <td class="px-3 py-2">{{ row.total }}</td>
                  <td class="px-3 py-2">{{ row.unique_users }}</td>
                </tr>
              </tbody>
            </table>
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

const dauCanvasRef = ref<HTMLCanvasElement | null>(null)
const bucketCanvasRef = ref<HTMLCanvasElement | null>(null)
let dauChart: import('chart.js').Chart | null = null
let bucketChart: import('chart.js').Chart | null = null

const dauSeries = computed(() => analyticsStore.userLoginPatterns?.dau_series || [])
const buckets = computed(() => analyticsStore.userLoginPatterns?.frequency_buckets || null)
const cohorts = computed(() => analyticsStore.userCohorts?.cohorts || [])
const retentionWeeks = computed(() => {
  const first = cohorts.value?.[0]
  const len = first?.retention?.length || 0
  return Array.from({ length: len }, (_, i) => i)
})
const featureRows = computed(() => analyticsStore.featureAdoption?.results || [])

async function renderCharts(): Promise<void> {
  const Chart = (await import('chart.js/auto')).default

  if (dauCanvasRef.value) {
    const ctx = dauCanvasRef.value.getContext('2d')
    if (ctx) {
      if (dauChart) dauChart.destroy()
      const labels = dauSeries.value.map((p: any) => p.date)
      const data = dauSeries.value.map((p: any) => p.active_users)
      dauChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [{ label: 'DAU', data, borderColor: '#3b82f6', tension: 0.25, pointRadius: 0 }],
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } },
      })
    }
  }

  if (bucketCanvasRef.value && buckets.value) {
    const ctx = bucketCanvasRef.value.getContext('2d')
    if (ctx) {
      if (bucketChart) bucketChart.destroy()
      const labels = ['daily', 'weekly', 'monthly', 'rare']
      const data = labels.map((k) => Number((buckets.value as any)[k] || 0))
      bucketChart = new Chart(ctx, {
        type: 'bar',
        data: { labels, datasets: [{ label: 'Users', data, backgroundColor: '#10b981' }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
      })
    }
  }
}

async function refresh(): Promise<void> {
  await analyticsStore.fetchUserLoginPatterns({ days: 30 })
  await analyticsStore.fetchUserCohorts({ cohort_weeks: 8, retention_weeks: 8 })
  await analyticsStore.fetchFeatureAdoption({ days: 30 })
  await nextTick()
  await renderCharts()
}

watch(
  () => [analyticsStore.userLoginPatterns, analyticsStore.userCohorts],
  async () => {
    await nextTick()
    await renderCharts()
  }
)

onMounted(async () => {
  await refresh()
})

onUnmounted(() => {
  if (dauChart) dauChart.destroy()
  if (bucketChart) bucketChart.destroy()
})
</script>


