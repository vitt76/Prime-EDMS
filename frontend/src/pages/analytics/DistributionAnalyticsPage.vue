<template>
  <div class="container mx-auto px-4 py-6">

      <Card padding="lg" class="mb-6">
        <div class="flex items-center justify-between gap-4">
          <div class="text-sm text-neutral-700">Матрица каналов · Конвертация · CDN</div>
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
            <h3 class="text-base font-semibold text-neutral-900">Матрица дистрибуции</h3>
            <div class="text-xs text-neutral-500">последний статус по каналам</div>
          </div>
          <div v-if="matrix.length === 0" class="text-sm text-neutral-500">Нет данных за выбранный период</div>
          <div v-else class="overflow-auto border border-neutral-200 rounded-lg">
            <table class="min-w-full text-sm">
              <thead class="bg-neutral-50">
                <tr class="text-left">
                  <th class="px-3 py-2 font-semibold text-neutral-700">Channel</th>
                  <th class="px-3 py-2 font-semibold text-neutral-700">Status</th>
                  <th class="px-3 py-2 font-semibold text-neutral-700">Last sync</th>
                  <th class="px-3 py-2 font-semibold text-neutral-700">Events</th>
                  <th class="px-3 py-2 font-semibold text-neutral-700">Issues</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in matrix" :key="row.channel" class="border-t border-neutral-200">
                  <td class="px-3 py-2">{{ row.channel }}</td>
                  <td class="px-3 py-2">{{ row.status }}</td>
                  <td class="px-3 py-2">{{ formatDate(row.last_sync) }}</td>
                  <td class="px-3 py-2">{{ row.events }}</td>
                  <td class="px-3 py-2">{{ row.issues }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </Card>

        <Card padding="lg">
          <div class="flex items-center justify-between gap-4 mb-4">
            <h3 class="text-base font-semibold text-neutral-900">Успешность конвертации</h3>
            <div class="text-xs text-neutral-500">события конвертации</div>
          </div>
          <div v-if="conversion.length === 0" class="text-sm text-neutral-500">Нет данных</div>
          <div v-else class="overflow-auto border border-neutral-200 rounded-lg">
            <table class="min-w-full text-sm">
              <thead class="bg-neutral-50">
                <tr class="text-left">
                  <th class="px-3 py-2 font-semibold text-neutral-700">Channel</th>
                  <th class="px-3 py-2 font-semibold text-neutral-700">Success</th>
                  <th class="px-3 py-2 font-semibold text-neutral-700">Total</th>
                  <th class="px-3 py-2 font-semibold text-neutral-700">Failed</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in conversion" :key="row.channel" class="border-t border-neutral-200">
                  <td class="px-3 py-2">{{ row.channel }}</td>
                  <td class="px-3 py-2">{{ row.success_rate != null ? `${row.success_rate}%` : '—' }}</td>
                  <td class="px-3 py-2">{{ row.total }}</td>
                  <td class="px-3 py-2">{{ row.failed }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </Card>
      </div>

      <div class="mt-6">
        <Card padding="lg">
          <div class="flex items-center justify-between gap-4 mb-4">
            <h3 class="text-base font-semibold text-neutral-900">Производительность CDN</h3>
            <div class="text-xs text-neutral-500">события доставки</div>
          </div>
          <div v-if="cdnPerf.length === 0" class="text-sm text-neutral-500">Нет данных</div>
          <div v-else class="overflow-auto border border-neutral-200 rounded-lg">
            <table class="min-w-full text-sm">
              <thead class="bg-neutral-50">
                <tr class="text-left">
                  <th class="px-3 py-2 font-semibold text-neutral-700">Channel</th>
                  <th class="px-3 py-2 font-semibold text-neutral-700">Bandwidth (GB)</th>
                  <th class="px-3 py-2 font-semibold text-neutral-700">Avg latency (ms)</th>
                  <th class="px-3 py-2 font-semibold text-neutral-700">Events</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in cdnPerf" :key="row.channel" class="border-t border-neutral-200">
                  <td class="px-3 py-2">{{ row.channel }}</td>
                  <td class="px-3 py-2">{{ row.bandwidth_gb }}</td>
                  <td class="px-3 py-2">{{ row.avg_latency_ms ?? '—' }}</td>
                  <td class="px-3 py-2">{{ row.events }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </Card>
      </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'

import Card from '@/components/Common/Card.vue'
import { useAnalyticsStore } from '@/stores/analyticsStore'

const analyticsStore = useAnalyticsStore()

const matrix = computed(() => analyticsStore.distributionDashboard?.matrix || [])
const conversion = computed(() => analyticsStore.distributionDashboard?.conversion_success || [])
const cdnPerf = computed(() => analyticsStore.distributionDashboard?.cdn_performance || [])

function formatDate(v: any): string {
  try {
    if (!v) return '—'
    return new Date(v).toLocaleString()
  } catch {
    return String(v || '—')
  }
}

async function refresh(): Promise<void> {
  await analyticsStore.fetchDistributionDashboard({ days: 7 })
}

onMounted(async () => {
  await refresh()
})
</script>


