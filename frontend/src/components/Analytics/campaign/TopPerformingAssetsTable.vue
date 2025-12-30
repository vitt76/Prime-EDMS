<template>
  <Card padding="lg">
    <div class="flex items-center justify-between gap-4 mb-4">
      <h3 class="text-base font-semibold text-neutral-900">ТОП файлов кампании</h3>
      <div class="text-xs text-neutral-500">7-дневный тренд</div>
    </div>

    <div class="overflow-auto border border-neutral-200 rounded-lg">
      <table class="min-w-full text-sm">
        <thead class="bg-neutral-50">
          <tr class="text-left">
            <th class="px-3 py-2 font-semibold text-neutral-700">Файл</th>
            <th class="px-3 py-2 font-semibold text-neutral-700">Скачивания</th>
            <th class="px-3 py-2 font-semibold text-neutral-700">Просмотры</th>
            <th class="px-3 py-2 font-semibold text-neutral-700">Тренд (7 дней)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="rows.length === 0">
            <td class="px-3 py-4 text-neutral-500" colspan="4">Нет данных за выбранный период</td>
          </tr>
          <tr
            v-for="row in rows"
            :key="row.document_id"
            class="border-t border-neutral-200 hover:bg-neutral-50"
          >
            <td class="px-3 py-2">
              <div class="font-medium text-neutral-900">
                {{ row.document__label || `Document #${row.document_id}` }}
              </div>
              <div class="text-xs text-neutral-500">ID: {{ row.document_id }}</div>
            </td>
            <td class="px-3 py-2">{{ row.downloads }}</td>
            <td class="px-3 py-2">{{ row.views }}</td>
            <td class="px-3 py-2">
              <Sparkline :values="row.sparkline_data || []" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </Card>
</template>

<script setup lang="ts">
import Card from '@/components/Common/Card.vue'
import Sparkline from '@/components/Analytics/campaign/Sparkline.vue'
import type { CampaignTopAssetRow } from '@/stores/analyticsStore'

defineProps<{
  rows: CampaignTopAssetRow[]
}>()
</script>


