<template>
  <Card padding="lg">
    <div class="flex items-center justify-between gap-4 mb-4">
      <div>
        <h2 class="text-lg font-semibold text-neutral-900">Медиатека</h2>
        <p v-if="lastUpdated" class="text-xs text-neutral-500">
          Обновлено: {{ formatDateTime(lastUpdated) }}
        </p>
      </div>
      <button
        class="px-3 py-2 text-sm rounded-md border border-neutral-300 hover:bg-neutral-50"
        :disabled="isLoading"
        @click="$emit('refresh')"
      >
        Обновить
      </button>
    </div>

    <div class="grid grid-cols-2 lg:grid-cols-6 gap-4">
      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">Всего файлов</div>
        <div class="text-3xl font-semibold text-neutral-900 tracking-tight">
          {{ metrics?.total_assets ?? '—' }}
        </div>
      </div>

      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">Занято места</div>
        <div class="text-3xl font-semibold text-neutral-900 tracking-tight">
          {{ metrics ? formatBytes(metrics.storage_used_bytes) : '—' }}
        </div>
      </div>

      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">Активные (MAU)</div>
        <div class="text-3xl font-semibold text-neutral-900 tracking-tight">
          {{ metrics?.mau ?? '—' }}
        </div>
      </div>

      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">Успешность поиска</div>
        <div class="text-3xl font-semibold text-neutral-900 tracking-tight">
          {{ metrics ? formatPercent(metrics.search_success_rate) : '—' }}
        </div>
      </div>

      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">Ср. время поиска</div>
        <div class="text-3xl font-semibold text-neutral-900 tracking-tight">
          {{ metrics?.avg_find_time_minutes != null ? `${metrics.avg_find_time_minutes.toFixed(1)} мин` : '—' }}
        </div>
      </div>

      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">CDN: стоимость/мес</div>
        <div class="text-3xl font-semibold text-neutral-900 tracking-tight">
          {{ metrics?.cdn_cost_per_month != null ? formatMoney(metrics.cdn_cost_per_month) : '—' }}
        </div>
      </div>
    </div>
  </Card>
</template>

<script setup lang="ts">
import Card from '@/components/Common/Card.vue'
import type { AssetBankTopMetrics } from '@/stores/analyticsStore'

defineProps<{
  metrics: AssetBankTopMetrics | null
  lastUpdated: Date | null
  isLoading: boolean
  error: string | null
}>()

defineEmits<{
  refresh: []
}>()

function formatBytes(bytes: number): string {
  if (!Number.isFinite(bytes) || bytes <= 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let value = bytes
  let unit = 0
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024
    unit += 1
  }
  return `${value.toFixed(unit >= 3 ? 2 : 0)} ${units[unit]}`
}

function formatPercent(value: number): string {
  if (!Number.isFinite(value)) return '—'
  return `${value.toFixed(1)}%`
}

function formatMoney(value: number): string {
  if (!Number.isFinite(value)) return '—'
  return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'USD' }).format(value)
}

function formatDateTime(date: Date): string {
  return date.toLocaleString('ru-RU')
}
</script>


