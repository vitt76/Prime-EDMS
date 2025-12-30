<template>
  <div class="container mx-auto px-4 py-6">

      <Card padding="lg" class="mb-6">
        <div class="flex items-center justify-between gap-4">
          <div class="text-sm text-neutral-700">Нулевые поиски → пробелы контента</div>
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
            <h3 class="text-base font-semibold text-neutral-900">Content Gaps</h3>
            <div class="text-xs text-neutral-500">top null queries</div>
          </div>
          <div v-if="gaps.length === 0" class="text-sm text-neutral-500">Нет данных</div>
          <div v-else class="space-y-3">
            <div v-for="row in gaps" :key="row.query" class="p-3 border border-neutral-200 rounded-lg bg-white">
              <div class="flex items-center justify-between gap-3">
                <div class="text-sm font-semibold text-neutral-900">{{ row.query }}</div>
                <div class="text-xs text-neutral-500">{{ row.count }}</div>
              </div>
              <div class="text-sm text-neutral-700 mt-1">{{ row.recommendation }}</div>
            </div>
          </div>
        </Card>

        <Card padding="lg">
          <div class="flex items-center justify-between gap-4 mb-4">
            <h3 class="text-base font-semibold text-neutral-900">Compliance alerts</h3>
            <div class="text-xs text-neutral-500">metadata completeness</div>
          </div>
          <div v-if="alerts.length === 0" class="text-sm text-neutral-500">Нет алертов</div>
          <div v-else class="space-y-3">
            <div v-for="a in alerts" :key="a.id" class="p-3 border border-neutral-200 rounded-lg bg-white">
              <div class="text-sm font-semibold text-neutral-900">{{ a.title }}</div>
              <div class="text-sm text-neutral-700 mt-1">{{ a.message }}</div>
              <div class="text-xs text-neutral-500 mt-1">
                Doc: {{ a.document_id ?? '—' }} • {{ formatDate(a.created_at) }}
              </div>
            </div>
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

const gaps = computed(() => analyticsStore.contentGaps?.recommendations || [])
const alerts = computed(() => analyticsStore.metadataComplianceAlerts?.results || [])

function formatDate(v: any): string {
  try {
    if (!v) return '—'
    return new Date(v).toLocaleString()
  } catch {
    return String(v || '—')
  }
}

async function refresh(): Promise<void> {
  await Promise.all([
    analyticsStore.fetchContentGaps({ days: 30 }),
    analyticsStore.fetchMetadataComplianceAlerts({ limit: 50 }),
  ])
}

onMounted(async () => {
  await refresh()
})
</script>


