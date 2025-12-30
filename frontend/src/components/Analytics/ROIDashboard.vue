<template>
  <Card padding="lg">
    <div class="flex items-center justify-between gap-4 mb-4">
      <div>
        <h2 class="text-lg font-semibold text-neutral-900">ROI — сводка</h2>
        <p class="text-xs text-neutral-500">Оценка на основе допущений и измеримых метрик</p>
      </div>
      <div class="text-sm font-semibold text-neutral-900">
        ROI: {{ roiText }}
      </div>
    </div>

    <div v-if="!data" class="py-10 text-center text-neutral-500">
      <svg class="w-10 h-10 mx-auto text-neutral-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-6m4 6V7m4 10v-4M5 21h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v14a2 2 0 002 2z" />
      </svg>
      <div class="mt-3 text-sm">Нет данных за выбранный период</div>
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-5 gap-4">
      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">Экономия времени</div>
        <div class="text-sm font-semibold text-neutral-900">{{ money(data.breakdown.time_savings_usd) }}</div>
      </div>
      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">Экономия на reuse</div>
        <div class="text-sm font-semibold text-neutral-900">{{ money(data.breakdown.reuse_savings_usd) }}</div>
      </div>
      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">Compliance</div>
        <div class="text-sm font-semibold text-neutral-900">{{ money(data.breakdown.compliance_savings_usd) }}</div>
      </div>
      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">Хранилище</div>
        <div class="text-sm font-semibold text-neutral-900">{{ money(data.breakdown.storage_savings_usd) }}</div>
      </div>
      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">Стоимость DAM</div>
        <div class="text-sm font-semibold text-neutral-900">{{ money(data.dam_monthly_cost_usd) }}</div>
      </div>
    </div>

    <div v-if="data" class="mt-4 text-xs text-neutral-500">
      MAU: {{ data.measured.mau }} · Reuse rate: {{ data.measured.reuse_rate }}%
    </div>
  </Card>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import Card from '@/components/Common/Card.vue'
import type { RoiSummaryResponse } from '@/stores/analyticsStore'

const props = defineProps<{
  data: RoiSummaryResponse | null
}>()

const roiText = computed(() => {
  if (!props.data) return '—'
  if (props.data.roi_percent === null) return '—'
  return `${props.data.roi_percent.toFixed(2)}%`
})

function money(v: number): string {
  try {
    return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v)
  } catch {
    return `$${Number(v || 0).toFixed(0)}`
  }
}
</script>


