<template>
  <Card padding="lg">
    <div class="flex items-center justify-between gap-4 mb-4">
      <h3 class="text-base font-semibold text-neutral-900">Alerts</h3>
      <div class="text-xs text-neutral-500">{{ rows.length }} active</div>
    </div>

    <div v-if="rows.length === 0" class="text-sm text-neutral-500">Нет активных предупреждений</div>

    <div v-else class="space-y-2">
      <div
        v-for="a in rows"
        :key="a.id"
        class="p-3 rounded-md border border-neutral-200 bg-white"
      >
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-2">
            <span :class="badgeClass(a.severity)">{{ a.severity }}</span>
            <div class="font-semibold text-neutral-900">{{ a.title }}</div>
          </div>
          <div class="text-xs text-neutral-500">{{ formatDate(a.created_at) }}</div>
        </div>
        <div class="text-sm text-neutral-700 mt-1">{{ a.message }}</div>
        <div class="text-xs text-neutral-500 mt-1">
          <span v-if="a.document_id">Document: {{ a.document_id }}</span>
          <span v-if="a.campaign_id" class="ml-2">Campaign: {{ a.campaign_id }}</span>
        </div>
      </div>
    </div>
  </Card>
</template>

<script setup lang="ts">
import Card from '@/components/Common/Card.vue'
import type { AnalyticsAlertRow } from '@/stores/analyticsStore'

defineProps<{
  rows: AnalyticsAlertRow[]
}>()

function badgeClass(severity: AnalyticsAlertRow['severity']): string {
  if (severity === 'critical') return 'text-xs px-2 py-0.5 rounded bg-red-50 text-red-700 border border-red-200'
  if (severity === 'warning') return 'text-xs px-2 py-0.5 rounded bg-yellow-50 text-yellow-700 border border-yellow-200'
  return 'text-xs px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200'
}

function formatDate(value: string): string {
  try {
    return new Date(value).toLocaleString('ru-RU')
  } catch {
    return value
  }
}
</script>


