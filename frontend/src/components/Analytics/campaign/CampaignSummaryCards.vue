<template>
  <Card padding="lg">
    <div class="flex items-start justify-between gap-4">
      <div>
        <h2 class="text-lg font-semibold text-neutral-900">Сводка по кампании</h2>
        <p class="text-xs text-neutral-500" v-if="campaign">ID: {{ campaign.id }}</p>
      </div>
      <div v-if="campaign" class="text-xs text-neutral-500">Обновлено: {{ formatDate(campaign.updated_at) }}</div>
    </div>

    <div v-if="!campaign" class="mt-4 text-sm text-neutral-500">Нет данных</div>

    <div v-else class="grid grid-cols-2 lg:grid-cols-5 gap-4 mt-4">
      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">Кампания</div>
        <div class="text-sm font-semibold text-neutral-900 truncate" :title="campaign.label">
          {{ campaign.label }}
        </div>
      </div>
      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">Статус</div>
        <div class="text-sm font-semibold text-neutral-900">{{ formatStatus(campaign.status) }}</div>
      </div>
      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">Файлов</div>
        <div class="text-sm font-semibold text-neutral-900">{{ campaign.assets_count }}</div>
      </div>
      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">ROI</div>
        <div class="text-sm font-semibold text-neutral-900">{{ formatRoi(campaign.roi) }}</div>
      </div>

      <div class="rounded-lg border border-neutral-200 p-4">
        <div class="text-xs text-neutral-500 mb-1">Ср. вовлеченность</div>
        <div class="text-sm font-semibold text-neutral-900">
          {{ campaign.avg_engagement_minutes != null ? `${campaign.avg_engagement_minutes.toFixed(1)} мин` : '—' }}
        </div>
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

function formatStatus(status: string): string {
  const s = String(status || '').toLowerCase()
  if (s === 'draft') return 'Черновик'
  if (s === 'active') return 'Активна'
  if (s === 'completed') return 'Завершена'
  if (s === 'archived') return 'Архив'
  return status || '—'
}
</script>


