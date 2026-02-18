<template>
  <Card padding="lg">
    <div class="flex items-center justify-between gap-4 mb-4">
      <h3 class="text-base font-semibold text-neutral-900">Использование функций</h3>
      <div class="text-xs text-neutral-500">30 дней</div>
    </div>

    <div v-if="rows.length === 0" class="text-sm text-neutral-500">Нет данных</div>
    <div v-else class="overflow-auto border border-neutral-200 rounded-lg">
      <table class="min-w-full text-sm">
        <thead class="bg-neutral-50">
          <tr class="text-left">
            <th class="px-3 py-2 font-semibold text-neutral-700">Функция</th>
            <th class="px-3 py-2 font-semibold text-neutral-700">Пользователей</th>
            <th class="px-3 py-2 font-semibold text-neutral-700">Adoption, %</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.feature_name" class="border-t border-neutral-200">
            <td class="px-3 py-2">{{ row.feature_name }}</td>
            <td class="px-3 py-2">{{ row.users_count }}</td>
            <td class="px-3 py-2">{{ formatPercent(row.adoption_rate_percent) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </Card>
</template>

<script setup lang="ts">
import Card from '@/components/Common/Card.vue'

defineProps<{
  rows: Array<{ feature_name: string; users_count: number; adoption_rate_percent: number }>
}>()

function formatPercent(value: number): string {
  if (!Number.isFinite(value)) return '—'
  return `${value.toFixed(1)}%`
}
</script>
