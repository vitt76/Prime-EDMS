<template>
  <Card padding="lg">
    <div class="flex items-center justify-between gap-4 mb-4">
      <div>
        <h2 class="text-lg font-semibold text-neutral-900">ROI Dashboard</h2>
        <p class="text-xs text-neutral-500">Executive summary (assumption-driven)</p>
      </div>
      <div class="text-sm font-semibold text-neutral-900">
        ROI: {{ roiText }}
      </div>
    </div>

    <div v-if="!data" class="text-sm text-neutral-500">Нет данных</div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-5 gap-4">
      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">Time savings</div>
        <div class="text-sm font-semibold text-neutral-900">${{ data.breakdown.time_savings_usd.toFixed(0) }}</div>
      </div>
      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">Reuse savings</div>
        <div class="text-sm font-semibold text-neutral-900">${{ data.breakdown.reuse_savings_usd.toFixed(0) }}</div>
      </div>
      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">Compliance</div>
        <div class="text-sm font-semibold text-neutral-900">${{ data.breakdown.compliance_savings_usd.toFixed(0) }}</div>
      </div>
      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">Storage</div>
        <div class="text-sm font-semibold text-neutral-900">${{ data.breakdown.storage_savings_usd.toFixed(0) }}</div>
      </div>
      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">DAM cost</div>
        <div class="text-sm font-semibold text-neutral-900">${{ data.dam_monthly_cost_usd.toFixed(0) }}</div>
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
</script>


