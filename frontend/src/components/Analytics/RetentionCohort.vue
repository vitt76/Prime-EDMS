<template>
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
</template>

<script setup lang="ts">
import Card from '@/components/Common/Card.vue'
import { computed } from 'vue'

export interface CohortRow {
  cohort_week_start: string
  cohort_size: number
  retention: Array<{ week_index: number; retention_rate: number }>
}

const props = defineProps<{
  cohorts: CohortRow[]
}>()

const retentionWeeks = computed(() => {
  const first = props.cohorts?.[0]
  const len = first?.retention?.length || 0
  return Array.from({ length: len }, (_, i) => i)
})
</script>
