<template>
  <Card padding="lg">
    <div class="flex items-center justify-between gap-4 mb-4">
      <div>
        <h2 class="text-lg font-semibold text-neutral-900">Asset Bank</h2>
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

    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">Total Assets</div>
        <div class="text-2xl font-bold text-neutral-900">
          {{ metrics?.total_assets ?? '—' }}
        </div>
      </div>

      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">Storage Used</div>
        <div class="text-2xl font-bold text-neutral-900">
          {{ metrics ? formatBytes(metrics.storage_used_bytes) : '—' }}
        </div>
      </div>

      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">MAU</div>
        <div class="text-2xl font-bold text-neutral-900">
          {{ metrics?.mau ?? '—' }}
        </div>
        <div v-if="metrics && metrics.mau === 0" class="text-xs text-neutral-500 mt-1">
          (Phase 2)
        </div>
      </div>

      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">Search Success</div>
        <div class="text-2xl font-bold text-neutral-900">
          {{ metrics ? formatPercent(metrics.search_success_rate) : '—' }}
        </div>
        <div v-if="metrics && metrics.search_success_rate === 0" class="text-xs text-neutral-500 mt-1">
          (Phase 2)
        </div>
      </div>
    </div>

    <div v-if="error" class="mt-4 text-sm text-red-600">
      {{ error }}
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

function formatDateTime(date: Date): string {
  return date.toLocaleString('ru-RU')
}
</script>


