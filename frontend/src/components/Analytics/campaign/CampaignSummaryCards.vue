<template>
  <Card padding="lg">
    <div class="flex items-start justify-between gap-4">
      <div>
        <h2 class="text-lg font-semibold text-neutral-900">Campaign Summary</h2>
        <p class="text-xs text-neutral-500" v-if="campaign">ID: {{ campaign.id }}</p>
      </div>
      <div v-if="campaign" class="text-xs text-neutral-500">Updated: {{ formatDate(campaign.updated_at) }}</div>
    </div>

    <div v-if="!campaign" class="mt-4 text-sm text-neutral-500">Нет данных</div>

    <div v-else class="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">Campaign</div>
        <div class="text-sm font-semibold text-neutral-900 truncate" :title="campaign.label">
          {{ campaign.label }}
        </div>
      </div>
      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">Status</div>
        <div class="text-sm font-semibold text-neutral-900">{{ campaign.status }}</div>
      </div>
      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">Assets</div>
        <div class="text-sm font-semibold text-neutral-900">{{ campaign.assets_count }}</div>
      </div>
      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">ROI</div>
        <div class="text-sm font-semibold text-neutral-900">{{ formatRoi(campaign.roi) }}</div>
      </div>
    </div>
  </Card>
</template>

<script setup lang="ts">
import Card from '@/components/Common/Card.vue'
import type { CampaignDashboardResponse } from '@/stores/analyticsStore'

defineProps<{
  campaign: CampaignDashboardResponse['campaign']
}>()

function formatDate(value: string): string {
  try {
    return new Date(value).toLocaleString('ru-RU')
  } catch {
    return value
  }
}

function formatRoi(value: number | null): string {
  if (value === null || value === undefined) return '—'
  return `${value.toFixed(2)}`
}
</script>


